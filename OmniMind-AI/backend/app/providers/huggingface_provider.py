"""
Hugging Face Inference Provider for OmniMind AI.
Implements text generation and RAG capabilities using Hugging Face Inference API.
Enforces modality compatibility (text only; rejects image and audio with clear error message).
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from .base import BaseAIProvider
from .gemini_provider import _generate_deterministic_mock_embedding
from ..config import settings

logger = logging.getLogger("omnimind.providers.huggingface")


class HuggingFaceProvider(BaseAIProvider):
    def __init__(self):
        self._api_key = settings.HUGGINGFACE_API_KEY
        self.model_name = settings.HUGGINGFACE_MODEL
        self._client = None

        if self.is_configured():
            try:
                from huggingface_hub import InferenceClient
                self._client = InferenceClient(model=self.model_name, token=self._api_key)
                logger.info("Initialized Hugging Face Inference Client for model '%s'.", self.model_name)
            except Exception as e:
                logger.warning("Failed to initialize Hugging Face client: %s", e)
                self._client = None

    @property
    def name(self) -> str:
        return "huggingface"

    @property
    def display_name(self) -> str:
        return "Hugging Face"

    @property
    def supported_modalities(self) -> List[str]:
        return ["text", "rag_document", "embedding"]

    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    async def generate_text(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        self.check_modality("text")

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - Hugging Face ({self.model_name})]\n\n"
                f"You asked: \"{prompt}\"\n\n"
                "To connect directly to Hugging Face Inference API, configure `HUGGINGFACE_API_KEY` in `.env`."
            )

        try:
            # Format prompt as text or chat completion
            messages = []
            if history:
                for msg in history:
                    messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            messages.append({"role": "user", "content": prompt})

            try:
                response = self._client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=500
                )
                return response.choices[0].message.content or "No response from Hugging Face."
            except Exception:
                # Fallback to direct text_generation
                result = self._client.text_generation(prompt, max_new_tokens=500)
                return result
        except Exception as e:
            logger.error("Hugging Face generation error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Hugging Face API error: {str(e)}"
            )

    async def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: Optional[str] = None) -> str:
        self.check_modality("image")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hugging Face provider does not support image analysis in this configuration. Please choose 'gemini' or 'openai'."
        )

    async def process_audio(self, audio_bytes: bytes, mime_type: str, action: str = "transcribe") -> str:
        self.check_modality("audio")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hugging Face provider does not support audio processing in this configuration. Please choose 'gemini' or 'openai'."
        )

    async def get_embedding(self, text: str) -> List[float]:
        self.check_modality("embedding")
        return _generate_deterministic_mock_embedding(text)

    async def answer_with_context(self, question: str, context_chunks: List[str]) -> str:
        self.check_modality("rag_document")

        if not context_chunks:
            return "I could not find any relevant information in the uploaded document to answer your question."

        context_str = "\n\n---\n\n".join([f"[Source Chunk {i+1}]:\n{c}" for i, c in enumerate(context_chunks)])
        prompt = (
            "You are OmniMind AI Document Intelligence Assistant.\n"
            "Answer the question based SOLELY on the provided document excerpts below.\n"
            "If the document excerpts do not contain sufficient information to answer the question, "
            "explicitly state that the relevant information is not found in the uploaded document.\n"
            "Cite the source chunk numbers when referencing facts.\n\n"
            f"Context Excerpts:\n{context_str}\n\n"
            f"Question: {question}\n\n"
            "Answer:"
        )

        return await self.generate_text(prompt)
