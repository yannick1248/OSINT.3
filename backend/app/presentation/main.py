from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.infrastructure.config import get_settings
from app.presentation.routers import health, modules

LEGAL_DISCLAIMER = (
    "OSINT OMÉGA AI — usage légal et éthique uniquement. "
    "Toute requête est journalisée pour audit trail."
)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="OSINT OMÉGA AI",
        version=__version__,
        description=LEGAL_DISCLAIMER,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.env == "development" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(modules.router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"name": "OSINT OMÉGA AI", "version": __version__, "disclaimer": LEGAL_DISCLAIMER}

    return app


app = create_app()
