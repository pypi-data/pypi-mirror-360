import os
import glob
import yaml
from typing import Optional, Union, List, Type, Any
from abc import ABC, abstractmethod
from pydantic import BaseModel

from dtx_models.providers.hf import HFModels, HuggingFaceProviderConfig
from dtx_models.providers.litellm import LitellmProviderConfig


# --- Exceptions ---
class ModelNotFoundError(Exception):
    pass

class ModelFilesNotFoundError(Exception):
    pass


# --- Base Models ---
class LiteLLMModels(BaseModel):
    litellm: List[LitellmProviderConfig] = []


class BaseModelRepo(ABC):
    provider_name: str

    @abstractmethod
    def get_model(self, model_name: str) -> Any:
        pass

    @abstractmethod
    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        pass

    @abstractmethod
    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[Any]:
        pass

    @abstractmethod
    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[Any]:
        pass


# # --- Fetcher for HuggingFace ---
# class HuggingFaceModelFetcher:
#     TASK_TAGS_TO_ENUM = {
#         "text-generation": HuggingFaceTask.TEXT_GENERATION,
#         "text2text-generation": HuggingFaceTask.TEXT2TEXT_GENERATION,
#         "text-classification": HuggingFaceTask.TEXT_CLASSIFICATION,
#         "token-classification": HuggingFaceTask.TOKEN_CLASSIFICATION,
#         "fill-mask": HuggingFaceTask.FILL_MASK,
#         "feature-extraction": HuggingFaceTask.FEATURE_EXTRACTION,
#         "sentence-similarity": HuggingFaceTask.SENTENCE_SIMILARITY,
#     }

#     DEFAULT_CONFIGS = {
#         HuggingFaceTask.TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
#         HuggingFaceTask.TEXT2TEXT_GENERATION: {"max_new_tokens": 512, "temperature": 0.7, "top_p": 0.9},
#         HuggingFaceTask.FILL_MASK: {},
#         HuggingFaceTask.TEXT_CLASSIFICATION: {},
#         HuggingFaceTask.TOKEN_CLASSIFICATION: {},
#         HuggingFaceTask.FEATURE_EXTRACTION: {},
#         HuggingFaceTask.SENTENCE_SIMILARITY: {},
#     }

#     def __init__(self):
#         self.api = HfApi()

#     def fetch(self, model_name: str) -> HuggingFaceProviderConfig:
#         try:
#             info = self.api.model_info(model_name)

#             task_enum = next(
#                 (self.TASK_TAGS_TO_ENUM[tag] for tag in info.tags if tag in self.TASK_TAGS_TO_ENUM),
#                 HuggingFaceTask.TEXT_GENERATION
#             )

#             support_multi = any(
#                 re.search(r"(chat|dialog|instruct|conversational)", tag, re.IGNORECASE)
#                 for tag in info.tags
#             )

#             config = self.DEFAULT_CONFIGS.get(task_enum, {}).copy()
#             gen_cfg = info.config.get("generation_config") or {}
#             config.update({k: v for k, v in gen_cfg.items() if k in config})

#             return HuggingFaceProviderConfig(
#                 model=model_name,
#                 task=task_enum,
#                 support_multi_turn=support_multi,
#                 supported_input_format="openai",
#                 config=config,
#             )

#         except HfHubHTTPError as e:
#             raise ModelNotFoundError(model_name) from e


# --- HuggingFace Repo ---
class HFModelsRepo(BaseModelRepo):
    provider_name = "huggingface"

    def __init__(self, models_path=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self._models_path = os.path.join(script_dir, models_path or "hf_models.yml")
        self.models = self._load_from_file()

    def _load_from_file(self) -> HFModels:
        if not os.path.exists(self._models_path):
            return HFModels(huggingface=[])
        with open(self._models_path, "r") as file:
            data = yaml.safe_load(file) or {}
        return HFModels(
            huggingface=[HuggingFaceProviderConfig(**model) for model in data.get("huggingface", [])]
        )

    def get_model(self, model_name: str) -> HuggingFaceProviderConfig:
        model = self.get_huggingface_model(model_name)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def get_huggingface_model(self, model_name: str) -> HuggingFaceProviderConfig:
        return next((m for m in self.models.huggingface if m.model == model_name), None)

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models.huggingface]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[HuggingFaceProviderConfig]:
        keyword = keyword.lower()
        matches = [
            m for m in self.models.huggingface if keyword in str(m.model_dump_json()).lower()
        ]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[HuggingFaceProviderConfig]:
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models.huggingface
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]


