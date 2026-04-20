# OSINT OMÉGA AI

Plateforme d'investigation OSINT (Open-Source Intelligence) modulaire,
extensible et self-hostable, à destination des journalistes d'investigation,
enquêteurs agréés, équipes de cybersécurité et chercheurs académiques.

> **Usage légal et éthique uniquement.** Chaque module affiche un
> avertissement et journalise les requêtes pour audit trail.

## Architecture

- **Backend** — Python 3.12+, FastAPI (async), SQLAlchemy 2.0, Pydantic v2,
  Celery + Redis, PostgreSQL, Elasticsearch. Clean Architecture stricte :
  `domain` / `application` / `infrastructure` / `presentation`.
- **Frontend** — Next.js 15 (App Router), TypeScript strict, Tailwind CSS +
  shadcn/ui, Zustand, React Query, Cytoscape.js (graphes), Leaflet.js (carto),
  Recharts.
- **Infra** — Docker Compose (dev), manifests Kubernetes (prod), Nginx,
  Prometheus + Grafana, GitHub Actions.

## Modules OSINT

Chaque module implémente l'interface `OsintModule` (voir
`backend/app/domain/modules/base.py`). Un module d'exemple
(`DomainLookupModule`) est fourni sous
`backend/app/infrastructure/modules/domain_lookup.py`.

## Démarrage rapide

```bash
cp .env.example .env
docker compose up --build
```

- API : http://localhost:8000 (docs : `/docs`)
- Frontend : http://localhost:3000

## Développement

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest

# Frontend
cd frontend
npm install
npm run dev
```

## Prototype historique

Le prototype initial (neural graph Cytoscape) est archivé sous
`docs/prototype/` pour référence.

## Licence

À définir. Voir `LICENSE` (à ajouter).
