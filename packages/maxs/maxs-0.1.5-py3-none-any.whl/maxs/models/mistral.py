"""Create instance of SDK's Mistral model provider."""

from typing import Any

from strands.models.mistral import MistralModel
from strands.types.models import Model


def instance(**model_config: Any) -> Model:
    """Create instance of SDK's Mistral model provider.

    Args:
        **model_config: Configuration options for the Mistral model.

    Returns:
        Mistral model provider.
    """
    return MistralModel(**model_config)
