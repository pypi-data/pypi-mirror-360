from enum import StrEnum

class PromptRole(StrEnum):
    """Defines valid prompt roles."""
    SYSTEM = 'system'
    USER = 'user'
    ASSISTANT = 'assistant'

class AttachmentType(StrEnum):
    """Defines valid attachment types."""
    AUDIO = 'audio'
    DOCUMENT = 'document'
    IMAGE = 'image'
    VIDEO = 'video'
