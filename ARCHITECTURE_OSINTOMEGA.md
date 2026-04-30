# OsintOmegaAI — Architecture d’orchestrateur intelligent (version légale-by-design)

## 1) Périmètre et briques intégrées (sans omission)

Ce document intègre explicitement les briques demandées :

1. **Listes AVS inactivés/annulés CdC (ZAS)**, téléchargement périodique et détection de pattern `YYYYMM`.
2. **Service SMS 939 Genève (plaques → détenteur)** : contexte historique (presse/archives web), état actuel (accès réservé professionnels ou demande en ligne).
3. **eAutoindex / infocar.ch** : pas d’API publique de masse pour plaques suisses.
4. **Modules API** : OpenCorporates, Judilibre, Pappers, INPI, OpenSanctions, Wikidata SPARQL, Shodan, Censys, VesselFinder, OpenSky, Intelligence X, Have I Been Pwned, Telegram MTProto, CrossLinked, Maltego.
5. **Validation ID (microservice Perl)** : `Algorithm::CheckDigits::MXX_001` (modulo 7-3-1), documentation Kryptografie.de.
6. **Contraintes annuaires inversés local.ch/search.ch** : pas de scraping, alternatives légales pro (API/partenaires B2B), pas de constitution d’une base de masse.
7. **Registres des poursuites (Suisse) + registres cantonaux** : accès sur demande motivée.

---

## 2) Architecture d’orchestrateur intelligent

## 2.1 Principes

- **Légalité stricte** : toute requête passe par un moteur de politiques (juridique + ToS + finalité).
- **Transparence algorithmique** : chaque résultat conserve source, timestamp, méthode et score de confiance.
- **Profondeur temporelle** : données courantes + historiques (archives web, presse, snapshots).
- **Chaînage conservateur** : les liens forts exigent plusieurs corroborations ; sinon signal “hypothèse”.

## 2.2 Flux de traitement

Entrée possible :
- nom,
- téléphone,
- email,
- AVS inactivé,
- plaque GE.

Pipeline :
1. **Normalizer** : normalise formats (E.164, email canonique, plaque cantonale, clé AVS, etc.).
2. **Classifier** : détecte type d’identifiant + juridiction.
3. **Policy Engine** : autorise/refuse routes sources en fonction de la base légale et ToS.
4. **Source Router** : choisit connecteurs API / registres sur demande.
5. **Rate-limit + retry + cache TTL** : protège conformité et coûts.
6. **Entity Resolver** : fusionne résultats en graphe d’entités.
7. **Evidence Scorer** : calcule confiance (fraîcheur, qualité source, cohérence croisée).
8. **Dossier consolidé** : export JSON + PDF de traçabilité.

## 2.3 Pseudo-code Python (orchestrateur)

