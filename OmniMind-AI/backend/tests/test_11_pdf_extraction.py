"""
Test 11: PDF extraction.
Verifies PDF binary text extraction using pypdf.
"""

from fpdf import FPDF
from app.utils.document_parser import extract_text_from_pdf

def test_pdf_text_extraction():
    # Create valid in-memory PDF with known text
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=14)
    expected_sentence = "OmniMind AI is an advanced multimodal intelligence assistant."
    pdf.cell(text=expected_sentence)
    pdf_bytes = bytes(pdf.output())

    # Extract text using document parser
    extracted = extract_text_from_pdf(pdf_bytes)

    assert extracted is not None
    assert "OmniMind AI is an advanced multimodal intelligence assistant" in extracted
