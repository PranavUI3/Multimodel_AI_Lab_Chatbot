"""
Provider Factory for OmniMind AI.
Manages provider instances, compatibility verification, and retrieval.
"""

from typing import Any, Dict, List
from fastapi import HTTPException, status

from .base import BaseAIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .huggingface_provider import HuggingFaceProvider


class ProviderFactory:
    def __init__(self):
        self._providers: Dict[str, BaseAIProvider] = {}
        self._register_defaults()

    def _register_defaults(self):
        self._providers["gemini"] = GeminiProvider()
        self._providers["openai"] = OpenAIProvider()
        self._providers["huggingface"] = HuggingFaceProvider()

    def get_provider(self, name: str) -> BaseAIProvider:
        key = name.lower().strip()
        if key not in self._providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown AI provider '{name}'. Supported providers: {list(self._providers.keys())}"
            )
        return self._providers[key]

    def list_providers(self) -> List[Dict[str, Any]]:
        results = []
        for p_id, p in self._providers.items():
            results.append({
                "name": p.name,
                "display_name": p.display_name,
                "supported_modalities": p.supported_modalities,
                "configured": p.is_configured(),
                "is_mock": not p.is_configured(),
                "model": getattr(p, "model_name", "standard")
            })
        return results


provider_factory = ProviderFactory()
