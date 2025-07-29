from enum import Enum


class ProviderType(str, Enum):
    ECHO = "echo"
    ELIZA = "eliza"
    HF = "huggingface"
    HTTP = "http"
    GRADIO = "gradio"
    OLLAMA = "ollama"
    OPENAI = "openai"
    GROQ = "groq"
    LITE_LLM = "litellm"

    def __str__(self):
        return self.value  # Ensures correct YAML serialization

    @classmethod
    def values(cls):
        return [member.value for member in cls]
