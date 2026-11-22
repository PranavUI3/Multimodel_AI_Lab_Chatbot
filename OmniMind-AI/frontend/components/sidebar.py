"""
Sidebar component for OmniMind AI.
Includes branding, New Chat, Provider Selector, Conversation History, and Document Library.
"""

import streamlit as st
from typing import Any, Dict, List
from ..services.api_client import api_client


def render_sidebar():
    """Renders the dark-themed sidebar dashboard controls."""
    with st.sidebar:
        # 1. Branding Header
        st.markdown(
            """
            <div class="sidebar-branding">
                <div class="sidebar-title">
                    <span>🧠</span>
                    <span>OmniMind AI</span>
                </div>
                <div style="font-size: 0.8rem; color: #9CA3AF; margin-top: 4px;">
                    Multimodal Intelligence Platform
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 2. New Chat Action
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.session_state.active_document_id = None
            st.session_state.active_document_name = None
            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # 3. AI Provider Selection
        st.markdown("#### ⚡ AI Engine Provider")
        provider_options = {
            "gemini": "Google Gemini 2.5 Flash",
            "openai": "OpenAI GPT-4o",
            "huggingface": "Hugging Face (Mistral-7B)"
        }
        
        current_p = st.session_state.get("selected_provider", "gemini")
        provider_keys = list(provider_options.keys())
        current_idx = provider_keys.index(current_p) if current_p in provider_keys else 0

        selected_key = st.selectbox(
            "Select Active LLM",
            options=provider_keys,
            format_func=lambda k: provider_options[k],
            index=current_idx,
            label_visibility="collapsed"
        )
        st.session_state.selected_provider = selected_key

        # Provider capabilities badge
        if selected_key == "gemini":
            st.markdown(
                """
                <div class="provider-badge badge-gemini" style="width: 100%; justify-content: center; margin-top: 4px;">
                    <span>✦ Text • Vision • Audio • RAG</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif selected_key == "openai":
            st.markdown(
                """
                <div class="provider-badge badge-openai" style="width: 100%; justify-content: center; margin-top: 4px;">
                    <span>✦ Text • Vision • Whisper • RAG</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="provider-badge badge-huggingface" style="width: 100%; justify-content: center; margin-top: 4px;">
                    <span>✦ Text • Document Q&A</span>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<hr>", unsafe_allow_html=True)

        # 4. Document Library & Active RAG Context
        st.markdown("#### 📚 Document Intelligence (RAG)")
        docs = api_client.list_documents()

        if docs:
            doc_options = {None: "None (Standard Chat)"}
            for d in docs:
                doc_options[d["id"]] = f"📄 {d['filename']} ({d['chunk_count']} chunks)"

            active_doc = st.session_state.get("active_document_id")
            current_doc_idx = 0
            if active_doc in doc_options:
                current_doc_idx = list(doc_options.keys()).index(active_doc)

            selected_doc_id = st.selectbox(
                "Active Document Context:",
                options=list(doc_options.keys()),
                format_func=lambda k: doc_options[k],
                index=current_doc_idx
            )
            st.session_state.active_document_id = selected_doc_id
            if selected_doc_id:
                for d in docs:
                    if d["id"] == selected_doc_id:
                        st.session_state.active_document_name = d["filename"]
                        break
            else:
                st.session_state.active_document_name = None

            # Manage Documents Expander
            with st.expander(f"Manage Uploaded Files ({len(docs)})"):
                for d in docs:
                    col_info, col_del = st.columns([4, 1])
                    with col_info:
                        st.caption(f"**{d['filename']}** ({d['file_size']/1024:.1f} KB)")
                    with col_del:
                        if st.button("🗑️", key=f"del_doc_{d['id']}", help="Delete document"):
                            api_client.delete_document(d["id"])
                            if st.session_state.active_document_id == d["id"]:
                                st.session_state.active_document_id = None
                                st.session_state.active_document_name = None
                            st.rerun()
        else:
            st.caption("No documents indexed yet. Upload a PDF or DOCX below to enable grounded RAG answering.")

        st.markdown("<hr>", unsafe_allow_html=True)

        # 5. Conversation History
        st.markdown("#### 💬 Conversation History")
        conversations = api_client.list_conversations()

        if conversations:
            for conv in conversations[:8]:
                is_active = (st.session_state.get("conversation_id") == conv["id"])
                btn_label = f"{'🔹 ' if is_active else ''}{conv['title'][:26]}"
                col_btn, col_del_c = st.columns([5, 1])
                with col_btn:
                    if st.button(btn_label, key=f"conv_{conv['id']}", use_container_width=True):
                        st.session_state.conversation_id = conv["id"]
                        msgs = api_client.get_conversation_messages(conv["id"])
                        st.session_state.messages = [
                            {
                                "role": m["role"],
                                "content": m["content"],
                                "modality": m.get("modality", "text"),
                                "provider": m.get("provider", "gemini")
                            }
                            for m in msgs
                        ]
                        st.rerun()
                with col_del_c:
                    if st.button("✖", key=f"del_conv_{conv['id']}", help="Delete chat"):
                        api_client.delete_conversation(conv["id"])
                        if st.session_state.get("conversation_id") == conv["id"]:
                            st.session_state.conversation_id = None
                            st.session_state.messages = []
                        st.rerun()
        else:
            st.caption("No prior conversations saved.")

        # Clear conversation
        if st.session_state.get("messages"):
            if st.button("🧹 Clear Active Screen", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

        # System health status at bottom of sidebar
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        health = api_client.check_health()
        if health.get("status") in ("healthy", "degraded"):
            db_type = health.get("database", {}).get("type", "Active")
            st.caption(f"🟢 **System Online** | DB: {db_type}")
        else:
            st.caption("🔴 **Backend Offline** — check FastAPI server at :8000")
