from dataclasses import dataclass
from torch import Tensor
import torch.nn as nn
import torch
from argmaxtools.compress.palettize import _fake_palettize
import inspect
import math
from argmaxtools.utils import get_logger
from argmaxtools.finetune.finetuner import FinetuneConfig

logger = get_logger(__name__)

SUPPORTED_MODULES = (nn.Conv2d)


@dataclass
class PLoRAFinetuneConfig(FinetuneConfig):
    # LoRA configuration
    rank: int = 16
    lora_init: str = 'regular'
    dtype: torch.dtype = torch.float32

    # Mixed-bit palettization
    palettize_weight: bool = True
    recipe: str = None

    # Outlier decomposition
    decompose: bool = False


class PalettizedLoRAConv2d(nn.Module):
    """
    Args:
        module: `nn.Conv2d` layer module to adapt.
        rank: The rank of the approximation.
        nbits: Number of bits for palettization.
        alpha: Scaling parameter.
        dtype: `torch.float32` is supported.
        palettize_weight: Only LoRA modules are attached if set to `False`.
        lora_init: Type of initialization for LoRA modules.
            `regular`: Regular initialization written on the LoRA paper.
            `loftp.T`: LoftQ initialization with `T` steps.
        (LoftQ paper: https://arxiv.org/abs/2310.08659)
    """

    def __init__(self,
                 module,
                 rank,
                 nbits,
                 dtype=torch.float32,
                 palettize_weight=True,
                 lora_init='regular'):
        # TODO: support torch.float16 dtype
        if module.weight.dtype != torch.float32:
            logger.warning(f"Module weight {torch.float32} is supported for training. "
                           f"{module.weight.dtype} is given.")
        if not isinstance(module, nn.Conv2d):
            raise TypeError(f"`nn.Conv2d` layer module is supported. {type(module)} is given.")

        # copy the input args of the given module
        sig = inspect.signature(nn.Conv2d.__init__)
        module_kwargs = {
            param.name: getattr(module, param.name, None) for param in sig.parameters.values()
            }
        module_kwargs['bias'] = False if module_kwargs['bias'] is None else True
        module_kwargs.pop('self')

        super().__init__()
        pretrained_w = module.weight.data.detach().clone()
        device = pretrained_w.device

        self.lora_init = lora_init
        self.rank = rank
        self.nbits = nbits
        self.pretrained = nn.Conv2d(**module_kwargs).to(dtype).to(device)
        module_kwargs['bias'] = False

        self.in_channels = module_kwargs.pop('in_channels')
        self.out_channels = module_kwargs.pop('out_channels')

        self.loraA = nn.Conv2d(module.in_channels, self.rank, **module_kwargs).to(dtype).to(device)
        self.loraB = nn.Conv2d(self.rank, module.out_channels, **module_kwargs).to(dtype).to(device)

        self.init_error = [0, 0]  # [palett error w/ regular init, palett error w/ selected init]
        palett_w = pretrained_w

        # Initialize LoRA modules and calculate the initialization error.
        # `regular` initialization: `A` is initialized with `kaiming_uniform` and
        # `B` is initialized with `zeros`.
        if self.lora_init == 'regular':
            nn.init.kaiming_uniform_(self.loraA.weight, a=math.sqrt(5))
            nn.init.zeros_(self.loraB.weight)
            if palettize_weight:
                if nbits == 16:
                    palett_w = pretrained_w.to(torch.float16)
                    palett_w = palett_w.to(torch.float32)
                else:
                    palett_w = _fake_palettize(
                        pretrained_w.to(torch.float16),
                        self.nbits)[0].to(torch.float32)
                self.init_error = [
                    x + torch.norm(
                        pretrained_w[:, :, 0, 0] - palett_w[:, :, 0, 0] -
                        self.loraB.weight[:, :, 0, 0]@self.loraA.weight[:, :, 0, 0]
                        ).item() for x in self.init_error
                    ]
        # `loftp.T` initialization: LoftQ initialization with `T` steps.
        elif 'loftp' in self.lora_init:
            if nbits == 16:
                raise TypeError("LoftQ initialization is not supported for 16-bit palettization.")
            nn.init.zeros_(self.loraA.weight)
            nn.init.zeros_(self.loraB.weight)
            T = int(self.lora_init.split('.')[-1])
            if palettize_weight:
                self.init_error = self.loftp_(
                    palett_w,
                    self.loraA.weight,
                    self.loraB.weight,
                    T,
                    self.nbits)
        else:
            raise TypeError(f"{self.lora_init} is not a valid initialization option.")

        self.pretrained.weight = nn.Parameter(palett_w, requires_grad=False)

        if module.bias is not None:
            pretrained_b = module.bias.data.detach().clone()

            # no need to palettize bias
            palett_b = pretrained_b
            self.pretrained.bias = nn.Parameter(palett_b, requires_grad=False)

        # ensure that the weights in A and B are trainable
        self.loraA.weight.requires_grad = True
        self.loraB.weight.requires_grad = True

    def forward(self, input: Tensor) -> Tensor:
        pretrained_out = self.pretrained(input)
        lora_out = self.loraA(input)
        lora_out = self.loraB(lora_out)
        return pretrained_out + lora_out

    def loftp_(self, palett_w, loraA, loraB, T, nbits):
        """
        Args:
            w: Weight matrix with shape (m, n, 1, 1).
            loraA: LoRA A matrix with shape (rank, m, 1, 1)
            loraB: LoRA B matrix with shape (n, rank, 1, 1).
            T: Alternating step for the LoftQ algorithm.
            nbits: Number of bits for palettization.
        """
        if len(palett_w.shape) != 4:
            raise TypeError("Only works with 4-dim tensor. "
                            f"{len(palett_w.shape)}-dim tensor is given.")

        w = palett_w[:, :, 0, 0].T
        rank = loraA.shape[0]
        Q = _fake_palettize(w.to(torch.float16), nbits=nbits)[0].to(torch.float32)
        A = loraA[:, :, 0, 0].T
        B = loraB[:, :, 0, 0].T
        init_error = [torch.norm(w - Q - A@B).item()]
        with torch.no_grad():
            for t in range(T):
                # casting to float16 for using kmeans1d for palettization
                diff = w - A@B
                Q = _fake_palettize(diff.to(torch.float16), nbits=nbits)[0].to(torch.float32)
                palett_err = w - Q
                U, S, Vh = torch.linalg.svd(palett_err, full_matrices=False)
                A = U[:, :rank]@torch.diag(S[:rank])
                B = Vh[:rank, :]
            init_error.append(
                torch.norm(w - Q - A@B).item()
            )
            palett_w[:, :, 0, 0] = Q.T
            loraA[:, :, 0, 0] = A.T
            loraB[:, :, 0, 0] = B.T
        return init_error


