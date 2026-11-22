"""
Test 12: DOCX extraction.
Verifies Word DOCX text extraction using python-docx.
"""

import io
import docx
from app.utils.document_parser import extract_text_from_docx

def test_docx_text_extraction():
    # Create valid in-memory DOCX document
    doc = docx.Document()
    doc.add_heading("OmniMind AI Document Test", level=1)
    doc.add_paragraph("This document contains information regarding Retrieval-Augmented Generation.")
    
    # Add a table
    table = doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Feature"
    table.cell(0, 1).text = "Support"
    table.cell(1, 0).text = "Multimodal"
    table.cell(1, 1).text = "Yes"

    docx_buffer = io.BytesIO()
    doc.save(docx_buffer)
    docx_bytes = docx_buffer.getvalue()

    # Extract text using document parser
    extracted = extract_text_from_docx(docx_bytes)

    assert extracted is not None
    assert "OmniMind AI Document Test" in extracted
    assert "Retrieval-Augmented Generation" in extracted
    assert "Multimodal" in extracted
