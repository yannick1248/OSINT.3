# OSINT OMÉGA — Backend

FastAPI + Clean Architecture.

## Layout

```
app/
  domain/          # Entités, interfaces, règles métier pures
  application/     # Use cases, orchestration
  infrastructure/  # Adapters concrets (DB, modules OSINT, clients HTTP)
  presentation/    # FastAPI routers, schémas de requête/réponse
```

## Commandes

```bash
pip install -e ".[dev]"
uvicorn app.presentation.main:app --reload
pytest
ruff check .
mypy app
```
