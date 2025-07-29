"""
LLM client service for django-chain.
"""

import logging
import time
from typing import Any, Optional

from django.conf import settings

from django_chain.exceptions import LLMProviderAPIError, MissingDependencyError
from django_chain.providers import get_chat_model, get_embedding_model

logger = logging.getLogger(__name__)


class LLMClient:
    """Service for managing LLM interactions."""

    @classmethod
    def get_chat_model(cls, provider: Optional[str] = None, **kwargs) -> Any:
        """
        Get a configured chat model instance.

        Args:
            provider: Optional provider override
            **kwargs: Additional arguments for the chat model

        Returns:
            A configured chat model instance

        Raises:
            MissingDependencyError: If required provider package is not installed
            LLMProviderAPIError: If provider configuration is invalid
        """
        llm_settings = settings.DJANGO_LLM_SETTINGS
        provider = provider or llm_settings.get("DEFAULT_LLM_PROVIDER", "fake")
        default_chat_config = llm_settings.get(
            "DEFAULT_CHAT_MODEL",
            {
                "name": "fake-model",
                "temperature": 0.7,
                "max_tokens": 1024,
            },
        )

        api_key = llm_settings.get(f"{provider.upper()}_API_KEY")
        if not api_key and provider != "fake":
            raise LLMProviderAPIError(
                f"{provider.upper()}_API_KEY is not configured in DJANGO_LLM_SETTINGS"
            )

        try:
            model_config = {
                "api_key": api_key,
                "model_name": kwargs.get("model_name") or default_chat_config.get("name"),
                "temperature": kwargs.get("temperature")
                or default_chat_config.get("temperature", 0.7),
                **kwargs,
            }

            model = get_chat_model(provider=provider, **model_config)

            return model

        except ImportError as e:
            hint = f"Try running: pip install django-chain[{provider}]"
            raise MissingDependencyError(
                f"Required LLM provider '{provider}' is not installed.", hint=hint
            ) from e
        except Exception as e:
            logger.error(
                f"Error initializing LLM model for provider {provider}: {e}",
                exc_info=True,
            )
            raise LLMProviderAPIError(f"Failed to initialize LLM for provider {provider}") from e

    @classmethod
    def get_embedding_model(cls, provider: Optional[str] = None, **kwargs) -> Any:
        """
        Get a configured embedding model instance.

        Args:
            provider: Optional provider override
            **kwargs: Additional arguments for the embedding model

        Returns:
            A configured embedding model instance

        Raises:
            MissingDependencyError: If required provider package is not installed
            LLMProviderAPIError: If provider configuration is invalid
        """
        llm_settings = settings.DJANGO_LLM_SETTINGS
        embed_config = llm_settings.get("DEFAULT_EMBEDDING_MODEL", {})
        provider = provider or embed_config.get("provider", "fake")

        # Get API key for the provider
        api_key = llm_settings.get(f"{provider.upper()}_API_KEY")
        if not api_key and provider != "fake":
            raise LLMProviderAPIError(
                f"{provider.upper()}_API_KEY is not configured for embeddings"
            )

        try:
            # Get model configuration
            model_config = {
                "api_key": api_key,
                "model_name": kwargs.get("model_name") or embed_config.get("name"),
                **kwargs,
            }

            return get_embedding_model(provider=provider, **model_config)

        except ImportError as e:
            hint = f"Try running: pip install django-chain[{provider}]"
            raise MissingDependencyError(
                f"Required embedding provider '{provider}' is not installed.", hint=hint
            ) from e
        except Exception as e:
            logger.error(
                f"Error initializing embedding model for provider {provider}: {e}",
                exc_info=True,
            )
            raise LLMProviderAPIError(
                f"Failed to initialize embedding model for provider {provider}"
            ) from e
