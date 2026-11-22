# 🧠 OmniMind AI – Multimodal Intelligence Assistant

**OmniMind AI** is a full-stack multimodal AI assistant that brings text conversations, image understanding, audio processing, and document intelligence into one unified platform.

Built using **FastAPI, Streamlit, Python, and MySQL 8.0**, the application integrates multiple AI providers to deliver an intelligent and flexible user experience.

---

## 🚀 Project Overview

OmniMind AI allows users to interact with AI using multiple input formats instead of relying only on traditional text-based conversations.

### Key Features

- **AI Chat:** Intelligent text-based conversations.
- **Image Understanding:** Upload images and ask questions about their contents.
- **Audio Intelligence:** Process audio for transcription and summarization.
- **Document Intelligence:** Upload and analyze PDF and DOCX documents.
- **RAG Pipeline:** Retrieve relevant document information using embeddings and similarity search.
- **Multi-Provider Integration:** Switch between different AI providers.
- **Conversation Management:** Maintain conversation context and history.
- **Responsive Interface:** Modern chatbot interface built with Streamlit and custom CSS.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| Data Validation | Pydantic v2 |
| Server | Uvicorn |
| Frontend | Streamlit, Custom CSS |
| Database | MySQL 8.0 |
| Primary AI | Google Gemini API |
| Secondary AI | OpenAI API |
| Optional AI | Hugging Face API |
| Embeddings | Gemini Embedding API |
| PDF Processing | pypdf |
| Word Processing | python-docx |
| Text Chunking | Recursive Character Chunking |
| Testing | pytest |

## 🏗️ Project Architecture

```text
OmniMind-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── providers/
│   │   └── utils/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app.py
│   ├── components/
│   ├── services/
│   ├── styles/
│   └── utils/
│
├── docs/
│   ├── SPEC.md
│   └── API_DOCUMENTATION.md
│
├── README.md
└── .gitignore
```

## ⚙️ Installation & Setup

### 1. Prerequisites

Make sure you have installed:

- Python 3.10 or higher (compatible with project dependencies).
- MySQL 8.0.
- Git.
- pip.
- API credentials for the AI providers you want to use.

### 2. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd OmniMind-AI
```

### 3. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file inside the backend directory using `.env.example` as a template.

Configure the following variables:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=omnimind_ai

BACKEND_PORT=8000
GEMINI_MODEL=your_supported_gemini_model
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
```

**Important:** Never upload your `.env` file or API keys to GitHub.

### 5. Database Setup

Start your MySQL server and create the database:

```sql
CREATE DATABASE omnimind_ai;
```

Configure your database credentials in the `.env` file.

Ensure the application initializes the required tables before using database-dependent features.

### 6. Frontend Setup

Open a second terminal and navigate to the frontend directory:

```bash
cd OmniMind-AI/frontend
```

If you are using a shared virtual environment, activate it before running Streamlit.

Install any additional frontend dependencies if they are not already included in the backend requirements.

## ▶️ Running the Application

You need two terminals to run the application.

**Terminal 1 – Backend (FastAPI)**

```bash
cd OmniMind-AI/backend
python -m uvicorn app.main:app --reload --port 8000
```

Backend API:

http://localhost:8000

Interactive API documentation:

http://localhost:8000/docs

**Terminal 2 – Frontend (Streamlit)**

```bash
cd OmniMind-AI/frontend
streamlit run app.py
```

Frontend application:

http://localhost:8501

## 🧪 Testing

OmniMind AI includes a pytest suite designed to cover different application layers.

Run the tests:

```bash
cd OmniMind-AI/backend
pytest -v
```

The planned test coverage includes:

1. Health endpoint.
2. Text request validation.
3. Empty message validation.
4. Pydantic schema validation.
5. Gemini provider handling.
6. OpenAI provider handling.
7. Hugging Face provider handling.
8. Provider selection.
9. Image upload validation.
10. Audio upload validation.
11. PDF text extraction.
12. DOCX text extraction.
13. Recursive text chunking.
14. Embedding generation.
15. RAG retrieval.
16. Database operations and conversation persistence.

External API calls should be mocked during automated testing.

## 🔄 RAG Workflow

The document intelligence module follows this pipeline:

```text
Document Upload
      ↓
Text Extraction
      ↓
Text Cleaning
      ↓
Recursive Chunking
      ↓
Embedding Generation
      ↓
MySQL Storage
      ↓
User Question
      ↓
Question Embedding
      ↓
Similarity Search
      ↓
Relevant Context Retrieval
      ↓
AI Response Generation
```

## 🔐 Security

- API credentials are stored in environment variables.
- Backend handles provider authentication.
- Uploaded files undergo validation.
- Database queries use parameterized operations.
- Provider failures and invalid requests are handled.
- Sensitive information should not be committed to version control.

## 🎯 Project Objectives

This project demonstrates practical implementation of:

- Full-stack Python development.
- REST API development using FastAPI.
- Integration of multiple AI providers.
- Multimodal AI processing.
- Retrieval-Augmented Generation (RAG).
- Embeddings and semantic similarity.
- Relational database management.
- Automated testing with pytest.

## 🚧 Future Enhancements

- Real-time voice conversations.
- Advanced document comparison.
- AI Model Arena for comparing provider responses.
- Improved semantic document retrieval.
- User authentication and personalized workspaces.
- Cloud deployment.

## 👨‍💻 Project Information

**Project Name:** OmniMind AI – Multimodal Intelligence Assistant

**Category:** Full-Stack Development | Generative AI | Multimodal AI

**Backend:** FastAPI

**Frontend:** Streamlit

**Database:** MySQL 8.0

**AI Providers:** Google Gemini | OpenAI | Hugging Face

---

*Built as a hands-on exploration of multimodal AI, backend engineering, and intelligent application development.*