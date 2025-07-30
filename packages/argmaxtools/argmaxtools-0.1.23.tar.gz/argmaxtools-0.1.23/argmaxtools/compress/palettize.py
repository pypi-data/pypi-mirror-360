#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
import coremltools as ct

import json
import numpy as np
import os

import torch
import torch.nn as nn

from tqdm import tqdm, trange
from typing import Callable, List, Optional

from argmaxtools.utils import get_fastest_device, get_logger
from argmaxtools.compress.utils import compress_subbyte_data, decompress_subbyte_data
from argmaxtools.compress.sparse_outlier import SparseOutlierDecomposer
from argmaxtools.test_utils import _create_coreml_model, _create_coreml_inputs
import argmaxtools.test_utils as argmaxtools_test_utils

logger = get_logger(__name__)


# See https://apple.github.io/coremltools/docs-guides/source/post-training-palettization.html
SUPPORTED_NBITS = [1, 2, 3, 4, 6, 8]

# Accelerate compression by disregarding insignificantly small parameter tensors
MIN_COMPRESSIBLE_PARAMETER_NUMEL = 1e5

# Skip palettizing highly-sparse tensors
MAX_SPARSITY = 0.8

# Test data batch size for end-to-end signal integrity tests
TEST_BATCH_SIZE = 32

# Number of mixed-bit recipe models to build and measure
NUM_MIXED_BIT_RECIPES = 3

# Palettizable nn.Module types (with ".weight")
PALETTIZABLE_MODULES = (nn.Linear, nn.Conv1d, nn.Conv2d, nn.Conv3d)

# Number of highest-sensitiity tensors to skip
DONT_PALETTIZE_TOP_K = 3

# Tolerance for the fraction of results that exhibit inverted trends
# (when lower bit precision outperforms higher bit precision)
INVERTED_RESULT_THR = 0.1

# Whether to apply sparse outlier decomposition (and only palettize the inlier component)
SPARSE_OUTLIER_DECOMPOSITION = False

# number of channels in a group
PALETTIZATION_GROUP_SIZE = None


