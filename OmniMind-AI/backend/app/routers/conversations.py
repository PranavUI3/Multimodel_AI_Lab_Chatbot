"""
Conversations router: retrieval of conversation history and messages.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status

from ..database import db
from ..schemas.schemas import ConversationInfo, MessageInfo

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("", response_model=List[ConversationInfo], status_code=status.HTTP_200_OK)
async def list_conversations(user_id: int = 1):
    """Retrieves all conversation sessions for the user with message counts."""
    rows = db.fetch_all(
        """
        SELECT c.id, c.user_id, c.title, c.provider, c.created_at,
               COUNT(m.id) as message_count
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.user_id = %s
        GROUP BY c.id, c.user_id, c.title, c.provider, c.created_at
        ORDER BY c.id DESC
        """,
        (user_id,)
    )
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "title": r["title"],
            "provider": r["provider"],
            "created_at": str(r["created_at"]),
            "message_count": r.get("message_count", 0)
        }
        for r in rows
    ]


@router.get("/{conversation_id}/messages", response_model=List[MessageInfo], status_code=status.HTTP_200_OK)
async def get_conversation_messages(conversation_id: int):
    """Retrieves all messages for a specific conversation in chronological order."""
    rows = db.fetch_all(
        """
        SELECT id, conversation_id, role, content, modality, provider, created_at
        FROM messages
        WHERE conversation_id = %s
        ORDER BY id ASC
        """,
        (conversation_id,)
    )
    return [
        {
            "id": r["id"],
            "conversation_id": r["conversation_id"],
            "role": r["role"],
            "content": r["content"],
            "modality": r["modality"],
            "provider": r["provider"],
            "created_at": str(r["created_at"])
        }
        for r in rows
    ]


@router.delete("/{conversation_id}", status_code=status.HTTP_200_OK)
async def delete_conversation(conversation_id: int):
    """Deletes a conversation and its messages."""
    db.execute_query("DELETE FROM messages WHERE conversation_id = %s", (conversation_id,))
    db.execute_query("DELETE FROM conversations WHERE id = %s", (conversation_id,))
    return {"success": True, "message": f"Conversation {conversation_id} deleted."}
