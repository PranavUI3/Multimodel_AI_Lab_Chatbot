# OmniMind AI – Multimodal Intelligence Assistant

OmniMind AI is a full-stack, multimodal AI platform that allows users to interact with state-of-the-art AI through **Text, Images, Audio, and Documents (PDF & DOCX)** using a **Retrieval-Augmented Generation (RAG)** pipeline.

---

## 🌟 Features

- **Multimodal Interaction**:
  - 💬 **Conversational Chat**: Multi-turn dialogue with memory persistence.
  - 🖼️ **Vision Understanding**: Image analysis, object detection, diagram explanation.
  - 🎙️ **Audio Processing**: Verbatim speech transcription and executive bulleted summaries.
  - 📑 **Document Intelligence & RAG**: Upload PDF and Word DOCX documents, parse, recursively chunk, embed, and ask grounded questions with source citations.
- **Multi-Provider AI Engine**:
  - 🔷 **Google Gemini**: Gemini 2.5 Flash / 1.5 Flash + Gemini Embeddings.
  - 🟢 **OpenAI**: GPT-4o Vision + Whisper-1 audio transcription.
  - 🟡 **Hugging Face**: Mistral-7B text generation & document Q&A.
- **Relational Data Persistence (MySQL 8.0)**:
  - Tables for users, conversations, multi-turn messages, documents, and vector chunks.
  - Parameterized queries and foreign keys with cascading deletes.
  - Seamless fallback to local storage if MySQL credentials are not yet configured.
- **Premium Streamlit Interface**:
  - Modern dark dashboard aesthetic.
  - Glassmorphic panels, provider capability pills, and citation cards.
- **Comprehensive Quality Assurance**:
  - **16 automated pytest unit & integration tests** covering all endpoints, providers, chunking, parsing, embeddings, and database persistence.

---

## 📁 Project Structure

```
OmniMind-AI/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI application & lifecycle
│   │   ├── config.py               # Pydantic settings & environment configuration
│   │   ├── database.py             # MySQL 8.0 connection pool & query execution
│   │   ├── models/                 # Table DDL & relational definitions
│   │   ├── schemas/                # Pydantic v2 validation schemas
│   │   ├── routers/                # FastAPI endpoints (chat, documents, providers, convs)
│   │   ├── services/               # ChatService, DocumentService, RAGService
│   │   ├── providers/              # Gemini, OpenAI, Hugging Face integrations & factory
│   │   └── utils/                  # Chunking, cosine similarity, document parsers, validators
│   ├── tests/                      # 16 automated pytest unit & integration tests
│   ├── init_db.sql                 # MySQL 8.0 schema initialization script
│   ├── requirements.txt            # Python dependencies
│   ├── pytest.ini                  # Pytest configuration
│   └── .env.example                # Sample environment variables
├── frontend/
│   ├── app.py                      # Streamlit entry point
│   ├── components/                 # Sidebar, chat area, document uploader
│   ├── services/                   # HTTP API client for backend communication
│   └── styles/                     # Dark theme custom CSS
├── docs/
│   ├── SPEC.md                     # Technical architecture & pipeline specification
│   └── API_DOCUMENTATION.md        # Complete REST API reference
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python**: Version 3.10+ (tested on Python 3.14)
- **Database**: MySQL 8.0 (optional for local mock testing; SQLite fallback is built-in)

### 2. Install Dependencies

Open a terminal in `OmniMind-AI/backend`:
```bash
pip install -r requirements.txt
```

---

### 3. Environment Configuration

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` to supply your credentials:
```env
# AI Providers (Leave blank to run in labeled Mock Mode)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# MySQL 8.0 Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=omnimind_ai

# Server Port
BACKEND_PORT=8000
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
OPENAI_MODEL=gpt-4o
HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.3
```

> **Note on Mock Mode**: If any API key is missing or invalid, OmniMind AI operates in a clean, labeled **Mock Mode**. All multimodal pipelines (Vision, Audio, RAG, Text) remain completely demonstrable and testable without requiring paid API credits.

---

### 4. Database Setup (MySQL 8.0)

If using MySQL 8.0 locally:
```bash
mysql -u root -p < backend/init_db.sql
```
*If MySQL is not currently running or credentials are not yet entered, the application automatically initializes a standalone fallback database (`omnimind_local.db`) so you can run and demonstrate the app immediately.*

---

### 5. Start the FastAPI Backend

From the project root:
```bash
cd OmniMind-AI/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

---

### 6. Start the Streamlit Frontend

In a separate terminal:
```bash
cd OmniMind-AI/frontend
streamlit run app.py
```
- Streamlit Web Dashboard: `http://localhost:8501`

---

## 🧪 Automated Testing (16 Tests)

Run the full automated test suite:
```bash
cd OmniMind-AI/backend
pytest -v
```

### Test Suite Summary:
| # | Test File | Description |
|---|---|---|
| 1 | `test_01_health_endpoint.py` | Health endpoint status, database connection, and providers |
| 2 | `test_02_text_request_validation.py` | Text chat request validation & response structure |
| 3 | `test_03_empty_message_validation.py` | Rejection of empty and whitespace messages (HTTP 422) |
| 4 | `test_04_pydantic_schema_validation.py` | Pydantic v2 request/response schema validation |
| 5 | `test_05_gemini_provider_handling.py` | Google Gemini multimodal handling & mock fallback |
| 6 | `test_06_openai_provider_handling.py` | OpenAI GPT-4o & Whisper handling |
| 7 | `test_07_huggingface_provider_handling.py` | Hugging Face provider & modality rejection |
| 8 | `test_08_provider_selection.py` | Dynamic provider switching & invalid provider rejection |
| 9 | `test_09_image_upload_validation.py` | Image validation (size, MIME type, empty file checks) |
| 10 | `test_10_audio_upload_validation.py` | Audio stream validation (format & size checks) |
| 11 | `test_11_pdf_extraction.py` | PDF parsing and text extraction using pypdf |
| 12 | `test_12_docx_extraction.py` | Word DOCX extraction using python-docx |
| 13 | `test_13_recursive_chunking.py` | Recursive character chunking & semantic boundaries |
| 14 | `test_14_embedding_generation.py` | Normalized vector embedding generation |
| 15 | `test_15_rag_retrieval.py` | Cosine similarity ranking and chunk retrieval |
| 16 | `test_16_db_and_persistence.py` | Database CRUD, message persistence, & cascading deletes |

**Result**: 16 passed, 0 failed.

---

## 🔒 Security & Data Privacy

- Uploaded files are processed in memory and validated against allowed MIME types and maximum size limits (25MB).
- Vector embeddings and document text chunks are indexed with parameterized SQL queries.
- API keys are secured on the server side and never passed to the browser or frontend state.
- External AI providers process uploaded content according to their respective privacy terms.