class Palettizer(ABC):
    """ Abstract class that defines the template for Mixed-Bit Palettization
    of `torch.nn.Module` derived models
    """
    @abstractmethod
    def init_model_and_test_data(self, **cfg) -> None:
        """ Initializes the model to analyze for compression and a single batch of test
        data to quickly measure the end-to-end impact of various compression functions
        """
        pass

    @property
    @abstractmethod
    def default_dtype(self) -> torch.dtype:
        """ The default weight and activation precision for the model
        """
        pass

    @abstractmethod
    def divergence_fn(self, reference: torch.Tensor, proxy: torch.Tensor) -> float:
        """ Quantifies the difference across original and compressed model outputs
        """
        pass

    def __init__(self, model_version: str, cache_dir: str) -> None:
        """
        Args:
            model_version:  String that identifies the model configuration. This is generally
                            the name of the model as published on huggingface.co/models
            cache_dir:      Intermediate compressed artifacts will be cached to this directory
                            for rapid recipe generation and warm restarts. Cache size might exceed
                            original model size!

        """
        self.model_version = model_version
        dev = get_fastest_device()

        model, test_data = self.init_model_and_test_data(model_version)
        if SPARSE_OUTLIER_DECOMPOSITION:
            SparseOutlierDecomposer.patch_module(model)

        self.model = model.to(self.default_dtype).to(dev)
        self.coreml_model = None

        self.test_data = {
            k: v.to(self.default_dtype).to(dev) if v.dtype.is_floating_point else v.to(dev)
            for k, v in test_data.items()
        }

        # Cache reference output
        self.reference_out = self.model(**self.test_data)
        if isinstance(self.reference_out, (list, tuple)):
            logger.info("Testing based on outputs[0] from the model")
            self.reference_out = self.reference_out[0]

        # Stubs for results
        self.compressible_modules = _get_compressible_modules(self.model)
        self.per_layer_results = defaultdict(dict)
        self.cumulative_results = defaultdict(OrderedDict)
        self.mixed_bit_recipes = defaultdict(dict)
        self.mixed_bit_recipes_results = defaultdict(dict)

        self.cache_dir = os.path.join(cache_dir, model_version)
        if os.path.exists(self.cache_dir):
            logger.warning(f"Reusing cached intermediate results from {self.cache_dir}")
        else:
            logger.warning(f"Caching intermediate results to {self.cache_dir}")
            os.makedirs(self.cache_dir)

        with open(os.path.join(self.cache_dir, "metadata.json"), "w") as f:
            metadata = {
                "class": self.__class__.__name__,
                "model_version": model_version
            }
            json.dump(metadata, f, indent=2)

    def compute_divergence(self, compression_fn: Callable, restore_fn: Callable) -> float:
        """ Quantify the impact of compression_fn on end-to-end model function
        """
        compression_fn(self.model)
        proxy = self.model(**self.test_data)
        if isinstance(proxy, (list, tuple)):
            logger.debug(
                "Detected multiple model outputs, divergence will only consider outputs[0]")
            proxy = proxy[0]

        divergence = self.divergence_fn(self.reference_out, proxy)
        restore_fn(self.model)
        return divergence

    def fake_palettize(self, name, parameter_tensor, nbits):
        """ Apply nbits-bit palettization to the parameter tensor without
        changing the numerical precision
        """
        cache_path = os.path.join(self.cache_dir, name + f"_{nbits}-bit.npy")

        if os.path.exists(cache_path):
            compressed = np.load(cache_path, allow_pickle=True).item()

            # Reconstruct indices from packed bits
            lut = compressed.pop("lut")
            shape = compressed.pop("shape")
            indices = decompress_subbyte_data(**compressed)

            fake_palettized = torch.from_numpy(lut[indices]).view(shape)
            fake_palettized = fake_palettized.to(parameter_tensor.dtype)
            fake_palettized = fake_palettized.to(parameter_tensor.device)
        else:
            fake_palettized, compressed = _fake_palettize(
                parameter_tensor=parameter_tensor,
                nbits=nbits,
            )
            np.save(cache_path, compressed)

        return fake_palettized

    def profile_per_layer_response(self):
        """ Computes the end-to-end divergence observed while palettizing
        with nbits one layer at a time
        """
        logger.info("Profiling per-layer response to post-training weight palettization")

        per_layer_results_json = os.path.join(self.cache_dir, "per_layer_results.json")
        if os.path.exists(per_layer_results_json):
            with open(per_layer_results_json, "r") as f:
                self.per_layer_results.update(json.load(f))

        for nbits in tqdm(SUPPORTED_NBITS):
            for idx, (name, compressible_module) in enumerate(self.compressible_modules.items()):
                if str(nbits) in self.per_layer_results and \
                   name in self.per_layer_results[str(nbits)]:
                    logger.info(f"[{nbits}-bit] Reusing divergence computation for {name}")
                    continue

                original = compressible_module.weight.data
                fake_palettized = self.fake_palettize(name, compressible_module.weight.data, nbits)

                def current_compression_fn(model):
                    compressible_module.weight.data = fake_palettized

                def current_restore_fn(model):
                    compressible_module.weight.data = original

                self.per_layer_results[str(nbits)][name] = self.compute_divergence(
                    current_compression_fn,
                    current_restore_fn
                )

                logger.info(
                    f"[{nbits}-bit] Module {idx+1}/{len(self.compressible_modules)}={name}: "
                    f"divergence={self.per_layer_results[str(nbits)][name]:.3g}")

            with open(per_layer_results_json, "w") as f:
                json.dump(self.per_layer_results, f, indent=2)

    def profile_cumulative_response(self):
        """ Computes the end-to-end divergence observed while palettizing
        with an increasing number of layers with nbits
        """
        logger.info("Profiling cumulative response to post-training weight palettization")

        cumulative_results_json_path = os.path.join(self.cache_dir, "cumulative_results.json")
        if os.path.exists(cumulative_results_json_path):
            with open(cumulative_results_json_path, "r") as f:
                self.cumulative_results.update(json.load(f))

        # Ensure per-layer profiling was completed (reuse cache if exists)
        self.profile_per_layer_response()

        for nbits in tqdm(SUPPORTED_NBITS):
            if len(self.cumulative_results[str(nbits)]) == len(self.compressible_modules):
                logger.info(
                    f"Reusing cached results from {cumulative_results_json_path} for nbits={nbits}"
                )
                continue

            # Sorted in ascending divergence order to delay impact as much as possible
            sorted_modules = sorted(
                self.per_layer_results[str(nbits)].items(),
                key=lambda kv: kv[1]
            )

            for idx, (name, per_layer_divergence) in enumerate(sorted_modules):
                compressible_module = self.compressible_modules[name]

                if name in self.cumulative_results[str(nbits)]:
                    logger.debug(f"[{nbits}-bit] Reusing divergence computation for {name}")
                    continue

                fake_palettized = self.fake_palettize(name, compressible_module.weight.data, nbits)

                def current_compression_fn(model):
                    compressible_module.weight.data = fake_palettized

                # Will restore entire model after each outer loop iteration
                def current_restore_fn(model): return model

                self.cumulative_results[str(nbits)][name] = self.compute_divergence(
                    current_compression_fn,
                    current_restore_fn
                )

                logger.info(
                    f"[{nbits}-bit] Module {idx+1}/{len(self.compressible_modules)}={name}: \n"
                    f"cumulative div={self.cumulative_results[str(nbits)][name]:.3g}, "
                    f"per-layer div={per_layer_divergence:.3g}")

            # Save recipe
            with open(cumulative_results_json_path, "w") as f:
                json.dump(self.cumulative_results, f, indent=2)

            # Restore full model
            self.restore_pristine_model()

    def profile_mixed_bit_response(self,
                                   allowed_nbits: List[int] = SUPPORTED_NBITS,
                                   top_k_in_default_dtype: Optional[int] = DONT_PALETTIZE_TOP_K
                                   ) -> None:
        """
        Generate mixed-bit recipes via per-layer divergence thresholding
        """
        assert all(nbits in SUPPORTED_NBITS for nbits in allowed_nbits)

        recipes_json_path = os.path.join(self.cache_dir, "recipes.json")
        recipe_results_json_path = os.path.join(self.cache_dir, "recipe_results.json")

        # Sanity check per-layer results
        self._sanity_check_per_layer_results()

        # Ensure per-layer profiling was completed (reuse cache if exists)
        self.profile_per_layer_response()

        # margin from each end of the spectrum
        thresholds = np.geomspace(
            max(self.per_layer_results[str(min(allowed_nbits))].values()) * 0.98,
            max(self.per_layer_results[str(max(allowed_nbits))].values()) * 1.02,
            NUM_MIXED_BIT_RECIPES
        )

        # find (if any) layers to keep in default_dtype
        layers_in_default_dtype = []
        if top_k_in_default_dtype is not None:
            assert top_k_in_default_dtype >= 0
            layers_in_default_dtype = []

            for allowed_nbit in allowed_nbits:
                per_layer = self.per_layer_results[str(allowed_nbit)]
                layer_names, per_layer_divs = zip(*[(k, v) for k, v in per_layer.items()])
                assert top_k_in_default_dtype < len(per_layer_divs)
                top_k_inds = np.array(per_layer_divs).argsort()[::-1][:top_k_in_default_dtype]
                top_k_layers = [layer_names[i] for i in top_k_inds]
                logger.info(
                    f"[{allowed_nbit}-bit] Keeping {top_k_in_default_dtype}: {top_k_layers}")
                layers_in_default_dtype.extend(top_k_layers)
            layers_in_default_dtype = list(set(layers_in_default_dtype))
            logger.info(
                f"Preserving precision of {len(layers_in_default_dtype)} layers with default dtype")

        total_numel = sum([
            module.weight.data.numel() for module in self.compressible_modules.values()
        ])

        for i in trange(len(thresholds)):
            recipe = {}
            for name in self.compressible_modules:
                recipe[name] = self.default_dtype.itemsize * 8

                if name not in layers_in_default_dtype:
                    for nbits in allowed_nbits:
                        if self.per_layer_results[str(nbits)][name] < thresholds[i]:
                            recipe[name] = nbits
                            break
                else:
                    logger.info(
                        f"Skipped {name} due to top_k_in_default_dtype={top_k_in_default_dtype}"
                    )

            # Update recipe keys from indices to average bit precision
            compressed_nbits = sum([
                self.compressible_modules[name].weight.data.numel() * nbits
                for name, nbits in recipe.items()
            ])

            average_bit_precision = compressed_nbits / total_numel

            recipe_key = f"{average_bit_precision:.1f}"
            self.mixed_bit_recipes[recipe_key] = recipe

            # Evaluate the end-to-end impact of recipe
            self.mixed_bit_recipes_results[
                average_bit_precision] = self.apply_recipe_torch(recipe_key)

            # Save recipe
            with open(recipes_json_path, "w") as f:
                json.dump(self.mixed_bit_recipes, f, indent=2)

        # Save recipe results
        with open(recipe_results_json_path, "w") as f:
            json.dump(self.mixed_bit_recipes_results, f, indent=2)

    def _sanity_check_per_layer_results(self):
        """ Ensure per-layer results consistently decrease with increasing precision
        """
        inverted = 0
        total = 0

        bit_precision_pairs = [
            (SUPPORTED_NBITS[lower], SUPPORTED_NBITS[higher])
            for lower in range(len(SUPPORTED_NBITS))
            for higher in range(lower+1, len(SUPPORTED_NBITS))
        ]

        for module in self.compressible_modules:
            for lower, higher in bit_precision_pairs:
                lower_bit_div = self.per_layer_results[str(lower)][module]
                higher_bit_div = self.per_layer_results[str(higher)][module]
                if lower_bit_div < higher_bit_div:
                    logger.debug(
                        "Inverted trend in per-layer results!"
                        f"{lower}-bit result is better than {higher}-bit result for {module}: "
                        f"{lower_bit_div:.3g} < {higher_bit_div:.3g}"
                    )
                    inverted += 1
                total += 1

        percent_inverted = inverted / max(total, 1)
        if percent_inverted > INVERTED_RESULT_THR:
            raise ValueError(
                f"{percent_inverted*100.:.1f}% of results are inverted "
                "(lower bit precision outperforms higher bit precision) "
                "Please use higher TEST_BATCH_SIZE and "
                "double check your Palettizer subclass implementation.")
        else:
            logger.info(
                "Passed sanity check for inverted results: "
                f"{percent_inverted*100.:.1f}% < {INVERTED_RESULT_THR*100}%")

    def apply_recipe_torch(self, recipe_key: str, restore: bool = True) -> float:
        """
        Given a (potentially mixed-bit) per-layer nbits recipe, fake palettizes
        self.model in-place to simulate the impact
        """
        if recipe_key not in self.mixed_bit_recipes:
            raise KeyError(
                f"{recipe_key} not found in recipes. Available: {list(self.mixed_bit_recipes)}"
            )

        # Simulate recipe while stayin in self.default_dtype
        for name, nbits in self.mixed_bit_recipes[recipe_key].items():
            compressible_module = self.compressible_modules[name]
            if nbits in SUPPORTED_NBITS:
                fake_palettized = self.fake_palettize(name, compressible_module.weight.data, nbits)
                compressible_module.weight.data = fake_palettized

        # Measure divergence from reference outputs
        divergence_due_to_recipe = self.compute_divergence(
            compression_fn=lambda x: x,
            restore_fn=lambda x: x,
        )

        if restore:
            self.restore_pristine_model()

        return divergence_due_to_recipe

    def convert_current_model_to_coreml(self, output_names: List[str]) -> None:
        """ Converts the current state of self.model to Core ML
        """
        # Slice batch_size=1 from test data
        self.torch_jit_trace_data = {
            k: v[0:1].to(torch.float32)
            if v.dtype.is_floating_point else v[0:1]
            for k, v in self.test_data.items()
        }

        self.sample_coreml_data = _create_coreml_inputs(
            self.torch_jit_trace_data)

        # Get the model states if they exist
        self.argmax_model_states = getattr(self, "argmax_model_states", None)

        self.coreml_model = _create_coreml_model(
            self.model.to(torch.float32),
            self.torch_jit_trace_data,
            output_names,
            self.argmax_model_states)

    def apply_recipe_coreml(self, recipe_key: str) -> None:
        """ Given a layer name to nbits precision recipe,
        compress the input coreml_model
        """
        if PALETTIZATION_GROUP_SIZE is not None:
            assert argmaxtools_test_utils.TEST_MIN_DEPLOYMENT_TARGET >= ct.target.macOS15, \
                "`per_grouped_channel` palettization requires iOS18/macOS15 or later"

        recipe = self.mixed_bit_recipes[recipe_key]

        # Keep track of precision stats
        precision_stats = {
            nbits: {'num_tensors': 0, 'numel': 0} for nbits in SUPPORTED_NBITS + [16]
        }

        # Override 32-bits with 16-bits (in case recipe had to be generated with torch.float32)
        recipe = {k: v if v != 32 else 16 for k, v in recipe.items()}

        assert all(nbits in SUPPORTED_NBITS + [16] for nbits in recipe.values()), \
            f"Some nbits values in the recipe are illegal. Allowed values: {SUPPORTED_NBITS}"

        # Hash np.ndarrays to be able to match torch tensors to mil tensors
        # (associate torch names to mil tensors)
        def get_tensor_hash(tensor: np.ndarray) -> float:
            """ Hash np.float16 np.ndarrays to np.float64 value
            """
            hash_indices = [0, 13, 39, 42]
            assert tensor.dtype == np.float16 and tensor.size >= max(hash_indices)
            t = tensor.ravel()

            def float2bits(val): return np.unpackbits(val.view(np.uint8))
            return np.packbits([float2bits(t[hi:hi+1]) for hi in hash_indices]).view(np.float64)[0]

        hashed_recipe = {}
        for torch_module_name, nbits in recipe.items():
            tensor = self.compressible_modules[torch_module_name]
            tensor = tensor.weight.data.cpu().numpy().astype(np.float16)
            hashed_key = get_tensor_hash(tensor)
            if hashed_key in hashed_recipe:
                raise KeyError("Hash collision! Please try modifying get_tensor_hash above")

            hashed_recipe[hashed_key] = {"nbits": nbits, "name": torch_module_name}

        def _find_nbits_in_recipe(parameter_tensor: np.ndarray):
            """ Given Core ML weight tensor, find the corresponding precision in the recipe
            with corresponding PyTorch module names
            """
            if parameter_tensor.size < MIN_COMPRESSIBLE_PARAMETER_NUMEL:
                logger.info(
                    "\tSkipping palettization: Small parameter tensor "
                    f"({parameter_tensor.size}<{MIN_COMPRESSIBLE_PARAMETER_NUMEL})")
                return None

            if parameter_tensor.dtype != np.float16:
                logger.info(
                    "\tSkipping palettization: dtype ({parameter_tensor.dtype}) != np.float16")
                return None

            tensor_hash = get_tensor_hash(parameter_tensor)
            hashes = list(hashed_recipe)
            pdist = np.abs(np.array(hashes) - tensor_hash)

            if pdist.min() != 0:
                logger.info(
                    "\tSkipping palettization: Hash not found in recipe "
                    f"(closest hash distance={pdist.min():.3g})")
                return None

            matched = pdist.argmin()
            target_nbits = hashed_recipe[hashes[matched]]["nbits"]
            target_module = hashed_recipe[hashes[matched]]["name"]

            logger.info(f"\t{target_module}:\tCompressing with {target_nbits}-bit palette")
            precision_stats[target_nbits]['num_tensors'] += 1
            precision_stats[target_nbits]['numel'] += np.prod(parameter_tensor.shape)

            # 16-bits imply no palettization
            if target_nbits == 16:
                precision_stats[16]['num_tensors'] += 1
                precision_stats[16]['numel'] += np.prod(parameter_tensor.shape)
                logger.info(
                    f"\t{target_module}:\tSkipping palettization: Recipe specifies float16")
                return None

            return target_nbits

        op_name_configs = {}
        weight_metadata = ct.optimize.coreml.get_weights_metadata(
            self.coreml_model, weight_threshold=MIN_COMPRESSIBLE_PARAMETER_NUMEL)

        granularity = (
            "per_grouped_channel" if PALETTIZATION_GROUP_SIZE is not None else "per_tensor"
        )

        # Map layer to weight precision
        for name, metadata in weight_metadata.items():
            nbits = _find_nbits_in_recipe(metadata.val)
            logger.info(f"\t{name}: nbits={nbits}")
            if nbits is None:
                op_name_configs[name] = None
            else:
                op_name_configs[name] = ct.optimize.coreml.OpPalettizerConfig(
                    mode="kmeans",
                    nbits=nbits,
                    weight_threshold=int(MIN_COMPRESSIBLE_PARAMETER_NUMEL),
                    group_size=PALETTIZATION_GROUP_SIZE,
                    granularity=granularity
                )

        config = ct.optimize.coreml.OptimizationConfig(op_name_configs=op_name_configs)
        self.coreml_model = ct.optimize.coreml.palettize_weights(
            self.coreml_model,
            config=config)

        from pprint import pprint
        total_bits = sum(
            nbits_stats["numel"] * nbits for nbits, nbits_stats in precision_stats.items())
        total_numel = sum(
            nbits_stats["numel"] for nbits, nbits_stats in precision_stats.items())
        final_precision = total_bits / total_numel

        logger.info(
            f"\t Final achieved precision is {final_precision:.2f}-bit from a {recipe_key}-bit"
            " recipe. The difference (if any) is due to parameters not tracked in recipe."
        )
        pprint(precision_stats)

        # Switch to sparse representation for the weight outlier component
        if SPARSE_OUTLIER_DECOMPOSITION:
            self.coreml_model = SparseOutlierDecomposer.compress_outlier(self.coreml_model)
            logger.info("Applied sparse compression to outlier components")

        return final_precision

    def restore_pristine_model(self):
        """ Restores full pristine model
        """
        model = self.init_model_and_test_data(self.model_version)[0]
        if SPARSE_OUTLIER_DECOMPOSITION:
            SparseOutlierDecomposer.patch_module(model)
        self.model = model.to(self.default_dtype).to(get_fastest_device())
        self.compressible_modules = _get_compressible_modules(self.model)

    def create_recipe_with_forced_nbits(self, allowed_nbits: List[int] = SUPPORTED_NBITS):
        """ Create a recipe with a forced nbits precision for all layers
        """
        self.mixed_bit_recipes = {
            nbits: {
                name: nbits for name in self.compressible_modules
            } for nbits in allowed_nbits
        }

    def plot_specs(self, f, ax):
        ax.set_yscale("log")
        ax.set_xlabel("Model Size Reduction (%)")
        ax.set_ylabel("Output Divergence")
        ax.set_title(f"{self.model_version} Palettization Response Curves")
        ax.legend()
        f.savefig(os.path.join(self.cache_dir, "cumulative_response_plots.png"))
        f.show()

    def plot(self):
        """ Plot cumulative results per bit precision and mixed-bit recipe results
        """
        # Generate/cache data to plot if it wasn't computed already
        self.profile_cumulative_response()

        try:
            import matplotlib.pyplot as plt
        except ModuleNotFoundError:
            logger.warning("Bail from plot() due to missing matplotlib package")
            return

        f, ax = plt.subplots(1, 1, figsize=(6, 3))

        for nbits in SUPPORTED_NBITS:
            numels = []
            divs = []
            for name, divergence in self.cumulative_results[str(nbits)].items():
                module = self.compressible_modules[name]
                divs.append(divergence)
                numels.append(module.weight.data.numel())

            progress = np.cumsum(np.array(numels)).astype(np.float32)
            progress *= 1. / progress[-1]
            max_reduction_ratio = nbits / (self.default_dtype.itemsize * 8)
            size_reduction_progress = 1. - (1. - progress * (1. - max_reduction_ratio))
            ax.plot(size_reduction_progress * 100., divs, label=f"{nbits}-bit")

            mixed_bit_plot = []

        if len(self.mixed_bit_recipes_results) > 0:
            for average_nbits, divergence in self.mixed_bit_recipes_results.items():
                size_reduction = 1. - (average_nbits / (self.default_dtype.itemsize * 8))
                mixed_bit_plot.append((size_reduction * 100., divergence))

            ax.plot(
                [m[0] for m in mixed_bit_plot], [m[1] for m in mixed_bit_plot],
                label="mixed-bit")

        self.plot_specs(f, ax)
        f.savefig(os.path.join(self.cache_dir, "cumulative_response_plots.png"))
        f.show()


