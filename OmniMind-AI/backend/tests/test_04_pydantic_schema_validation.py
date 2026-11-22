"""
Test 4: Pydantic schema validation.
Verifies Pydantic v2 schemas reject malformed data and accept valid fields.
"""

import pytest
from pydantic import ValidationError
from app.schemas.schemas import ChatRequest, DocumentAskRequest, ProviderInfo

def test_pydantic_schema_rules():
    # Valid ChatRequest
    valid_chat = ChatRequest(message="Valid prompt", provider="openai")
    assert valid_chat.message == "Valid prompt"
    assert valid_chat.provider == "openai"

    # Invalid provider in ChatRequest
    with pytest.raises(ValidationError):
        ChatRequest(message="Prompt", provider="unsupported_bot")

    # Empty whitespace question in DocumentAskRequest
    with pytest.raises(ValidationError):
        DocumentAskRequest(question="   ", provider="gemini")

    # Valid ProviderInfo
    p_info = ProviderInfo(
        name="gemini",
        display_name="Google Gemini",
        supported_modalities=["text", "image"],
        configured=True,
        is_mock=False,
        model="gemini-2.5-flash"
    )
    assert p_info.name == "gemini"
    assert p_info.configured is True
