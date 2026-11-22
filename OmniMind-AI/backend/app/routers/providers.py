"""
Providers & Health router: returns provider list, capabilities, and system health status.
"""

from datetime import datetime
from fastapi import APIRouter, status

from ..database import db
from ..providers.factory import provider_factory
from ..schemas.schemas import HealthResponse, ProvidersResponse

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/providers", response_model=ProvidersResponse, status_code=status.HTTP_200_OK)
async def get_providers():
    """Returns available AI providers and their supported modalities."""
    providers_list = provider_factory.list_providers()
    return {"providers": providers_list}


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Returns health status of the backend, database connection, and AI providers."""
    db_status = db.get_status()
    providers = provider_factory.list_providers()
    provider_config = {p["name"]: p["configured"] for p in providers}

    return {
        "status": "healthy" if db_status.get("connected") else "degraded",
        "service": "OmniMind AI Multimodal Intelligence Assistant",
        "database": db_status,
        "providers": provider_config,
        "timestamp": datetime.now().isoformat()
    }
