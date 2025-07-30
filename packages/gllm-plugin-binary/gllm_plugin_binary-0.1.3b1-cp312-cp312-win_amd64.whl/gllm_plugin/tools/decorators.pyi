from _typeshed import Incomplete
from langchain_core.tools import BaseTool
from typing import Any, Callable

logger: Incomplete

def tool_plugin(version: str = '1.0.0') -> Callable[[type[BaseTool]], type[BaseTool]]:
    '''Decorator to mark a BaseTool class as a tool plugin.

    This decorator adds metadata to the tool class that will be used by the
    plugin system when the tool is loaded. It doesn\'t directly register
    the tool with any system, allowing for use in external repositories.
    The actual tool name and description are intended to be retrieved
    from the tool instance at runtime.

    Args:
        version (str): Version of the plugin. Defaults to "1.0.0".

    Returns:
        Callable[[Type[BaseTool]], Type[BaseTool]]: A decorator function that wraps the tool class.

    Example:
        ```python
        @tool_plugin(version="1.0.0")
        class MyAwesomeTool(BaseTool):
            name = "my_awesome_tool"
            description = "Does something awesome"

            def _run(self, **kwargs):
                return "Awesome result!"
        ```
    '''
def is_tool_plugin(obj: Any) -> bool:
    """Check if an object is a tool plugin.

    Args:
        obj (Any): The object to check.

    Returns:
        bool: True if the object is a decorated tool plugin, False otherwise.
    """
def get_plugin_metadata(tool_class: type[BaseTool]) -> dict[str, Any]:
    """Get the plugin metadata from a decorated tool class.

    Args:
        tool_class (Type[BaseTool]): The tool class to get metadata from.

    Returns:
        dict[str, Any]: A dictionary of plugin metadata.

    Raises:
        ValueError: If the tool class is not a decorated tool plugin.
    """
