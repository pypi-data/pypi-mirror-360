#
# For licensing see accompanying LICENSE.md file.
# Copyright (C) 2023 Argmax, Inc. All Rights Reserved.
#

from abc import ABC, abstractmethod
import contextlib
import coremltools as ct
import json
import numpy as np
import os
import unittest
import shutil
import subprocess
from statistics import median
import tempfile
import time
import torch
import torch.nn as nn
from torch.utils.flop_counter import FlopCounterMode
from typing import Dict, List, Callable, Optional
from pprint import pprint
from tqdm import tqdm

from argmaxtools.utils import get_logger

logger = get_logger(__name__)

# Fixed Constants
_DEFAULT_ALLOWED_NBITS = [1, 2, 4, 6, 8]

# CoreMLTests
TEST_COMPUTE_UNIT = ct.ComputeUnit.CPU_AND_NE
TEST_COMPRESSION_MIN_SPEEDUP = 0.95
TEST_COREML_IO_FLOAT_DTYPE = np.float16
TEST_WEIGHT_COMPRESS_NBITS = 1
TEST_MIN_SPEEDUP_VS_CPU = 1.
TEST_PSNR_THR = 35
TEST_MIN_DEPLOYMENT_TARGET = ct.target.macOS13
TEST_DEFAULT_NBITS = None
TEST_COREML_PRECISION = ct.precision.FLOAT16
TEST_SKIP_SPEED_TESTS = False
TEST_COMPILE_COREML = True
TEST_COREML_INPUT_SPEC_OVERRIDE = None
TEST_BISECT_MODEL = False

# CoreMLPalettizerTests
TEST_ALLOWED_NBITS = [1, 2, 4, 6, 8]
TEST_DONT_PALETTIZE_TOP_K = 4


