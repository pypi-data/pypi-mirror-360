from argmaxtools.finetune.finetuner import Finetuner
from argmaxtools.finetune.lora import PLoRAFinetuneConfig
import torch
from typing import Callable, Optional
import json
from huggingface_hub import hf_hub_download
from tabulate import tabulate
from pprint import pprint
from argmaxtools.utils import get_logger
from copy import deepcopy
from argmaxtools.compress import sparse_outlier
import torch.nn as nn
import torch.nn.functional as F
import wandb
from dataclasses import dataclass
from argmaxtools.finetune.lora import update_model_, filter_recipe
from collections import OrderedDict
from pathlib import Path

RECIPE_REPO_ID = 'argmaxinc/compression_artifacts'
RECIPE_FILENAME = 'recipes.json'

logger = get_logger(__name__)


@dataclass
class QLoRAFinetuneConfig(PLoRAFinetuneConfig):
    enc_recipe: str = Optional[None]
    dec_recipe: str = Optional[None]
    save_ckpt_dir: str = "ckpt"
    train: bool = True
    local_enc_checkpoint: Optional[str] = None
    local_dec_checkpoint: Optional[str] = None
    submodule: str = "decoder"
    palettize_weight: bool = True
    encoder_attn: str = "self"
    hf_model_loader: Callable = None
    encoder_class: nn.Module = None
    decoder_class: nn.Module = None


