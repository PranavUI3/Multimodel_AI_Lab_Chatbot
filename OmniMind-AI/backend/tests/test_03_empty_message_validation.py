"""
Test 3: Empty message validation.
Verifies empty and whitespace-only messages are rejected with 422 Unprocessable Entity.
"""

def test_empty_message_rejected(client):
    # Empty string
    response = client.post("/api/chat", json={"message": "", "provider": "gemini"})
    assert response.status_code == 422

    # Whitespace only
    response_ws = client.post("/api/chat", json={"message": "   \n\t  ", "provider": "gemini"})
    assert response_ws.status_code == 422
