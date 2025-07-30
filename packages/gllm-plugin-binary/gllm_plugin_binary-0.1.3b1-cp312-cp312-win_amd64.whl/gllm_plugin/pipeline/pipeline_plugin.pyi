import abc
from abc import ABC, abstractmethod
from bosa_core.plugin.plugin import Plugin
from gllm_inference.catalog.catalog import BaseCatalog as BaseCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline as Pipeline
from gllm_plugin.pipeline.pipeline_handler import PipelineHandler as PipelineHandler
from typing import Any, Generic, TypeVar

PipelineState = TypeVar('PipelineState')
PipelinePresetConfig = TypeVar('PipelinePresetConfig', bound='BasePipelinePresetConfig')
PipelineRuntimeConfig = TypeVar('PipelineRuntimeConfig', bound='BaseModel')

class PipelineBuilderPlugin(Plugin, ABC, Generic[PipelineState, PipelinePresetConfig], metaclass=abc.ABCMeta):
    """Base class for pipeline builder plugins.

    This class combines the Plugin architecture with the Pipeline Builder functionality.

    Attributes:
        name (str): The name of the plugin.
        description (str): The description of the plugin.
        version (str): The version of the plugin.
        catalog (BaseCatalog): The catalog instance.
        additional_config_class (Type[PipelineRuntimeConfig] | None): The additional runtime configuration class.
        preset_config_class (Type[PipelinePresetConfig] | None): The preset configuration class.
    """
    name: str
    description: str
    version: str
    catalog: BaseCatalog[Any]
    additional_config_class: type[PipelineRuntimeConfig] | None
    preset_config_class: type[PipelinePresetConfig] | None
    @classmethod
    def get_preset_config_class(cls) -> type[PipelinePresetConfig]:
        """Get the preset_config_class.

        Returns:
            Type[PipelinePresetConfig]: The pipeline preset config class.

        Raises:
            NotImplementedError: If the preset_config_class is not defined.
        """
    @abstractmethod
    def build_initial_state(self, request_config: dict[str, Any], pipeline_config: dict[str, Any], **kwargs: Any) -> PipelineState:
        """Build the initial pipeline state.

        Args:
            request_config (dict[str, Any]): Request configuration.
            pipeline_config (dict[str, Any]): Pipeline configuration.
            kwargs (Any): Additional state arguments.

        Returns:
            PipelineState: Initial pipeline state.
        """
    @abstractmethod
    async def build(self, pipeline_config: dict[str, Any]) -> Pipeline:
        """Build a pipeline instance.

        Args:
            pipeline_config (dict[str, Any]): Pipeline configuration including model name and other settings.

        Returns:
            Pipeline: Built pipeline instance.
        """
    async def cleanup(self) -> None:
        """Cleanup the pipeline resources, if needed."""
    def build_additional_runtime_config(self, pipeline_config: dict[str, Any]) -> dict[str, Any]:
        """Build additional runtime configuration.

        Args:
            pipeline_config (dict[str, Any]): Pipeline configuration.

        Returns:
            dict[str, Any]: Additional runtime configuration.
        """
    def get_config(self) -> dict[str, Any]:
        """Get the pipeline configuration.

        Returns:
            dict[str, Any]: Pipeline configuration.
        """
