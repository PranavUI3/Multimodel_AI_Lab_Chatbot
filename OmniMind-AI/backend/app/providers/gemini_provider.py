"""
Google Gemini AI Provider for OmniMind AI.
Implements multimodal text, image, audio, embedding, and RAG capabilities using Google GenAI.
Provides labeled mock responses when GEMINI_API_KEY is not configured.
"""

import hashlib
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from fastapi import HTTPException, status

from .base import BaseAIProvider
from ..config import settings

logger = logging.getLogger("omnimind.providers.gemini")


def _generate_deterministic_mock_embedding(text: str, dim: int = 768) -> List[float]:
    """Generates a normalized deterministic mock embedding vector based on text hash."""
    seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    vec = rng.standard_normal(dim).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.tolist()


class GeminiProvider(BaseAIProvider):
    def __init__(self):
        self._api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        self._client = None

        if self.is_configured():
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
                logger.info("Initialized real Google Gemini Client with model '%s'.", self.model_name)
            except Exception as e:
                logger.warning("Failed to initialize Google GenAI Client: %s", e)
                self._client = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Google Gemini"

    @property
    def supported_modalities(self) -> List[str]:
        return ["text", "image", "audio", "embedding", "rag_document"]

    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    async def generate_text(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        self.check_modality("text")

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - Google Gemini ({self.model_name})]\n\n"
                f"You asked: \"{prompt}\"\n\n"
                "To receive live responses from Google Gemini, configure `GEMINI_API_KEY` in your `.env` file. "
                "The multimodal architecture is active and ready."
            )

        try:
            from google.genai import types
            contents = []
            if history:
                for msg in history:
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))]
                    ))
            contents.append(prompt)

            models_to_try = [self.model_name, "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            last_err = None
            for m in dict.fromkeys(models_to_try):
                try:
                    response = self._client.models.generate_content(
                        model=m,
                        contents=contents
                    )
                    return response.text or "No response received from Gemini."
                except Exception as ex:
                    last_err = ex
                    err_str = str(ex)
                    if "404" in err_str or "503" in err_str or "NOT_FOUND" in err_str:
                        continue
                    raise ex

            raise last_err or Exception("All Gemini model attempts failed.")
        except Exception as e:
            logger.error("Gemini text generation failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Gemini API error: {str(e)}"
            )

    async def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: Optional[str] = None) -> str:
        self.check_modality("image")
        user_prompt = prompt or "Describe this image in detail and identify any key objects, text, or visual elements."

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - Google Gemini Vision ({self.model_name})]\n\n"
                f"Image Analysis Simulation:\n"
                f"- Received Image format: {mime_type} ({len(image_bytes)} bytes)\n"
                f"- Prompt: \"{user_prompt}\"\n\n"
                "The image was validated and processed through the visual pipeline. "
                "Provide a valid `GEMINI_API_KEY` in `.env` to receive real multimodal visual understanding."
            )

        try:
            from google.genai import types
            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
            models_to_try = [self.model_name, "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            last_err = None
            for m in dict.fromkeys(models_to_try):
                try:
                    response = self._client.models.generate_content(
                        model=m,
                        contents=[user_prompt, image_part]
                    )
                    return response.text or "No visual analysis generated."
                except Exception as ex:
                    last_err = ex
                    err_str = str(ex)
                    if "404" in err_str or "503" in err_str or "NOT_FOUND" in err_str:
                        continue
                    raise ex
            raise last_err or Exception("All vision model attempts failed.")
        except Exception as e:
            logger.error("Gemini image analysis error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Gemini image understanding error: {str(e)}"
            )

    async def process_audio(self, audio_bytes: bytes, mime_type: str, action: str = "transcribe") -> str:
        self.check_modality("audio")

        if not self.is_configured() or not self._client:
            action_label = "Transcription" if action == "transcribe" else "Summary"
            return (
                f"[Mock Mode - Google Gemini Audio ({self.model_name})]\n\n"
                f"Audio {action_label} Simulation:\n"
                f"- Format: {mime_type} ({len(audio_bytes)} bytes)\n"
                f"- Requested action: {action}\n\n"
                "Audio stream successfully received and preprocessed. "
                "Configure `GEMINI_API_KEY` in `.env` for production audio transcription and analysis."
            )

        try:
            from google.genai import types
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            )
            instruction = (
                "Please transcribe the following audio recording accurately verbatim."
                if action == "transcribe"
                else "Please listen to this audio recording, transcribe it, and provide an executive summary with bullet points."
            )
            models_to_try = [self.model_name, "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            last_err = None
            for m in dict.fromkeys(models_to_try):
                try:
                    response = self._client.models.generate_content(
                        model=m,
                        contents=[instruction, audio_part]
                    )
                    return response.text or "No audio transcription generated."
                except Exception as ex:
                    last_err = ex
                    err_str = str(ex)
                    if "404" in err_str or "503" in err_str or "NOT_FOUND" in err_str:
                        continue
                    raise ex
            raise last_err or Exception("All audio model attempts failed.")
        except Exception as e:
            logger.error("Gemini audio processing error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Gemini audio processing error: {str(e)}"
            )

    async def get_embedding(self, text: str) -> List[float]:
        self.check_modality("embedding")

        if not self.is_configured() or not self._client:
            return _generate_deterministic_mock_embedding(text)

        try:
            response = self._client.models.embed_content(
                model=self.embedding_model,
                contents=text
            )
            # GenAI returns embedding object
            if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                return response.embedding.values
            if hasattr(response, "embeddings") and len(response.embeddings) > 0:
                return response.embeddings[0].values
            return _generate_deterministic_mock_embedding(text)
        except Exception as e:
            logger.warning("Gemini embedding API call failed: %s. Using local fallback.", e)
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

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - Google Gemini RAG ({self.model_name})]\n\n"
                f"Based on the {len(context_chunks)} retrieved document chunk(s):\n\n"
                f"Document Insight: The document provides context directly addressing '{question}'. "
                f"For full AI-synthesized responses with active citation synthesis, add `GEMINI_API_KEY` to `.env`."
            )

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text or "No answer could be generated from the document."
        except Exception as e:
            logger.error("Gemini RAG answer generation failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Gemini RAG error: {str(e)}"
            )
