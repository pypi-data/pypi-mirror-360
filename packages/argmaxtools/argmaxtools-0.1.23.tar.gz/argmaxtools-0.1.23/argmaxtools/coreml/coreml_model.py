from typing import Self

import numpy as np
import coremltools as ct

from .coreml_metadata import CoreMLModelMetadata
from .coreml_load import load_compiled_model_from_hub, load_compiled_model_from_path


class CoreMLModel:
    """
    A wrapper around a compiled CoreML model (.mlmodelc) with convenient 
    input formatting, based on the model's metadata, and inference.

    Args:
        model (ct.models.CompiledMLModel):
            The compiled CoreML model (.mlmodelc)
        model_metadata (CoreMLModelMetadata):
            The metadata of the CoreML model (.mlmodelc)
    """
    def __init__(
        self,
        model: ct.models.CompiledMLModel,
        model_metadata: CoreMLModelMetadata,
    ) -> None:
        self.model = model
        self.model_metadata = model_metadata

    def format_inputs(
        self, **input_data: dict[str, np.ndarray]
    ) -> dict[str, np.ndarray]:
        """
        Format the input data according to the model's metadata.
        """
        return {
            _input.name: input_data[_input.name].astype(_input.numpy_dtype)
            for _input in self.model_metadata.input_schema.items
        }

    def forward(self, **input_data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        """
        Forward pass through the model.
        """
        model_inputs = self.format_inputs(**input_data)
        model_outputs = self.model.predict(model_inputs)
        return model_outputs

    @classmethod
    def from_hub(
        cls,
        repo_id: str,
        model_name: str,
        variant_name: str,
        version_dir: str | None = None,
        model_compute_units: ct.ComputeUnit = ct.ComputeUnit.CPU_ONLY,
    ) -> Self:
        (model, model_metadata) = load_compiled_model_from_hub(
            repo_id=repo_id,
            model_name=model_name,
            variant_name=variant_name,
            version_dir=version_dir,
            model_compute_units=model_compute_units,
        )
        return cls(
            model=model,
            model_metadata=model_metadata,
        )
    
    @classmethod
    def from_path(
        cls,
        model_path: str,
        model_compute_units: ct.ComputeUnit = ct.ComputeUnit.CPU_ONLY,
    ) -> Self:
        (model, model_metadata) = load_compiled_model_from_path(
            model_path=model_path,
            compute_units=model_compute_units,
        )
        return cls(
            model=model,
            model_metadata=model_metadata,
        )