def _get_compressible_modules(model: torch.nn.Module,
                              min_numel: int = MIN_COMPRESSIBLE_PARAMETER_NUMEL,
                              max_sparsity: float = MAX_SPARSITY):
    """ Returns a list of submodules that have "weight" parameters of at least min_numel to compress
    """
    compressible_submodules = {}
    compressible_numel = 0
    tot_numel = sum([
        p.numel() for p in model.parameters()]) + sum([b.numel() for b in model.buffers()])

    for name, module in model.named_modules():
        if hasattr(module, 'weight') and isinstance(module, PALETTIZABLE_MODULES):
            module_numel = module.weight.data.numel()
            module_sparsity = module.weight.data.eq(0.).float().mean().item()

            if module_numel > min_numel and module_sparsity < max_sparsity:
                compressible_submodules[name] = module
                compressible_numel += module_numel
            else:
                logger.info(
                    f"Skipping palettization for {name}: "
                    f"numel={module_numel}, sparsity={module_sparsity:.3g}")

    compressible_percent = compressible_numel / tot_numel
    logger.info(
        f"{len(compressible_submodules)} candidate tensors accounting for "
        f"{compressible_numel / 1e6:.1f}M/{tot_numel / 1e6:.1f} M total parameters "
        f"({compressible_percent * 100:.1f}% of total size is compressible)"
    )

    return compressible_submodules