class CoreMLTestsMixin(unittest.TestCase):
    """ Mixin class for PyTorch to Core ML conversion,
    correctness and speedup testing
    """
    @classmethod
    def setUpClass(cls):
        assert hasattr(cls, "test_torch_model")
        assert hasattr(cls, "test_torch_inputs")
        assert hasattr(cls, "test_output_names")

        if not hasattr(cls, "test_torch_states"):
            cls.test_torch_states = None

        cls.test_coreml_inputs = _create_coreml_inputs(cls.test_torch_inputs)
        cls.test_coreml_model = _create_coreml_model(
            cls.test_torch_model,
            cls.test_torch_inputs,
            cls.test_output_names,
            cls.test_torch_states,
        )
        cls._latencies = dict()

        if TEST_DEFAULT_NBITS is not None:
            cls.test_coreml_model = _compress_coreml_model(cls.test_coreml_model)

        if TEST_BISECT_MODEL:
            cls.test_coreml_model = _bisect_coreml_model(cls.test_coreml_model, cls.test_cache_dir)

        if cls.test_torch_states is not None:
            cls.coreml_test_states = cls.test_coreml_model.make_state()
            predict_kwargs = dict(
                data=cls.test_coreml_inputs,
                state=cls.coreml_test_states)
        else:
            predict_kwargs = dict(data=cls.test_coreml_inputs,)

        cls.coreml_predict_kwargs = predict_kwargs
        cls.test_coreml_output = cls.test_coreml_model.predict(**predict_kwargs
                                                               )[cls.test_output_names[0]].squeeze()

    @classmethod
    def tearDownClass(cls):
        cls.test_coreml_inputs = None
        cls.test_coreml_model = None
        cls.test_coreml_output = None

        cls.test_torch_inputs = None
        cls.test_torch_model = None
        cls.test_torch_states = None

    def test_torch2coreml_correctness_and_speedup(self):
        """ Coverage:
        - Torchscript tracing for test torch model
        - PyTorch to Core ML conversion
        - Core ML output correctness wrt original PyTorch model
        - Core ML speedup on TEST_COMPUTE_UNIT vs CPU_ONLY
        - Core ML speedup pre- vs post-weight compression
        """
        assert hasattr(self, "test_torch_inputs")
        assert hasattr(self, "test_torch_model")
        assert hasattr(self, "test_cache_dir")

        with self.subTest(phase="torch2coreml_correctness"):
            if hasattr(self, "test_torch_output"):
                reference = self.test_torch_output
            else:
                reference = self.test_torch_model(**self.test_torch_inputs)
                if isinstance(reference, (list, tuple)):
                    reference = reference[0]

            proxy = torch.from_numpy(self.test_coreml_output).to(reference)
            psnr = compute_psnr(reference, proxy)

            logger.info(f"torch2coreml PSNR={psnr:.3g}")
            self.assertGreater(psnr, TEST_PSNR_THR)

            remove_mlpackage = TEST_COMPILE_COREML
            if hasattr(self, "create_fast_load_asset"):
                remove_mlpackage = False

            # Save asset if correctness test passes
            _save_coreml_asset(
                self.test_coreml_model,
                self.test_cache_dir,
                self.model_name,
                do_compile=TEST_COMPILE_COREML,
                do_remove_mlpackage=remove_mlpackage,
            )

        with self.subTest(phase="coreml_cpu2multiengine_speedup"):
            if not TEST_SKIP_SPEED_TESTS:
                flops = median_user_latency(
                    call_fn=lambda: self.test_torch_model(**self.test_torch_inputs)[0],
                    return_flops=True,
                )["#flops"]
                logger.info(f"#GFlops: {flops / 1e9:.3g}")

                accel_latency = median_user_latency(
                    lambda: self.test_coreml_model.predict(**self.coreml_predict_kwargs)
                )["latency"]

                # Save and reload Core ML model for CPU_ONLY execution
                tmp_path = "/tmp/model.mlpackage"
                self.test_coreml_model.save(tmp_path)
                cpu_coreml_model = ct.models.MLModel(
                    tmp_path,
                    compute_units=ct.ComputeUnit.CPU_ONLY
                )

                cpu_latency = median_user_latency(
                    lambda: cpu_coreml_model.predict(**self.coreml_predict_kwargs)
                )["latency"]

                speedup = cpu_latency / accel_latency
                logger.info(
                    f"coreml: {TEST_COMPUTE_UNIT}={accel_latency:.3g} ms "
                    f"({flops / accel_latency / 1e9:.3g} tflop/s), "
                    f"CPU_ONLY={cpu_latency:.3g} ms "
                    f"({flops / cpu_latency / 1e9:.3g} tflop/s), "
                    f"speed-up={speedup:.3g}x"
                )

                self._latencies.update({
                    "cpu_latency": cpu_latency,
                    "accel_latency": accel_latency
                })

                self.assertGreater(speedup, TEST_MIN_SPEEDUP_VS_CPU)

        if not TEST_SKIP_SPEED_TESTS:
            with self.subTest(phase="coreml_weight_compression"):
                op_config = ct.optimize.coreml.OpPalettizerConfig(
                    mode="kmeans",
                    nbits=TEST_WEIGHT_COMPRESS_NBITS,
                )

                config = ct.optimize.coreml.OptimizationConfig(
                    global_config=op_config,
                    # op_type_configs={
                    #     "gather": None  # avoid quantizing the embedding table
                    # }
                )

                compressed_model = ct.optimize.coreml.palettize_weights(
                    self.test_coreml_model,
                    config=config)

            with self.subTest(phase="coreml_compressed_model_speedup"):
                compressed_accel_latency = median_user_latency(
                    lambda: compressed_model.predict(**self.coreml_predict_kwargs)
                )["latency"]

                self._latencies.update({
                    "compressed_accel_latency": compressed_accel_latency
                })

                compression_speedup = accel_latency / compressed_accel_latency
                logger.info(
                    f"coreml: {TEST_COMPUTE_UNIT}={accel_latency:.3g} ms, "
                    f"{TEST_WEIGHT_COMPRESS_NBITS}-bit compressed "
                    f"{TEST_COMPUTE_UNIT}={compressed_accel_latency:.3g} ms, "
                    f"speedup={compression_speedup:.3g}x"
                )

                self.assertGreater(
                    compression_speedup, TEST_COMPRESSION_MIN_SPEEDUP
                )