class QLoRAFinetuner(Finetuner):
    def __init__(self,
                 model_version: str,
                 cache_dir: str,
                 config: QLoRAFinetuneConfig,
                 data: Optional[torch.utils.data.DataLoader],
                 device: Optional[torch.device]):
        super().__init__(model_version,
                         cache_dir,
                         config,
                         data,
                         device)

        if config.submodule == "full":
            assert (config.encoder_class is not None) and (config.decoder_class is not None)
        elif config.submodule == "encoder":
            assert (config.encoder_class is not None)
        elif config.submodule == "decoder":
            assert (config.decoder_class is not None)
        else:
            raise ValueError(f"Invalid submodule: {config.submodule}")

        assert (config.hf_model_loader is not None)

        # Initialize test data
        self.test_data = self.get_batch()
        if self.config.submodule == 'full':
            self.test_data['encoder'] = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in self.test_data['encoder'].items()
            }
            self.test_data['decoder'] = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in self.test_data['decoder'].items()
            }
        else:
            self.test_data = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in self.test_data.items()
            }

        self.min_val_loss = float('inf')

    def init_scheduler(self):
        return torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer,
            self.config.num_iter
        )

    def get_batch(self):
        batch = super().get_batch()
        if self.config.submodule == "full":
            batch = {k: {kk: vv.squeeze(0) for kk, vv in v.items()} for k, v in batch.items()}
        else:
            batch = {k: v.squeeze(0) for k, v in batch.items()}

        return batch

    def init_teacher_and_train_models(self):
        # Initialize HF whisper model `model`
        model = self.config.hf_model_loader(
            self.model_version,
            torch_dtype=self.default_dtype
        )
        model.to(self.dev)

        # Reference whisper submodule `teacher_model`
        if self.config.submodule == 'decoder':
            self.config.encoder_attn = 'N/A'
            teacher_model = self.config.decoder_class(model.config)
            teacher_model.load_state_dict(model.model.decoder.state_dict())
        elif self.config.submodule == 'encoder':
            if (self.config.encoder_attn != 'causal') and (self.config.encoder_attn != 'self'):
                raise ValueError(
                    f"Invalid encoder attention type: {self.encoder_attn}. "
                    "Available options: `causal`, `self`."
                )
            teacher_model = self.config.encoder_class(model.config)
            teacher_model.load_state_dict(model.model.encoder.state_dict())
        elif self.config.submodule == 'full':
            if (self.config.encoder_attn != 'causal') and (self.config.encoder_attn != 'self'):
                raise ValueError(
                    f"Invalid encoder attention type: {self.config.encoder_attn}. "
                    "Available options: `causal`, `self`."
                )
            teacher_dec_model = self.config.decoder_class(model.config)
            teacher_enc_model = self.config.encoder_class(model.config)
            teacher_dec_model.load_state_dict(model.model.decoder.state_dict())
            teacher_enc_model.load_state_dict(model.model.encoder.state_dict())
        else:
            raise ValueError(f"Invalid submodule: {self.config.submodule}")

        # FIXME(arda): This is a temporary fix for whisper. Make this configurable for other models
        self.config.recipe_repo_id = RECIPE_REPO_ID
        if self.config.submodule == 'decoder':
            self.config.recipe_subfolder = f'palettization/TextDecoder/{self.model_version}'
        elif self.config.submodule == 'encoder':
            self.config.recipe_subfolder = f'palettization/AudioEncoder/{self.model_version}'
        elif self.config.submodule == 'full':
            self.config.dec_recipe_subfolder = f'palettization/TextDecoder/{self.model_version}'
            self.config.enc_recipe_subfolder = f'palettization/AudioEncoder/{self.model_version}'
        else:
            raise ValueError(f"Invalid submodule: {self.config.submodule}")
        self.config.recipe_filename = RECIPE_FILENAME

        if self.config.submodule == 'full':
            with open(hf_hub_download(
                repo_id=self.config.recipe_repo_id,
                filename=self.config.recipe_filename,
                subfolder=self.config.dec_recipe_subfolder
            ), "r") as json_file:
                dec_recipes = json.load(json_file)
            with open(hf_hub_download(
                repo_id=self.config.recipe_repo_id,
                filename=self.config.recipe_filename,
                subfolder=self.config.enc_recipe_subfolder
            ), "r") as json_file:
                enc_recipes = json.load(json_file)
            if self.config.dec_recipe not in dec_recipes:
                raise KeyError(
                    f"{self.config.dec_recipe} is not valid for decoder. "
                    f"Available recipes: {list(dec_recipes.keys())}"
                )
            if self.config.enc_recipe not in enc_recipes:
                raise KeyError(
                    f"{self.config.enc_recipe} is not valid for encoder. "
                    f"Available recipes: {list(enc_recipes.keys())}"
                )
            filtered_dec_recipe = filter_recipe(
                dec_recipes[self.config.dec_recipe],
                teacher_dec_model
            )
            filtered_enc_recipe = filter_recipe(
                enc_recipes[self.config.enc_recipe],
                teacher_enc_model
            )
            orig_dec_recipe = {
                k: {
                    'n_bits': v
                } for k, v in filtered_dec_recipe.items() if v != 16
            }
            orig_enc_recipe = {
                k: {
                    'n_bits': v
                } for k, v in filtered_enc_recipe.items() if v != 16
            }

        else:
            with open(hf_hub_download(
                repo_id=self.config.recipe_repo_id,
                filename=self.config.recipe_filename,
                subfolder=self.config.recipe_subfolder
            ), "r") as json_file:
                recipes = json.load(json_file)

            if self.config.recipe not in recipes:
                raise KeyError(
                    f"{self.config.recipe} is not valid. Available recipes: {list(recipes.keys())}"
                )
            filtered_recipe = filter_recipe(
                recipes[self.config.recipe],
                teacher_model
            )
            orig_recipe = {
                k: {
                    'n_bits': v
                } for k, v in filtered_recipe.items() if v != 16
            }

        param_table = [[k, v] for k, v in self.config.__dict__.items()]

        print(
            "==================================================\n"
            f"Whisper {self.config.submodule.title()} Finetuning\n"
            "=================================================="
        )
        print(tabulate(param_table, tablefmt="heavy_outline"))
        if self.config.submodule == 'full':
            print(
                "==================================================\n"
                "Decoder Recipe\n"
                "=================================================="
            )
            pprint(orig_dec_recipe)
            print(
                "==================================================\n"
                "Encoder Recipe\n"
                "=================================================="
            )
            pprint(orig_enc_recipe)
        else:
            print(
                "==================================================\n"
                "Recipe\n"
                "=================================================="
            )
            pprint(orig_recipe)

        # Prepared palettized LoRA whisper text decoder for training `train_model`
        logger.info("Adding palettized LoRA layers to the train model...")
        if self.config.submodule == 'encoder' and self.config.encoder_attn == 'causal':
            raise NotImplementedError("Causal audio encoder is not supported yet.")
        elif (self.config.submodule == 'encoder') or (self.config.submodule == 'decoder'):
            train_model = deepcopy(teacher_model)
        elif self.config.submodule == 'full':
            if self.config.encoder_attn == 'causal':
                raise NotImplementedError("Causal Encoder is not supported yet.")
            else:
                train_enc_model = deepcopy(teacher_enc_model)
            train_dec_model = deepcopy(teacher_dec_model)
        else:
            raise ValueError(f"Invalid submodule: {self.config.submodule}")

        if self.config.decompose:
            if self.config.submodule == 'full':
                decompose_model_(train_enc_model, orig_enc_recipe)
                decompose_model_(train_dec_model, orig_dec_recipe)
                filtered_enc_recipe = {
                    k+".inlier_module": v for k, v in filtered_enc_recipe.items()
                }
                filtered_dec_recipe = {
                    k+".inlier_module": v for k, v in filtered_dec_recipe.items()
                }
                orig_enc_recipe = {
                    k: {'n_bits': v} for k, v in filtered_enc_recipe.items() if v != 16
                }
                orig_dec_recipe = {
                    k: {'n_bits': v} for k, v in filtered_dec_recipe.items() if v != 16
                }
            else:
                decompose_model_(train_model, orig_recipe)
                filtered_recipe = {
                    k+".inlier_module": v for k, v in filtered_recipe.items()
                }
                orig_recipe = {
                    k: {'n_bits': v} for k, v in filtered_recipe.items() if v != 16
                }

        # Load local checkpoint if provided
        if self.config.submodule == 'full':
            if (
                self.config.local_enc_checkpoint is not None
            ) and (
                self.config.local_dec_checkpoint is not None
            ):
                enc_load_state, enc_test_loss = load_state_dict_from_ckpt(
                    self.config.local_enc_checkpoint,
                    self.config
                )
                dec_load_state, dec_test_loss = load_state_dict_from_ckpt(
                    self.config.local_dec_checkpoint,
                    self.config
                )

                assert (enc_test_loss == dec_test_loss)
                self.min_val_loss = enc_test_loss

                update_model_(
                    train_enc_model,
                    orig_enc_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype
                )
                update_model_(
                    train_dec_model,
                    orig_dec_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype
                )
                remove_all_hooks(train_enc_model)
                remove_all_hooks(train_dec_model)
                train_enc_model.load_state_dict(enc_load_state, strict=False)
                train_dec_model.load_state_dict(dec_load_state, strict=False)
            else:
                update_model_(
                    train_enc_model,
                    orig_enc_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype,
                    lora_init=self.config.lora_init
                )
                update_model_(
                    train_dec_model,
                    orig_dec_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype,
                    lora_init=self.config.lora_init
                )
        else:
            if (
                self.config.local_enc_checkpoint is not None
            ) or (
                self.config.local_dec_checkpoint is not None
            ):
                if self.config.submodule == 'encoder':
                    self.config.local_checkpoint = self.config.local_enc_checkpoint
                elif self.config.submodule == 'decoder':
                    self.config.local_checkpoint = self.config.local_dec_checkpoint
                else:
                    raise ValueError(f"Invalid submodule: {self.config.submodule}")

                load_state, self.min_val_loss = load_state_dict_from_ckpt(
                    self.config.local_checkpoint,
                    self.config
                )

                update_model_(
                    train_model,
                    orig_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype
                )

                remove_all_hooks(train_model)
                train_model.load_state_dict(load_state, strict=False)

            else:
                update_model_(
                    train_model,
                    orig_recipe,
                    self.config.rank,
                    palettize_weight=self.config.palettize_weight,
                    dtype=self.default_dtype,
                    lora_init=self.config.lora_init
                )

        if self.config.submodule == 'full':
            teacher_model = nn.ModuleList([teacher_enc_model, teacher_dec_model])
            train_model = nn.ModuleList([train_enc_model, train_dec_model])
        return teacher_model, train_model

    def forward_pass(self, data_batch):
        loss = None
        div = None
        lr = None

        if self.config.submodule == 'full':
            enc_batch = data_batch['encoder']
            dec_batch = data_batch['decoder']

            # Place the encoder and decoder data batch on the device
            enc_batch = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in enc_batch.items()
            }
            dec_batch = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in dec_batch.items()
            }

            # Calculate target logits from the teacher model
            with torch.no_grad():
                enc_target = self.teacher_model[0](**enc_batch)
                teacher_dec_batch = deepcopy(dec_batch)
                teacher_dec_batch['encoder_output_embeds'] = enc_target
                target = self.teacher_model[1](**teacher_dec_batch)[0]

            enc_output = self.train_model[0](**enc_batch)
            dec_batch['encoder_output_embeds'] = enc_output
            output = self.train_model[1](**dec_batch)[0]
            criterion = nn.MSELoss()
            loss = criterion(output, target)
            div = divergence_fn(target, output)
            lr = self.optimizer.param_groups[-1]['lr']
        else:
            # Place the data batch on the device
            batch = data_batch
            batch = {
                k: v.to(self.default_dtype).to(
                    self.dev
                ) if v.dtype.is_floating_point else v.to(self.dev)
                for k, v in batch.items()
            }

            # Calculate target logits from the teacher model
            with torch.no_grad():
                target = self.teacher_model(**batch)[0]
            output = self.train_model(**batch)[0]
            criterion = nn.MSELoss()
            loss = criterion(output, target)
            div = divergence_fn(target, output)
            lr = self.optimizer.param_groups[-1]['lr']

        self.metrics = {
            "train/loss": loss.item(),
            "train/divergence": div,
            "train/lr": lr
        }

        return loss

    def get_metrics(self):
        return self.metrics

    def report_metrics(self, metrics):
        s = " | ".join([f"{k}: {v:.4f}" for k, v in metrics.items()])
        print()
        print(s)
        wandb.log({**metrics})

    def evaluate(self):
        self.train_model.eval()

        test_loss = 0
        div = 0
        val_metrics = None

        criterion = nn.MSELoss()
        if self.config.submodule == 'full':
            with torch.no_grad():
                enc_output = self.train_model[0](**self.test_data['encoder'])
                self.test_data['decoder']['encoder_output_embeds'] = enc_output
                output = self.train_model[1](**self.test_data['decoder'])[0]

                teacher_enc_output = self.teacher_model[0](**self.test_data['encoder'])
                self.test_data['decoder']['encoder_output_embeds'] = teacher_enc_output
                target = self.teacher_model[1](**self.test_data['decoder'])[0]

                div = divergence_fn(target, output)
                test_loss = criterion(output, target).item()
        else:
            with torch.no_grad():
                output = self.train_model(**self.test_data)[0]
                target = self.teacher_model(**self.test_data)[0]
                div = divergence_fn(target, output)
                test_loss = criterion(output, target).item()

        val_metrics = {
            'val/test_loss': test_loss,
            'val/div': div
        }

        if test_loss < self.min_val_loss:
            self.min_val_loss = test_loss
            logger.info(f"New min loss: {self.min_val_loss}.")
            if self.config.submodule == "full":
                save_ckpt(
                    self.train_model[0],
                    self.config,
                    self.min_val_loss,
                    'enc/'
                )
                save_ckpt(
                    self.train_model[1],
                    self.config,
                    self.min_val_loss,
                    'dec/'
                )
            else:
                save_ckpt(
                    self.train_model,
                    self.config,
                    self.min_val_loss
                )

        return val_metrics


