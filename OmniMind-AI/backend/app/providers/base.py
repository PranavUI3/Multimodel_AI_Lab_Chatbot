"""
Base AI Provider abstract interface for OmniMind AI.
Standardizes text, image, audio, embeddings, and RAG across multiple AI providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status


class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'gemini', 'openai', 'huggingface')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name."""
        pass

    @property
    @abstractmethod
    def supported_modalities(self) -> List[str]:
        """List of supported modalities: 'text', 'image', 'audio', 'embedding', 'rag_document'."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if valid API credentials are provided in settings."""
        pass

    def check_modality(self, modality: str):
        """Validates whether this provider supports the requested modality."""
        if modality not in self.supported_modalities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Provider '{self.display_name}' does not support '{modality}' modality. "
                    f"Supported modalities are: {', '.join(self.supported_modalities)}. "
                    "Please choose another provider."
                )
            )

    @abstractmethod
    async def generate_text(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Generates a text completion or chat response."""
        pass

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: Optional[str] = None) -> str:
        """Analyzes an image with an optional question/prompt."""
        pass

    @abstractmethod
    async def process_audio(self, audio_bytes: bytes, mime_type: str, action: str = "transcribe") -> str:
        """Transcribes or summarizes audio."""
        pass

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Generates embedding vector for text chunking/search."""
        pass

    @abstractmethod
    async def answer_with_context(self, question: str, context_chunks: List[str]) -> str:
        """Answers a question based strictly on provided document context chunks."""
        pass
