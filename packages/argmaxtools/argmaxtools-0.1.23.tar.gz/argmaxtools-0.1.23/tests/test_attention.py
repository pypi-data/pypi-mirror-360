#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#
import copy
import coremltools as ct
import json
import os
import random
import torch
import unittest

from argmaxtools.nn import (
    Attention, AttentionType, AttentionHeadType, StatefulKVCachedAttention,
    SharedSplitKVCachedSelfAttention, StatefulSharedSplitKVCachedSelfAttention
)
from argmaxtools import _sdpa, test_utils
from argmaxtools.test_utils import CoreMLTestsMixin, median_user_latency, _get_test_cache_dir
from argmaxtools.utils import get_logger, get_fastest_device

from beartype.typing import Dict, Any, List
from pprint import pprint

GLOBAL_LATENCIES = dict()

logger = get_logger(__name__)

torch.set_grad_enabled(False)
torch.use_deterministic_algorithms(True)

# Test configuration
# whisper-large-v3
ARCH_CFG = dict(n_heads=20, embed_dim=1280, n_kv_heads=None)
INPUT_CFG = dict(batch_size=4, kv_seq_len=448, q_seq_len=1, batch_shared_kv_cache=True)

# # mistral-7b
# ARCH_CFG = dict(n_heads=32, embed_dim=4096, n_kv_heads=4)
# INPUT_CFG = dict(batch_size=1, kv_seq_len=4096, q_seq_len=1)
TEST_TORCH_DTYPE = torch.float32
TEST_DEV = get_fastest_device()
TEST_CACHE_DIR = os.getenv("TEST_CACHE_DIR", None) or "/tmp"
TEST_SDPA_IMPLEMENTATION = os.getenv("SDPA_IMPLEMENTATION", None) or _sdpa.Cat


# Disable CPU relative speedup test
# (toy test models are roughly similar in speed across CPU and ANE)
test_utils.TEST_MIN_SPEEDUP_VS_CPU = -1
test_utils.TEST_PSNR_THR = 30
test_utils.TEST_COMPUTE_UNIT = ct.ComputeUnit.CPU_AND_NE


# Nested class to avoid base unittest discovery
class AttentionTest:
    class AttentionTest(CoreMLTestsMixin, unittest.TestCase):

        _attention_class: Attention = None
        arch_args: Dict[Any] = None
        input_args: Dict[Any] = None
        test_output_names: List[str] = None

        @classmethod
        def _init_test_model(cls):
            cls.model_name = cls._attention_class.__name__
            cls.test_torch_model = cls._attention_class(
                **cls.arch_args,
            ).to(TEST_TORCH_DTYPE).to(TEST_DEV).eval()

        @classmethod
        def _maybe_init_reference_model(cls):
            pass

        @classmethod
        def _prepare_test_inputs(cls):
            raise NotImplementedError

        @classmethod
        def setUpClass(cls):
            cls.test_cache_dir = TEST_CACHE_DIR

            # Initialize test model
            cls._init_test_model()
            assert hasattr(cls, "test_torch_model")
            assert hasattr(cls, "model_name")

            # Initialize reference model (optional)
            cls._maybe_init_reference_model()

            cls.test_torch_model.sdpa_implementation = TEST_SDPA_IMPLEMENTATION
            logger.info(f"Using SDPA implementation: {TEST_SDPA_IMPLEMENTATION}")

            # Initialize test inputs
            cls.test_torch_inputs = cls._prepare_test_inputs()
            cls.test_torch_inputs = {
                k: v.to(TEST_TORCH_DTYPE).to(TEST_DEV)
                for k, v in cls.test_torch_inputs.items()
            }

            # Initialize Core ML models and test data
            super().setUpClass()

            cls.results = {}
            cls.results["config"] = {"architecture": ARCH_CFG, "input": INPUT_CFG}
            cls.results["bench"] = {
                "torch": median_user_latency(
                    lambda: cls.test_torch_model(**cls.test_torch_inputs),
                    return_flops=True,
                ),
                "coreml": median_user_latency(
                    lambda: cls.test_coreml_model.predict(cls.test_coreml_inputs)
                ),
            }

            cls.out_path = os.path.join(
                TEST_CACHE_DIR,
                f"test_{cls.__class__.__name__}.json"
            )

            with open(cls.out_path, "w") as f:
                json.dump(cls.results, f, indent=2)

        def test_torch2coreml_correctness_and_speedup(self):
            super().test_torch2coreml_correctness_and_speedup()
            GLOBAL_LATENCIES[self.__class__.__name__] = self._latencies


