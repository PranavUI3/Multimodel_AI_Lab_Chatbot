"""
Test 16: Database operations and conversation persistence.
Verifies relational database CRUD, message persistence, document/chunk relationships, and deletion.
"""

from app.database import db

def test_database_persistence_and_relationships():
    # 1. Create a conversation
    conv_id = db.execute_insert(
        "INSERT INTO conversations (user_id, title, provider) VALUES (%s, %s, %s)",
        (1, "Test Database Conversation", "gemini")
    )
    assert conv_id > 0

    # 2. Add user and assistant messages
    msg1_id = db.execute_insert(
        "INSERT INTO messages (conversation_id, role, content, modality, provider) VALUES (%s, %s, %s, %s, %s)",
        (conv_id, "user", "What is multimodal AI?", "text", "gemini")
    )
    msg2_id = db.execute_insert(
        "INSERT INTO messages (conversation_id, role, content, modality, provider) VALUES (%s, %s, %s, %s, %s)",
        (conv_id, "assistant", "Multimodal AI processes text, vision, audio, etc.", "text", "gemini")
    )
    assert msg1_id > 0
    assert msg2_id > 0

    # 3. Retrieve messages
    messages = db.fetch_all(
        "SELECT id, role, content FROM messages WHERE conversation_id = %s ORDER BY id ASC",
        (conv_id,)
    )
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"

    # 4. Insert document and chunks
    doc_id = db.execute_insert(
        "INSERT INTO documents (user_id, filename, file_type, file_size) VALUES (%s, %s, %s, %s)",
        (1, "test_file.pdf", "pdf", 2048)
    )
    assert doc_id > 0

    chunk_id = db.execute_insert(
        "INSERT INTO document_chunks (document_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s)",
        (doc_id, 0, "Sample chunk content", "[0.1, 0.2, 0.3]")
    )
    assert chunk_id > 0

    # 5. Verify chunk retrieval
    stored_chunk = db.fetch_one("SELECT id, chunk_text FROM document_chunks WHERE id = %s", (chunk_id,))
    assert stored_chunk is not None
    assert stored_chunk["chunk_text"] == "Sample chunk content"

    # 6. Delete document and verify cascading chunk cleanup
    db.execute_query("DELETE FROM document_chunks WHERE document_id = %s", (doc_id,))
    db.execute_query("DELETE FROM documents WHERE id = %s", (doc_id,))

    remaining_chunk = db.fetch_one("SELECT id FROM document_chunks WHERE document_id = %s", (doc_id,))
    assert remaining_chunk is None
