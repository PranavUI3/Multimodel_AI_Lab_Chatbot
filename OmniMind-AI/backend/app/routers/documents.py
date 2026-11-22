"""
Document router: upload, indexing, listing, deletion, and RAG document QA.
"""

from typing import List
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from ..schemas.schemas import DocumentAskRequest, DocumentAskResponse, DocumentInfo, DocumentUploadResponse
from ..services.document_service import document_service
from ..services.rag_service import rag_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(..., description="PDF or DOCX document to index"),
    provider: str = Form("gemini", description="Provider for embedding generation")
):
    """Uploads a PDF or DOCX file, extracts text, chunks it, embeds it, and stores it in MySQL."""
    file_bytes = await file.read()
    result = await document_service.upload_and_process_document(
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        file_bytes=file_bytes,
        provider_name=provider
    )
    return result


@router.get("", response_model=List[DocumentInfo], status_code=status.HTTP_200_OK)
async def list_documents(user_id: int = 1):
    """Lists all uploaded documents with chunk counts and metadata."""
    return document_service.list_documents(user_id=user_id)


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_document(document_id: int):
    """Deletes a document and all its associated chunks from the database."""
    document_service.delete_document(document_id=document_id)
    return {"success": True, "message": f"Document {document_id} and associated chunks deleted successfully."}


@router.post("/{document_id}/ask", response_model=DocumentAskResponse, status_code=status.HTTP_200_OK)
async def ask_document(document_id: int, request: DocumentAskRequest):
    """Performs RAG semantic retrieval over the document and answers the question with citations."""
    result = await rag_service.answer_document_question(
        document_id=document_id,
        question=request.question,
        provider_name=request.provider
    )
    return result