class TestKVCachedSelfAttention(AttentionTest.AttentionTest):
    """ Unit tests for `argmaxtools.nn.Attention` with
    `attention_type=AttentionType.KVCachedSelfAttention`
    """
    _attention_class = Attention
    arch_args = dict(attention_type=AttentionType.KVCachedSelfAttention, **ARCH_CFG)
    input_args = INPUT_CFG
    test_output_names = [
        "attention_output",
        "key_cache_update",
        "value_cache_update",
    ]

    @classmethod
    def _prepare_test_inputs(cls):
        # Decode a random token index (implies a random valid KV cache length)
        cls.decode_idx = random.randint(1, cls.input_args["kv_seq_len"])
        logger.info(
            f"Decoding {cls.decode_idx}th token of {cls.input_args['kv_seq_len']} "
            "max tokens for AttentionType.KVCachedSelfAttention"
        )

        test_torch_inputs = dict(
            input_embeds=torch.randn(
                cls.input_args["batch_size"],
                cls.arch_args["embed_dim"],
                1,
                cls.input_args["q_seq_len"]
            ),
            # 0: not masked, -1e4: masked
            key_padding_mask=torch.cat([
                    torch.zeros((
                        cls.input_args["batch_size"],
                        cls.decode_idx
                    )),
                    torch.ones((
                        cls.input_args["batch_size"],
                        cls.input_args["kv_seq_len"] - cls.decode_idx)
                    ) * -1e4
                ],
                dim=1,
            ),
            key_cache=torch.randn(
                1 if cls.input_args["batch_shared_kv_cache"] else cls.input_args["batch_size"],
                cls.test_torch_model.kv_proj_embed_dim,
                1,
                cls.input_args["kv_seq_len"]
            ),
            value_cache=torch.randn(
                1 if cls.input_args["batch_shared_kv_cache"] else cls.input_args["batch_size"],
                cls.test_torch_model.kv_proj_embed_dim,
                1,
                cls.input_args["kv_seq_len"]
            ),
            kv_cache_update_mask=torch.zeros(
                1 if cls.input_args["batch_shared_kv_cache"] else cls.input_args["batch_size"],
                cls.input_args["kv_seq_len"]
            ),
            # qk_mask=
            )

        # Update the mask to indicate the current decode index
        test_torch_inputs["kv_cache_update_mask"][:, cls.decode_idx - 1] = 1.

        return test_torch_inputs


class TestSharedSplitKVCachedSelfAttention(TestKVCachedSelfAttention):
    """ Unit tests for `argmaxtools.nn.SharedSplitKVCachedSelfAttention`
    """
    _attention_class = SharedSplitKVCachedSelfAttention
    arch_args = ARCH_CFG

    @classmethod
    def _maybe_init_reference_model(cls):
        assert hasattr(cls, "test_torch_model")
        cls.orig_torch_model = Attention(
            **cls.arch_args,
            attention_type=AttentionType.KVCachedSelfAttention
        ).to(TEST_TORCH_DTYPE).to(TEST_DEV).eval()
        cls.orig_torch_model.load_state_dict(cls.test_torch_model.state_dict())

        cls.orig_torch_inputs = super()._prepare_test_inputs()
        cls.orig_torch_inputs = {
                k: v.to(TEST_TORCH_DTYPE).to(TEST_DEV)
                for k, v in cls.orig_torch_inputs.items()
            }

    @classmethod
    def _prepare_test_inputs(cls):
        if hasattr(cls, "orig_torch_inputs"):
            logger.info("Reusing orig_torch_inputs for test_torch_model")
            test_torch_inputs = copy.deepcopy(cls.orig_torch_inputs)
        else:
            test_torch_inputs = super()._prepare_test_inputs()

        # Note: SharedSplitKVCachedSelfAttention does not read or write into the KV
        # cache for current query positions (write is assumed to happen externally)
        test_torch_inputs.pop("kv_cache_update_mask")
        test_torch_inputs["key_padding_mask"][:, cls.decode_idx - 1] = -1e4

        return test_torch_inputs

    def test_torch2torch_correctness(self):
        test_torch_outputs = self.test_torch_model(**self.test_torch_inputs)
        orig_torch_outputs = self.orig_torch_model(**self.orig_torch_inputs)
        psnr = test_utils.compute_psnr(
            orig_torch_outputs[0],
            test_torch_outputs[0],
        )
        logger.info(f"torch2torch PSNR={psnr:.2f}")
        self.assertGreater(psnr, test_utils.TEST_PSNR_THR)


