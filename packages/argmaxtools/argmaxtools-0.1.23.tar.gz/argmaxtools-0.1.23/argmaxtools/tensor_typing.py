#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

from beartype.typing import Tuple, Union
from jaxtyping import Float
from torch import Tensor

__doc__ = """
argmaxtools uses `beartype` and `jaxtyping` packages to enforce dtype and shapes
torch.nn.module.forward() inputs and outputs. This is intended to:
    - Help catch silent broadcasting issues, shape and dtype mismatches etc. earlier
    - Offer actionable and localized error messages
    - Offer interpretable documentation for compute graph interfaces
"""

# _sdpa.SDPAImplementation type hints
# Inputs
SDPAQueryType = Float[Tensor, "batch embed_dim 1 q_seq_len"]
SDPAKeyType = Float[Tensor, "batch embed_dim 1 kv_seq_len"]
SDPAValueType = Float[Tensor, "batch embed_dim 1 kv_seq_len"]
SDPAKeyPaddingMaskType = Float[Tensor, "batch kv_seq_len"]
SDPAQKMaskType = Union[
    Float[Tensor, "batch n_heads q_seq_len kv_seq_len"],
    Float[Tensor, "batch q_seq_len kv_seq_len"],
]
RoPEEmbedsType = Float[Tensor, "batch_size per_head_dim q_seq_len"]

# Outputs
SDPAOutputAttnType = Float[Tensor, "batch embed_dim 1 q_seq_len"]
SDPAOutputAttnWeightsType = Float[Tensor, "batch n_heads q_seq_len kv_seq_len"]
SDPAOutputType = Union[
    SDPAOutputAttnType,
    Tuple[SDPAOutputAttnType, SDPAOutputAttnWeightsType]
]

# ._sdpa.SharedSplitKVCached additional type hints
# Inputs
SharedSplitKVCachedSDPAKeyType = Tuple[
    Float[Tensor, "batch embed_dim 1 kv_seq_len"],
    Float[Tensor, "batch embed_dim 1 q_seq_len"]
]
SharedSplitKVCachedSDPAValueType = Tuple[
    Float[Tensor, "batch embed_dim 1 kv_seq_len"],
    Float[Tensor, "batch embed_dim 1 q_seq_len"]
]
SharedSplitKVCachedSDPAQKMaskType = Float[Tensor, "batch q_seq_len q_seq_len"]

# nn.Attention type hints
# Inputs
InputEmbedsType = Float[Tensor, "batch embed_dim 1 q_seq_len"]
AttentionMaskType = Float[Tensor, "batch kv_seq_len"]
KVCacheType = Float[Tensor, "batch embed_dim 1 kv_seq_len"]
EncoderOutputEmbedsType = Float[Tensor, "batch embed_dim 1 _"]

# Outputs
SelfAttentionReturnType = Tuple[Float[Tensor, "batch embed_dim 1 q_seq_len"]]
EncoderDecoderAttentionReturnType = Tuple[Float[Tensor, "batch embed_dim 1 q_seq_len"]]
KVCachedSelfAttentionReturnType = Tuple[
    Float[Tensor, "batch embed_dim 1 q_seq_len"],  # outputs
    Float[Tensor, "batch embed_dim 1 q_seq_len"],  # current_key
    Float[Tensor, "batch embed_dim 1 q_seq_len"]   # current_value
]

SelfAttentionWAWReturnType = Tuple[
    Float[Tensor, "batch embed_dim 1 q_seq_len"],
    SDPAOutputAttnWeightsType
]
EncoderDecoderAttentionWAWReturnType = Tuple[
    Float[Tensor, "batch embed_dim 1 q_seq_len"],
    SDPAOutputAttnWeightsType]
KVCachedSelfAttentionWAWReturnType = Tuple[
    Float[Tensor, "batch embed_dim 1 q_seq_len"],  # outputs
    Float[Tensor, "batch embed_dim 1 q_seq_len"],  # current_key
    Float[Tensor, "batch embed_dim 1 q_seq_len"],  # current_value
    SDPAOutputAttnWeightsType,                     # attn_weights
]

# Combine into union
SelfAttentionReturnType = Union[
    SelfAttentionReturnType, SelfAttentionWAWReturnType]
EncoderDecoderAttentionReturnType = Union[
    EncoderDecoderAttentionReturnType, EncoderDecoderAttentionWAWReturnType]
KVCachedSelfAttentionReturnType = Union[
    KVCachedSelfAttentionReturnType, KVCachedSelfAttentionWAWReturnType]
