"""
Test 2: Text request validation.
Verifies valid chat request processes correctly and returns conversation ID and assistant response.
"""

def test_valid_text_request(client):
    payload = {
        "message": "Hello OmniMind, explain what multimodal AI is.",
        "provider": "gemini",
        "user_id": 1
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] > 0
    assert "message" in data
    assert len(data["message"]) > 0
    assert data["provider"] == "gemini"
    assert data["role"] == "assistant"
