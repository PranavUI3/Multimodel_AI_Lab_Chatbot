"""
Chat Area component for OmniMind AI.
Displays header, welcome screen, chat history bubbles, multimedia attachments, and citations.
"""

import streamlit as st
from typing import Any, Dict, List


def render_header():
    """Renders top header with logo and provider pill."""
    provider = st.session_state.get("selected_provider", "gemini")
    active_doc = st.session_state.get("active_document_name")

    badge_class = f"badge-{provider}"
    provider_labels = {
        "gemini": "Google Gemini 2.5 Flash",
        "openai": "OpenAI GPT-4o",
        "huggingface": "Hugging Face"
    }

    doc_indicator = f"<span style='color: #38BDF8; font-size: 0.85rem; margin-left: 10px;'>📄 Document: <b>{active_doc}</b></span>" if active_doc else ""

    st.markdown(
        f"""
        <div class="omnimind-header">
            <div>
                <div class="omnimind-logo-title">
                    <span>⚡</span> OmniMind AI
                </div>
                <div class="omnimind-tagline">
                    Multimodal Intelligence Assistant — Text • Vision • Audio • Documents {doc_indicator}
                </div>
            </div>
            <div>
                <div class="provider-badge {badge_class}">
                    <span>Active: {provider_labels.get(provider, provider.upper())}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_welcome_screen():
    """Renders high-impact welcome screen with quick starter prompts."""
    st.markdown(
        """
        <div class="welcome-hero">
            <div class="welcome-title">What would you like to explore today?</div>
            <div class="welcome-desc">
                Engage in natural conversations, inspect visual diagrams & photos, transcribe audio memos, 
                or upload complex PDF / DOCX documents for instant citation-backed question answering.
            </div>
            <div class="quick-prompts-grid">
                <div class="quick-prompt-card">
                    <div class="quick-prompt-icon">💬</div>
                    <div class="quick-prompt-text">"Explain quantum computing principles with everyday analogies."</div>
                </div>
                <div class="quick-prompt-card">
                    <div class="quick-prompt-icon">🖼️</div>
                    <div class="quick-prompt-text">"Upload an image and ask for a visual component breakdown."</div>
                </div>
                <div class="quick-prompt-card">
                    <div class="quick-prompt-icon">🎙️</div>
                    <div class="quick-prompt-text">"Upload a recorded voice note and request an executive summary."</div>
                </div>
                <div class="quick-prompt-card">
                    <div class="quick-prompt-icon">📑</div>
                    <div class="quick-prompt-text">"Upload a research paper or contract and ask for key takeaways."</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_messages():
    """Renders conversation messages from session state."""
    messages = st.session_state.get("messages", [])

    if not messages:
        render_welcome_screen()
        return

    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        modality = msg.get("modality", "text")
        citations = msg.get("citations", [])

        if role == "user":
            st.markdown(
                f"""
                <div class="chat-bubble-user">
                    <b>You</b><br>
                    {content}
                </div>
                """,
                unsafe_allow_html=True
            )
            # If there is an image in session preview for this message
            if msg.get("image_preview"):
                st.image(msg["image_preview"], width=300)

        else:
            provider_label = msg.get("provider", "OmniMind").capitalize()
            st.markdown(
                f"""
                <div class="chat-bubble-assistant">
                    <div style="font-size: 0.8rem; color: #818CF8; font-weight: 600; margin-bottom: 6px;">
                        ✦ {provider_label} Assistant
                    </div>
                    {content}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Render citations if present
            if citations:
                with st.expander(f"📌 Grounded Source Citations ({len(citations)})", expanded=False):
                    for c in citations:
                        score_pct = int(c.get("score", 0.0) * 100)
                        st.markdown(
                            f"""
                            <div class="citation-box">
                                <b>Chunk #{c.get('chunk_index', 0) + 1}</b> (Similarity: {score_pct}%)<br>
                                <i>"{c.get('chunk_text', '')}"</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