```python
from dataclasses import dataclass
from typing import Dict, List, Any
import time

@dataclass
class QueryContext:
    input_raw: str
    input_type: str
    jurisdiction: str
    purpose: str
    operator_id: str

class PolicyEngine:
    def authorize(self, source_name: str, ctx: QueryContext) -> bool:
        forbidden_scraping = {"local.ch", "search.ch"}
        if source_name in forbidden_scraping:
            return False
        # règles complémentaires: finalité, proportionnalité, base légale, ToS
        return True

class Cache:
    def __init__(self):
        self.store = {}
    def get(self, key):
        v = self.store.get(key)
        if not v:
            return None
        if v["exp"] < time.time():
            return None
        return v["data"]
    def set(self, key, data, ttl_sec=3600):
        self.store[key] = {"data": data, "exp": time.time() + ttl_sec}

class SourceRouter:
    def routes_for(self, input_type: str) -> List[str]:
        base = {
            "name": ["OpenCorporates", "Pappers", "INPI", "Wikidata", "OpenSanctions", "Judilibre"],
            "phone": ["HIBP", "IntelligenceX", "CrossLinked", "TelegramMTProto"],
            "email": ["HIBP", "OpenSanctions", "Wikidata", "IntelligenceX"],
            "avs_inactive": ["ZAS_AVS_YYYYMM"],
            "plate_ge": ["GE_939_professional_or_online_request", "InfocarManual"],
        }
        return base.get(input_type, [])

class PerlIDValidatorClient:
    """Microservice wrapper pour Algorithm::CheckDigits::MXX_001 (mod 7-3-1)."""
    def validate(self, id_value: str) -> Dict[str, Any]:
        # appel HTTP local vers microservice Perl
        return {"valid": True, "algo": "MXX_001_7-3-1", "source": "Kryptografie.de"}

class Orchestrator:
    def __init__(self, connectors: Dict[str, Any]):
        self.policy = PolicyEngine()
        self.cache = Cache()
        self.router = SourceRouter()
        self.connectors = connectors
        self.id_validator = PerlIDValidatorClient()

    def execute(self, ctx: QueryContext) -> Dict[str, Any]:
        routes = self.router.routes_for(ctx.input_type)
        evidence = []

        for source in routes:
            if not self.policy.authorize(source, ctx):
                evidence.append({"source": source, "status": "blocked_policy"})
                continue

            cache_key = f"{source}:{ctx.input_raw}"
            cached = self.cache.get(cache_key)
            if cached:
                evidence.append({"source": source, "status": "cache_hit", "data": cached})
                continue

            connector = self.connectors.get(source)
            if connector is None:
                evidence.append({"source": source, "status": "missing_connector"})
                continue

            result = connector.query(ctx.input_raw)  # connector gère rate-limit + pagination
            self.cache.set(cache_key, result, ttl_sec=connector.ttl)
            evidence.append({"source": source, "status": "ok", "data": result})

        # validation optionnelle d’un identifiant document
        id_check = self.id_validator.validate(ctx.input_raw) if ctx.input_type == "id_number" else None

        consolidated = self._consolidate(evidence, id_check)
        return consolidated

    def _consolidate(self, evidence, id_check):
        # résolution d'entité conservatrice: pas de fusion forte sans 2+ sources cohérentes
        return {
            "entity_profile": {"name": None, "phones": [], "emails": [], "organizations": []},
            "evidence": evidence,
            "id_validation": id_check,
            "confidence": "medium",
            "audit": {"method": "conservative_chaining", "timestamp": int(time.time())}
        }
```

## 2.4 Intégration microservice Perl (exemple)

- Service local isolé : `perl-id-validator`.
- Endpoint : `POST /validate-id`.
- Implémente `Algorithm::CheckDigits::MXX_001` (pondération modulo 7-3-1).
- Retour : `{valid, normalized, checksum_method, explanation}`.

Exemple wrapper minimal:

```bash
# Docker interne (réseau privé)
docker run --rm -p 127.0.0.1:9077:9077 osint/perl-id-validator:latest
```

---