def save_ckpt(
    model: nn.Module,
    args,
    min_loss,
    subfolder=''
):
    saved_args = deepcopy(args)
    save_dir = (
        args.save_ckpt_dir + f"/{args.model_version}/{args.submodule}/{args.lora_init}/" + subfolder
    )
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    if args.submodule == 'full':
        if 'Encoder' in model.__class__.__name__:
            saved_args.recipe = args.enc_recipe
            saved_args.recipe_subfolder = args.enc_recipe_subfolder
        elif 'Decoder' in model.__class__.__name__:
            saved_args.recipe = args.dec_recipe
            saved_args.recipe_subfolder = args.dec_recipe_subfolder
        else:
            raise ValueError(f"Invalid class name: {model.__class__.__name__}")

    full_save_dir = save_dir + f"{saved_args.recipe}-bits.pth"
    save_state = model.state_dict()
    save_state['args'] = saved_args
    save_state['test_loss'] = min_loss
    torch.save(save_state, full_save_dir)
    dict_to_save = args.__dict__

    def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except TypeError:
            return False
    dict_to_save = {k: v for k, v in dict_to_save.items() if is_jsonable(v)}
    with open(save_dir + "config.json", "w") as write_file:
        json.dump(dict_to_save, write_file, indent=4)

    logger.info(f"Saved ckpt: {full_save_dir}")


