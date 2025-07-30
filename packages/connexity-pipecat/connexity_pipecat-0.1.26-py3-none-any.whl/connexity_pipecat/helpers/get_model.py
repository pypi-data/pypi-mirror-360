"""
Factory utilities for creating Pipecat LLM service instances.

Supported vendors:
    * OpenAI
    * Groq
    * Google Vertex AI
    * Fireworks AI
"""

from __future__ import annotations

import inspect
from typing import Any, Dict, Type

# Pipecat service wrappers

from pipecat.services.openai.llm import OpenAILLMService
from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.google.llm_vertex import GoogleVertexLLMService
from pipecat.services.fireworks.llm import FireworksLLMService

# Application‑wide API keys / credentials
import connexity_pipecat.data.consts as consts


class ModelFactory:
    """Factory for creating Pipecat LLM service instances based on vendor name."""

    _registry: Dict[str, Type[Any]] = {
        # OpenAI
        "openai": OpenAILLMService,
        # Groq
        "groq": GroqLLMService,
        # Google Vertex AI (multiple aliases accepted)
        "google": GoogleVertexLLMService,
        "vertex": GoogleVertexLLMService,
        "vertexai": GoogleVertexLLMService,
        # Fireworks AI
        "fireworks": FireworksLLMService,
        "fireworksai": FireworksLLMService,
    }

    # Attribute names inside `consts` that contain each vendor's credential
    _API_KEY_ATTRS: Dict[str, str] = {
        "openai": "OPENAI_API_KEY",
        "groq": "GROQ_API_KEY",
        "fireworks": "FIREWORKS_API_KEY",
        "fireworksai": "FIREWORKS_API_KEY",
        "google": "GOOGLE_CREDENTIALS",
        "vertex": "GOOGLE_CREDENTIALS",
        "vertexai": "GOOGLE_CREDENTIALS",
    }

    # --------------------------------------------------------------------- #
    # Public helpers                                                        #
    # --------------------------------------------------------------------- #
    @classmethod
    def register_vendor(cls, vendor: str, service_cls: Type[Any]) -> None:
        """
        Register a custom vendor implementation.

        Args:
            vendor: Name of the vendor (e.g. ``"anthropic"``).
            service_cls: Concrete Pipecat service class implementing that vendor.
        """
        cls._registry[vendor.strip().lower()] = service_cls

    @classmethod
    def get_model(cls, vendor: str, model_name: str, **init_kwargs) -> Any:
        """
        Instantiate a Pipecat LLM service.

        Args:
            vendor: The LLM vendor identifier (case‑insensitive).
            model_name: The model identifier that the vendor understands.
            **init_kwargs: Additional kwargs forwarded to the service constructor
                           (e.g. ``api_key``, ``params``, ``credentials_path``).

        Returns:
            Instantiated service object ready to be used in Pipecat pipelines.

        Raises:
            ValueError: If the vendor is unknown.
        """
        key = vendor.strip().lower()
        if key not in cls._registry:
            valid = ", ".join(sorted(cls._registry.keys()))
            raise ValueError(f"Unknown vendor '{vendor}'. Expected one of: {valid}")

        service_cls = cls._registry[key]

        # ------------------------------------------------------------------ #
        # Inject vendor‑specific credential (api_key / credentials) if absent
        # ------------------------------------------------------------------ #
        if key in cls._API_KEY_ATTRS:
            cred_value = getattr(consts, cls._API_KEY_ATTRS[key], None)
            if cred_value:
                cred_kw = "credentials" if key in {"google", "vertex", "vertexai"} else "api_key"
                # Only supply it when the concrete __init__ accepts the kwarg
                sig = inspect.signature(cls._registry[key].__init__)
                if cred_kw in sig.parameters and cred_kw not in init_kwargs:
                    init_kwargs[cred_kw] = cred_value

        # ------------------------------------------------------------------ #
        # Build a sensible default InputParams if none was provided
        # ------------------------------------------------------------------ #
        if "params" not in init_kwargs or init_kwargs["params"] is None:
            params_cls = getattr(service_cls, "InputParams", None)
            if params_cls:
                try:
                    # Keep only arguments actually accepted by the params class
                    params_sig = inspect.signature(params_cls.__init__)
                    defaults = {"top_p": 0.05, "temperature": 1, "max_tokens": 1000}
                    param_kwargs = {
                        k: v for k, v in defaults.items() if k in params_sig.parameters
                    }
                    init_kwargs["params"] = params_cls(**param_kwargs)
                except Exception:  # pylint: disable=broad-except
                    # Fall back silently if we cannot construct params
                    pass

        # Keep only kwargs accepted by the concrete service constructor
        sig = inspect.signature(service_cls.__init__)
        accepted = set(sig.parameters)
        filtered_kwargs = {k: v for k, v in init_kwargs.items() if k in accepted}

        # Ensure the model identifier is passed with the correct keyword
        if "model" in accepted:
            filtered_kwargs["model"] = model_name
        else:  # Fallback: prepend as first positional arg
            filtered_kwargs = {f"_model_arg": model_name, **filtered_kwargs}

        return service_cls(**filtered_kwargs)



# Convenience aliases
get_llm_service = ModelFactory.get_model  # Preferred
