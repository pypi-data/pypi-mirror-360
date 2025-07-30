"""
This module provides functionality to parse the application's YAML configuration files.
It supports loading a single config (as 'default') or multiple configs from a folder.
"""

import os
import yaml
from typing import Optional

__all__ = ["load_config", "init_config", "get_config", "init_configs_from_folder", "list_config_names"]

_config_cache: dict[str, dict] = {}


def _parse_config_file(config_file_path: str) -> dict:
    """
    Parse a YAML configuration file and return its contents as a dictionary.
    """
    config_file_path = os.path.abspath(config_file_path)
    with open(config_file_path, "r") as file:
        return yaml.safe_load(file)


def load_config(config_file_path: str) -> dict:
    """
    Load and parse a YAML configuration file.
    This does not cache the result.
    """
    config_file_path = os.path.abspath(config_file_path)
    if not os.path.isfile(config_file_path):
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
    return _parse_config_file(config_file_path)


def init_config(config_file_path: str) -> None:
    """
    Load a config file and cache it as the 'default' config.
    """
    config = load_config(config_file_path)
    _config_cache["default"] = config


def init_configs_from_folder(folder_path: str) -> None:
    """
    Load all YAML config files from a given folder and cache them by name (filename without extension).
    """
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"Config folder not found: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.endswith((".yaml", ".yml")):
            name = os.path.splitext(filename)[0]
            full_path = os.path.join(folder_path, filename)
            _config_cache[name] = _parse_config_file(full_path)


def get_config(name: str | None = "default") -> dict:
    """
    Retrieve a previously loaded configuration by name.
    Raises if not initialized.
    """
    name = name or "default"
    if name not in _config_cache:
        raise KeyError(f"Config '{name}' not found. Make sure it's initialized.")
    return _config_cache[name]


def list_config_names() -> list[str]:
    """
    List all loaded config names.
    """
    return list(_config_cache.keys())
