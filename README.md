# OmniMind AI – Multimodal Intelligence Assistant

Full-stack multimodal AI assistant platform built with FastAPI, Streamlit, and MySQL 8.0.

Please refer to [`OmniMind-AI/README.md`](OmniMind-AI/README.md) for full documentation and instructions.

### Quick Start:

1. **Backend**:
   ```bash
   cd OmniMind-AI/backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend**:
   ```bash
   cd OmniMind-AI/frontend
   streamlit run app.py
   ```

3. **Pytest**:
   ```bash
   cd OmniMind-AI/backend
   pytest -v
   ```
