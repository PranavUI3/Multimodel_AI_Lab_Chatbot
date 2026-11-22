"""
Pytest configuration and shared fixtures for OmniMind AI tests.
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is in sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app
from app.database import db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Ensures test database is initialized."""
    db.init_db()
    yield

@pytest.fixture
def client():
    """Provides a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client
