# OmniMind AI — REST API Documentation

Base URL: `http://localhost:8000`  
Interactive Swagger Docs: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 1. System Endpoints

### `GET /api/health`
Checks backend service health, database connectivity, and provider status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "OmniMind AI Multimodal Intelligence Assistant",
  "database": {
    "connected": true,
    "type": "MySQL 8.0",
    "is_mysql": true
  },
  "providers": {
    "gemini": false,
    "openai": false,
    "huggingface": false
  },
  "timestamp": "2026-11-22T12:00:00.000000"
}
```

---

### `GET /api/providers`
Lists configured AI providers and supported modalities.

**Response (200 OK):**
```json
{
  "providers": [
    {
      "name": "gemini",
      "display_name": "Google Gemini",
      "supported_modalities": ["text", "image", "audio", "embedding", "rag_document"],
      "configured": false,
      "is_mock": true,
      "model": "gemini-2.5-flash"
    },
    {
      "name": "openai",
      "display_name": "OpenAI",
      "supported_modalities": ["text", "image", "audio", "embedding", "rag_document"],
      "configured": false,
      "is_mock": true,
      "model": "gpt-4o"
    },
    {
      "name": "huggingface",
      "display_name": "Hugging Face",
      "supported_modalities": ["text", "rag_document", "embedding"],
      "configured": false,
      "is_mock": true,
      "model": "mistralai/Mistral-7B-Instruct-v0.3"
    }
  ]
}
```

---

## 2. Multimodal Chat Endpoints

### `POST /api/chat`
Submits a text prompt for conversational AI.

**Request Body (`application/json`):**
```json
{
  "conversation_id": null,
  "message": "Explain quantum entanglement in simple terms.",
  "provider": "gemini",
  "user_id": 1
}
```

**Response (200 OK):**
```json
{
  "conversation_id": 1,
  "message": "Quantum entanglement is a phenomenon where...",
  "provider": "gemini",
  "role": "assistant",
  "created_at": "2026-11-22T12:00:00.000000"
}
```

---

### `POST /api/chat/image`
Submits an image file for visual analysis.

**Request (`multipart/form-data`):**
- `image`: Binary file (PNG, JPG, WEBP)
- `prompt`: String (optional)
- `provider`: String (`gemini` or `openai`)
- `conversation_id`: Integer (optional)

**Response (200 OK):**
```json
{
  "conversation_id": 1,
  "prompt": "Analyze this chart.",
  "analysis": "The image depicts a quarterly revenue graph...",
  "provider": "gemini",
  "created_at": "2026-11-22T12:00:00.000000"
}
```

---

### `POST /api/chat/audio`
Submits an audio recording for transcription or summarization.

**Request (`multipart/form-data`):**
- `audio`: Binary file (MP3, WAV, M4A, OGG)
- `action`: String (`transcribe` or `summarize`)
- `provider`: String (`gemini` or `openai`)
- `conversation_id`: Integer (optional)

**Response (200 OK):**
```json
{
  "conversation_id": 1,
  "action": "transcribe",
  "result": "Good morning team, today we are reviewing...",
  "provider": "gemini",
  "created_at": "2026-11-22T12:00:00.000000"
}
```

---

## 3. Document Intelligence & RAG Endpoints

### `POST /api/documents/upload`
Uploads and indexes a PDF or DOCX file.

**Request (`multipart/form-data`):**
- `file`: Binary file (.pdf or .docx)
- `provider`: String (optional, default `gemini`)

**Response (201 Created):**
```json
{
  "document_id": 1,
  "filename": "Research_Report.pdf",
  "file_type": "pdf",
  "file_size": 245100,
  "chunks_created": 12,
  "message": "Successfully parsed and indexed 12 chunks using Google Gemini embeddings."
}
```

---

### `GET /api/documents`
Lists uploaded documents for the user.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "Research_Report.pdf",
    "file_type": "pdf",
    "file_size": 245100,
    "chunk_count": 12,
    "created_at": "2026-11-22 12:00:00"
  }
]
```

---

### `DELETE /api/documents/{document_id}`
Deletes an uploaded document and its vector chunks.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Document 1 and associated chunks deleted successfully."
}
```

---

### `POST /api/documents/{document_id}/ask`
Performs semantic retrieval and grounds an answer in document citations.

**Request Body (`application/json`):**
```json
{
  "question": "What is the primary conclusion in section 3?",
  "provider": "gemini",
  "user_id": 1
}
```

**Response (200 OK):**
```json
{
  "document_id": 1,
  "question": "What is the primary conclusion in section 3?",
  "answer": "According to section 3 [Source Chunk 1], the primary conclusion is...",
  "provider": "gemini",
  "citations": [
    {
      "chunk_index": 0,
      "chunk_text": "Section 3: Key findings demonstrate...",
      "score": 0.8921
    }
  ]
}
```

---

## 4. Conversation History Endpoints

### `GET /api/conversations`
Retrieves all conversation sessions with message counts.

### `GET /api/conversations/{conversation_id}/messages`
Retrieves messages for a conversation session.

### `DELETE /api/conversations/{conversation_id}`
Deletes a conversation session and its messages.
