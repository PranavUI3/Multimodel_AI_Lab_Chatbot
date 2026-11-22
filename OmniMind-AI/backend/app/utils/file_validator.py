"""
File validation utilities for images, audio, and documents.
"""

import os
import re
from fastapi import HTTPException, status
from ..config import settings


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename against path traversal and special characters."""
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)
    return clean if clean else "uploaded_file"


def validate_file_size(file_bytes: bytes, max_size_bytes: int = settings.MAX_FILE_SIZE_BYTES):
    """Ensures file size does not exceed the allowed maximum."""
    size = len(file_bytes)
    if size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )
    if size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        actual_mb = size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({actual_mb:.2f} MB) exceeds maximum allowed limit ({max_mb:.1f} MB)."
        )


def validate_image_file(filename: str, content_type: str, file_bytes: bytes):
    """Validates image file extension, MIME type, and non-empty content."""
    validate_file_size(file_bytes)
    allowed_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    ext = os.path.splitext(filename.lower())[1]
    
    if ext not in allowed_exts and content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format '{ext or content_type}'. Supported: PNG, JPG, JPEG, WEBP, GIF."
        )


def validate_audio_file(filename: str, content_type: str, file_bytes: bytes):
    """Validates audio file extension, MIME type, and non-empty content."""
    validate_file_size(file_bytes)
    allowed_exts = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".aac", ".flac"}
    ext = os.path.splitext(filename.lower())[1]

    if ext not in allowed_exts and content_type not in settings.ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format '{ext or content_type}'. Supported: MP3, WAV, M4A, OGG, WEBM."
        )


def validate_document_file(filename: str, content_type: str, file_bytes: bytes):
    """Validates document format (PDF or DOCX)."""
    validate_file_size(file_bytes)
    ext = os.path.splitext(filename.lower())[1]
    if ext not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported document format '{ext}'. Only PDF (.pdf) and Word DOCX (.docx) files are supported."
        )
