# OmniMind AI — Technical Specification

## 1. System Overview

**OmniMind AI** is a unified multimodal intelligence platform designed to enable cross-modal interaction through a modern, dark-themed Streamlit dashboard and a resilient, high-performance FastAPI backend.

The system supports:
1. **Conversational Intelligence**: Context-aware multi-turn conversations.
2. **Vision Intelligence**: Image inspection, visual object/scene understanding, and OCR.
3. **Audio Intelligence**: Audio stream transcription and executive summarization.
4. **Document Intelligence & RAG**: End-to-end PDF and Word DOCX ingestion, recursive text chunking, vector embedding, and grounded citation-backed question answering.
5. **Multi-Provider Engine**: Dynamic dispatch between Google Gemini (Gemini 2.5 Flash), OpenAI (GPT-4o / Whisper), and Hugging Face (Mistral-7B).

---

## 2. Architecture & Design

### 2.1 Component Interaction Diagram

```
+-------------------------------------------------------------------+
|                  Streamlit Modern Dark Dashboard                  |
|  - Sidebar: Provider selection, Doc Library, Conversation History |
|  - Main Chat: Multi-turn messages, Image & Audio previews, Cards  |
|  - Tabs: Text / RAG Chat, Vision Analyzer, Audio Transcriber      |
+---------------------------------+---------------------------------+
                                  | HTTP (REST / JSON / Multipart)
                                  v
+---------------------------------+---------------------------------+
|                         FastAPI Backend                           |
|  - Routers: /api/chat, /api/documents, /api/providers, etc.       |
|  - Services: ChatService, DocumentService, RAGService             |
|  - Utils: Recursive Chunking, Cosine Similarity, Parsers          |
+-------------------+-----------------------------+-----------------+
                    |                             |
                    v                             v
+-------------------+-------------+     +---------+-----------------+
|     AI Provider Abstraction     |     |    MySQL 8.0 Database     |
| - Gemini 2.5 Flash / Embeddings |     |  - users                  |
| - OpenAI GPT-4o / Whisper-1     |     |  - conversations          |
| - Hugging Face Inference API    |     |  - messages               |
| - Unified Base Provider Interface|     |  - documents              |
| - Graceful Mock Mode Fallback   |     |  - document_chunks        |
+---------------------------------+     +---------------------------+
```

---

## 3. Database Specification (MySQL 8.0)

The relational schema implements relational integrity with primary keys, foreign keys, and indexes:

### 3.1 Tables
- `users`: User identity (`id`, `username`, `email`, `created_at`).
- `conversations`: Chat sessions (`id`, `user_id`, `title`, `provider`, `created_at`).
- `messages`: Multi-turn turns (`id`, `conversation_id`, `role`, `content`, `modality`, `provider`, `created_at`).
- `documents`: Uploaded document tracking (`id`, `user_id`, `filename`, `file_type`, `file_size`, `created_at`).
- `document_chunks`: Parsed text chunks and embedding vectors (`id`, `document_id`, `chunk_index`, `chunk_text`, `embedding`, `created_at`).

### 3.2 Resilience & Local Development
When a production MySQL 8.0 instance is reachable, PyMySQL connects and initializes the database. If MySQL credentials are not yet configured or the server is temporarily unreachable, the database layer automatically initializes an embedded SQLite database (`omnimind_local.db`) with identical schema semantics, guaranteeing zero downtime.

---

## 4. Document Intelligence & RAG Pipeline

1. **Ingestion**: Supports `.pdf` (via `pypdf`) and `.docx` (via `python-docx`).
2. **Text Sanitization**: Normalizes character encodings, strips null bytes, compresses excessive linebreaks.
3. **Recursive Character Chunking**:
   - Primary separators: `\n\n` (paragraphs), `\n` (lines), `. ` (sentences), ` ` (words).
   - Default Chunk Size: 800 characters.
   - Default Overlap: 150 characters.
4. **Vector Embedding**: Generates vector representations via Gemini (`gemini-embedding-001` or `text-embedding-004`) or OpenAI (`text-embedding-3-small`).
5. **Storage**: Vector arrays are JSON-serialized in MySQL `document_chunks.embedding`.
6. **Retrieval**: Cosine similarity is computed directly in Python using `numpy`:
   $$\text{Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$
7. **Ranking & Threshold**: Top $K=4$ chunks exceeding minimum similarity ($\tau \ge 0.20$) are extracted. If no chunk meets the threshold, the system explicitly reports that no relevant information was found.
8. **Synthesis**: The selected LLM is prompted with strict instruction to cite source chunk excerpts.

---

## 5. Security & Boundary Defenses

- **File Validation**: Enforces MIME type checks and a 25MB file size limit.
- **Path Sanitization**: `sanitize_filename` strips traversal characters (`../`, `\`, non-alphanumeric symbols).
- **Credential Protection**: API keys are isolated in the backend environment and never exposed to the frontend client.
- **Safe SQL**: All SQL statements use parameterized queries to eliminate SQL injection risks.