class CoreMLPalettizerTestsMixin(unittest.TestCase):
    """ Mixin class for testing `argmaxtools.compress.palettize.Palettizer`
    and derived classes
    """
    def test_profile_response(self):
        """ Coverage:
        - Per-layer palettization
        - Cumulative palettization
        - Mixed-bit palettization
        """
        assert hasattr(self, "palettizer")

        self._check_allowed_nbits()

        from argmaxtools.compress.palettize import Palettizer
        self.palettizer: Palettizer

        with self.subTest(phase="per_layer_response"):
            self.palettizer.profile_per_layer_response()

        with self.subTest(phase="mixed_bit_response"):
            self.palettizer.profile_mixed_bit_response(
                allowed_nbits=TEST_ALLOWED_NBITS,
                top_k_in_default_dtype=TEST_DONT_PALETTIZE_TOP_K)

        # with self.subTest(phase="plot_responses"):
        #     self.palettizer.plot()

    def test_create_recipe_with_forced_nbits(self):
        assert hasattr(self, "palettizer")

        self._check_allowed_nbits()

        from argmaxtools.compress.palettize import Palettizer
        self.palettizer: Palettizer
        with self.subTest(phase="create_recipe_with_forced_nbits"):
            logger.info(f"Creating recipe with forced nbits={TEST_ALLOWED_NBITS}")
            self.palettizer.create_recipe_with_forced_nbits(
                allowed_nbits=TEST_ALLOWED_NBITS
            )

    def test_palettized_torch2coreml_conversion_and_correctness(self):
        """ Coverage:
        - Fake palettization of torch models
        (change values only, keep original precision)
        - Fake palettized torch2coreml conversion
        - Real palettization of Core ML models
        - End-to-end correctness checks
        """
        assert hasattr(self, "palettizer")
        assert hasattr(self, "output_names")

        self._check_allowed_nbits()

        for recipe_key in self.palettizer.mixed_bit_recipes:
            logger.info(f"Applying {recipe_key}-bit palettization recipe")
            # Fake palettize torch model
            self.palettizer.apply_recipe_torch(recipe_key, restore=False)

            # Convert fake palettized torch model to Core ML
            self.palettizer.convert_current_model_to_coreml(self.output_names)

            # Create Core ML predict kwargs for stateful model compatibility
            if self.palettizer.argmax_model_states is not None:
                self.palettizer.coreml_test_states = self.palettizer.coreml_model.make_state()
                predict_kwargs = dict(
                    data=self.palettizer.sample_coreml_data,
                    state=self.palettizer.coreml_test_states)
            else:
                predict_kwargs = dict(data=self.palettizer.sample_coreml_data)

            self.palettizer.coreml_predict_kwargs = predict_kwargs

            # Run fake palettized Core ML model
            coreml_fake_palettized_out = self.palettizer.coreml_model.predict(
                **self.palettizer.coreml_predict_kwargs
            )[self.output_names[0]]

            # Run fake palettized torch model
            reference_torch_out = self.palettizer.model(
                **self.palettizer.torch_jit_trace_data
            )[0]

            # Apply real palettization to reduce weight precision
            final_precision = self.palettizer.apply_recipe_coreml(recipe_key)  # noqa: F841,E501

            # Run real palettized Core ML model
            coreml_real_palettized_out = self.palettizer.coreml_model.predict(
                **self.palettizer.coreml_predict_kwargs
            )[self.output_names[0]]

            # Correctness check: Fake palette torch vs fake palette Core ML
            psnr_faketorch2fakecoreml = compute_psnr(
                reference_torch_out,
                torch.from_numpy(coreml_fake_palettized_out)
            )

            logger.info(
                f"[{recipe_key}-bit] torch2coreml  "
                "(Fake palettized vs fake palettized): "
                f"PSNR={psnr_faketorch2fakecoreml:.3g}"
            )

            # Correctness check: Fake palette Core ML vs real palette Core ML
            psnr_fake2realcoreml = compute_psnr(
                torch.from_numpy(coreml_fake_palettized_out),
                torch.from_numpy(coreml_real_palettized_out)
            )

            logger.info(
                f"[{recipe_key}-bit] coreml2coreml "
                "(Fake palettized vs real palettized): "
                f"PSNR={psnr_fake2realcoreml:.3g}"
            )

            # Correctness check: Fake palette torch vs real palette Core ML
            # (strictest test)
            psnr_faketorch2realcoreml = compute_psnr(
                reference_torch_out,
                torch.from_numpy(coreml_real_palettized_out)
            )

            logger.info(
                f"[{recipe_key}-bit] torch2coreml  "
                "(Fake palettized vs real palettized): "
                f"PSNR={psnr_faketorch2realcoreml:.3g}"
            )

            # Saves the asset only if the tests pass
            with self.subTest(phase=f"mixed_bit_{recipe_key}-bit_correctness"):
                self.assertGreater(psnr_faketorch2fakecoreml, TEST_PSNR_THR)
                self.assertGreater(psnr_fake2realcoreml, TEST_PSNR_THR)
                self.assertGreater(psnr_faketorch2realcoreml, TEST_PSNR_THR)

                logger.info(
                    f"[{recipe_key}-bit] torch2coreml correctness passed. "
                    "Saving Core ML asset."
                )

                remove_mlpackage = True
                if hasattr(self, "create_fast_load_asset"):
                    remove_mlpackage = False

                _save_coreml_asset(
                    self.palettizer.coreml_model,
                    self.palettizer.cache_dir,
                    f"{self.model_name}_mixedBitPalettized_{recipe_key}-bit",
                    do_compile=TEST_COMPILE_COREML,
                    do_remove_mlpackage=remove_mlpackage,
                )

            # Restore pristine model before applying the next recipe
            self.palettizer.restore_pristine_model()

    def _check_allowed_nbits(self):
        # Add 3-bit palettization if allowed and deployment target is macOS15+
        global TEST_ALLOWED_NBITS
        if (
            TEST_ALLOWED_NBITS == _DEFAULT_ALLOWED_NBITS and  # check if allowed nbits is default
            TEST_MIN_DEPLOYMENT_TARGET >= ct.target.macOS15
        ):
            TEST_ALLOWED_NBITS += [3]

        if 3 in TEST_ALLOWED_NBITS:
            assert TEST_MIN_DEPLOYMENT_TARGET >= ct.target.macOS15, \
                "3-bit palettization requires iOS18/macOS15 or later"