def load_state_dict_from_ckpt(
    ckpt_path: str,
    args,
):
    load_state = torch.load(ckpt_path, map_location="cpu")
    load_config = load_state.pop('args')
    assert (args.model_version == load_config.model_version)
    assert (args.rank == load_config.rank)
    assert (args.recipe_repo_id == load_config.recipe_repo_id)
    # assert (args.recipe_subfolder == load_config.recipe_subfolder)
    assert (args.recipe_filename == load_config.recipe_filename)
    assert (args.decompose == load_config.decompose)
    assert (args.submodule == load_config.submodule)
    if args.submodule == 'full':
        assert (args.enc_recipe == load_config.enc_recipe)
        assert (args.dec_recipe == load_config.dec_recipe)
    else:
        assert (args.recipe == load_config.recipe)
    assert (args.encoder_attn == load_config.encoder_attn)
    # assert (args.no_palette == load_config.no_palette)

    test_loss = load_state.pop('test_loss')
    if test_loss != 'N/A':
        logger.info(f"Loaded model min loss: {test_loss}")
    else:
        test_loss = float('inf')
    return load_state, test_loss


def decompose_model_(model, recipe, num_std: int = sparse_outlier.OUTLIER_NUM_STD):
    """Sparse outlier decomposition for the given model and recipe.
    """
    for layer_key in recipe.keys():
        layer_key_parent = '.'.join(layer_key.split('.')[:-1])
        layer_key_child = layer_key.split('.')[-1]

        def _patch_module(module: nn.Module, layer_key_child):
            for name, child_module in module.named_children():
                if name == layer_key_child and \
                   isinstance(child_module, sparse_outlier.DECOMPOSABLE_MODULES) and \
                   child_module.weight.shape[0] < sparse_outlier.MAX_CHANNELS and \
                   child_module.weight.numel() > sparse_outlier.MIN_COMPRESSIBLE_PARAMETER_NUMEL:
                    setattr(module, name, sparse_outlier.DecomposedModule(child_module, num_std))

        for name, module in model.named_modules():
            if name == layer_key_parent:
                _patch_module(module, layer_key_child)


def divergence_fn(reference: torch.Tensor, proxy: torch.Tensor) -> float:
    """ WhisperTextDecoder emits logits over a token vocabulary. The function
    used to quantify output change is KL divergence (lower the better)
    """
    div = F.kl_div(
        F.log_softmax(
            proxy.squeeze(1).cpu().to(torch.float64),
            dim=1,
            dtype=torch.float64,
        ),
        target=F.log_softmax(
            reference.squeeze(1).cpu().to(torch.float64),
            dim=1,
            dtype=torch.float64
        ),
        log_target=True,
        reduction="batchmean").item()

    if div < 0:
        raise ValueError(f"KL divergence is negative: {div}")
    return div


def remove_all_hooks(model: torch.nn.Module) -> None:
    for _, child in model._modules.items():
        if child is not None:
            if hasattr(child, "_load_state_dict_pre_hooks"):
                child._load_state_dict_pre_hooks = OrderedDict()
            remove_all_hooks(child)
