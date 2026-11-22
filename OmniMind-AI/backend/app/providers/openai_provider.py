"""
OpenAI Provider for OmniMind AI.
Implements text, vision (GPT-4o), audio transcription (Whisper-1), and RAG capabilities.
Provides labeled mock responses when OPENAI_API_KEY is not configured.
"""

import base64
import io
import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from .base import BaseAIProvider
from .gemini_provider import _generate_deterministic_mock_embedding
from ..config import settings

logger = logging.getLogger("omnimind.providers.openai")


class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        self._api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_MODEL
        self._client = None

        if self.is_configured():
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self._api_key)
                logger.info("Initialized OpenAI AsyncClient with model '%s'.", self.model_name)
            except Exception as e:
                logger.warning("Failed to initialize OpenAI Client: %s", e)
                self._client = None

    @property
    def name(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI"

    @property
    def supported_modalities(self) -> List[str]:
        return ["text", "image", "audio", "embedding", "rag_document"]

    def is_configured(self) -> bool:
        return bool(self._api_key and self._api_key.strip())

    async def generate_text(self, prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        self.check_modality("text")

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - OpenAI ({self.model_name})]\n\n"
                f"You asked: \"{prompt}\"\n\n"
                "To receive live responses from OpenAI GPT-4o, configure `OPENAI_API_KEY` in your `.env` file. "
                "OpenAI integration code is fully implemented and operational."
            )

        try:
            messages = []
            if history:
                for msg in history:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            messages.append({"role": "user", "content": prompt})

            completion = await self._client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content or "No response received from OpenAI."
        except Exception as e:
            logger.error("OpenAI text generation error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI API error: {str(e)}"
            )

    async def analyze_image(self, image_bytes: bytes, mime_type: str, prompt: Optional[str] = None) -> str:
        self.check_modality("image")
        user_prompt = prompt or "Describe this image in detail and identify any key objects, text, or visual elements."

        if not self.is_configured() or not self._client:
            return (
                f"[Mock Mode - OpenAI GPT-4o Vision]\n\n"
                f"Visual Analysis Simulation:\n"
                f"- Image format: {mime_type} ({len(image_bytes)} bytes)\n"
                f"- User prompt: \"{user_prompt}\"\n\n"
                "To process live images with GPT-4o Vision, specify `OPENAI_API_KEY` in your `.env` file."
            )

        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_uri = f"data:{mime_type};base64,{b64_image}"

            response = await self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {"type": "image_url", "image_url": {"url": data_uri}}
                        ]
                    }
                ]
            )
            return response.choices[0].message.content or "No image analysis generated."
        except Exception as e:
            logger.error("OpenAI vision error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI Vision API error: {str(e)}"
            )

    async def process_audio(self, audio_bytes: bytes, mime_type: str, action: str = "transcribe") -> str:
        self.check_modality("audio")

        if not self.is_configured() or not self._client:
            action_label = "Transcription" if action == "transcribe" else "Summary"
            return (
                f"[Mock Mode - OpenAI Whisper-1 Audio]\n\n"
                f"Audio {action_label} Simulation:\n"
                f"- Stream format: {mime_type} ({len(audio_bytes)} bytes)\n"
                f"- Action: {action}\n\n"
                "To transcribe and summarize audio using OpenAI Whisper, configure `OPENAI_API_KEY` in `.env`."
            )

        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.mp3"

            transcription = await self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            text = transcription.text

            if action == "summarize":
                summary_prompt = f"Please provide a concise, structured executive summary of the following audio transcript:\n\n{text}"
                return await self.generate_text(summary_prompt)

            return text
        except Exception as e:
            logger.error("OpenAI audio error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"OpenAI Audio API error: {str(e)}"
            )

    async def get_embedding(self, text: str) -> List[float]:
        self.check_modality("embedding")

        if not self.is_configured() or not self._client:
            return _generate_deterministic_mock_embedding(text)

        try:
            response = await self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning("OpenAI embedding API call failed: %s. Using local fallback.", e)
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
