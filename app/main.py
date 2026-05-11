from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.pipelines.missing_person_pipeline import MissingPersonPipeline

app = FastAPI(title="OSINT Omega AI Backend", version="1.0.0")
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


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/modules")
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


@app.post("/api/v1/modules/run")
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


@app.post("/api/v1/investigate/missing-person")
async def investigate_missing_person(request: InvestigationRequest) -> dict[str, Any]:
    try:
        return await pipeline.investigate(request.as_inputs())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/investigate/general")
async def investigate_general(request: InvestigationRequest) -> dict[str, Any]:
    try:
        return await pipeline.investigate(request.as_inputs())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
