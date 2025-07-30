import os
import json
from pathlib import Path

import coremltools as ct
from huggingface_hub import snapshot_download, HfFileSystem

from .coreml_metadata import CoreMLModelMetadata
from ..utils import get_logger

logger = get_logger(__name__)

def load_metadata(mlmodelc_path: str) -> CoreMLModelMetadata:
    """
    Load the metadata from a CoreML model/preprocessor.
    """
    with open(os.path.join(mlmodelc_path, "metadata.json"), "r") as f:
        metadata = json.load(f)[0]
    return CoreMLModelMetadata(**metadata)


def download_model_from_hub(
    repo_id: str,
    model_name: str,
    variant_name: str,
    version_dir: str | None,
    max_download_workers: int | None = None,
) -> str:
    """Downloads a CoreML model and its preprocessor from the Hugging Face Hub.

    The function expects the following directory structure in the Hugging Face repo:
    repo_id/
    ├── version_1/                # Optional version directory. If not provided assume this level does not exist
    │   └── variant_name/         # e.g. "base", "large", etc.
    │       ├── <model_name_1>.mlmodelc/   # CoreML model directory
    │       └── <model_name_1>Preprocessor.mlmodelc/  # Preprocessor directory
    ├── version_2/
    │   └── variant_name/
    │       ├── <model_name_2>.mlmodelc/
    │       └── <model_name_2>Preprocessor.mlmodelc/
    └── ...

    Args:
        repo_id (str):
            The Hugging Face repository ID where the model is stored.
        model_name (str):
            The name of the CoreML model to download (without .mlmodelc extension).
        variant_name (str):
            The variant/configuration name of the model (e.g. "base", "large").
        version_dir (str | None):
            Optional version directory to look in. If None, searches across all versions.
        max_download_workers (int | None):
            Maximum number of workers for parallel download. If None, uses CPU count - 2.

    Returns:
        str: Path to the downloaded CoreML model (.mlmodelc)

    Raises:
        AssertionError: If more than one matching model is found for the given parameters.
    """
    fs = HfFileSystem(skip_instance_cache=True)
    pattern = f"{repo_id}/**/{variant_name}/{model_name}.mlmodelc"
    if version_dir is not None:
        pattern = f"{repo_id}/**/{version_dir}/{variant_name}/{model_name}.mlmodelc"

    model_paths = fs.glob(pattern)
    assert (
        len(model_paths) == 1
    ), f"Should find 1 match only, but found {len(model_paths)} for {version_dir=} - {variant_name=} - {model_name=}"

    dir_to_download = Path(model_paths[0].split(repo_id)[-1].lstrip("/")).parent
    max_download_workers = max_download_workers or max(os.cpu_count() - 2, 1)

    local_snapshot_path = snapshot_download(
        repo_id=repo_id,
        revision="main",
        use_auth_token=os.getenv("HF_TOKEN"),
        max_workers=max_download_workers,
        allow_patterns=f"{dir_to_download}/*",
    )
    local_dir = os.path.join(local_snapshot_path, dir_to_download)
    model_path = os.path.join(local_dir, f"{model_name}.mlmodelc")

    return model_path

def load_compiled_model_from_path(model_path: str, compute_units: ct.ComputeUnit) -> tuple[ct.models.CompiledMLModel, CoreMLModelMetadata]:
    """Load a CoreML model from a local path.

    Args:
        model_path (str):
            The path to the CoreML model (.mlmodelc)
        compute_units (ct.ComputeUnit):
            The compute units to use for the model.
    Returns:
        tuple[ct.models.CompiledMLModel, CoreMLModelMetadata]: The loaded CoreML model and its metadata
    """
    logger.info(f"Loading {model_path} as CoreML model...")
    model = ct.models.CompiledMLModel(model_path, compute_units=compute_units)
    model_metadata = load_metadata(model_path)
    return model, model_metadata


def load_compiled_model_from_hub(
    repo_id: str,
    model_name: str,
    variant_name: str,
    version_dir: str | None,
    model_compute_units: ct.ComputeUnit,
    max_download_workers: int | None = None,
) -> tuple[ct.models.CompiledMLModel, CoreMLModelMetadata]:
    """
    Load a CoreML model from Hugging Face Hub at specified repo_id.

    Args:
        model_name (str):
            The name of the model to load from Hugging Face hub at `repo_id`.
        repo_id (str):
            The Hugging Face repository to use for downloading the model.
        compute_units (ct.ComputeUnit):
            The compute units to use for the model.
        preprocessor_compute_units (ct.ComputeUnit | None):
            The compute units to use for the preprocessor. Defaults to None.
        max_download_workers (int | None):
            The maximum number of workers to use for downloading the model from Hugging Face Hub.
            Defaults to the number of CPUs - 1.

    Returns:
        tuple[ct.models.MLModel, ct.models.MLModel | None, CoreMLModelInputMetadata]:
            A tuple containing the model, preprocessor, and input metadata.
    """
    max_download_workers = max_download_workers or os.cpu_count() - 1

    model_path = download_model_from_hub(
        repo_id=repo_id,
        model_name=model_name,
        variant_name=variant_name,
        version_dir=version_dir,
        max_download_workers=max_download_workers,
    )

    model, model_metadata = load_compiled_model_from_path(model_path, model_compute_units)

    return (model, model_metadata)