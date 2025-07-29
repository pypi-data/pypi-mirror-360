from _typeshed import Incomplete
from enum import Enum
from gllm_core.constants import EventLevel as EventLevel, EventType as EventType
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.multimodal_lm_invoker.multimodal_lm_invoker import BaseMultimodalLMInvoker as BaseMultimodalLMInvoker
from gllm_inference.utils import get_mime_type as get_mime_type, invoke_google_multimodal_lm as invoke_google_multimodal_lm, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path
from io import BytesIO
from pydantic import BaseModel
from typing import Any

VALID_EXTENSION_MAP: Incomplete
VALID_EXTENSIONS: Incomplete
DEPRECATION_MESSAGE: str

class GoogleFileAttributes(BaseModel, arbitrary_types_allowed=True):
    """A class to define the attributes of a file to be uploaded to Google's servers.

    Attributes:
        content (BytesIO): The content of the file.
        mime_type (str): The MIME type of the file.
        display_name (str): The display name of the file, which is a hash of the content's bytes.
    """
    content: BytesIO
    mime_type: str
    display_name: str

class GoogleGenerativeAIMultimodalLMInvoker(BaseMultimodalLMInvoker[str | bytes, str]):
    """An invoker to interact with multimodal language models hosted through Google's Generative AI API endpoints.

    The `GoogleGenerativeAIMultimodalLMInvoker` class is designed to interact with multimodal language models hosted
    through Google's Generative AI API endpoints. It provides a framework for invoking multimodal language models with
    the provided prompt and hyperparameters. It supports both standard and streaming invocation. Streaming mode is
    enabled if an event emitter is provided.

    Attributes:
        client (genai.GenerativeModel): The Google Gemini client instance.
        extra_kwargs (dict[str, Any]): Additional keyword arguments for the `generate_content_async` method.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the multimodal language model.

    Notes:
        The `GoogleGenerativeAIMultimodalLMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Audio, which can be passed as:
            1. Base64 encoded audio bytes.
            2. URL pointing to an audio file.
            3. Local audio file path.
        3. Image, which can be passed as:
            1. Base64 encoded image bytes.
            2. URL pointing to an image.
            3. Local image file path.
        4. Video, which can be passed as:
            1. Base64 encoded video bytes.
            2. URL pointing to a video.
            3. Local video file path.
        5. Document, which can be passed as:
            1. Base64 encoded document bytes.
            2. URL pointing to a document.
            3. Local document file path.

        The `GoogleGenerativeAIMultimodalLMInvoker` also supports structured outputs through the `response_schema`
        argument, which accepts either:
        1. A Pydantic `BaseModel` class, in which the output will be parsed into an instance of the class.
        2. An instance of `typing_extensions.TypedDict`, in which the output will be parsed into a dictionary.
           2.1. Please make sure to import the `TypedDict` class from `typing_extensions` as the `TypedDict` class
                imported from the standard `typing` module is not supported.
        3. An `Enum` class, in which the output will be the most appropriate enum value.
        For more information, please refer to https://ai.google.dev/gemini-api/docs/structured-output?lang=python.
    """
    client: Incomplete
    extra_kwargs: Incomplete
    def __init__(self, model_name: str, api_key: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, response_schema: BaseModel | Enum | None = None) -> None:
        """Initializes a new instance of the GoogleGenerativeAIMultimodalLMInvoker class.

        Args:
            model_name (str): The name of the Google Gemini model.
            api_key (str): The API key for authenticating with Google Gemini.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            response_schema (BaseModel | Enum | None, optional): The response schema for the model. Defaults to None.
        """