class CoreMLMultifunctionTestsMixin(unittest.TestCase):
    """ Mixin class for testing multifunction Core ML models
    """

    def test_multifunction_torch2coreml_conversion_and_correctness(self):
        """ Coverage:
        - Variable input shape torch2coreml with multifunction conversion
        - End-to-end correctness checks
        """

        if not hasattr(self, "test_torch_states"):
            self.test_torch_states = None

        with self.subTest(phase="torch2coreml_multifunction_correctness"):
            assert hasattr(self, "test_torch_variable_inputs")
            assert hasattr(self, "test_torch_model")

            # multifunction inputs
            self.test_coreml_variable_inputs = []
            self.test_coreml_variable_outputs = []

            for idx, test_torch_input in tqdm(enumerate(self.test_torch_variable_inputs)):
                dummy_coreml_inputs = _create_coreml_inputs(test_torch_input)

                dummy_coreml_model = _create_coreml_model(
                    self.test_torch_model,
                    test_torch_input,
                    self.test_output_names,
                    self.test_torch_states,
                )
                if self.test_torch_states is not None:
                    dummy_coreml_test_states = dummy_coreml_model.make_state()
                    predict_kwargs = dict(
                        data=dummy_coreml_inputs,
                        state=dummy_coreml_test_states)
                else:
                    predict_kwargs = dict(data=dummy_coreml_inputs,)

                self.test_coreml_variable_inputs.append(
                    predict_kwargs
                )

                dummy_coreml_output = dummy_coreml_model.predict(
                    **predict_kwargs
                )[self.test_output_names[0]].squeeze()
                self.test_coreml_variable_outputs.append(dummy_coreml_output)
                dummy_torch_output = self.test_torch_model(**test_torch_input)
                if isinstance(dummy_torch_output, (list, tuple)):
                    dummy_torch_output = dummy_torch_output[0]

                reference = dummy_torch_output
                proxy = torch.from_numpy(dummy_coreml_output).to(reference)

                psnr = compute_psnr(reference, proxy)

                logger.info(
                    f"torch2coreml multifunction [{idx+1}/{len(self.test_torch_variable_inputs)}] "
                    f"PSNR={psnr:.3g}"
                )
                self.assertGreater(psnr, TEST_PSNR_THR)

                # Save asset if correctness test passes
                _save_coreml_asset(
                    dummy_coreml_model,
                    os.path.join(self.test_cache_dir, "multifunction_dummies"),
                    self.model_name + f"_multifunction_{idx}",
                    do_compile=TEST_COMPILE_COREML,
                    do_remove_mlpackage=False,
                )

            # Create multifunction model
            desc = ct.utils.MultiFunctionDescriptor()
            for idx in range(len(self.test_coreml_variable_inputs)):
                desc.add_function(
                    os.path.join(
                        self.test_cache_dir,
                        "multifunction_dummies",
                        f"{self.model_name}_multifunction_{idx}.mlpackage",
                    ),
                    src_function_name="main",
                    target_function_name=f"f_{idx}"
                )
            desc.default_function_name = "f_0"
            self.test_coreml_multifunction_model_path = os.path.join(
                self.test_cache_dir,
                f"{self.model_name}_multifunction.mlpackage"
            )
            ct.utils.save_multifunction(
                desc,
                self.test_coreml_multifunction_model_path
            )

        with self.subTest(phase="coreml2coreml_multifunction_loading_and_correctness"):
            assert hasattr(self, "test_coreml_multifunction_model_path")
            assert hasattr(self, "test_coreml_variable_inputs")
            assert hasattr(self, "test_coreml_variable_outputs")

            for idx, test_coreml_input in tqdm(enumerate(self.test_coreml_variable_inputs)):
                dummy_multi_function_model = ct.models.MLModel(
                    self.test_coreml_multifunction_model_path,
                    function_name=f"f_{idx}"
                )
                dummy_coreml_output = dummy_multi_function_model.predict(
                    **test_coreml_input
                )[self.test_output_names[0]].squeeze()
                reference = torch.from_numpy(self.test_coreml_variable_outputs[idx])
                proxy = torch.from_numpy(dummy_coreml_output)

                psnr = compute_psnr(reference, proxy)

                logger.info(
                    "coreml2coreml multifunction "
                    f"[{idx+1}/{len(self.test_coreml_variable_inputs)}] "
                    f"PSNR={psnr:.3g}"
                )
                self.assertGreater(psnr, TEST_PSNR_THR)

            logger.info("All multifunction tests passed.")


