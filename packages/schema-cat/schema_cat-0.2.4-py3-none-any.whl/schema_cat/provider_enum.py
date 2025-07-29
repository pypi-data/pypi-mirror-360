import logging
import os
from enum import Enum
from typing import List, Dict, Any

from dotenv import load_dotenv

from schema_cat.providers import OpenRouterProvider, OpenAIProvider, AnthropicProvider
from schema_cat.providers.comet_provider import CometProvider


class Provider(str, Enum):
    OPENROUTER = "openrouter"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COMET = "comet"

    @property
    def call(self):
        if self == Provider.OPENROUTER:
            return OpenRouterProvider().call
        elif self == Provider.OPENAI:
            return OpenAIProvider().call
        elif self == Provider.ANTHROPIC:
            return AnthropicProvider().call
        elif self == Provider.COMET:
            return CometProvider().call
        else:
            raise NotImplementedError(f"No call method for provider {self}")

    async def init_models(self) -> List[Dict[str, Any]]:
        """
        Retrieve all available models from the provider's endpoint.

        Returns:
            List of model dictionaries containing model information.
            Each dictionary contains at least:
            - 'id': Model identifier/name
            - 'object': Model object type (usually 'model')
            Additional fields may include context_length, pricing, etc.
        """
        if self == Provider.OPENROUTER:
            return await OpenRouterProvider().get_available_models()
        elif self == Provider.OPENAI:
            return await OpenAIProvider().get_available_models()
        elif self == Provider.ANTHROPIC:
            return await AnthropicProvider().get_available_models()
        elif self == Provider.COMET:
            return await CometProvider().get_available_models()
        else:
            raise NotImplementedError(f"No init_models method for provider {self}")


def _provider_api_key_available(provider: Provider) -> bool:
    if provider == Provider.OPENROUTER:
        return bool(os.getenv("OPENROUTER_API_KEY"))
    elif provider == Provider.OPENAI:
        return bool(os.getenv("OPENAI_API_KEY"))
    elif provider == Provider.ANTHROPIC:
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    elif provider == Provider.COMET:
        return bool(os.getenv("COMET_API_KEY"))
    return False


logger = logging.getLogger("schema-cat")


def get_preferred_providers_from_env(preferred_providers: list) -> list[Provider]:
    load_dotenv()
    # First check environment variable
    env_providers = os.getenv('SCHEMA_CAT_PREFERRED_PROVIDERS')
    if env_providers:
        for provider_str in env_providers.split(','):
            provider_str = provider_str.strip()
            if provider_str:
                try:
                    preferred_providers.append(Provider(provider_str))
                except ValueError:
                    logger.warning(f'Invalid provider {provider_str}'"")
    return preferred_providers
