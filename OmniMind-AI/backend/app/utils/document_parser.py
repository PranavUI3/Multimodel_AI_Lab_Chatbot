"""
Document parser for PDF and DOCX files.
Uses pypdf and python-docx.
"""

import io
import re
from typing import Optional
from pypdf import PdfReader
import docx


def clean_extracted_text(raw_text: str) -> str:
    """Cleans extracted text: removes null bytes, normalizes whitespace and line breaks."""
    if not raw_text:
        return ""
    # Remove null bytes and non-printable control characters
    text = raw_text.replace("\x00", " ")
    # Normalize multiple carriage returns and line feeds
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove excessive consecutive spaces or tabs
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove excessive blank lines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text content from PDF binary data using pypdf."""
    reader = PdfReader(io.BytesIO(file_bytes))
    extracted_pages = []

    for idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            if page_text.strip():
                extracted_pages.append(f"--- Page {idx + 1} ---\n{page_text.strip()}")
        except Exception:
            continue

    combined_text = "\n\n".join(extracted_pages)
    return clean_extracted_text(combined_text)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text content from Word DOCX binary data using python-docx."""
    doc = docx.Document(io.BytesIO(file_bytes))
    extracted_paragraphs = []

    for para in doc.paragraphs:
        if para.text and para.text.strip():
            extracted_paragraphs.append(para.text.strip())

    # Also extract text from tables
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                extracted_paragraphs.append(" | ".join(row_cells))

    combined_text = "\n\n".join(extracted_paragraphs)
    return clean_extracted_text(combined_text)
