# OsintOmegaAI — Synthèse opérationnelle complète (v3)

_Date : 29 avril 2026_  
_Objectif : architecture OSINT légale à haute puissance, sans scraping de masse._

## A) Architecture d’orchestrateur intelligent (Python/pseudo-code)

### A.1 Briques intégrées (exhaustif)
1. **CdC/ZAS NAVS** : listes inactivés/annulés (`NAVSInact.YYYYMM`, `NAVSAnnul.YYYYMM`, archives annuelles).
2. **Service 939 Genève** : historique + état actuel (accès encadré, professionnels/demande autorisée).
3. **eAutoindex / infocar.ch** : pas d’API publique de masse plaques CH.
4. **APIs juridiques/OSINT** : OpenCorporates, Judilibre, Pappers, INPI, OpenSanctions, Wikidata SPARQL, Shodan, Censys, VesselFinder, OpenSky, Intelligence X, HIBP, Telegram MTProto, CrossLinked, Maltego.
5. **Validation ID (Perl)** : `Algorithm::CheckDigits::MXX_001` (modulo 7-3-1) microservice.
6. **Annuaires inversés** : `local.ch` / `search.ch` sans scraping ; uniquement voies légales (API pro/partenaires B2B/accord contractuel).
7. **Registre des poursuites CH + registres cantonaux** : accès sur demande motivée/intérêt légitime.

### A.2 Entrées supportées
- `name`
- `phone_e164`
- `email`
- `avs_inactive`
- `plate_ge`

### A.3 Règles d’orchestration
- **No-go absolu**: pas de scraping automatisé de local.ch/search.ch.
- **Priorité source**: officielle primaire > API réglementée > fournisseur contractuel > source communautaire.
- **Gating légal**: chaque requête nécessite `purpose`, `legal_basis`, `operator_id`.
- **Résilience**: rate-limit par fournisseur, cache TTL, retry exponentiel, circuit-breaker.

### A.4 Pseudo-code Python (asynchrone)
```python
from dataclasses import dataclass
from enum import Enum

class Confidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

@dataclass
class QueryContext:
    operator_id: str
    purpose: str
    legal_basis: str
    retention_days: int = 30

@dataclass
class InputIdentifier:
    kind: str   # name|phone_e164|email|avs_inactive|plate_ge
    value: str

async def orchestrate(identifier: InputIdentifier, ctx: QueryContext):
    assert ctx.purpose and ctx.legal_basis, "legal gating required"

    # 1) Normalisation
    normalized = normalize_identifier(identifier)

    # 2) Plan de collecte légal (sans scraping annuaires)
    plan = select_legal_sources(normalized)
    # Exemple plan selon type:
    # - avs_inactive -> ZAS NAVSInact + UPI (autorisé)
    # - plate_ge -> module ge_index_auto (rôle pro requis)
    # - phone/email/name -> APIs contractuelles + registres + OSINT public API

    # 3) Exécution avec rate-limits
    raw_results = []
    for source in plan:
        if not allowed_by_policy(source, ctx):
            continue
        result = await call_source_with_limits(
            source=source,
            payload=normalized,
            cache_ttl=source.ttl,
            qps=source.qps,
            retries=3,
            backoff="exponential",
        )
        raw_results.append(result)

    # 4) Validation identité (microservice Perl modulo 7-3-1)
    id_validation = await call_perl_id_validator_if_needed(raw_results)

    # 5) Entity resolution / crosslinks
    entity = consolidate_entity(raw_results, id_validation)
    entity.confidence = score_confidence(entity)

    # 6) Production fiche consolidée + audit trail
    report = build_entity_sheet(entity, ctx)
    await write_audit_log(ctx, normalized, plan, report)
    return report
```

### A.5 Microservice Perl (validation carte ID)
- Implémentation dédiée (conteneur isolé) exposant `/validate-id`.
- Bibliothèque : `Algorithm::CheckDigits::MXX_001` (méthode modulo 7-3-1, référence Kryptografie.de).
- Contrat JSON :
```json
{ "document_number": "X1234567", "country": "CH" }
```
Réponse:
```json
{ "valid": true, "method": "MXX_001", "checksum": "7-3-1" }
```

