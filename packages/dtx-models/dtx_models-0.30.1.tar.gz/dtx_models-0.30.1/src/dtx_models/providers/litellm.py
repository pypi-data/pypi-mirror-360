from typing import Literal, Optional

from pydantic import BaseModel, Field

from .openai import OpenaiProviderConfig


class LitellmProviderConfig(OpenaiProviderConfig):
    type: Literal["litellm"] = Field("litellm", description="Provider type discriminator.")
    
    endpoint: Optional[str] = Field(
        default=None,
        description="Base URL of the OpenAI server or proxy endpoint.",
    )


class LitellmProvider(BaseModel):
    """Wrapper for OpenAI provider configuration."""

    provider: Literal["litellm"] = Field(
        "litellm", description="Provider ID, always set to 'openai'."
    )
    config: LitellmProviderConfig
