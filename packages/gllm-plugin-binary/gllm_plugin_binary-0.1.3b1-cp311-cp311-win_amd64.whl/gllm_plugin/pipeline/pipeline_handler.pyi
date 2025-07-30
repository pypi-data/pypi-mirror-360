from _typeshed import Incomplete
from bosa_core import Plugin as Plugin
from bosa_core.plugin.handler import PluginHandler
from gllm_inference.catalog import LMRequestProcessorCatalog as LMRequestProcessorCatalog, PromptBuilderCatalog as PromptBuilderCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline as Pipeline
from gllm_plugin.config.app_config import AppConfig as AppConfig
from gllm_plugin.storage.base_chat_history_storage import BaseChatHistoryStorage as BaseChatHistoryStorage
from pydantic import BaseModel
from typing import Any

class ChatbotConfig(BaseModel):
    """Chatbot configuration class containing pipeline configs and metadata.

    Attributes:
        pipeline_type (str): Type of pipeline to use.
        pipeline_config (dict[str, Any]): Pipeline configuration dictionary.
        prompt_builder_catalogs (dict[str, PromptBuilderCatalog] | None): Mapping of prompt builder catalogs.
        lmrp_catalogs (dict[str, LMRequestProcessorCatalog] | None): Mapping of LM request processor catalogs.
    """
    pipeline_type: str
    pipeline_config: dict[str, Any]
    prompt_builder_catalogs: dict[str, PromptBuilderCatalog] | None
    lmrp_catalogs: dict[str, LMRequestProcessorCatalog] | None
    model_config: Incomplete

class PipelinePresetConfig(BaseModel):
    """Pipeline preset configuration class.

    Attributes:
        preset_id (str): Unique identifier for the pipeline preset.
        supported_models (list[dict[str, Any]]): List of models (including config) supported by this preset.
    """
    preset_id: str
    supported_models: list[dict[str, Any]]

class ChatbotPresetMapping(BaseModel):
    """Chatbot preset mapping.

    Attributes:
        pipeline_type (str): Type of pipeline.
        chatbot_preset_map (dict[str, PipelinePresetConfig]):
            Mapping of chatbot IDs to their pipeline preset configurations.
    """
    pipeline_type: str
    chatbot_preset_map: dict[str, PipelinePresetConfig]

logger: Incomplete

class PipelineHandler(PluginHandler):
    """Handler for pipeline builder plugins.

    This handler manages pipeline builder plugins and provides caching for built pipelines.

    Attributes:
        app_config (AppConfig): Application configuration.
        _activated_configs (dict[str, ChatbotPresetMapping]): Collection of chatbot preset mapping by pipeline types.
        _chatbot_configs (dict[str, ChatbotConfig]): Mapping of chatbot IDs to their configurations.
        _builders (dict[str, Plugin]): Mapping of chatbot IDs to their pipeline builder plugins.
        _plugins (dict[str, Plugin]): Mapping of pipeline types to their plugins.
        _pipeline_cache (dict[tuple[str, str], Pipeline]): Cache mapping (chatbot_id, model_name) to Pipeline instances.
        _chatbot_pipeline_keys (dict[str, set[tuple[str, str]]]): Mapping of chatbot IDs to their pipeline keys.
    """
    app_config: AppConfig
    chat_history_storage: Incomplete
    def __init__(self, app_config: AppConfig, chat_history_storage: BaseChatHistoryStorage) -> None:
        """Initialize the pipeline handler.

        Args:
            app_config (AppConfig): Application configuration.
            chat_history_storage (BaseChatHistoryStorage): Chat history storage.
        """
    @classmethod
    def create_injections(cls, instance: PipelineHandler) -> dict[type[Any], Any]:
        """Create injection mappings for pipeline builder plugins.

        Args:
            instance (PipelineHandler): The handler instance providing injections.

        Returns:
            dict[Type[Any], Any]: Dictionary mapping service types to their instances.
        """
    @classmethod
    def initialize_plugin(cls, instance: PipelineHandler, plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.
        For each pipeline builder plugin, we build pipelines for all supported models and cache them.

        Args:
            instance (PipelineHandler): The handler instance.
            plugin (Plugin): The pipeline builder plugin instance.
        """
    @classmethod
    async def ainitialize_plugin(cls, instance: PipelineHandler, plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.
        For each pipeline builder plugin, we build pipelines for all supported models and cache them.

        Args:
            instance (PipelineHandler): The handler instance.
            plugin (Plugin): The pipeline builder plugin instance.
        """
    @classmethod
    async def acleanup_plugins(cls, instance: PipelineHandler) -> None:
        """Cleanup all plugins.

        Args:
            instance (PipelineHandler): The handler instance.
        """
    def get_pipeline_builder(self, chatbot_id: str) -> Plugin:
        """Get a pipeline builder instance for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            Plugin: The pipeline builder instance.

        Raises:
            ValueError: If the chatbot ID is invalid or the model name is not supported.
        """
    def get_pipeline(self, chatbot_id: str, model_name: str) -> Pipeline:
        """Get a pipeline instance for the given chatbot and model name.

        Args:
            chatbot_id (str): The chatbot ID.
            model_name (str): The model to use for inference.

        Returns:
            Pipeline: The pipeline instance.

        Raises:
            ValueError: If the chatbot ID is invalid.
        """
    async def aget_pipeline(self, chatbot_id: str, model_name: str) -> Pipeline:
        """Get a pipeline instance for the given chatbot and model name (async version).

        Args:
            chatbot_id (str): The chatbot ID.
            model_name (str): The model to use for inference.

        Returns:
            Pipeline: The pipeline instance.

        Raises:
            ValueError: If the chatbot ID is invalid.
        """
    def get_pipeline_config(self, chatbot_id: str) -> dict[str, Any]:
        """Get the pipeline configuration by chatbot ID.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            dict[str, Any]: The pipeline configuration.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
    def get_pipeline_type(self, chatbot_id: str) -> str:
        """Get the pipeline type for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.
        """
    def get_use_docproc(self, chatbot_id: str) -> bool:
        """Get whether DocProc should be used for this chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            bool: Whether DocProc should be used.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
    def get_max_file_size(self, chatbot_id: str) -> int | None:
        """Get maximum file size for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            int | None: The maximum file size if provided.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
    async def create_chatbot(self, app_config: AppConfig, chatbot_id: str) -> None:
        """Create a new chatbot.

        Args:
            app_config (AppConfig): The application configuration.
            chatbot_id (str): The ID of the chatbot.
        """
    async def delete_chatbot(self, chatbot_id: str) -> None:
        """Delete a chatbot.

        Args:
            chatbot_id (str): The ID of the chatbot.
        """
    async def update_chatbots(self, app_config: AppConfig, chatbot_ids: list[str]) -> None:
        """Update the chatbots.

        Args:
            app_config (AppConfig): The application configuration.
            chatbot_ids (list[str]): The updated chatbot IDs.
        """
    async def aget_pipeline_builder(self, chatbot_id: str) -> Plugin:
        """Get a pipeline builder instance for the given chatbot (async version).

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            Plugin: The pipeline builder instance.

        Raises:
            ValueError: If the chatbot ID is invalid or the model name is not supported.
        """