## 3) Schéma SQLite (temporaire) — entities, number_pool, crosslinks

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type TEXT NOT NULL,                 -- person|org|device|vehicle|account
  display_name TEXT,
  jurisdiction TEXT,
  legal_basis TEXT,                          -- ex: intérêt prépondérant, consentement, obligation légale
  risk_level TEXT DEFAULT 'medium',
  confidence_score REAL DEFAULT 0.0,
  first_seen_utc TEXT NOT NULL,
  last_seen_utc TEXT NOT NULL,
  created_by TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS number_pool (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_id INTEGER,
  number_type TEXT NOT NULL,                 -- phone|email|avs|plate|id_doc|ip
  raw_value TEXT NOT NULL,
  normalized_value TEXT,
  country_hint TEXT,
  validation_status TEXT,                    -- valid|invalid|unknown|not_applicable
  validation_method TEXT,                    -- ex: MXX_001_7-3-1
  source_name TEXT NOT NULL,
  source_url TEXT,
  source_timestamp_utc TEXT,
  legal_collection_mode TEXT NOT NULL,       -- api|manual_request|public_registry|archive
  retention_until_utc TEXT,
  hash_sha256 TEXT,
  UNIQUE(number_type, normalized_value, source_name),
  FOREIGN KEY(entity_id) REFERENCES entities(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS crosslinks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  from_entity_id INTEGER NOT NULL,
  to_entity_id INTEGER NOT NULL,
  link_type TEXT NOT NULL,                   -- same_as|possible_match|owns|controls|associated_with
  strength REAL NOT NULL,                    -- 0..1
  evidence_count INTEGER DEFAULT 1,
  rationale TEXT,
  created_utc TEXT NOT NULL,
  reviewer TEXT,
  review_status TEXT DEFAULT 'pending',      -- pending|validated|rejected
  FOREIGN KEY(from_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
  FOREIGN KEY(to_entity_id) REFERENCES entities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(display_name);
CREATE INDEX IF NOT EXISTS idx_pool_norm ON number_pool(number_type, normalized_value);
CREATE INDEX IF NOT EXISTS idx_cross_from_to ON crosslinks(from_entity_id, to_entity_id);
```

---

## 4) Analyse juridique par type de croisement (CH/EU)

> **Important** : cette section est opérationnelle, pas un avis juridique formel. Validation finale par conseil juridique suisse recommandé.

## 4.1 Cadre normatif

- **LPD suisse (nLPD)** : principes de licéité, bonne foi, proportionnalité, finalité, exactitude, sécurité, durée de conservation limitée.
- **RGPD (UE)** si traitement lié à des personnes dans l’UE : base légale (art. 6), minimisation/finalité, DPIA si risque élevé, droits des personnes.
- **LCD suisse** (concurrence déloyale) : respect des conditions d’utilisation, pas d’exploitation parasitaire ou trompeuse.
- **CGA/ToS des plateformes** : contractuellement contraignantes ; une violation peut engager responsabilité civile.

## 4.2 Matrice de légalité par croisement

1. **Téléphone/email ↔ fuites (HIBP, Intelligence X)**
   - Légal si finalité légitime (ex. cybersécurité, due diligence), minimisation et journalisation.
   - Interdit : réutilisation intrusive, profilage de masse sans base légale.

2. **Nom ↔ sociétés (OpenCorporates, Pappers, INPI, Judilibre)**
   - Légal car sources officielles/ouverts, sous réserve de proportionnalité et exactitude.
   - Exiger mention d’origine + date d’extraction.

3. **Plaque GE ↔ détenteur (939 / requête officielle)**
   - Utiliser uniquement canaux autorisés (professionnels habilités ou formulaire officiel).
   - Interdit : contournement technique, scraping d’interfaces non prévues.

4. **AVS inactivé ↔ listes CdC (ZAS)**
   - Légal en contrôle de validité/qualité des données, pas en usage discriminatoire.
   - Conserver preuve de source + cycle `YYYYMM`.

5. **Annuaires inversés local.ch/search.ch**
   - Pas de scraping automatisé.
   - Alternative légale : API pro, fournisseurs B2B licenciés, requêtes unitaires documentées.

6. **Registre des poursuites / registres cantonaux**
   - Accès sur demande motivée ; principe du besoin de connaître.
   - Archiver justificatif de la demande et limiter la diffusion du résultat.

## 4.3 Conditions opérationnelles de conformité

- Registre de traitement + base légale par requête.
- Politique de rétention courte (TTL, purge automatique).
- Sécurité : chiffrement at-rest, contrôle d’accès, audit trail.
- Human-in-the-loop pour liens “gris” (crosslinks < seuil confiance).
- Mécanisme de rectification/suppression lorsque requis.

---

## 5) 5 prompts de veille mensuelle (Perplexity)

1. **Registres suisses et accès**
   - « Quelles modifications officielles (12 derniers mois) touchent l’accès aux registres cantonaux suisses, au registre des poursuites et aux procédures de demande motivée ? Donne sources administratives officielles et dates exactes. »

2. **Plaques GE / services détenteurs**
   - « État actuel du service genevois lié aux plaques (historique SMS 939, alternatives actuelles), conditions d’accès professionnels/particuliers, URLs officielles et date de dernière mise à jour. »

3. **APIs OSINT légales**
   - « Quelles nouveautés API/pricing/ToS pour OpenCorporates, Pappers, INPI, OpenSanctions, Shodan, Censys, OpenSky, VesselFinder, HIBP, Intelligence X ce mois-ci ? Inclure limitations légales d’usage. »

4. **Cadre légal données perso CH/EU**
   - « Recense les évolutions récentes nLPD Suisse, RGPD, jurisprudences et recommandations autorités (PFPDT/EDPB) impactant l’OSINT et le data matching. Fournis dates et textes officiels. »

5. **Annuaire inversé et anti-scraping**
   - « Nouvelles clauses ToS, décisions de justice ou avis régulateurs concernant scraping d’annuaires (local.ch/search.ch et équivalents UE). Quelles alternatives B2B/API sont explicitement autorisées ? »

---

## 6) Tableau récapitulatif (outil → usage → légalité → coût)

| Outil / Source | Usage OSINT | Légalité (conditions) | Coût indicatif |
|---|---|---|---|
| CdC/ZAS listes AVS inactivés (`YYYYMM`) | Vérifier statut AVS invalide/inactivé | Oui si finalité légitime + non-discrimination + minimisation | Faible (public) |
| Service GE 939 (historique) / demande officielle | Plaque GE → détenteur (canal autorisé) | Oui via circuits autorisés uniquement | Variable / administratif |
| eAutoindex / infocar.ch | Consultation ponctuelle véhicule | Pas d’API de masse publique ; usage selon ToS | Faible à moyen |
| OpenCorporates | Liens sociétés/personnes | Oui (ToS + attribution) | Gratuit/Payant |
| Judilibre | Jurisprudence FR | Oui (licence ouverte + finalité) | Faible |
| Pappers | Données entreprises FR | Oui selon licence/ToS | Freemium |
| INPI | Marques/sociétés/propriété industrielle | Oui (portail/API officielle) | Faible |
| OpenSanctions | Screening sanctions/PEP | Oui si proportionnalité + contrôle humain | Gratuit/Payant |
| Wikidata SPARQL | Enrichissement entités | Oui (CC0) | Gratuit |
| Shodan | Exposition services internet | Oui si usage défensif/légal | Payant |
| Censys | Cartographie internet | Oui si usage défensif/légal | Payant |
| VesselFinder | OSINT maritime | Oui selon licence API | Freemium |
| OpenSky | OSINT aérien | Oui selon ToU/API | Gratuit/Payant |
| Intelligence X | Index d’archives/fuites | Oui si finalité légitime et non abusive | Payant |
| Have I Been Pwned | Vérif compromission email/téléphone | Oui avec consentement/usage sécurité | Payant API |
| Telegram MTProto | Collecte canaux publics | Oui si public + ToS + pas d’intrusion | Faible à moyen |
| CrossLinked | Corrélation identité/infra | Oui si finalité légitime + contrôle | Variable |
| Maltego | Fusion visuelle / graph analytics | Oui selon données sources et licences | Payant |
| local.ch / search.ch | Annuaire inversé | **Pas de scraping** ; API pro/B2B seulement | Variable |
| Registre des poursuites | Vérif solvabilité sur motif | Oui sur demande motivée | Frais administratifs |

---

## 7) Garde-fous à imposer en production

- Feature flag “**strict_legal_mode=true**” non désactivable.
- Blocage hard des connecteurs interdits (scraping annuaires).
- Quota par opérateur + justification obligatoire pour sources sensibles.
- Purge automatique des tables temporaires (ex. 30/60/90 jours selon base légale).
- Rapport d’audit exportable (qui, quoi, quand, pourquoi, source, résultat).

