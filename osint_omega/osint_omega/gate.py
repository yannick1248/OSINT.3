"""LegalEthicsGate — barrière de conformité en amont de toute collecte.

Inspirée du prompt multi-agent forensique : chaque mission doit être classée
dans un périmètre explicite et est refusée/restreinte sinon.
"""

from __future__ import annotations

from dataclasses import dataclass

from osint_omega.types import Scope, Target, TargetType


@dataclass(frozen=True, slots=True)
class GateDecision:
    allowed: bool
    restricted: bool
    notes: tuple[str, ...]

    @property
    def status_text(self) -> str:
        if not self.allowed:
            return "REFUSED"
        return "RESTRICTED" if self.restricted else "ALLOWED"


class LegalEthicsGate:
    """Filtre les missions hors cadre et ajoute des notes de minimisation."""

    PERSONAL_TYPES = frozenset({TargetType.EMAIL, TargetType.PERSON, TargetType.USERNAME})

    def evaluate(self, target: Target, scope: Scope) -> GateDecision:
        notes: list[str] = []

        if scope == Scope.LEGALLY_RESTRICTED:
            notes.append(
                "Périmètre LEGALLY_RESTRICTED : seule une simulation / "
                "une méthodologie peut être produite ; aucune collecte réelle."
            )
            return GateDecision(allowed=False, restricted=True, notes=tuple(notes))

        if target.type in self.PERSONAL_TYPES and scope in {
            Scope.SANDBOX_TEST,
            Scope.PUBLIC_INTEREST_RESEARCH,
        }:
            notes.append(
                "Cible personnelle hors périmètre mandaté : minimisation "
                "obligatoire, ne pas attribuer d'identité réelle sans base forte."
            )

        if target.type == TargetType.ONION:
            notes.append(
                "Cible .onion : activer Tor, journaliser chaque requête, "
                "ne jamais télécharger de contenu illégal."
            )

        if scope == Scope.SANDBOX_TEST:
            notes.append("SANDBOX_TEST : résultats à considérer comme non probatoires.")

        return GateDecision(allowed=True, restricted=False, notes=tuple(notes))
