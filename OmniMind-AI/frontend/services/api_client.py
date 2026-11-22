"""
API Client for OmniMind AI Frontend.
Communicates with FastAPI backend over HTTP using requests.
Handles error formatting, timeouts, and file uploads.
"""

import os
from typing import Any, Dict, List, Optional
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class OmniMindAPIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}{endpoint}"

    def check_health(self) -> Dict[str, Any]:
        """Checks if backend service is reachable."""
        try:
            resp = requests.get(self._url("/api/health"), timeout=4)
            if resp.status_code == 200:
                return resp.json()
            return {"status": "unhealthy", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    def get_providers(self) -> List[Dict[str, Any]]:
        """Retrieves list of AI providers and capabilities."""
        try:
            resp = requests.get(self._url("/api/providers"), timeout=5)
            if resp.status_code == 200:
                return resp.json().get("providers", [])
            return []
        except Exception:
            return []

    def send_chat(
        self,
        message: str,
        provider: str = "gemini",
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sends text chat message to FastAPI backend."""
        payload = {
            "message": message,
            "provider": provider,
            "conversation_id": conversation_id,
            "user_id": 1
        }
        try:
            resp = requests.post(self._url("/api/chat"), json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            err_detail = resp.json().get("detail", resp.text)
            return {"error": f"Backend error ({resp.status_code}): {err_detail}"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out waiting for AI provider response."}
        except Exception as e:
            return {"error": f"Failed to connect to backend: {str(e)}"}

    def send_image(
        self,
        image_bytes: bytes,
        filename: str,
        mime_type: str,
        prompt: Optional[str] = None,
        provider: str = "gemini",
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sends image for multimodal visual analysis."""
        files = {"image": (filename, image_bytes, mime_type)}
        data = {"provider": provider}
        if prompt:
            data["prompt"] = prompt
        if conversation_id:
            data["conversation_id"] = str(conversation_id)

        try:
            resp = requests.post(self._url("/api/chat/image"), files=files, data=data, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            err_detail = resp.json().get("detail", resp.text)
            return {"error": f"Image analysis failed ({resp.status_code}): {err_detail}"}
        except Exception as e:
            return {"error": f"Image upload error: {str(e)}"}

    def send_audio(
        self,
        audio_bytes: bytes,
        filename: str,
        mime_type: str,
        action: str = "transcribe",
        provider: str = "gemini",
        conversation_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sends audio for transcription or summarization."""
        files = {"audio": (filename, audio_bytes, mime_type)}
        data = {
            "action": action,
            "provider": provider
        }
        if conversation_id:
            data["conversation_id"] = str(conversation_id)

        try:
            resp = requests.post(self._url("/api/chat/audio"), files=files, data=data, timeout=90)
            if resp.status_code == 200:
                return resp.json()
            err_detail = resp.json().get("detail", resp.text)
            return {"error": f"Audio processing failed ({resp.status_code}): {err_detail}"}
        except Exception as e:
            return {"error": f"Audio upload error: {str(e)}"}

    def upload_document(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        provider: str = "gemini"
    ) -> Dict[str, Any]:
        """Uploads and indexes PDF or DOCX file."""
        files = {"file": (filename, file_bytes, mime_type)}
        data = {"provider": provider}
        try:
            resp = requests.post(self._url("/api/documents/upload"), files=files, data=data, timeout=60)
            if resp.status_code == 201:
                return resp.json()
            err_detail = resp.json().get("detail", resp.text)
            return {"error": f"Document upload failed ({resp.status_code}): {err_detail}"}
        except Exception as e:
            return {"error": f"Document upload error: {str(e)}"}

    def list_documents(self) -> List[Dict[str, Any]]:
        """Retrieves list of uploaded documents."""
        try:
            resp = requests.get(self._url("/api/documents"), timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception:
            return []

    def delete_document(self, document_id: int) -> bool:
        """Deletes a document and its chunks."""
        try:
            resp = requests.delete(self._url(f"/api/documents/{document_id}"), timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def ask_document(
        self,
        document_id: int,
        question: str,
        provider: str = "gemini"
    ) -> Dict[str, Any]:
        """Performs RAG query against an uploaded document."""
        payload = {
            "question": question,
            "provider": provider,
            "user_id": 1
        }
        try:
            resp = requests.post(self._url(f"/api/documents/{document_id}/ask"), json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            err_detail = resp.json().get("detail", resp.text)
            return {"error": f"Document QA failed ({resp.status_code}): {err_detail}"}
        except Exception as e:
            return {"error": f"RAG query error: {str(e)}"}

    def list_conversations(self) -> List[Dict[str, Any]]:
        """Retrieves user conversation sessions."""
        try:
            resp = requests.get(self._url("/api/conversations"), timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception:
            return []

    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Retrieves messages for a conversation."""
        try:
            resp = requests.get(self._url(f"/api/conversations/{conversation_id}/messages"), timeout=5)
            if resp.status_code == 200:
                return resp.json()
            return []
        except Exception:
            return []

    def delete_conversation(self, conversation_id: int) -> bool:
        """Deletes a conversation."""
        try:
            resp = requests.delete(self._url(f"/api/conversations/{conversation_id}"), timeout=5)
            return resp.status_code == 200
        except Exception:
            return False


api_client = OmniMindAPIClient()
