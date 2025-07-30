"""Module for managing prompt retrieval from a centralized YAML configuration file."""

from enum import Enum

from connexity_pipecat.core.config import get_config
from connexity_pipecat.data.consts import PromptType


def get_prompt(
    prompt_type: PromptType,
    project_cfg: dict,
    language: str = "en",
) -> str:
    """
    Retrieve a prompt string from the global `config` mapping.

    Args:
        project_cfg:
        prompt_type: PromptType enum value.
        language: Language code (defaults to "en").

    Returns:
        The prompt string.

    Raises:
        KeyError / ValueError with descriptive messages if anything is missing.
    """
    if "prompts" not in project_cfg:
        raise ValueError(f"No 'prompts' section for project'.")

    prompt_type_key = prompt_type.value
    project_prompts = project_cfg["prompts"]

    if prompt_type_key not in project_prompts:
        raise ValueError(
            f"Prompt type '{prompt_type_key}' missing'."
        )

    lang_dict = project_prompts[prompt_type_key]

    if language in lang_dict:
        return lang_dict[language]
    if "en" in lang_dict:
        # Fallback to English
        return lang_dict["en"]

    raise ValueError(
        f"No prompt available in '{language}' or English for type "
        f"'{prompt_type_key}'."
    )
