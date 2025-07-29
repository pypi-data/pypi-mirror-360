from _typeshed import Incomplete
from gllm_inference.em_invoker import AzureOpenAIEMInvoker as AzureOpenAIEMInvoker, OpenAIEMInvoker as OpenAIEMInvoker, VoyageEMInvoker as VoyageEMInvoker
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker as BaseEMInvoker
from gllm_inference.schema.model_id import ModelId as ModelId, ModelProvider as ModelProvider
from typing import Any

PROVIDER_TO_EM_INVOKER_MAP: dict[str, type[BaseEMInvoker]]
logger: Incomplete

class Key:
    """Defines valid keys in the config."""
    API_KEY: str
    AZURE_DEPLOYMENT: str
    AZURE_ENDPOINT: str
    MODEL_NAME: str

def build_em_invoker(model_id: str | ModelId, credentials: str | dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> BaseEMInvoker:
    '''Build an embedding model invoker based on the provided configurations.

    Args:
        model_id (str | ModelId): The model id, can either be a ModelId instance or a string in the following format:
            1. For `azure-openai` provider: `azure-openai/azure-endpoint:azure-deployment`.
            2. For other providers: `provider/model-name`.
        credentials (str | dict[str, Any] | None, optional): The credentials for the embedding model.
            Currently, only API key is supported. Defaults to None, in which case the credentials will
            be loaded from the appropriate environment variables.
        config (dict[str, Any] | None, optional): Additional configuration for the embedding model. Defaults to None.

    Returns:
        BaseEMInvoker: The initialized embedding model invoker.

    Raises:
        ValueError: If the provider is invalid.

    Usage examples:
        # Using OpenAI
        ```python
        em_invoker = build_em_invoker(
            model_id="openai/text-embedding-3-small",
            credentials="sk-..."
        )
        ```
        The credentials can also be provided through the `OPENAI_API_KEY` environment variable.

        # Using Azure OpenAI
        ```python
        em_invoker = build_em_invoker(
            model_id="azure-openai/https://my-resource.openai.azure.com:my-deployment",
            credentials="azure-api-key"
        )
        ```
        The credentials can also be provided through the `AZURE_OPENAI_API_KEY` environment variable.

        # Using Voyage
        ```python
        em_invoker = build_em_invoker(
            model_id="voyage/voyage-3.5-lite",
            credentials="sk-..."
        )
        ```
        The credentials can also be provided through the `VOYAGE_API_KEY` environment variable.

    Security warning:
        Please provide the EM invoker credentials ONLY to the `credentials` parameter. Do not put any kind of
        credentials in the `config` parameter as the content of the `config` parameter will be logged.
    '''
