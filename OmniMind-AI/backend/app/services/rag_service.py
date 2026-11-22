"""
RAG (Retrieval-Augmented Generation) Service for OmniMind AI.
Performs semantic retrieval across document chunks via cosine similarity and synthesizes grounded answers.
"""

import json
import logging
from typing import Any, Dict, List
from fastapi import HTTPException, status

from ..config import settings
from ..database import db
from ..providers.factory import provider_factory
from ..utils.similarity import find_top_k_chunks

logger = logging.getLogger("omnimind.services.rag")


class RAGService:
    @classmethod
    async def answer_document_question(
        cls,
        document_id: int,
        question: str,
        provider_name: str = "gemini"
    ) -> Dict[str, Any]:
        """Performs retrieval and generation for document question answering."""
        # 1. Verify document exists
        doc = db.fetch_one("SELECT id, filename FROM documents WHERE id = %s", (document_id,))
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document ID {document_id} not found."
            )

        # 2. Retrieve all chunks and embeddings for the document
        chunks_rows = db.fetch_all(
            """
            SELECT id, chunk_index, chunk_text, embedding 
            FROM document_chunks 
            WHERE document_id = %s 
            ORDER BY chunk_index ASC
            """,
            (document_id,)
        )

        if not chunks_rows:
            return {
                "document_id": document_id,
                "question": question,
                "answer": "This document does not contain any readable text chunks.",
                "provider": provider_name,
                "citations": []
            }

        # 3. Generate query embedding
        provider = provider_factory.get_provider(provider_name)
        try:
            query_vector = await provider.get_embedding(question)
        except Exception as e:
            logger.warning("Error generating embedding for query: %s. Using local fallback.", e)
            from ..providers.gemini_provider import _generate_deterministic_mock_embedding
            query_vector = _generate_deterministic_mock_embedding(question)

        # 4. Find top-K chunks using cosine similarity
        top_chunks = find_top_k_chunks(
            query_vector=query_vector,
            chunks=chunks_rows,
            top_k=settings.TOP_K_CHUNKS,
            min_similarity=settings.SIMILARITY_THRESHOLD
        )

        # 5. Handle case where relevant information is not found
        if not top_chunks:
            return {
                "document_id": document_id,
                "question": question,
                "answer": (
                    "I could not find any relevant information in the uploaded document to answer your question. "
                    "The retrieved content did not match the question with sufficient semantic confidence."
                ),
                "provider": provider_name,
                "citations": []
            }

        # 6. Extract text excerpts and prepare citations
        context_texts = [c["chunk_text"] for c in top_chunks]
        citations = [
            {
                "chunk_index": c["chunk_index"],
                "chunk_text": c["chunk_text"][:300] + ("..." if len(c["chunk_text"]) > 300 else ""),
                "score": c["score"]
            }
            for c in top_chunks
        ]

        # 7. Generate answer via provider
        answer = await provider.answer_with_context(question=question, context_chunks=context_texts)

        return {
            "document_id": document_id,
            "question": question,
            "answer": answer,
            "provider": provider_name,
            "citations": citations
        }


rag_service = RAGService()