### A.6 Alternatives légales à local.ch/search.ch
- API professionnelles sous contrat (si disponibles).
- Data providers B2B contractualisés.
- Registres officiels/sectoriels selon finalité.
- Jamais de constitution de miroir “annuaire national” via extraction automatisée.
## B) Schéma SQLite (temporaire) — `entities`, `number_pool`, `crosslinks`

```sql
CREATE TABLE entities (
  id TEXT PRIMARY KEY,
  entity_type TEXT NOT NULL,          -- person|company|vehicle|phone|email|avs|domain
  display_name TEXT,
  canonical_hash TEXT NOT NULL,
  confidence TEXT NOT NULL,           -- LOW|MEDIUM|HIGH
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  source_count INTEGER NOT NULL DEFAULT 0,
  legal_basis TEXT NOT NULL,
  retention_until TEXT NOT NULL
);

CREATE TABLE number_pool (
  id TEXT PRIMARY KEY,
  number_type TEXT NOT NULL,          -- phone|plate_ge|avs
  normalized_value TEXT NOT NULL,
  status TEXT,                        -- active|inactive|cancelled|unknown
  validation_method TEXT,             -- E164|NAVSInact|MXX_001|manual
  related_entity_id TEXT,
  source_ref TEXT NOT NULL,
  observed_at TEXT NOT NULL,
  FOREIGN KEY (related_entity_id) REFERENCES entities(id)
);

CREATE TABLE crosslinks (
  id TEXT PRIMARY KEY,
  src_entity_id TEXT NOT NULL,
  dst_entity_id TEXT NOT NULL,
  link_type TEXT NOT NULL,            -- owns|uses|registered_at|appears_in|same_as
  evidence_score REAL NOT NULL,
  confidence TEXT NOT NULL,
  source_ref TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (src_entity_id) REFERENCES entities(id),
  FOREIGN KEY (dst_entity_id) REFERENCES entities(id)
);
```

**Contraintes opérationnelles**
- Données minimisées (hash + références sources).
- TTL court par défaut (30 jours) sauf obligation légale contraire.
- Purge automatique + journal d’audit inviolable.
## C) Analyse juridique par type de croisement
> **Avertissement**: synthèse opérationnelle, non conseil juridique formel.
### C.1 Téléphone ↔ identité
- **Risque**: profilage illicite, détournement de finalité, violation CGU annuaires.
- **Cadre**: LPD (principes de licéité/finalité/proportionnalité), RGPD (base légale, minimisation), LCD (appropriation parasitaire potentielle).
- **Condition de légalité**: source autorisée + finalité explicite + journalisation + conservation limitée.
### C.2 Plaque GE ↔ détenteur
- **Risque**: consultation hors intérêt légitime.
- **Cadre**: accès réglementé cantonal (service encadré), protection données personnelles.
- **Condition**: rôle autorisé/professionnel, justification documentée, usage au cas par cas.
### C.3 AVS inactif/annulé ↔ AVS actif
- **Risque**: réidentification abusive.
- **Cadre**: publication CdC + usages autorisés UPI/UPIServices, LPD.
- **Condition**: usage organisationnel légitime (qualité de données/identité), accès restreint, audit.
### C.4 Croisement fuites (HIBP/Intelligence X) ↔ personne/organisation
- **Risque**: traitement excessif de données sensibles/exposées.
- **Cadre**: finalité défensive cybersécurité, minimisation stricte.
- **Condition**: ne conserver que l’indicateur de compromission utile (pas aspirer la fuite complète).
### C.5 Registre poursuites / registres cantonaux
- **Risque**: collecte sans motif.
- **Cadre**: accès sur demande motivée/intérêt légitime, règles cantonales.
- **Condition**: dossier documenté, périmètre restreint, contrôle interne.
## D) 5 prompts de veille mensuelle (Perplexity)

1. **Nouvelles APIs annuaires et B2B**  
   _« Quelles APIs (Suisse/UE) apparues ou modifiées depuis le mois dernier permettent l’enrichissement légal de contact (B2B/pro), avec CGU, quotas et prix ? »_

