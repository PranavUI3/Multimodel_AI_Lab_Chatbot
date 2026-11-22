"""
Pytest configuration and shared fixtures for OmniMind AI tests.
Mocks external API calls so tests run deterministically and without consuming paid credentials.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import db
from app.providers.gemini_provider import GeminiProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.huggingface_provider import HuggingFaceProvider


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensures test database is initialized."""
    db.init_db()
    yield


@pytest.fixture(autouse=True)
def mock_external_ai_apis(monkeypatch):
    """Mocks external network calls for all 3 AI providers during test runs."""

    async def mock_gemini_generate_text(self, prompt, history=None):
        return f"[Mock Mode - Google Gemini] Answer to: {prompt}"

    async def mock_gemini_analyze_image(self, image_bytes, mime_type, prompt=None):
        return f"[Mock Mode - Google Gemini Vision] Analysis of image ({len(image_bytes)} bytes)"

    async def mock_gemini_process_audio(self, audio_bytes, mime_type, action="transcribe"):
        return f"[Mock Mode - Google Gemini Audio] {action.capitalize()} completed ({len(audio_bytes)} bytes)"

    async def mock_openai_generate_text(self, prompt, history=None):
        return f"[Mock Mode - OpenAI] Response to: {prompt}"

    async def mock_openai_analyze_image(self, image_bytes, mime_type, prompt=None):
        return f"[Mock Mode - OpenAI GPT-4o Vision] Visual analysis ({len(image_bytes)} bytes)"

    async def mock_openai_process_audio(self, audio_bytes, mime_type, action="transcribe"):
        return f"[Mock Mode - OpenAI Whisper-1 Audio] Transcribed audio ({len(audio_bytes)} bytes)"

    async def mock_hf_generate_text(self, prompt, history=None):
        return f"[Mock Mode - Hugging Face] Response to: {prompt}"

    monkeypatch.setattr(GeminiProvider, "generate_text", mock_gemini_generate_text)
    monkeypatch.setattr(GeminiProvider, "analyze_image", mock_gemini_analyze_image)
    monkeypatch.setattr(GeminiProvider, "process_audio", mock_gemini_process_audio)

    monkeypatch.setattr(OpenAIProvider, "generate_text", mock_openai_generate_text)
    monkeypatch.setattr(OpenAIProvider, "analyze_image", mock_openai_analyze_image)
    monkeypatch.setattr(OpenAIProvider, "process_audio", mock_openai_process_audio)

    monkeypatch.setattr(HuggingFaceProvider, "generate_text", mock_hf_generate_text)


@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
