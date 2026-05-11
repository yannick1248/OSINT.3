from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

from app.pipelines.missing_person_pipeline import MissingPersonPipeline

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def _has_runtime_dependencies() -> bool:
    return importlib.util.find_spec("fastapi") is not None and importlib.util.find_spec("pydantic") is not None


class DependencyNoticeApp:
    """Tiny ASGI fallback that keeps `import app.main` working before dependencies are installed."""

    title = "OSINT Omega AI Backend"
    missing_dependencies = ("fastapi", "pydantic")

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        body = (
            "OSINT Omega AI dependencies are not installed. "
            "Run `python -m pip install -r requirements.txt` or use the Docker image."
        ).encode()
        await send(
            {
                "type": "http.response.start",
                "status": 503,
                "headers": [(b"content-type", b"text/plain; charset=utf-8"), (b"content-length", str(len(body)).encode())],
            }
        )
        await send({"type": "http.response.body", "body": body})


def create_app() -> Any:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field

    api = FastAPI(title="OSINT Omega AI Backend", version="1.0.0")
    api.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    pipeline = MissingPersonPipeline()

    class InvestigationRequest(BaseModel):
        requestor_id: str = Field(..., min_length=1)
        legal_basis: str = Field(..., min_length=1)
        name: str | None = None
        email: str | None = None
        phone: str | None = None
        username: str | None = None
        domain: str | None = None
        image_path: str | None = None
        investigation_id: str | None = None

        def as_inputs(self) -> dict[str, Any]:
            return self.model_dump(exclude_none=True)

    class ModuleRunRequest(InvestigationRequest):
        module: str

    @api.get("/", include_in_schema=False)
    async def web_console() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @api.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.get("/api/v1/modules")
    async def modules() -> list[dict[str, Any]]:
        return [
            {
                "name": module.name,
                "description": module.description,
                "required_inputs": sorted(module.required_inputs),
                "optional_inputs": sorted(module.optional_inputs),
                "required_env": sorted(module.required_env),
            }
            for module in pipeline.modules
        ]

    @api.post("/api/v1/modules/run")
    async def run_module(request: ModuleRunRequest) -> dict[str, Any]:
        inputs = request.as_inputs()
        module = next((candidate for candidate in pipeline.modules if candidate.name == request.module), None)
        if module is None:
            raise HTTPException(status_code=404, detail=f"module not found: {request.module}")
        can_run, missing = module.can_run(inputs, os.environ)
        if not can_run:
            raise HTTPException(status_code=400, detail={"missing": missing})
        result = await module.run(inputs, os.environ)
        return result.to_dict()

    @api.post("/api/v1/investigate/missing-person")
    async def investigate_missing_person(request: InvestigationRequest) -> dict[str, Any]:
        try:
            return await pipeline.investigate(request.as_inputs())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @api.post("/api/v1/investigate/general")
    async def investigate_general(request: InvestigationRequest) -> dict[str, Any]:
        try:
            return await pipeline.investigate(request.as_inputs())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return api


app = create_app() if _has_runtime_dependencies() else DependencyNoticeApp()
