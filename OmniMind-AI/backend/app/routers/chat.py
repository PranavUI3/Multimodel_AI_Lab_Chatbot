"""
Chat router: handles text chat, visual understanding, and audio transcription/summarization.
"""

from typing import Optional
from fastapi import APIRouter, File, Form, UploadFile, status

from ..schemas.schemas import AudioChatResponse, ChatRequest, ChatResponse, ImageChatResponse
from ..services.chat_service import chat_service
from ..utils.file_validator import validate_audio_file, validate_image_file

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_text(request: ChatRequest):
    """Handles text conversations with provider selection and conversation history."""
    result = await chat_service.process_chat(
        message=request.message,
        provider_name=request.provider,
        conversation_id=request.conversation_id,
        user_id=request.user_id
    )
    return result


@router.post("/image", response_model=ImageChatResponse, status_code=status.HTTP_200_OK)
async def chat_image(
    image: UploadFile = File(..., description="Image file to analyze (PNG, JPG, WEBP)"),
    prompt: Optional[str] = Form(None, description="Optional question or instruction about the image"),
    provider: str = Form("gemini", description="AI provider (gemini, openai)"),
    conversation_id: Optional[int] = Form(None, description="Optional conversation ID to append to")
):
    """Processes an image upload with multimodal visual understanding."""
    image_bytes = await image.read()
    validate_image_file(image.filename, image.content_type, image_bytes)

    result = await chat_service.process_image_chat(
        image_bytes=image_bytes,
        mime_type=image.content_type or "image/jpeg",
        prompt=prompt,
        provider_name=provider,
        conversation_id=conversation_id
    )
    return result


@router.post("/audio", response_model=AudioChatResponse, status_code=status.HTTP_200_OK)
async def chat_audio(
    audio: UploadFile = File(..., description="Audio file (MP3, WAV, M4A, OGG)"),
    action: str = Form("transcribe", description="Action: 'transcribe' or 'summarize'"),
    provider: str = Form("gemini", description="AI provider (gemini, openai)"),
    conversation_id: Optional[int] = Form(None, description="Optional conversation ID")
):
    """Processes an audio upload for transcription or summarization."""
    audio_bytes = await audio.read()
    validate_audio_file(audio.filename, audio.content_type, audio_bytes)

    result = await chat_service.process_audio_chat(
        audio_bytes=audio_bytes,
        mime_type=audio.content_type or "audio/mpeg",
        action=action,
        provider_name=provider,
        conversation_id=conversation_id
    )
    return result
