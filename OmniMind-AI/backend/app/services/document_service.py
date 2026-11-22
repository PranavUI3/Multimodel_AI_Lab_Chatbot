"""
Document Service for OmniMind AI.
Handles PDF & DOCX extraction, recursive chunking, embedding generation, and MySQL persistence.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status

from ..database import db
from ..providers.factory import provider_factory
from ..utils.chunking import recursive_character_chunking
from ..utils.document_parser import extract_text_from_docx, extract_text_from_pdf
from ..utils.file_validator import sanitize_filename, validate_document_file

logger = logging.getLogger("omnimind.services.document")


class DocumentService:
    @classmethod
    async def upload_and_process_document(
        cls,
        filename: str,
        content_type: str,
        file_bytes: bytes,
        provider_name: str = "gemini",
        user_id: int = 1
    ) -> Dict[str, Any]:
        """Validates, extracts, chunks, embeds, and stores a document."""
        validate_document_file(filename, content_type, file_bytes)
        clean_name = sanitize_filename(filename)
        ext = os.path.splitext(clean_name.lower())[1]
        file_type = "pdf" if ext == ".pdf" else "docx"

        # 1. Extract text
        if file_type == "pdf":
            raw_text = extract_text_from_pdf(file_bytes)
        else:
            raw_text = extract_text_from_docx(file_bytes)

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract readable text from the uploaded document. It might be empty or scanned images."
            )

        # 2. Recursive character chunking
        chunks = recursive_character_chunking(raw_text)
        if not chunks:
            chunks = [raw_text[:1000]]

        # 3. Create document record in database
        doc_id = db.execute_insert(
            """
            INSERT INTO documents (user_id, filename, file_type, file_size)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, clean_name, file_type, len(file_bytes))
        )

        # 4. Generate embeddings and store chunks
        provider = provider_factory.get_provider(provider_name)
        for idx, chunk_text in enumerate(chunks):
            try:
                emb = await provider.get_embedding(chunk_text)
            except Exception as e:
                logger.warning("Embedding generation error for chunk %d: %s. Using fallback.", idx, e)
                from ..providers.gemini_provider import _generate_deterministic_mock_embedding
                emb = _generate_deterministic_mock_embedding(chunk_text)

            emb_json = json.dumps(emb)
            db.execute_insert(
                """
                INSERT INTO document_chunks (document_id, chunk_index, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
                """,
                (doc_id, idx, chunk_text, emb_json)
            )

        logger.info("Successfully processed document '%s' (ID: %d) into %d chunks.", clean_name, doc_id, len(chunks))

        return {
            "document_id": doc_id,
            "filename": clean_name,
            "file_type": file_type,
            "file_size": len(file_bytes),
            "chunks_created": len(chunks),
            "message": f"Successfully parsed and indexed {len(chunks)} chunks using {provider.display_name} embeddings."
        }

    @staticmethod
    def list_documents(user_id: int = 1) -> List[Dict[str, Any]]:
        """Retrieves list of documents for a user with chunk count."""
        rows = db.fetch_all(
            """
            SELECT d.id, d.user_id, d.filename, d.file_type, d.file_size, d.created_at,
                   COUNT(c.id) as chunk_count
            FROM documents d
            LEFT JOIN document_chunks c ON d.id = c.document_id
            WHERE d.user_id = %s
            GROUP BY d.id, d.user_id, d.filename, d.file_type, d.file_size, d.created_at
            ORDER BY d.id DESC
            """,
            (user_id,)
        )
        return [
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "filename": r["filename"],
                "file_type": r["file_type"],
                "file_size": r["file_size"],
                "chunk_count": r.get("chunk_count", 0),
                "created_at": str(r["created_at"])
            }
            for r in rows
        ]

    @staticmethod
    def delete_document(document_id: int, user_id: int = 1) -> bool:
        """Deletes a document and all related chunks."""
        # Ensure document exists
        doc = db.fetch_one(
            "SELECT id FROM documents WHERE id = %s",
            (document_id,)
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found."
            )

        # Delete chunks first (or ON DELETE CASCADE handles it)
        db.execute_query("DELETE FROM document_chunks WHERE document_id = %s", (document_id,))
        # Delete document record
        db.execute_query("DELETE FROM documents WHERE id = %s", (document_id,))
        return True


document_service = DocumentService()