class TestStatefulKVCachedSelfAttention(TestKVCachedSelfAttention):
    """ Unit tests for `argmaxtools.nn.Attention` with
    `attention_type=AttentionType.StatefulKVCachedSelfAttention`
    """
    _attention_class = StatefulKVCachedAttention
    arch_args = dict(max_kv_seq_len=INPUT_CFG["kv_seq_len"], **ARCH_CFG)

    @classmethod
    def _prepare_test_inputs(cls):
        test_torch_inputs = super()._prepare_test_inputs()
        test_torch_inputs.pop("key_cache")
        test_torch_inputs.pop("value_cache")
        return test_torch_inputs


class TestStatefulSharedSplitKVCachedSelfAttention(TestStatefulKVCachedSelfAttention):
    _attention_class = StatefulSharedSplitKVCachedSelfAttention

    @classmethod
    def _prepare_test_inputs(cls):
        test_torch_inputs = super()._prepare_test_inputs()

        # Note: SharedSplitKVCachedSelfAttention does not read or write into the KV
        # cache for current query positions (write is assumed to happen externally)
        test_torch_inputs.pop("kv_cache_update_mask")
        test_torch_inputs["key_padding_mask"][:, cls.decode_idx - 1] = -1e4

        return test_torch_inputs


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--persistent-cache-dir", default=None, type=str)
    parser.add_argument(
        "--head-type",
        choices=tuple(AttentionHeadType._member_names_),
        default="MultiHead",
    )
    parser.add_argument(
        "--sdpa-implementation",
        choices=tuple(_sdpa.__all__),
    )

    args = parser.parse_args()

    # Configure head type
    head_type = AttentionHeadType[args.head_type]
    if head_type == AttentionHeadType.MultiQuery:
        n_kv_heads = 1
    elif head_type == AttentionHeadType.GroupQuery:
        n_kv_heads = ARCH_CFG["n_heads"] // 4
    elif head_type == AttentionHeadType.MultiHead:
        n_kv_heads = None

    # Configure SDPA implementation
    sdpa_impl = args.sdpa_implementation
    if sdpa_impl is not None:
        TEST_SDPA_IMPLEMENTATION = getattr(_sdpa, sdpa_impl)

    ARCH_CFG["n_kv_heads"] = n_kv_heads

    maybe_dir = args.persistent_cache_dir
    with _get_test_cache_dir(maybe_dir) as TEST_CACHE_DIR:
        suite = unittest.TestSuite()
        suite.addTest(
            TestKVCachedSelfAttention(
                "test_torch2coreml_correctness_and_speedup"))
        suite.addTest(
            TestSharedSplitKVCachedSelfAttention(
                "test_torch2coreml_correctness_and_speedup"))
        suite.addTest(
            TestSharedSplitKVCachedSelfAttention(
                "test_torch2torch_correctness"))
        suite.addTest(
            TestStatefulKVCachedSelfAttention(
                "test_torch2coreml_correctness_and_speedup"))
        suite.addTest(
            TestStatefulSharedSplitKVCachedSelfAttention(
                "test_torch2coreml_correctness_and_speedup"))

        if os.getenv("DEBUG", False):
            suite.debug()
        else:
            runner = unittest.TextTestRunner()
            runner.run(suite)

    print(test_utils.TEST_COMPUTE_UNIT)
    pprint(ARCH_CFG)
    pprint(INPUT_CFG)
    pprint(GLOBAL_LATENCIES)
