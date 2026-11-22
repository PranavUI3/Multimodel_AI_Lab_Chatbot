"""
Document upload and indexing component for OmniMind AI.
Allows uploading PDF or DOCX documents to the FastAPI backend.
"""

import streamlit as st
from services.api_client import api_client


def render_document_uploader():
    """Renders the document upload widget."""
    with st.expander("📄 Upload Document to Knowledge Base (PDF / DOCX)", expanded=False):
        uploaded_doc = st.file_uploader(
            "Choose a PDF or Word DOCX file",
            type=["pdf", "docx"],
            key="doc_uploader",
            help="Files will be parsed, chunked with recursive character splitting, embedded, and stored in MySQL."
        )

        col_prov, col_btn = st.columns([3, 2])
        with col_prov:
            doc_prov = st.selectbox(
                "Embedding Provider:",
                options=["gemini", "openai"],
                format_func=lambda x: "Google Gemini" if x == "gemini" else "OpenAI",
                key="doc_embed_provider"
            )

        with col_btn:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if uploaded_doc is not None:
                if st.button("🚀 Upload & Index Document", key="btn_upload_doc"):
                    with st.spinner("Processing document (extracting, chunking, and embedding)..."):
                        doc_bytes = uploaded_doc.getvalue()
                        res = api_client.upload_document(
                            file_bytes=doc_bytes,
                            filename=uploaded_doc.name,
                            mime_type=uploaded_doc.type or "application/pdf",
                            provider=doc_prov
                        )

                        if "error" in res:
                            st.error(res["error"])
                        else:
                            st.success(f"Indexed '{res['filename']}' ({res['chunks_created']} chunks) successfully!")
                            st.session_state.active_document_id = res["document_id"]
                            st.session_state.active_document_name = res["filename"]
                            st.rerun()
