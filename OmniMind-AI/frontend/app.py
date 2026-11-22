"""
OmniMind AI – Multimodal Intelligence Assistant Frontend.
Streamlit Application Entry Point.
"""

import os
from pathlib import Path
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="OmniMind AI – Multimodal Intelligence Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom CSS
css_file = Path(__file__).parent / "styles" / "custom.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Import Components & Services
from components.sidebar import render_sidebar
from components.chat_area import render_header, render_messages
from components.document_modal import render_document_uploader
from services.api_client import api_client

# 4. Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = "gemini"
if "active_document_id" not in st.session_state:
    st.session_state.active_document_id = None
if "active_document_name" not in st.session_state:
    st.session_state.active_document_name = None

# 5. Render Sidebar
render_sidebar()

# 6. Render Main Header
render_header()

# 7. Document Uploader Component
render_document_uploader()

# 8. Render Chat Messages
render_messages()

# 9. Multimodal Input Area
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

input_tab1, input_tab2, input_tab3 = st.tabs([
    "💬 Text / Document Chat",
    "🖼️ Image Analysis",
    "🎙️ Audio Transcription"
])

current_provider = st.session_state.selected_provider
conv_id = st.session_state.conversation_id

# TAB 1: Text Chat & RAG Document Question
with input_tab1:
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([6, 1])
        with col_input:
            active_doc_hint = (
                f" (Answering from: {st.session_state.active_document_name})"
                if st.session_state.active_document_id
                else ""
            )
            user_text = st.text_input(
                "Message OmniMind AI...",
                placeholder=f"Type your message here{active_doc_hint}...",
                label_visibility="collapsed"
            )
        with col_send:
            submit_btn = st.form_submit_button("Send ➔", use_container_width=True)

    if submit_btn and user_text.strip():
        # Check if RAG mode is active
        if st.session_state.active_document_id:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": f"📄 **[Doc Q&A: {st.session_state.active_document_name}]** {user_text}",
                "modality": "document"
            })

            with st.spinner(f"Searching '{st.session_state.active_document_name}' and synthesizing grounded answer..."):
                rag_res = api_client.ask_document(
                    document_id=st.session_state.active_document_id,
                    question=user_text,
                    provider=current_provider
                )

                if "error" in rag_res:
                    st.error(rag_res["error"])
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": rag_res["answer"],
                        "modality": "document",
                        "provider": rag_res["provider"],
                        "citations": rag_res.get("citations", [])
                    })
            st.rerun()

        else:
            # Standard conversational text chat
            st.session_state.messages.append({
                "role": "user",
                "content": user_text,
                "modality": "text"
            })

            with st.spinner(f"Consulting {current_provider.upper()}..."):
                chat_res = api_client.send_chat(
                    message=user_text,
                    provider=current_provider,
                    conversation_id=conv_id
                )

                if "error" in chat_res:
                    st.error(chat_res["error"])
                else:
                    st.session_state.conversation_id = chat_res["conversation_id"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": chat_res["message"],
                        "modality": "text",
                        "provider": chat_res["provider"]
                    })
            st.rerun()

# TAB 2: Image Understanding
with input_tab2:
    col_img_up, col_img_p = st.columns([1, 1])
    with col_img_up:
        uploaded_image = st.file_uploader(
            "Upload an image",
            type=["png", "jpg", "jpeg", "webp"],
            key="img_uploader"
        )
    with col_img_p:
        img_prompt = st.text_area(
            "Optional Question or Instruction",
            placeholder="e.g., Identify the objects, translate any text, or explain the architecture shown in this diagram.",
            key="img_prompt_input"
        )
        send_image_btn = st.button("🔍 Analyze Image", key="btn_send_image", use_container_width=True)

    if send_image_btn:
        if not uploaded_image:
            st.warning("Please upload an image first.")
        else:
            img_bytes = uploaded_image.getvalue()
            st.session_state.messages.append({
                "role": "user",
                "content": f"🖼️ **[Image Analysis Request]** {img_prompt or 'Describe this image.'}",
                "modality": "image",
                "image_preview": img_bytes
            })

            with st.spinner("Analyzing image with multimodal vision..."):
                img_res = api_client.send_image(
                    image_bytes=img_bytes,
                    filename=uploaded_image.name,
                    mime_type=uploaded_image.type or "image/jpeg",
                    prompt=img_prompt,
                    provider=current_provider,
                    conversation_id=conv_id
                )

                if "error" in img_res:
                    st.error(img_res["error"])
                else:
                    if img_res.get("conversation_id"):
                        st.session_state.conversation_id = img_res["conversation_id"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": img_res["analysis"],
                        "modality": "image",
                        "provider": img_res["provider"]
                    })
            st.rerun()

# TAB 3: Audio Processing
with input_tab3:
    col_aud_up, col_aud_act = st.columns([2, 1])
    with col_aud_up:
        uploaded_audio = st.file_uploader(
            "Upload an audio recording",
            type=["mp3", "wav", "m4a", "ogg"],
            key="audio_uploader"
        )
    with col_aud_act:
        audio_action = st.radio(
            "Audio Processing Task:",
            options=["transcribe", "summarize"],
            format_func=lambda x: "Verbatim Transcription" if x == "transcribe" else "Executive Summary",
            key="audio_action_radio"
        )
        send_audio_btn = st.button("🎙️ Process Audio", key="btn_send_audio", use_container_width=True)

    if send_audio_btn:
        if not uploaded_audio:
            st.warning("Please upload an audio file first.")
        else:
            aud_bytes = uploaded_audio.getvalue()
            st.session_state.messages.append({
                "role": "user",
                "content": f"🎙️ **[Audio Upload]** Action: {audio_action.capitalize()} ({uploaded_audio.name})",
                "modality": "audio"
            })

            with st.spinner(f"Processing audio with {current_provider.upper()}..."):
                aud_res = api_client.send_audio(
                    audio_bytes=aud_bytes,
                    filename=uploaded_audio.name,
                    mime_type=uploaded_audio.type or "audio/mpeg",
                    action=audio_action,
                    provider=current_provider,
                    conversation_id=conv_id
                )

                if "error" in aud_res:
                    st.error(aud_res["error"])
                else:
                    if aud_res.get("conversation_id"):
                        st.session_state.conversation_id = aud_res["conversation_id"]
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": aud_res["result"],
                        "modality": "audio",
                        "provider": aud_res["provider"]
                    })
            st.rerun()
