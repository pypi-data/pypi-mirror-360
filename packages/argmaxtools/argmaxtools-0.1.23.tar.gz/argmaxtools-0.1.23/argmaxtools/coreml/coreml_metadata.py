import ast

import numpy as np
from pydantic import BaseModel, Field, model_validator

def to_camel(string: str) -> str:
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class SchemaItem(BaseModel):
    has_shape_flexibility: str
    is_optional: str
    data_type: str
    shape: list[int]
    name: str
    type: str

    class Config:
        alias_generator = to_camel
        validate_by_name = True

    @model_validator(mode="before")
    @classmethod
    def parse_shape(cls, data: dict) -> dict:
        if isinstance(data["shape"], str):
            data["shape"] = ast.literal_eval(data["shape"])
        return data

    @property
    def numpy_dtype(self) -> np.dtype:
        if self.data_type == "Float32":
            return np.float32
        elif self.data_type == "Float16":
            return np.float16
        elif self.data_type == "Int32":
            return np.int32


class ListOfSchemaItems(BaseModel):
    items: list[SchemaItem]

    def get_by_name(self, name: str) -> SchemaItem:
        for item in self.items:
            if item.name == name:
                return item
        raise ValueError(f"Item with name {name} not found.")

    def return_names(self) -> list[str]:
        return [item.name for item in self.items]

    def is_input(self, name: str) -> bool:
        if name in self.return_names():
            return True
        return False


class UserDefinedMetadata(BaseModel):
    source_dialect: str = Field(
        ..., alias="com.github.apple.coremltools.source_dialect"
    )
    version: str = Field(..., alias="com.github.apple.coremltools.version")
    source: str = Field(..., alias="com.github.apple.coremltools.source")


# This class is supposed to be used by reading a metadata.json file associated with a CoreML model
# see https://huggingface.co/argmaxinc/whisperkit-coreml/blob/main/openai_whisper-large-v3-v20240930_626MB/AudioEncoder.mlmodelc/metadata.json
class CoreMLModelMetadata(BaseModel):
    metadata_output_version: str
    storage_precision: str
    output_schema: ListOfSchemaItems
    model_parameters: list
    specification_version: int
    ml_program_operation_type_histogram: dict[str, int]
    compute_precision: str
    is_updatable: str
    state_schema: ListOfSchemaItems | None = Field(default=None)
    model_type: str
    user_defined_metadata: UserDefinedMetadata
    input_schema: ListOfSchemaItems
    generated_class_name: str
    method: str

    @model_validator(mode="before")
    @classmethod
    def parse_model_type(cls, data: dict) -> dict:
        if isinstance(data["modelType"], dict):
            data["modelType"] = data["modelType"]["name"]
        return data

    @model_validator(mode="before")
    @classmethod
    def parse_schemas(cls, data: dict) -> dict:
        keys = ["inputSchema", "outputSchema", "stateSchema"]
        for key in keys:
            data[key] = ListOfSchemaItems(
                items=[SchemaItem(**item) for item in data[key]]
            )
        return data

    class Config:
        alias_generator = to_camel
        validate_by_name = True
