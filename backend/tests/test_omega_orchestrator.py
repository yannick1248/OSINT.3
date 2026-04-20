from __future__ import annotations

import pytest

from app.infrastructure.modules.omega_orchestrator import (
    OmegaOrchestratorModule,
    OmegaOrchestratorParams,
)

pytest.importorskip("osint_omega")


async def test_omega_module_runs_domain_syntax_end_to_end() -> None:
    module = OmegaOrchestratorModule()
    result = await module.execute(
        OmegaOrchestratorParams(
            target="example.com",
            target_type="domain",
            scope="OWNED_ASSETS",
            only=["domain_syntax"],
        )
    )
    assert result.status.value in {"SUCCESS", "PARTIAL"}
    assert result.data is not None
    mission = result.data.mission
    assert mission["scope"] == "OWNED_ASSETS"
    assert any(r["source"] == "domain_syntax" for r in mission["results"])


async def test_omega_module_blocks_legally_restricted() -> None:
    module = OmegaOrchestratorModule()
    result = await module.execute(
        OmegaOrchestratorParams(
            target="example.com",
            target_type="domain",
            scope="LEGALLY_RESTRICTED",
        )
    )
    mission = result.data.mission  # type: ignore[union-attr]
    assert all(r["status"] == "OUT_OF_SCOPE" for r in mission["results"])
