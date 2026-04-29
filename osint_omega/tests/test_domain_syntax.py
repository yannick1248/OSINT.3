from __future__ import annotations

from osint_omega.tools.domain_syntax import DomainSyntaxTool
from osint_omega.types import Confidence, Target, TargetType, ToolStatus


async def test_well_formed_domain() -> None:
    tool = DomainSyntaxTool()
    result = await tool.run(Target(value="Sub.example.com", type=TargetType.DOMAIN))
    assert result.status is ToolStatus.SUCCESS
    assert result.confidence is Confidence.VERY_HIGH
    assert result.data["tld"] == "com"
    assert result.data["labels"] == ["sub", "example", "com"]


async def test_malformed_domain_fails() -> None:
    tool = DomainSyntaxTool()
    result = await tool.run(Target(value="not_a_domain", type=TargetType.DOMAIN))
    assert result.status is ToolStatus.FAILED
    assert result.confidence is Confidence.LOW
