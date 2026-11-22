"""
Test 10: Audio upload validation.
Verifies rejection of empty audio, invalid file extensions, and acceptance of valid audio streams.
"""

def test_audio_upload_validation(client):
    # 1. Empty audio file -> 400
    empty_file = ("empty.mp3", b"", "audio/mpeg")
    res_empty = client.post("/api/chat/audio", files={"audio": empty_file}, data={"provider": "gemini"})
    assert res_empty.status_code == 400

    # 2. Invalid audio extension -> 400
    invalid_file = ("audio.txt", b"not audio text", "text/plain")
    res_invalid = client.post("/api/chat/audio", files={"audio": invalid_file}, data={"provider": "gemini"})
    assert res_invalid.status_code == 400

    # 3. Valid MP3 dummy stream
    dummy_audio_bytes = b"ID3\x03\x00\x00\x00\x00\x00\x23" + (b"\xff\xfb\x90\x44" * 64)
    valid_file = ("sample.mp3", dummy_audio_bytes, "audio/mpeg")
    res_valid = client.post(
        "/api/chat/audio",
        files={"audio": valid_file},
        data={"action": "transcribe", "provider": "gemini"}
    )
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "result" in data
    assert data["action"] == "transcribe"
