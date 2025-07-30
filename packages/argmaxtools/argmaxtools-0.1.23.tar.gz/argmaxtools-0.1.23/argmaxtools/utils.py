#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

import logging
import os
import subprocess
import torch
from typing import Optional


def get_logger(name: str, level: int = logging.INFO) -> logging.RootLogger:
    logging.basicConfig()
    logger = logging.getLogger(name)
    # Allow setting the log level via the LOG_LEVEL environment variable
    # This is useful when running a script with a different log level than the default
    # Example: LOG_LEVEL=DEBUG python script.py
    level = os.getenv("LOG_LEVEL") or level
    logger.setLevel(level)
    return logger


logger = get_logger(__name__)


def get_fastest_device():
    device = "cpu"
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.backends.cudnn.is_available():
        device = "cuda"
    return device


def _maybe_git_clone(out_dir: str,
                     hub_url: str,
                     repo_name: str,
                     repo_owner: str,
                     commit_hash: Optional[str] = None,) -> str:
    """ Helper function for cloning a git repo from GitHub
    """
    out_path = os.path.join(out_dir, repo_name)

    if os.path.exists(out_path):
        is_inside_worktree = subprocess.check_output(
            "git rev-parse --is-inside-work-tree",
            cwd=out_path, shell=True, text=True
        ).strip() == "true"

        assert is_inside_worktree, f"{out_path} is not a git repo"
        logger.info(f"Reusing repo at {out_path}")
    else:
        # Clone repo if not cached already
        os.makedirs(out_dir, exist_ok=True)
        if subprocess.check_call(f"git clone https://{hub_url}/{repo_owner}/{repo_name}.git",
                                 cwd=out_dir, shell=True):
            raise RuntimeError(f"Failed to clone {repo_name} repo")
        logger.info(f"Successfuly cloned {repo_name} repo")

    if commit_hash is not None:
        # Checkout commit hash if specified
        commit_exists = subprocess.check_output(
            f"git fetch && git cat-file -t {commit_hash}",
            cwd=out_path, shell=True, text=True
        ).strip() == "commit"

        if not commit_exists:
            raise ValueError(f"{commit_hash} does not exist in {repo_name}")

        if subprocess.check_call(f"git reset --hard {commit_hash}",
                                 cwd=out_path, shell=True):
            raise RuntimeError(f"Failed to checkout {commit_hash} in {repo_name}")

        logger.info(f"Successfuly checked out {commit_hash} in {repo_name}")
    else:
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=out_path, text=True).strip()
        logger.info(f"Using unmodified HEAD commit hash: {commit_hash}")

    return out_path, commit_hash


# State dict source adapters for argmaxtools.nn.Attention and argmaxtools.nn.FFN
def linear_to_conv2d_map_attention(state_dict, prefix, local_metadata, strict,
                                   missing_keys, unexpected_keys, error_msgs):
    common_name_mappings = {
        "q_proj": ["q_proj", "query_proj", "q", "linear_q", "query_net"],
        "k_proj": ["k_proj", "key_proj", "k", "linear_k", "key_net"],
        "v_proj": ["v_proj", "val_proj", "v", "value_proj", "linear_v", "value_net"],
        "o_proj": ["o_proj", "out_proj", "o", "output_proj", "linear_out", "out_projection"],
    }
    return linear_to_conv2d_map_base(common_name_mappings, state_dict, prefix, local_metadata,
                                     strict, missing_keys, unexpected_keys, error_msgs)


def linear_to_conv2d_map_ffn(state_dict, prefix, local_metadata, strict,
                             missing_keys, unexpected_keys, error_msgs):
    common_name_mappings = {
        "fc1": ["fc1", "wi", "linear1", "linear_1", "dense_in"],
        "fc2": ["fc2", "wo", "linear2", "linear_2", "dense_out"],
    }
    return linear_to_conv2d_map_base(common_name_mappings, state_dict, prefix, local_metadata,
                                     strict, missing_keys, unexpected_keys, error_msgs)


def linear_to_conv2d_map_mlp(state_dict, prefix, local_metadata, strict,
                             missing_keys, unexpected_keys, error_msgs):
    common_name_mappings = {
        "up_proj": ["up_proj"],
        "down_proj": ["down_proj"],
        "gate_proj": ["gate_proj"],
    }
    return linear_to_conv2d_map_base(common_name_mappings, state_dict, prefix, local_metadata,
                                     strict, missing_keys, unexpected_keys, error_msgs)


def linear_to_conv2d_map_base(common_name_mappings, state_dict, prefix, local_metadata,
                              strict, missing_keys, unexpected_keys, error_msgs):
    """ Map state_dict from nn.Linear to nn.Conv2d
    """
    for tgt_name, src_names in common_name_mappings.items():

        matches = list(filter(
            lambda k: any(prefix + src_name + ".weight" == k for src_name in src_names),
            state_dict))
        if len(matches) > 1:
            raise ValueError(f"More than 1 match for {tgt_name}: {matches}")

        elif len(matches) == 0:
            raise KeyError(
                f"Could not match {tgt_name} to any of the state_dict keys: {list(state_dict)}")

        elif len(matches) == 1:
            matched_src_name = ".".join(matches[0].rsplit(".")[:-1])
            logger.debug(f"Matched {prefix + matched_src_name} -> {prefix + tgt_name}")

        # Expand dims on weight if needed
        weight = state_dict.pop(matched_src_name + ".weight")
        if len(weight.shape) == 2:
            weight = weight[:, :, None, None]
        state_dict[prefix + tgt_name + ".weight"] = weight

        # Impute bias with zeros if missing in state_dict
        bias_key = matched_src_name + ".bias"

        if tgt_name in ["k_proj", "up_proj", "down_proj", "gate_proj"]:
            # Key projection bias is redundant, discard it
            if bias_key in state_dict:
                state_dict.pop(bias_key)
                logger.debug(
                    f"Discarding redundant {tgt_name}.bias in state_dict with key: {bias_key}")
        else:
            if bias_key not in state_dict:
                embed_dim = weight.shape[0]
                bias = weight.new_zeros((embed_dim,))
                logger.debug(
                    f"{bias_key} parameter is missing in the state_dict, imputing with zeros. "
                    "Verify this is expected!")
            else:
                bias = state_dict.pop(bias_key)

            state_dict[prefix + tgt_name + ".bias"] = bias
