"""
Test 9: Image upload validation.
Verifies rejection of empty images, invalid file types, and acceptance of valid images.
"""

import io

def test_image_upload_validation(client):
    # 1. Empty image bytes -> 400
    empty_file = ("empty.png", b"", "image/png")
    res_empty = client.post("/api/chat/image", files={"image": empty_file}, data={"provider": "gemini"})
    assert res_empty.status_code == 400

    # 2. Invalid file type -> 400
    invalid_file = ("script.exe", b"binary content", "application/octet-stream")
    res_invalid = client.post("/api/chat/image", files={"image": invalid_file}, data={"provider": "gemini"})
    assert res_invalid.status_code == 400

    # 3. Valid PNG image
    valid_png_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    valid_file = ("pixel.png", valid_png_bytes, "image/png")
    res_valid = client.post(
        "/api/chat/image",
        files={"image": valid_file},
        data={"prompt": "What color is this pixel?", "provider": "gemini"}
    )
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "analysis" in data
    assert len(data["analysis"]) > 0