def _term_exec(cmd):
    return subprocess.run(
        cmd, stdout=subprocess.PIPE, shell=True
    ).stdout.decode("utf-8").strip()


class InferenceContextSpec(ABC):
    """ Schema that specifies a context to reproduce the computation
    """
    @abstractmethod
    def device_spec(self):
        pass

    @abstractmethod
    def os_spec(self):
        pass

    @abstractmethod
    def code_spec(self):
        pass

    @abstractmethod
    def model_spec(self):
        pass

    def spec_dict(self):
        return {
            "os_spec": self.os_spec(),
            "code_spec": self.code_spec(),
            "model_spec": self.model_spec(),
            "device_spec": self.device_spec(),
        }


class AppleSiliconContextMixin:
    """ Inference context spec for Apple Silicon devices
    """
    def device_spec(self):
        # Validate Apple Silicon
        platform = _term_exec("uname -s")
        assert platform == "Darwin", f"Unexpected platform={platform}"

        arch = _term_exec("uname -m")
        assert arch == "arm64", f"Unpexted arch: {arch}"

        # Gather GPU core count
        gpu_core_count = _term_exec("ioreg -l | grep gpu-core-count")
        gpu_core_count = gpu_core_count.rsplit("=", 1)[-1].strip()

        assert all(ch.isdigit() for ch in gpu_core_count), \
            f"Unable to parse gpu_core_count: {gpu_core_count}"
        gpu_core_count = int(gpu_core_count)

        # Gather CPU core count
        cpu_core_count = _term_exec("sysctl -a | grep machdep.cpu.core_count")
        cpu_core_count = cpu_core_count.rsplit(":", 1)[-1].strip()
        assert [i.isdigit() for i in cpu_core_count], \
            f"Unable to parse cpu_core_count: {cpu_core_count}"
        cpu_core_count = int(cpu_core_count)

        # Gather product name
        product_name = _term_exec("sysctl -a | grep machdep.cpu.brand_string")
        product_name = product_name.rsplit(":", 1)[-1].strip()

        # Get RAM size
        max_ram = _term_exec("sysctl -a | grep hw.memsize")
        max_ram = max_ram.rsplit(":", 1)[-1].strip()

        return {
            "gpu_core_count": gpu_core_count,
            "cpu_core_count": cpu_core_count,
            "product_name": product_name,
            "max_ram": max_ram,
        }

    def os_spec(self):
        sw_vers = _term_exec("sw_vers")
        """
        % sw_vers
        ProductName:        xOS
        ProductVersion:     d.d
        BuildVersion:       dXd

        - d.  -> digit(s)
        - x,X -> letter(s)
        """
        os_type, os_version, os_build_number = [
            line.rsplit("\t\t")[1]
            for line in sw_vers.rsplit("\n")
        ]

        return {
            "os_version": os_version,
            "os_type": os_type,
            "os_build_number": os_build_number,
        }


