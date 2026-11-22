"""
Chat Service for OmniMind AI.
Manages conversations, message persistence, multi-turn history, and provider dispatch.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from ..database import db
from ..providers.factory import provider_factory


class ChatService:
    @staticmethod
    def get_or_create_conversation(
        conversation_id: Optional[int],
        user_id: int,
        initial_prompt: str,
        provider: str
    ) -> int:
        """Finds existing conversation or creates a new one with a derived title."""
        if conversation_id:
            row = db.fetch_one(
                "SELECT id FROM conversations WHERE id = %s",
                (conversation_id,)
            )
            if row:
                return row["id"]

        # Derive clean title from prompt (up to 40 chars)
        clean_prompt = initial_prompt.strip().replace("\n", " ")
        title = clean_prompt[:40] + ("..." if len(clean_prompt) > 40 else "")
        if not title:
            title = "New Multimodal Chat"

        new_id = db.execute_insert(
            "INSERT INTO conversations (user_id, title, provider) VALUES (%s, %s, %s)",
            (user_id, title, provider)
        )
        return new_id

    @staticmethod
    def get_conversation_history(conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieves recent conversation messages for multi-turn context."""
        rows = db.fetch_all(
            """
            SELECT role, content FROM messages 
            WHERE conversation_id = %s 
            ORDER BY id ASC LIMIT %s
            """,
            (conversation_id, limit)
        )
        return [{"role": r["role"], "content": r["content"]} for r in rows]

    @staticmethod
    def save_message(
        conversation_id: int,
        role: str,
        content: str,
        modality: str,
        provider: str
    ) -> int:
        """Persists a message to the database."""
        return db.execute_insert(
            """
            INSERT INTO messages (conversation_id, role, content, modality, provider)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (conversation_id, role, content, modality, provider)
        )

    @classmethod
    async def process_chat(
        cls,
        message: str,
        provider_name: str,
        conversation_id: Optional[int] = None,
        user_id: int = 1
    ) -> Dict[str, Any]:
        """Handles full text chat cycle: validation, persistence, AI generation, response persistence."""
        provider = provider_factory.get_provider(provider_name)
        conv_id = cls.get_or_create_conversation(conversation_id, user_id, message, provider_name)

        # Retrieve prior history
        history = cls.get_conversation_history(conv_id)

        # Save user message
        cls.save_message(conv_id, "user", message, "text", provider_name)

        # Generate response from AI provider
        ai_response = await provider.generate_text(prompt=message, history=history)

        # Save assistant message
        cls.save_message(conv_id, "assistant", ai_response, "text", provider_name)

        return {
            "conversation_id": conv_id,
            "message": ai_response,
            "provider": provider_name,
            "role": "assistant",
            "created_at": datetime.now().isoformat()
        }

    @classmethod
    async def process_image_chat(
        cls,
        image_bytes: bytes,
        mime_type: str,
        prompt: Optional[str],
        provider_name: str,
        conversation_id: Optional[int] = None,
        user_id: int = 1
    ) -> Dict[str, Any]:
        """Handles multimodal image understanding."""
        provider = provider_factory.get_provider(provider_name)
        user_prompt = prompt or "Analyze this image and describe its contents."
        conv_id = cls.get_or_create_conversation(conversation_id, user_id, f"[Image] {user_prompt}", provider_name)

        # Save user message
        cls.save_message(conv_id, "user", f"[Image Upload]: {user_prompt}", "image", provider_name)

        # Analyze image
        analysis = await provider.analyze_image(image_bytes, mime_type, user_prompt)

        # Save assistant response
        cls.save_message(conv_id, "assistant", analysis, "image", provider_name)

        return {
            "conversation_id": conv_id,
            "prompt": user_prompt,
            "analysis": analysis,
            "provider": provider_name,
            "created_at": datetime.now().isoformat()
        }

    @classmethod
    async def process_audio_chat(
        cls,
        audio_bytes: bytes,
        mime_type: str,
        action: str,
        provider_name: str,
        conversation_id: Optional[int] = None,
        user_id: int = 1
    ) -> Dict[str, Any]:
        """Handles audio transcription and summarization."""
        provider = provider_factory.get_provider(provider_name)
        action_clean = action.lower().strip() if action else "transcribe"
        conv_id = cls.get_or_create_conversation(conversation_id, user_id, f"[Audio {action_clean}]", provider_name)

        cls.save_message(conv_id, "user", f"[Audio Upload - {action_clean}]", "audio", provider_name)

        result = await provider.process_audio(audio_bytes, mime_type, action=action_clean)

        cls.save_message(conv_id, "assistant", result, "audio", provider_name)

        return {
            "conversation_id": conv_id,
            "action": action_clean,
            "result": result,
            "provider": provider_name,
            "created_at": datetime.now().isoformat()
        }


chat_service = ChatService()
