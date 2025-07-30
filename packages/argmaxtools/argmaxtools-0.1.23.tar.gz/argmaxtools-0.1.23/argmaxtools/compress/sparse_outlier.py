#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

from copy import deepcopy
from beartype.typing import Tuple
import coremltools as ct
from coremltools.optimize.coreml import (
    OpThresholdPrunerConfig,
    OptimizationConfig,
    prune_weights,
)

import torch
import torch.nn as nn

from argmaxtools.utils import get_logger

logger = get_logger(__name__)

# Decomposable nn.Module types (with ".weight")
DECOMPOSABLE_MODULES = (nn.Embedding, nn.Linear, nn.Conv1d, nn.Conv2d, nn.Conv3d)
MIN_COMPRESSIBLE_PARAMETER_NUMEL = 1e5
MAX_CHANNELS = 16385

# Reasonable number of standard deviations for outlier detection
ALLOWED_NUM_STD = [2, 3, 4, 5, 6]
OUTLIER_NUM_STD = 3


class SparseOutlierDecomposer:
    """ Patches supported torch.nn.Module instances to decompose the weight matrices into
    inlier and outlier components and to compress the sparse outlier components in Core ML
    """
    @staticmethod
    def patch_module(module: nn.Module):
        """ Patch module to decompose its weight matrices into inlier and outlier components
        """
        def _patch_module(module: nn.Module):
            for name, child_module in module.named_children():
                if isinstance(child_module, DECOMPOSABLE_MODULES) and \
                   child_module.weight.shape[0] < MAX_CHANNELS and \
                   child_module.weight.numel() > MIN_COMPRESSIBLE_PARAMETER_NUMEL:
                    setattr(module, name, DecomposedModule(child_module, OUTLIER_NUM_STD))

        module.apply(_patch_module)

    @staticmethod
    def compress_outlier(mlmodel: ct.models.MLModel) -> ct.models.MLModel:
        # Only compress the outlier components with sparse representation in Core ML
        op_name_configs = {
            name: OpThresholdPrunerConfig(threshold=1e-6) if "outlier_module" in name else None
            for name in ct.optimize.coreml.get_weights_metadata(mlmodel)
        }

        # Since outlier weights are already zero-masked, a simple threshold is sufficient
        config = OptimizationConfig(op_name_configs=op_name_configs)
        mlmodel = prune_weights(mlmodel, config=config)
        return mlmodel


class DecomposedModule(nn.Module):
    def __init__(self, module: nn.Module, num_std: int):
        super().__init__()
        assert hasattr(module, "weight")
        w_inlier, w_outlier, _ = decompose(module.weight.data.clone(), num_std)

        self.inlier_module = deepcopy(module)
        self.inlier_module.weight.data = w_inlier

        self.outlier_module = deepcopy(module)
        self.outlier_module.weight.data = w_outlier
        self.outlier_module.bias = None

    def forward(self, x):
        return self.inlier_module(x) + self.outlier_module(x)

    @property
    def weight(self):
        logger.debug("Accessing weight of a decomposed module is not recommended")
        return self.inlier_module.weight + self.outlier_module.weight


def decompose(w: torch.Tensor, num_std: int) -> Tuple[torch.Tensor]:
    assert num_std > 2.

    outlier_inds = (w - w.mean()).abs() > w.std() * num_std

    # Inlier component is the regular weight matrix
    w_inlier = w.clone()
    w_inlier[outlier_inds] = 0.

    # Outlier component is an distinct parameter to be compressed in Core ML
    # forward_pass_hook is registered to compute the contribution of the outlier component
    w_outlier = w.clone()
    w_outlier[outlier_inds.logical_not()] = 0.

    outlier_numel = w_outlier.eq(0.).logical_not().int().sum().item()
    outlier_stats = dict(
        outlier_sparsity=w_outlier.eq(0.).float().mean().item(),
        bits_overhead=1 + outlier_numel / w_outlier.numel() * 16,
        num_std=num_std,
    )

    logger.info(
        f"Decomposed with w>mean+{num_std}*std, "
        f"shape={w.shape}, "
        f"outlier_count={w_outlier.bool().sum().item()}, "
        f"outlier_sparsity={outlier_stats['outlier_sparsity']:.3g}, "
        f"bits_overhead={outlier_stats['bits_overhead']:.3f}"
    )
    return w_inlier, w_outlier, outlier_stats