2. **Changements CGU local.ch/search.ch**  
   _« Compare les CGU actuelles de local.ch et search.ch vs version du mois précédent ; extrais les clauses scraping, automatisation, usage commercial et API. »_
3. **PFPDT + jurisprudence LPD**  
   _« Quelles décisions/recommandations 2025–2026 du PFPDT (ou jurisprudence suisse) touchent annuaires inversés, profilage, proportionnalité et conservation ? »_
4. **Registres suisses accessibles sur intérêt légitime**  
   _« Liste les nouveaux services cantonaux/fédéraux (poursuites, foncier, entreprises) ouverts/modernisés depuis 2025 et leurs conditions d’accès. »_
5. **Surveillance stack API OSINT**  
   _« Vérifie les changements d’accès/coûts/limits pour OpenCorporates, INPI, Pappers, OpenSanctions, Censys, Shodan, HIBP, IntelX, Telegram MTProto, OpenSky, VesselFinder/AISHub. »_
## E) Tableau récapitulatif (Outil → Usage OSINT → Légalité → Coût)

| Outil | Usage OSINT | Légalité (cadre) | Coût |
|---|---|---|---|
| CdC NAVSInact/NAVSAnnul | correction AVS, détection inactif/annulé | oui si finalité légitime + contrôle accès | gratuit/public |
| UPI/UPIServices | réidentification AVS autorisée | réglementé (organismes autorisés) | variable |
| GE Index Auto (939) | plaque GE -> détenteur | accès encadré pro/demande motivée | payant selon service |
| eAutoindex/infocar.ch | recherche véhicule/infos index | pas d’API de masse publique | variable |
| OpenCorporates | liens sociétés-dirigeants | API/CGU | freemium/payant |
| Judilibre | jurisprudence FR | open data | gratuit |
| Pappers API | données société FR | API/CGU | freemium |
| INPI | propriété/entreprises FR | API/CGU | freemium |
| OpenSanctions | screening sanctions/PEP | licence source/API | gratuit/freemium |
| Wikidata SPARQL | pivot graphes publics | open query policy | gratuit |
| Shodan | exposition infra | API contractuelle | payant |
| Censys | certs/hosts/ASN | API contractuelle | freemium/payant |
| VesselFinder | maritime AIS | API/CGU | freemium/payant |
| OpenSky | trafic aérien | API/politique usage | gratuit/freemium |
| Intelligence X | index leaks/web | API contractuelle | payant |
| HIBP | compromission email/domain | API contractuelle | payant |
| Telegram MTProto | veille publics/canaux | API policy + droit local | gratuit (usage encadré) |
| CrossLinked | OSINT personnes/sociaux | usage légal + CGU cibles | open-source |
| Maltego | chaînage/transforms | licence + sources conformes | freemium/payant |
| local.ch / search.ch | annuaire inversé ponctuel | **pas de scraping** ; uniquement voies pro/autorisées | variable |
| Registre des poursuites CH | situation poursuites | accès sur intérêt légitime | payant |
| Perl MXX_001 (ID check) | validation checksum doc | légal si finalité vérification | faible (infra interne) |
---

## Sources de référence (29 avril 2026)
- Wayback GE : http://web.archive.org/web/*/https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
- CdC NAVS : https://www.zas.admin.ch/fr/numeros-inactives-ou-annules
- CdC UPIServices : https://www.zas.admin.ch/fr/interface-upiservices
- TDG index (historique 2013) : https://www.tdg.ch/geneve/2013/04/22
- Module Perl MXX_001 (doc communautaire) : https://www.kryptografie.de/kryptografie/chiffre/machine-readable-zone.htm
## Sources principales (consultées le 29 avril 2026)
- GE Index Auto: https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
- Wayback endpoint demandé: http://web.archive.org/web/*/https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
- CdC numéros inactivés/annulés: https://www.zas.admin.ch/fr/numeros-inactives-ou-annules
- CdC UPIServices: https://www.zas.admin.ch/fr/interface-upiservices
- TDG (archive index, article 2013 mentionné): https://www.tdg.ch/geneve/2013/04/22