def freeze_parameters_(model):
    for param in model.parameters():
        param.requires_grad_(False)


def update_model_(model,
                  recipe: dict,
                  rank: int,
                  palettize_weight=True,
                  dtype=torch.float32,
                  lora_init='regular',
                  verbose=True):
    '''
    In-place replaces layers with palettized LoRA layers according to the recipe.

    Args:
        model: The model to update
        recipe: The palettization recipe
        rank: Rank of LoRA
    '''

    freeze_parameters_(model)

    for layer_key in recipe.keys():
        layer_key_parent = '.'.join(layer_key.split('.')[:-1])
        layer_key_child = layer_key.split('.')[-1]

        for name, module in model.named_modules():
            if name == layer_key_parent:
                if type(getattr(module, layer_key_child)) == nn.Conv2d:
                    setattr(
                        module,
                        layer_key_child,
                        PalettizedLoRAConv2d(
                            module=getattr(module, layer_key_child),
                            rank=rank,
                            nbits=recipe[layer_key]['n_bits'],
                            palettize_weight=palettize_weight,
                            dtype=dtype,
                            lora_init=lora_init
                        )
                    )
                else:
                    raise TypeError(f"{type(module)} is not supported.")
                if verbose:
                    init_error = getattr(module, layer_key_child).init_error
                    init_error = [float(f"{x:.3f}") for x in init_error]
                    logger.info(f"{layer_key} {init_error}")

    if verbose:
        logger.info(f"Overhead bits: {calculate_overhead_bits(model)}")


def calculate_palettization_diff_svd(model, recipe):
    palettization_diff_svd = {}
    for layer_key in recipe.keys():
        for name, module in model.named_modules():
            if name == layer_key:
                w = module.weight.data.detach().clone()
                palett_w, _ = _fake_palettize(w,
                                              recipe[layer_key]['n_bits'])
                palett_diff = w - palett_w
                palettization_diff_svd[layer_key] = torch.linalg.svdvals(palett_diff[:, :, 0, 0])
    return palettization_diff_svd


def loftp_(palett_w, loraA, loraB, T, nbits):
    """
    Args:
        w: Weight matrix with shape (m, n, 1, 1).
        loraA: LoRA A matrix with shape (rank, m, 1, 1)
        loraB: LoRA B matrix with shape (n, rank, 1, 1).
        T: Alternating step for the LoftQ algorithm.
        nbits: Number of bits for palettization.
    """
    if len(palett_w.shape) != 4:
        raise TypeError(f"Only works with 4-dim tensor. {len(palett_w.shape)}-dim tensor is given.")

    w = palett_w[:, :, 0, 0].T
    rank = loraA.shape[0]
    Q, _ = _fake_palettize(w, nbits=nbits)
    A = loraA[:, :, 0, 0].T
    B = loraB[:, :, 0, 0].T
    init_error = [torch.norm(w - Q - A@B).item()]
    with torch.no_grad():
        for t in range(T):
            Q, _ = _fake_palettize(w - A@B, nbits=nbits)
            palett_err = w - Q
            U, S, Vh = torch.linalg.svd(palett_err, full_matrices=False)
            A = U[:, :rank]@torch.diag(S[:rank])
            B = Vh[:rank, :]
        init_error.append(
            torch.norm(w - Q - A@B).item()
        )
        palett_w[:, :, 0, 0] = Q.T
        loraA[:, :, 0, 0] = A.T
        loraB[:, :, 0, 0] = B.T
    return init_error


def calculate_overhead_bits(model: torch.nn.Module) -> float:
    countlora = 0
    countreg = 0
    for name, parameter in model.named_parameters():
        if 'outlier' in name:
            continue
        if 'lora' in name:
            countlora += parameter.numel()
        else:
            countreg += parameter.numel()
    return (1.*countlora/countreg)*16


def filter_recipe(recipe: dict, model: torch.nn.Module) -> dict:
    filtered_recipe = {k.removesuffix(".inlier_module"): v for k, v in recipe.items()}
    for n, m in model.named_modules():
        if n in filtered_recipe and not isinstance(m, SUPPORTED_MODULES):
            logger.warning(
                f"Layer {n}[{m.__class__.__name__}] is not supported. "
                f"Removing {n} from recipe."
            )
            filtered_recipe.pop(n)

    return filtered_recipe
