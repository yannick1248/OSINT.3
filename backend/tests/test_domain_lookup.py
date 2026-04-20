from __future__ import annotations

import pytest

from app.domain.modules.base import ConfidenceLevel, OsintResultStatus
from app.infrastructure.modules.domain_lookup import (
    DomainLookupModule,
    DomainLookupParams,
)


@pytest.fixture
def module() -> DomainLookupModule:
    return DomainLookupModule()


async def test_valid_domain_returns_success_high_confidence(
    module: DomainLookupModule,
) -> None:
    result = await module.execute(DomainLookupParams(domain="Example.com"))
    assert result.status is OsintResultStatus.SUCCESS
    assert result.confidence is ConfidenceLevel.HIGH
    assert result.data is not None
    assert result.data.domain == "example.com"
    assert result.data.tld == "com"
    assert result.data.labels == ["example", "com"]


async def test_malformed_domain_returns_failed_low_confidence(
    module: DomainLookupModule,
) -> None:
    result = await module.execute(DomainLookupParams(domain="not_a_domain"))
    assert result.status is OsintResultStatus.FAILED
    assert result.confidence is ConfidenceLevel.LOW
    assert result.data is not None
    assert result.data.is_well_formed is False


async def test_validate_input_rejects_garbage(module: DomainLookupModule) -> None:
    assert await module.validate_input(DomainLookupParams(domain="no-tld")) is False
    assert await module.validate_input(DomainLookupParams(domain="good.tld")) is True


def test_describe_exposes_schemas(module: DomainLookupModule) -> None:
    desc = module.describe()
    assert desc["name"] == "domain_lookup"
    assert "input_schema" in desc
    assert "output_schema" in desc
    assert desc["confidence_levels"] == ["LOW", "MEDIUM", "HIGH"]
