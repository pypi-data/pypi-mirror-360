"""Create instance of SDK's Ollama model provider."""

from typing import Any

from strands.models.ollama import OllamaModel
from strands.types.models import Model


def instance(**model_config: Any) -> Model:
    """Create instance of SDK's Ollama model provider.

    Args:
        **model_config: Configuration options for the Ollama model.

    Returns:
        Ollama model provider.
    """
    # Extract host as positional argument, rest as keyword arguments
    host = model_config.pop(
        "host", "http://localhost:11434"
    )  # Default host if not provided
    return OllamaModel(host, **model_config)
