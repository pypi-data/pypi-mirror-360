from gllm_inference.schema.enums import PromptRole as PromptRole
from gllm_inference.schema.model_io import Attachment as Attachment, ContentPlaceholder as ContentPlaceholder, LMOutput as LMOutput, Reasoning as Reasoning, ToolCall as ToolCall, ToolResult as ToolResult
from pydantic import BaseModel
from typing import Any

ResponseSchema = dict[str, Any] | type[BaseModel]
MultimodalContent = str | Attachment | bytes | ToolCall | ToolResult | Reasoning | ContentPlaceholder
MultimodalPrompt = list[tuple[PromptRole, list[MultimodalContent]]]
MultimodalOutput = str | LMOutput
EMContent = str | Attachment | tuple[str | Attachment, ...]
Vector = list[float]
UnimodalContent = str | list[str | ToolCall] | list[ToolResult]
UnimodalPrompt = list[tuple[PromptRole, UnimodalContent]]
