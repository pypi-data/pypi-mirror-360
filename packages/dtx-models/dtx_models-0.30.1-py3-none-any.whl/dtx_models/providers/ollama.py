from enum import Enum
from typing import Any, Dict, Literal, Optional
from dtx_models.utils.urls import url_2_name

from pydantic import BaseModel, Field, field_serializer, model_validator

## Supported Yaml

# """
# ollama:
#   - model: llama3


# ollama:
#   - model: llama3
#     task: text-generation
#     endpoint: http://localhost:11434
#     params:
#       temperature: 1.0
#       top_k: 50
#       top_p: 1.0
#       repeat_penalty: 1.1
#       max_tokens: 512
#       num_return_sequences: 1
#       extra_params:
#         stop: ["###", "User:"]
# """


class OllamaTask(str, Enum):
    TEXT_GENERATION = "text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    SAFETY_CLASSIFICATION = "safety-classification"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class OllamaProviderParams(BaseModel):
    temperature: Optional[float] = Field(
        None, ge=0, le=1, description="Controls randomness in generation."
    )
    top_k: Optional[int] = Field(
        None, ge=1, description="Top-k sampling strategy for generation."
    )
    top_p: Optional[float] = Field(
        None, ge=0, le=1, description="Nucleus sampling (top-p)."
    )
    repeat_penalty: Optional[float] = Field(
        None, ge=0, description="Penalty for repeating tokens."
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, description="Maximum number of tokens to generate."
    )
    num_return_sequences: Optional[int] = Field(
        None, ge=1, description="Number of sequences to return."
    )
    extra_params: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional parameters for Ollama model invocation.",
    )


class OllamaProviderConfig(BaseModel):
    type: Literal["ollama"] = Field("ollama", description="Provider type discriminator.")
    
    model: str = Field(..., description="Ollama model name (e.g. llama3, mistral).")
    task: Optional[OllamaTask] = Field(
        default=None,
        description="Task type for the Ollama model. If not provided, will be inferred from the model name.",
    )
    params: Optional[OllamaProviderParams] = Field(
        None, description="Optional parameters for customizing model behavior."
    )
    endpoint: Optional[str] = Field(
        default="http://localhost:11434", description="Base URL of the Ollama server."
    )

    @model_validator(mode="after")
    def compute_fields(cls, values):
        if not values.task:
            if "guard" in values.model:
                values.task = OllamaTask.TEXT_CLASSIFICATION
            else:
                values.task = OllamaTask.TEXT_GENERATION

        return values

    @field_serializer("task")
    def serialize_task(self, task: OllamaTask) -> str:
        return task.value


    def get_name(self) -> str:
        """
        Returns a name like 'llama3:http:localhost:11434:/' by combining model and formatted endpoint.
        """
        return f"{self.model}:{url_2_name(self.endpoint, level=3)}"


class OllamaProvider(BaseModel):
    provider: Literal["ollama"] = Field(
        "ollama", description="Provider ID, always set to 'ollama'."
    )
    config: OllamaProviderConfig
