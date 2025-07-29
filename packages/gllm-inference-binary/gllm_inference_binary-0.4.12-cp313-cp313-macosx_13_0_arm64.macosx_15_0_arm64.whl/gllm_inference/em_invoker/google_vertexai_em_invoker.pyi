from gllm_core.utils.retry import RetryConfig as RetryConfig
from gllm_inference.em_invoker.langchain_em_invoker import LangChainEMInvoker as LangChainEMInvoker
from gllm_inference.utils import load_google_vertexai_project_id as load_google_vertexai_project_id
from typing import Any

class GoogleVertexAIEMInvoker(LangChainEMInvoker):
    """An embedding model invoker to interact with embedding models hosted through Google Vertex AI API endpoints.

    The `GoogleVertexAIEMInvoker` class is responsible for invoking an embedding model using the Google Vertex AI API.
    It uses the embedding model to transform a text or a list of input text into their vector representations.

    Attributes:
        em (VertexAIEmbeddings): The embedding model instance to interact with Google Vertex AI models.
        retry_config (RetryConfig): The retry configuration for the embedding model.

    Notes:
        In order to use the `GoogleVertexAIEMInvoker`, a credentials JSON file for a Google Cloud service account with
        the Vertex AI API enabled must be provided. For more information on how to create the credentials file,
        please refer to the following pages:
        1. https://cloud.google.com/docs/authentication/application-default-credentials.
        2. https://developers.google.com/workspace/guides/create-credentials.
    """
    def __init__(self, model_name: str, credentials_path: str, project_id: str | None = None, location: str = 'us-central1', model_kwargs: Any = None, retry_config: RetryConfig | None = None) -> None:
        '''Initializes a new instance of the GoogleVertexAIEMInvoker class.

        Args:
            model_name (str): The name of the multimodal embedding model to be used.
            credentials_path (str): The path to the Google Cloud service account credentials JSON file.
            project_id (str | None, optional): The Google Cloud project ID. Defaults to None, in which case the
                project ID will be loaded from the credentials file.
            location (str, optional): The location of the Google Cloud project. Defaults to "us-central1".
            model_kwargs (Any, optional): Additional keyword arguments to initiate the Google Vertex AI model.
                Defaults to None.
            retry_config (RetryConfig | None, optional): The retry configuration for the embedding model.
                Defaults to None, in which case a default config with no retry and 30.0 seconds timeout is used.
        '''
