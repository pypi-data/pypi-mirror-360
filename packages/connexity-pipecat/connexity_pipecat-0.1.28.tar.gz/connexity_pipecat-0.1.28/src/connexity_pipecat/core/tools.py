from pipecat_tools import ToolManager

tool_manager = ToolManager()


def register_custom_tools(handlers_dir, config_file):
    tool_manager.register_tools_from_directory(
        handlers_dir=handlers_dir,
        config_file=config_file
    )
    return tool_manager


def get_tool_manager():
    """
    Return the current global ToolManager instance, reflecting all registrations.
    """
    return tool_manager


def get_required_constants(function_names):
    """Return unresolved constants for the supplied functions.

    Args:
        function_names: Iterable of function names to inspect.

    Returns:
        Dict[str, List[str]]: A mapping where each key is a function name
        and the value is a sorted list of constant names that are still
        unset (``None``).
    """
    return tool_manager.get_required_constants(function_names)


def get_all_set_constants():
    """Return every constant that already has a value.

    Returns:
        Dict[str, Dict[str, object]]: Mapping of function names to a
        sub‑mapping of constant names and their current values.
    """
    return tool_manager.get_all_set_constants()


def set_constants(path_to_configs: str) -> ToolManager:
    """Load constants from JSON files located in a directory.

    Each ``*.json`` file should be named after a function (e.g.
    ``book_appointment.json``) and contain a flat JSON object whose keys
    are constant names.

    Args:
        path_to_configs: Path to the directory containing the JSON files.

    Raises:
        ValueError: If the provided path is not a directory.

    Returns:
        updated tool_manager.
    """
    tool_manager.set_constants(path_to_configs)
    return tool_manager

