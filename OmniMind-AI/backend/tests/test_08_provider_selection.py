"""
Test 8: Provider selection.
Verifies switching between providers on the API endpoint and rejection of invalid provider names.
"""

def test_provider_selection_api(client):
    # Select Gemini
    res_gem = client.post("/api/chat", json={"message": "Test Gemini", "provider": "gemini"})
    assert res_gem.status_code == 200
    assert res_gem.json()["provider"] == "gemini"

    # Select OpenAI
    res_oai = client.post("/api/chat", json={"message": "Test OpenAI", "provider": "openai"})
    assert res_oai.status_code == 200
    assert res_oai.json()["provider"] == "openai"

    # Select Hugging Face
    res_hf = client.post("/api/chat", json={"message": "Test HF", "provider": "huggingface"})
    assert res_hf.status_code == 200
    assert res_hf.json()["provider"] == "huggingface"

    # Invalid Provider
    res_inv = client.post("/api/chat", json={"message": "Test Invalid", "provider": "claude_invalid"})
    assert res_inv.status_code == 422
