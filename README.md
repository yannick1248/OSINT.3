# OSINT.3

Service de l’information mondiale — backend OSINT Omega AI pour enquêtes auditées.

## Livrables principaux

- Interface de domaine `OsintModule` avec `Finding`, `OsintResult` et niveaux de confiance normalisés.
- 9 plugins dans `infrastructure/plugins/` : WhatsMyName, Holehe, Intelligence X, HIBP, Telegram, InsightFace, EyeOfWeb, Wayback Machine et Ahmia.
- Pipeline `MissingPersonPipeline` avec exécution concurrente, fiche entité, résultats normalisés et audit trail obligatoire.
- API FastAPI exposant `/`, `/health`, `/api/v1/modules`, `/api/v1/modules/run`, `/api/v1/investigate/missing-person` et `/api/v1/investigate/general`.
- Interface graphique Web responsive servie à la racine `/`, avec formulaire d’enquête, inventaire des modules et visualisation des résultats/audits.
- Infrastructure Docker Compose : API, worker, PostgreSQL, Redis, Elasticsearch, EyeOfWeb, Milvus, Prometheus et Grafana.

## Démarrage rapide

```bash
cp .env.example .env
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Ouvrir ensuite `http://localhost:8000/` pour utiliser la console Web. Voir [`docs/INTEGRATION.md`](docs/INTEGRATION.md) pour les variables d’environnement, l’authentification Telegram et les exemples `curl`.