def _bisect_coreml_model(original_model: ct.models.MLModel, output_dir: str) -> ct.models.MLModel:
    _ = ct.models.utils.bisect_model(
        model=original_model,
        output_dir=output_dir,
        merge_chunks_to_pipeline=True,
        check_output_correctness=True
    )
    return ct.models.MLModel(f"{output_dir}/chunked_pipeline.mlpackage",
                             compute_units=TEST_COMPUTE_UNIT)


# Helper functions
def _create_coreml_inputs(torch_inputs: Dict[str, torch.Tensor]) -> Dict[str, np.ndarray]:
    return {
        k: v.cpu().numpy().astype(TEST_COREML_IO_FLOAT_DTYPE)
        if v.dtype.is_floating_point else v.cpu().numpy().astype(np.int32)
        for k, v in torch_inputs.items()
    }


def _create_coreml_model(
        torch_model: nn.Module,
        torch_inputs: Dict[str, torch.Tensor],
        output_names: List[str],
        torch_states: Optional[Dict[str, torch.Tensor]] = None,
        ) -> ct.models.MLModel:

    # Model internal states spec (if specified)
    # Do this first to remove torch_inputs that become states for Core ML
    kwargs = {}

    if torch_states is not None:
        assert TEST_MIN_DEPLOYMENT_TARGET >= ct.target.iOS18 or \
            TEST_MIN_DEPLOYMENT_TARGET >= ct.target.macOS15, \
            "State support requires iOS18+ or macOS15+"
        logger.debug("Adding states to Core ML model")
        kwargs["states"] = [
            ct.StateType(
                name=k,
                wrapped_type=ct.TensorType(shape=v.shape, dtype=TEST_COREML_IO_FLOAT_DTYPE))
            for k, v in torch_states.items()
        ]

        inputs_to_remove = []
        for k in torch_inputs:
            if k in torch_states:
                inputs_to_remove.append(k)

        if len(inputs_to_remove) > 0:
            logger.debug(
                f"Ignoring the following inputs that are now states: {inputs_to_remove}")
            torch_inputs = {k: v for k, v in torch_inputs.items() if k not in inputs_to_remove}

    # Model I/O spec
    coreml_inputs = _create_coreml_inputs(torch_inputs)
    kwargs.update(dict(
        inputs=TEST_COREML_INPUT_SPEC_OVERRIDE or [
            ct.TensorType(k, shape=v.shape, dtype=v.dtype)
            for k, v in coreml_inputs.items()
        ],
        outputs=[
            ct.TensorType(output_name, dtype=TEST_COREML_IO_FLOAT_DTYPE)
            for output_name in output_names
        ]
    ))

    # Model conversion
    logger.debug(f"Converting to Core ML with the following specs: {kwargs}")
    model = ct.convert(
        torch.jit.trace(
            torch_model.eval(),
            example_kwarg_inputs=torch_inputs
        ),
        minimum_deployment_target=TEST_MIN_DEPLOYMENT_TARGET,
        compute_units=TEST_COMPUTE_UNIT,
        compute_precision=TEST_COREML_PRECISION,
        skip_model_load=True,
        **kwargs,
    )

    logger.info("Conversion complete, testing first load time..")
    tmp_path = "/tmp/post_convert.mlpackage"
    model.save(tmp_path)

    s = time.time()
    model = ct.models.MLModel(tmp_path, compute_units=TEST_COMPUTE_UNIT)
    logger.info(
        f"First load time (Specialization for {TEST_COMPUTE_UNIT}): {time.time() - s:.3g} seconds")

    return model


