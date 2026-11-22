"""
Pydantic v2 schemas for request and response validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = Field(default=None, description="Existing conversation ID if continuing")
    message: str = Field(..., min_length=1, description="User text message")
    provider: str = Field(default="gemini", description="AI Provider name (gemini, openai, huggingface)")
    user_id: int = Field(default=1, description="User ID")

    @field_validator("message")
    @classmethod
    def message_not_empty_or_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Message cannot be empty or only whitespace")
        return stripped

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = {"gemini", "openai", "huggingface"}
        norm = v.lower().strip()
        if norm not in allowed:
            raise ValueError(f"Provider '{v}' not supported. Must be one of: {', '.join(sorted(allowed))}")
        return norm


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    provider: str
    role: str = "assistant"
    created_at: str


class ImageChatResponse(BaseModel):
    conversation_id: Optional[int] = None
    prompt: Optional[str] = None
    analysis: str
    provider: str
    created_at: str


class AudioChatResponse(BaseModel):
    conversation_id: Optional[int] = None
    action: str
    result: str
    provider: str
    created_at: str


class ProviderInfo(BaseModel):
    name: str
    display_name: str
    supported_modalities: List[str]
    configured: bool
    is_mock: bool
    model: str


class ProvidersResponse(BaseModel):
    providers: List[ProviderInfo]


class HealthResponse(BaseModel):
    status: str
    service: str
    database: Dict[str, Any]
    providers: Dict[str, bool]
    timestamp: str


class DocumentInfo(BaseModel):
    id: int
    user_id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    created_at: str


class DocumentUploadResponse(BaseModel):
    document_id: int
    filename: str
    file_type: str
    file_size: int
    chunks_created: int
    message: str


class DocumentAskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question about the document")
    provider: str = Field(default="gemini", description="Provider for answering")
    user_id: int = Field(default=1, description="User ID")

    @field_validator("question")
    @classmethod
    def question_not_empty_or_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Question cannot be empty or only whitespace")
        return stripped


class DocumentCitation(BaseModel):
    chunk_index: int
    chunk_text: str
    score: float


class DocumentAskResponse(BaseModel):
    document_id: int
    question: str
    answer: str
    provider: str
    citations: List[DocumentCitation]


class ConversationInfo(BaseModel):
    id: int
    user_id: int
    title: str
    provider: str
    created_at: str
    message_count: int = 0


class MessageInfo(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    modality: str
    provider: str
    created_at: str
