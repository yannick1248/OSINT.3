from __future__ import annotations

from osint_omega.gate import LegalEthicsGate
from osint_omega.types import Scope, Target, TargetType


def test_legally_restricted_scope_is_refused() -> None:
    gate = LegalEthicsGate()
    decision = gate.evaluate(
        Target(value="example.com", type=TargetType.DOMAIN),
        Scope.LEGALLY_RESTRICTED,
    )
    assert decision.allowed is False
    assert decision.status_text == "REFUSED"
    assert any("LEGALLY_RESTRICTED" in n for n in decision.notes)


def test_owned_assets_domain_is_allowed_without_notes() -> None:
    gate = LegalEthicsGate()
    decision = gate.evaluate(
        Target(value="example.com", type=TargetType.DOMAIN),
        Scope.OWNED_ASSETS,
    )
    assert decision.allowed is True
    assert decision.status_text == "ALLOWED"


def test_personal_target_in_sandbox_triggers_minimisation_note() -> None:
    gate = LegalEthicsGate()
    decision = gate.evaluate(
        Target(value="alice@example.com", type=TargetType.EMAIL),
        Scope.SANDBOX_TEST,
    )
    assert decision.allowed is True
    assert any("minimisation" in n.lower() for n in decision.notes)


def test_onion_target_adds_tor_note() -> None:
    gate = LegalEthicsGate()
    decision = gate.evaluate(
        Target(value="abc.onion", type=TargetType.ONION),
        Scope.CLIENT_AUTHORIZED_SCOPE,
    )
    assert any("tor" in n.lower() for n in decision.notes)