def _compress_coreml_model(mlmodel: ct.models.MLModel) -> ct.models.MLModel:
    return ct.optimize.coreml.palettize_weights(
        mlmodel,
        config=ct.optimize.coreml.OptimizationConfig(
            global_config=ct.optimize.coreml.OpPalettizerConfig(
                mode="kmeans",
                nbits=TEST_DEFAULT_NBITS,
            ),
        )
    )


def _save_coreml_asset(coreml_model: ct.models.MLModel,
                       out_dir: str,
                       fname: str,
                       do_compile: bool = True,
                       do_remove_mlpackage: bool = True,) -> None:
    """ Helper function to save Core ML models (`.mlpackage`) to disk
    """
    if TEST_DEFAULT_NBITS is not None:
        save_coreml_to = os.path.join(out_dir, f"{fname}_{TEST_DEFAULT_NBITS}-bit.mlpackage")
    else:
        save_coreml_to = os.path.join(out_dir, f"{fname}.mlpackage")

    logger.info(f"Saving Core ML test artifact to {save_coreml_to}")
    coreml_model.save(save_coreml_to)

    if do_compile:
        mlmodelc_path = _compile_coreml_model(save_coreml_to, out_dir, fname)
        logger.info(f"Compiled model at {mlmodelc_path}")

        if ct.version.__version__ >= "8.1":
            _print_compute_plan(mlmodelc_path, out_dir)

    if do_remove_mlpackage:
        logger.info(f"Removing {save_coreml_to}")
        shutil.rmtree(save_coreml_to)


def _compile_coreml_model(mlpackage_path: str,
                          output_dir: str,
                          final_name: str) -> str:
    """ Helper function to compile from .mlpackage to .mlmodelc
    """
    target_path = os.path.join(output_dir, f"{final_name}.mlmodelc")
    logger.info(f"Compiling {mlpackage_path}")
    source_fname = os.path.basename(os.path.splitext(mlpackage_path)[0])

    os.system(f"xcrun coremlcompiler compile {mlpackage_path} {output_dir}")
    compiled_output = os.path.join(output_dir, f"{source_fname}.mlmodelc")
    shutil.move(compiled_output, target_path)

    return target_path


def _print_compute_plan(mlmodelc_path: str, output_dir: str,) -> None:
    """ Print the compute plan (compute unit dispatch per op)
    for a compiled Core ML model
    """
    logger.info(f"Extracting compute plan from {mlmodelc_path}")
    compute_plan = ct.models.compute_plan.MLComputePlan.load_from_path(
        path=mlmodelc_path,
        compute_units=TEST_COMPUTE_UNIT
    )

    program = compute_plan.model_structure.program
    main_function = program.functions["main"]

    compute_unit_map = {
        "coremltools.models.compute_device.MLNeuralEngineComputeDevice": "ANE",
        "coremltools.models.compute_device.MLGPUComputeDevice": "GPU",
        "coremltools.models.compute_device.MLCPUComputeDevice": "CPU",
    }

    # FIXME(atila): Class name is ABCMeta and class instantiation requires a missing argument
    def device2key(device_cls): return str(device_cls)[1:].rsplit(" ")[0]

    compute_plan_per_op = {}
    total_cost = 0
    for idx, operation in enumerate(main_function.block.operations):
        name = "_".join([str(idx), operation.operator_name] + list(operation.inputs))
        device_usage = compute_plan.get_compute_device_usage_for_mlprogram_operation(operation)
        cost = compute_plan.get_estimated_cost_for_mlprogram_operation(operation)

        if device_usage is not None:
            compute_plan_per_op[name] = {
                "dispatch": compute_unit_map[device2key(device_usage.preferred_compute_device)],
                "supported": [
                    compute_unit_map[device2key(sd)]
                    for sd in device_usage.supported_compute_devices
                ],
                "cost": cost.weight if cost is not None else None
            }
            if cost is not None:
                total_cost += cost.weight

    eps = 1e-2
    if total_cost > 1.0 + eps or total_cost < 1.0 - eps:
        logger.warning(f"Total cost is not normalized to 1: {total_cost}")

    for k in compute_plan_per_op:
        if compute_plan_per_op[k]["cost"] is not None:
            compute_plan_per_op[k]["cost"] = round(
                compute_plan_per_op[k]["cost"] / total_cost * 100., 4)

    num_cost_estimated_ops = sum(cp["cost"] is not None for cp in compute_plan_per_op.values())
    cost_estimation_coverage = num_cost_estimated_ops / len(compute_plan_per_op) * 100
    logger.info(f"Total cost estimated ops: {num_cost_estimated_ops}/{len(compute_plan_per_op)} "
                f"({cost_estimation_coverage:.2f}%)")

    if cost_estimation_coverage < 99.:
        logger.warning(
            "Cost estimation coverage is less than 99%, not displaying top-10 ops by cost")
    else:
        top_k = 10
        logger.info(f"Top-{top_k} ops by latency cost %")
        pprint(dict(sorted(
            compute_plan_per_op.items(),
            key=lambda kv: -kv[1]["cost"] if kv[1]["cost"] is not None else 1)[:top_k]
        ))

    num_ops = len(compute_plan_per_op)
    ane_supported_ops = sum("ANE" in cp["supported"] for cp in compute_plan_per_op.values())
    logger.info("ANE support coverage = "
                f"{ane_supported_ops}/{num_ops} ({ane_supported_ops / num_ops * 100.:.2f}%)")

    ane_resident_num_ops = sum(cp["dispatch"] == "ANE" for cp in compute_plan_per_op.values())
    logger.info("ANE dispatch = "
                f"{ane_resident_num_ops}/{num_ops} ({ane_resident_num_ops / num_ops * 100.:.2f}%)")

    out_path = os.path.join(
        output_dir,
        mlmodelc_path.rsplit("/")[-1].replace(".mlmodelc", ".mlcomputeplan.json")
    )
    with open(out_path, "w") as f:
        json.dump(compute_plan_per_op, f, indent=4)


