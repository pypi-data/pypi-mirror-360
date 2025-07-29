from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_serializer, model_validator

from ..evaluator import  EvaluatorInScope
from ..prompts import SupportedFormat


class HuggingFaceTask(str, Enum):
    TEXT_GENERATION = "text-generation"
    TEXT2TEXT_GENERATION = "text2text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    TOKEN_CLASSIFICATION = "token-classification"
    FEATURE_EXTRACTION = "feature-extraction"
    SENTENCE_SIMILARITY = "sentence-similarity"
    FILL_MASK = "fill-mask"

class ClassificationModelScope(str, Enum):
    PROMPT = "prompt"
    RESPONSE="response"
    CONVERSATION="conversation"


class DType(str, Enum):
    FLOAT16 = "float16"
    BFLOAT16 = "bfloat16"
    FLOAT32 = "float32"


class HFEndpoint(BaseModel):
    api_endpoint: Optional[HttpUrl] = Field(
        None, description="Custom API endpoint for the model."
    )
    api_key: Optional[str] = Field(None, description="Your HuggingFace API key.")


class HuggingFaceProviderParams(BaseModel):
    temperature: Optional[float] = Field(
        None, ge=0, le=1, description="Controls randomness in generation."
    )
    top_k: Optional[int] = Field(
        None, ge=1, description="Controls diversity via the top-k sampling strategy."
    )
    top_p: Optional[float] = Field(
        None, ge=0, le=1, description="Controls diversity via nucleus sampling."
    )
    repetition_penalty: Optional[float] = Field(
        None, ge=0, description="Penalty for repetition."
    )
    max_new_tokens: Optional[int] = Field(
        None, ge=1, description="The maximum number of new tokens to generate."
    )
    max_time: Optional[float] = Field(
        None, ge=0, description="The maximum time in seconds for the model to respond."
    )
    return_full_text: Optional[bool] = Field(
        None, description="Whether to return the full text or just new text."
    )
    num_return_sequences: Optional[int] = Field(
        None, ge=1, description="The number of sequences to return."
    )
    do_sample: Optional[bool] = Field(None, description="Whether to sample the output.")
    use_cache: Optional[bool] = Field(None, description="Whether to use caching.")
    wait_for_model: Optional[bool] = Field(
        None, description="Whether to wait for the model to be ready."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        None, description="Additional parameters to pass to HuggingFace API."
    )
    dtype: Optional[DType] = Field(
        DType.BFLOAT16, description="Data type for model computation."
    )

    @field_serializer("dtype")
    def serialize_dtype(self, dtype: DType) -> str:
        """Serialize the enum to a string."""
        if dtype:
            return dtype.value
        else:
            return dtype


class HuggingFaceProviderConfig(BaseModel):
    type: Literal["huggingface"] = Field("huggingface", description="Provider type discriminator.")
    model: str = Field(..., description="HuggingFace model name.")
    task: HuggingFaceTask = Field(
        ..., description="Task type for the HuggingFace model."
    )
    params: Optional[HuggingFaceProviderParams] = Field(
        None, description="Configuration parameters for HuggingFace model."
    )
    endpoint: Optional[HFEndpoint] = Field(
        None, description="HuggingFace API endpoint configuration."
    )

    support_multi_turn: bool = Field(
        default=False,
        description="Does it support Multi Turn",
    )

    supported_input_format: Optional[SupportedFormat] = Field(
        default=SupportedFormat.TEXT,
        description="Supported Input format",
    )

    classification_model_scope: Optional[ClassificationModelScope] = Field(
        default=ClassificationModelScope.CONVERSATION,
        description="Scope of classification model  - prompt, response, or whole conversation",
    )

    id: Optional[str] = Field(
        None,
        description="HuggingFace model identifier computed as 'huggingface:<task>:<model>'",
    )

    preferred_evaluator: Optional[EvaluatorInScope] = Field(
        None,
        description="Preferred Evaluator for the provider",
    )

    @model_validator(mode="after")
    def compute_id(cls, values):
        if not values.id:
            values.id = f"huggingface:{values.task.value}:{values.model}"
        return values

    @field_serializer("task")
    def serialize_role(self, task: Optional[HuggingFaceTask]) -> Optional[str]:
        return task.value if task else None

    @field_serializer("supported_input_format")
    def serialize_supported_format(self, supported_input_format: Optional[SupportedFormat]) -> Optional[str]:
        return str(supported_input_format) if supported_input_format else None

    @field_serializer("classification_model_scope")
    def serialize_classification_model_scope(self, scope: Optional[ClassificationModelScope]):
        """Serialize classification model scope to string."""
        return scope.value if scope else None

    def get_name(self) -> str:
        """
        Returns the model name as the provider's name.
        """
        return self.model



class HuggingFaceGuardModelsProviderConfig(HuggingFaceProviderConfig):
    safe_value: str = Field(
        "",
        description="JSONPath expression indicating the condition for input to be safe.",
    )

    """
    Example Usage:
    ----------------
    provider = HuggingFaceGuardModelsProviderConfig(safe_value="$.score[?(@ < 0.6)]")
    
    This JSONPath expression checks if all scores in the input JSON are below 0.6.
    """


class HFProvider(BaseModel):
    provider: Literal["huggingface"] = Field(
        "huggingface", description="Provider ID, always set to 'http'."
    )
    config: HuggingFaceProviderConfig


class HFModels(BaseModel):
    huggingface: List[HuggingFaceProviderConfig | HuggingFaceGuardModelsProviderConfig] = Field(
        default_factory=list, description="List of predefined models."
    )
