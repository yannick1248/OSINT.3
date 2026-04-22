// Legal & ethics gate — mirrors osint_omega.gate.LegalEthicsGate
import { TargetType } from "./detect.js";

const PERSONAL_TYPES = new Set([
  TargetType.EMAIL, TargetType.PHONE, TargetType.PERSON, TargetType.USERNAME,
]);

export function evaluateGate(target, scope) {
  const notes = [];
  let allowed = true;
  let restricted = false;

  if (scope === "LEGALLY_RESTRICTED") {
    allowed = false;
    notes.push("Scope LEGALLY_RESTRICTED : aucune collecte autorisée.");
    return { allowed, restricted, notes };
  }

  if (PERSONAL_TYPES.has(target.type) && (scope === "SANDBOX_TEST" || scope === "PUBLIC_INTEREST_RESEARCH")) {
    restricted = true;
    notes.push("Donnée personnelle : appliquer la minimisation (RGPD art. 5). Justifier l'intérêt légitime et documenter la base légale.");
  }

  if (target.type === TargetType.ONION) {
    restricted = true;
    notes.push("Cible .onion : utiliser Tor/Whonix, ne pas dé-anonymiser sans mandat.");
  }

  if (target.type === TargetType.PERSON && scope !== "CLIENT_AUTHORIZED_SCOPE" && scope !== "INTERNAL_AUDIT") {
    restricted = true;
    notes.push("Identification d'une personne physique : vérifier le consentement ou l'intérêt public.");
  }

  if (scope === "SANDBOX_TEST") {
    notes.push("Mode sandbox : résultats à des fins pédagogiques uniquement, ne pas publier.");
  }

  return { allowed, restricted, notes };
}