def compute_psnr(reference: torch.Tensor, proxy: torch.Tensor) -> float:
    """ Peak-Signal-to-Noise-Ratio in dB between a reference
    and a proxy torch.Tensor
    """
    assert reference.squeeze().shape == proxy.squeeze().shape, \
        f"{reference.shape} is incompatible with {proxy.shape}!"
    reference = reference.flatten().detach().cpu()
    proxy = proxy.flatten().detach().cpu()

    peak_signal = reference.abs().max()
    mse = ((reference - proxy) ** 2).mean().sqrt()
    return 20 * torch.log10((peak_signal + 1e-5) / (mse + 1e-10)).item()


def _get_test_cache_dir(persistent_cache_dir: Optional[str] = None) -> str:
    """ Create a temporary or persistent cache directory for test artifacts
    """
    if persistent_cache_dir is not None:
        os.makedirs(persistent_cache_dir, exist_ok=True)
        return contextlib.nullcontext(enter_result=persistent_cache_dir)
    else:
        return tempfile.TemporaryDirectory(prefix="argmaxtools")


MAX_BENCH_TIME = 5  # seconds
MAX_BENCH_ITERS = 100
WARMUP_ITERS = 3
MIN_ITERS = 3


def median_user_latency(call_fn: Callable,
                        return_flops: bool = False) -> Dict[str, float]:
    """ Benchmark and return the median post-warmup TFlop/s and latency (ms)
    """
    results = {}

    for _ in range(WARMUP_ITERS):
        call_fn()

    # Estimate bench iters to fit given benchmarking time
    s = time.time()
    call_fn()
    latency = time.time() - s

    bench_iters = int(min(max(MAX_BENCH_TIME // latency, MIN_ITERS), MAX_BENCH_ITERS))
    logger.debug(
        f"benchmark_iterations={bench_iters} (rough estimate from {latency:.3g} sec/run)). "
        f"max_bench_time={MAX_BENCH_TIME}, min_iters={MIN_ITERS}, max_iters={MAX_BENCH_ITERS}"
    )

    user_latencies = []
    for _ in range(bench_iters):
        s = time.time()
        call_fn()
        user_latencies.append(time.time() - s)

    def sec2msec(s): return float(f"{s * 1e3:.3g}")
    results["latency"] = sec2msec(median(user_latencies))

    if return_flops:
        flop_counter = FlopCounterMode()
        with flop_counter:
            call_fn()
        total_flop_count = flop_counter.get_total_flops()
        median_tflops = float(
            f"{total_flop_count / results['latency'] / 1e9:.3g}")

        results.update({
            "tflops/s": median_tflops,
            "#flops": total_flop_count
        })

    return results
