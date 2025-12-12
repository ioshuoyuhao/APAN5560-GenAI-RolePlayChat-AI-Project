# API Routers - Export all routers for easy registration
from .api_providers import router as api_providers_router
from .characters import router as characters_router
from .conversations import router as conversations_router
from .discover import router as discover_router
from .knowledge_bases import router as knowledge_bases_router
from .prompt_templates import router as prompt_templates_router

__all__ = [
    "api_providers_router",
    "characters_router",
    "conversations_router",
    "discover_router",
    "knowledge_bases_router",
    "prompt_templates_router",
]