# --- LiteLLM Repo ---
class LiteLLMRepo(BaseModelRepo):
    provider_name = "litellm"

    def __init__(self, directory: str = None):
        self.directory = directory or os.path.dirname(os.path.abspath(__file__))
        self.models = self._load_models()

    def _load_models(self) -> LiteLLMModels:
        pattern = os.path.join(self.directory, "litellm_models_*.yml")
        files = glob.glob(pattern)
        if not files:
            raise ModelFilesNotFoundError(f"No model files matching pattern: {pattern}")

        merged_models = []
        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    data = yaml.safe_load(f) or {}
                    for model_dict in data.get("litellm", []):
                        merged_models.append(LitellmProviderConfig(**model_dict))
            except Exception as e:
                raise ModelFilesNotFoundError(f"Error loading file {file_path}: {e}") from e

        return LiteLLMModels(litellm=merged_models)

    def get_model(self, model_name: str) -> LitellmProviderConfig:
        model = next((m for m in self.models.litellm if m.model == model_name), None)
        if not model:
            raise ModelNotFoundError(model_name)
        return model

    def list_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        models = [m.model for m in self.models.litellm]
        return models[offset : offset + limit if limit is not None else None]

    def search_models_by_keyword(
        self, keyword: str, limit: Optional[int] = None, offset: int = 0
    ) -> List[LitellmProviderConfig]:
        keyword = keyword.lower()
        matches = [
            m for m in self.models.litellm if keyword in str(m.model_dump_json()).lower()
        ]
        return matches[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], limit: Optional[int] = None, offset: int = 0
    ) -> List[LitellmProviderConfig]:
        lower_keywords = [kw.lower() for kw in keywords]
        matches = [
            m for m in self.models.litellm
            if all(kw in str(m.model_dump_json()).lower() for kw in lower_keywords)
        ]
        return matches[offset : offset + limit if limit is not None else None]


# --- Model Registry ---
class ModelRegistry:
    def __init__(self):
        self.repos: List[BaseModelRepo] = self._initialize_repos()
        self.repo_map: dict[str, BaseModelRepo] = self._build_repo_map()

    def _initialize_repos(self) -> List[BaseModelRepo]:
        repo_classes: List[Type[BaseModelRepo]] = [HFModelsRepo, LiteLLMRepo]
        return [cls() for cls in repo_classes]

    def _build_repo_map(self) -> dict[str, BaseModelRepo]:
        repo_map = {}
        for repo in self.repos:
            repo_map[repo.provider_name] = repo
        return repo_map

    def _get_repos_by_provider(self, provider: Optional[str]) -> List[BaseModelRepo]:
        if provider is None:
            return self.repos
        repo = self.repo_map.get(provider.lower())
        return [repo] if repo else []

    def search_by_keyword(
        self, keyword: str, provider: Optional[str] = None,
        limit: Optional[int] = None, offset: int = 0
    ) -> List[Union[HuggingFaceProviderConfig, LitellmProviderConfig]]:
        results = []
        for repo in self._get_repos_by_provider(provider):
            results.extend(repo.search_models_by_keyword(keyword.lower()))
        return results[offset : offset + limit if limit is not None else None]

    def search_keywords_all(
        self, keywords: List[str], provider: Optional[str] = None,
        limit: Optional[int] = None, offset: int = 0
    ) -> List[Union[HuggingFaceProviderConfig, LitellmProviderConfig]]:
        lower_keywords = [kw.lower() for kw in keywords]
        results = []
        for repo in self._get_repos_by_provider(provider):
            results.extend(repo.search_keywords_all(lower_keywords))
        return results[offset : offset + limit if limit is not None else None]

    def list_all_models(self, limit: Optional[int] = None, offset: int = 0) -> List[str]:
        all_models = [model for repo in self.repos for model in repo.list_models()]
        return all_models[offset : offset + limit if limit is not None else None]

    def get_model(self, model_name: str, provider: Optional[str] = None
    ) -> Union[HuggingFaceProviderConfig, LitellmProviderConfig]:
        for repo in self._get_repos_by_provider(provider):
            try:
                return repo.get_model(model_name)
            except ModelNotFoundError:
                continue
        raise ModelNotFoundError(f"Model not found: {model_name}")
