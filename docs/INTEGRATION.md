# OSINT Omega AI Backend — Integration Guide

This backend exposes a normalized plugin interface and a concurrent missing-person
pipeline. Every investigation request must include `legal_basis` and `requestor_id`;
requests without those audit fields are rejected before plugins run.

## Local start

```bash
cp .env.example .env
uvicorn app.main:app --reload
```

Or with the full stack:

```bash
docker compose up --build
```

The compose file starts the API, Celery worker, PostgreSQL, Redis, Elasticsearch,
EyeOfWeb, Milvus, Prometheus, and Grafana.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/api/v1/modules` | Lists modules, inputs, and required environment variables |
| `POST` | `/api/v1/modules/run` | Runs a single plugin |
| `POST` | `/api/v1/investigate/missing-person` | Runs the concurrent missing-person pipeline |
| `POST` | `/api/v1/investigate/general` | Runs the same audited pipeline for general cases |

## Example missing-person investigation

```bash
curl -sS http://localhost:8000/api/v1/investigate/missing-person \
  -H 'content-type: application/json' \
  -d '{
    "requestor_id": "case-worker-17",
    "legal_basis": "missing_person_report_2026-001",
    "name": "Jane Doe",
    "email": "jane@example.org",
    "phone": "+41790000000",
    "username": "janedoe",
    "domain": "example.org"
  }'
```

## Run one module

```bash
curl -sS http://localhost:8000/api/v1/modules/run \
  -H 'content-type: application/json' \
  -d '{
    "module": "wayback",
    "requestor_id": "case-worker-17",
    "legal_basis": "missing_person_report_2026-001",
    "domain": "example.org"
  }'
```

## Telegram authentication

1. Create an application at `my.telegram.org` and copy `api_id` and `api_hash`.
2. Set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` in `.env`.
3. Run a local request once from a trusted terminal; Telethon will create the session
   file and may prompt for the phone login code.
4. Keep the generated session file encrypted and restricted to authorized operators.

## Environment variables

| Variable | Required by | Description |
|---|---|---|
| `HIBP_API_KEY` | `hibp` | Have I Been Pwned API key |
| `INTELX_API_KEY` | `intelx` | Intelligence X API key |
| `TELEGRAM_API_ID` | `telegram` | Telegram application ID |
| `TELEGRAM_API_HASH` | `telegram` | Telegram application hash |
| `EYEOFWEB_URL` | `eyeofweb` | Self-hosted facial-search endpoint |
| `DATABASE_URL` | API/worker | PostgreSQL connection string |
| `REDIS_URL` | worker | Redis broker/result backend |
| `ELASTICSEARCH_URL` | indexing | Elasticsearch endpoint |
| `MILVUS_HOST` / `MILVUS_PORT` | embeddings | Milvus vector database |

## Operational notes

- Plugins that lack inputs or API keys return skipped results instead of crashing the
  investigation.
- Network or provider failures are isolated per plugin and recorded in the result
  envelope.
- Facial embeddings and image paths should be treated as sensitive biometric data.
- The audit trail is returned with every investigation and should be persisted by the
  calling case-management system.
