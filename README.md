# OSINT OMÉGA AI

Plateforme d'investigation OSINT modulaire à **usage légal et éthique**, à
destination des journalistes, enquêteurs mandatés, équipes cyber et
chercheurs.

Le dépôt rassemble trois briques complémentaires :

| Brique        | Rôle                                                                 |
|---------------|----------------------------------------------------------------------|
| `osint_omega/`| Orchestrateur CLI Python — sélectionne et exécute les outils OSINT. |
| `backend/`    | API FastAPI (Clean Architecture) exposant les modules + l'orchestrateur. |
| `frontend/`   | Next.js 15 (App Router) — interface d'investigation.                |

Un prompt multi-agent forensique est fourni sous
`osint_omega/osint_omega/agents/system_prompt.xml` : il encode la gouvernance,
le modèle de confiance 4 niveaux et les garde-fous décrits ci-dessous, et
peut être injecté dans n'importe quel LLM orchestrateur amont.

## Démarrage ultra-rapide (CLI)

```bash
./install.sh core                           # installe osint_omega uniquement
python omega.py --list-tools
python omega.py --target example.com --type domain --scope OWNED_ASSETS --pretty
```

Résultat : une `Mission` JSON avec la cible, le périmètre, la liste des
`ToolResult` (chacun normalisé `source / status / confidence / timestamp /
data / error / cache_hit`) et les notes du `LegalEthicsGate`.

## Stack complète

```bash
cp .env.example .env
./install.sh full                           # core + backend + frontend
docker compose up --build                   # Postgres + Redis + ES + API + UI
```

- API : http://localhost:8000 (docs OpenAPI : `/docs`)
- Frontend : http://localhost:3000

## Gouvernance — périmètres obligatoires

Toute mission doit déclarer un `scope` (via CLI ou API) :

- `SANDBOX_TEST` — tests, jeux factices, non probatoire.
- `OWNED_ASSETS` — actifs que vous possédez ou administrez.
- `CLIENT_AUTHORIZED_SCOPE` — mandat explicite.
- `PUBLIC_INTEREST_RESEARCH` — recherche d'intérêt public documentée.
- `INTERNAL_AUDIT` — audit interne.
- `LEGALLY_RESTRICTED` — bloqué (seule la méthodologie peut être produite).

Le `LegalEthicsGate` ajoute automatiquement des notes de minimisation pour
les cibles personnelles (email, pseudo, personne) et les cibles `.onion`.

## Modèle de confiance (4 niveaux)

`LOW < MEDIUM < HIGH < VERY_HIGH` — identique entre
`osint_omega.Confidence`, `backend.ConfidenceLevel` et le prompt agent.
Le moteur applique un bonus de corroboration lorsque trois sources
indépendantes convergent.

## Catalogue d'outils actuels

| Outil           | Cible type         | Disponibilité                        |
|-----------------|--------------------|---------------------------------------|
| `domain_syntax` | domain             | toujours (local)                      |
| `crtsh`         | domain             | toujours (API crt.sh)                 |
| `hibp`          | email              | clé `HIBP_API_KEY`                    |
| `maigret`       | username           | binaire `maigret` dans `PATH`         |
| `holehe`        | email              | binaire `holehe`                      |
| `the_harvester` | domain             | binaire `theHarvester`                |
| `subfinder`     | domain             | binaire `subfinder`                   |
| `amass`         | domain             | binaire `amass`                       |
| `gosearch`      | username           | binaire `gosearch`                    |
| `httpx_probe`   | domain             | binaire `httpx` (projectdiscovery)    |

Les wrappers absents retournent `TOOL_NOT_INSTALLED` au lieu d'échouer — la
mission continue avec ce qui est disponible.

## Architecture

- **Clean Architecture** côté backend (`domain` / `application` /
  `infrastructure` / `presentation`).
- **OsintModule ABC** exposé par le backend ; `omega_orchestrator` est un
  module qui délègue à `osint_omega.Engine`.
- **Cache SQLite** (`data/cache.db`, TTL 24 h par défaut).
- **Audit trail** : chaque exécution émet un `AuditEvent` (acteur, scope,
  module, paramètres, issue).
- **Éthique by design** : voir [`ETHICS.md`](ETHICS.md).

## Tests

```bash
cd osint_omega && pytest
cd backend && pytest
```

## Prototype historique

Le prototype `index.html` (neural graph Cytoscape) est archivé sous
`docs/prototype/` pour référence.

## Licence

À définir (voir `LICENSE` à ajouter).
