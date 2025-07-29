from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.em_invoker.langchain_em_invoker import LangChainEMInvoker as LangChainEMInvoker
from typing import Any

class GoogleGenerativeAIEMInvoker(LangChainEMInvoker):
    """An embedding model invoker to interact with embedding models hosted through Google Generative AI API endpoints.

    The `GoogleGenerativeAIEMInvoker` class is responsible for invoking an embedding model using the Google
    Generative AI API. It uses the embedding model to transform a text or a list of input text into their vector
    representations.

    Attributes:
        em (GoogleGenerativeAIEmbeddings): The embedding model instance to interact with Google Generative AI models.
        retry_config (RetryConfig): The retry configuration for the embedding model.
    """
    def __init__(self, model_name: str, api_key: str, task_type: str | None = None, model_kwargs: Any = None, retry_config: RetryConfig | None = None) -> None:
        """Initializes a new instance of the GoogleGenerativeAIEMInvoker class.

        Args:
            model_name (str): The name of the Google Generative AI model to be used.
            api_key (str): The API key for accessing the Google Generative AI model.
            task_type (str | None, optional): The type of task to be performed by the embedding model. Defaults to None.
            model_kwargs (Any, optional): Additional keyword arguments to initiate the embedding model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
        """
