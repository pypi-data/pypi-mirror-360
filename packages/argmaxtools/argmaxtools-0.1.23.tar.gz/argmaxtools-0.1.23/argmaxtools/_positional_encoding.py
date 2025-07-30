# Code from:
# https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py
import torch


def rope(
        mh_q: torch.Tensor,
        mh_k: torch.Tensor,
        cos: torch.Tensor,
        sin: torch.Tensor,
        unsqueeze_dim=1
):
    """Applies Rotary Position Embedding to the query and key tensors.

    Args:
        mh_q (`torch.Tensor`): The query tensor.
        mh_k (`torch.Tensor`): The key tensor.
        cos (`torch.Tensor`): The cosine part of the rotary embedding.
        sin (`torch.Tensor`): The sine part of the rotary embedding.
        unsqueeze_dim (`int`, *optional*, defaults to 1):
            The 'unsqueeze_dim' argument specifies the dimension along which to unsqueeze
            cos[position_ids] and sin[position_ids] so that they can be properly broadcasted
            to the dimensions of q and k. For example, note that cos[position_ids] and
            sin[position_ids] have the shape [batch_size, seq_len, head_dim]. Then, if q and
            k have the shape [batch_size, heads, seq_len, head_dim], then setting
            unsqueeze_dim=1 makes cos[position_ids] and sin[position_ids] broadcastable
            to the shapes of q and k. Similarly, if q and k have
            the shape [batch_size, seq_len, heads, head_dim], then set unsqueeze_dim=2.
    Returns:
        `tuple(torch.Tensor)` comprising of the query and key tensors rotated
            using the Rotary Position Embedding.
    """
    def rotate_half(x):
        """Rotates half the hidden dims of the input."""
        x1 = x[..., :x.shape[-2]//2, :]
        x2 = x[..., x.shape[-2]//2:, :]
        return torch.cat((-x2, x1), dim=-2)

    cos = cos.unsqueeze(unsqueeze_dim)
    sin = sin.unsqueeze(unsqueeze_dim)
    mh_q_embed = (mh_q * cos) + (rotate_half(mh_q) * sin)
    mh_k_embed = (mh_k * cos) + (rotate_half(mh_k) * sin)
    return mh_q_embed, mh_k_embed