# Copied from:
# https://github.com/apple/coremltools/blob/7.0b1/coremltools/optimize/coreml/_quantization_passes.py#L423
def _fake_palettize(parameter_tensor: torch.Tensor, nbits: int) -> torch.Tensor:
    """ Simulate weight palettization in PyTorch without changing the actual
    precision mirroring coremltools implementation
    """
    assert nbits in SUPPORTED_NBITS
    import coremltools.models.neural_network.quantization_utils as ctq

    def compress_kmeans(val, nbits):
        lut, indices = ctq._get_kmeans_lookup_table_and_weight(nbits, val)
        lut = lut.astype(val.dtype)
        indices = indices.astype(np.uint8)
        return lut, indices

    original = parameter_tensor.clone()
    shape = original.shape
    dtype = original.dtype
    device = original.device

    lut, indices = compress_kmeans(
        val=parameter_tensor.cpu().numpy().astype(np.float16),
        nbits=nbits
    )

    # Build compressed representation for cache
    count = indices.shape[0]
    compressed = {"count": count, "nbits": nbits, "lut": lut, "shape": shape}
    compressed["data"] = compress_subbyte_data(indices, count, nbits)

    fake_palettized = np.reshape(lut[indices], shape)
    fake_palettized = torch.from_numpy(fake_palettized).to(dtype).to(device)

    return fake_palettized, compressed
