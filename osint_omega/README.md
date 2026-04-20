# osint_omega

Orchestrateur OSINT modulaire, à usage **légal et éthique**.

Une requête → le moteur choisit les meilleurs outils pour la cible, les exécute
en parallèle (asyncio), met les résultats en cache (SQLite), puis retourne un
JSON normalisé (`ToolResult`). Le prompt multi-agent forensique est fourni sous
`osint_omega/agents/system_prompt.xml` pour alimenter un orchestrateur LLM en
amont.

## Installation

```bash
pip install -e ./osint_omega
```

Outils binaires externes (optionnels) : voir `install.sh` à la racine du dépôt.
Chaque wrapper détecte l'absence de son binaire et le signale proprement
(`status=tool_not_installed`) au lieu d'échouer.

## Utilisation

```bash
# CLI
python -m osint_omega --target example.com --type domain
python -m osint_omega --target alice@example.com --type email --scope OWNED_ASSETS
python -m osint_omega --target "john_doe" --type username --module reconnaissance

# Depuis Python
import asyncio
from osint_omega import Engine
from osint_omega.types import Scope, Target, TargetType

async def main():
    engine = Engine()
    mission = await engine.run(
        Target(value="example.com", type=TargetType.DOMAIN),
        scope=Scope.OWNED_ASSETS,
    )
    print(mission.model_dump_json(indent=2))

asyncio.run(main())
```

## Architecture

- `types.py` — modèles Pydantic (`Target`, `ToolResult`, `Mission`, `Scope`,
  `Confidence`).
- `cache.py` — cache SQLite avec TTL configurable.
- `gate.py` — `LegalEthicsGate` : valide le périmètre avant toute collecte.
- `engine.py` — sélection des outils par type de cible + exécution parallèle.
- `tools/` — wrappers (locaux, API, ou binaires externes via subprocess).
- `agents/` — prompts multi-agent forensiques réutilisables.

## Outils exposés (état actuel)

| Nom              | Type          | Fonctionne sans binaire externe |
|------------------|---------------|---------------------------------|
| `domain_syntax`  | local         | oui                             |
| `crtsh`          | API           | oui (HTTP vers crt.sh)          |
| `hibp`           | API (clé)     | oui si `HIBP_API_KEY`           |
| `maigret`        | CLI externe   | détecte / skippe si absent      |
| `holehe`         | CLI externe   | détecte / skippe si absent      |
| `the_harvester`  | CLI externe   | détecte / skippe si absent      |
| `subfinder`      | CLI externe   | détecte / skippe si absent      |
| `amass`          | CLI externe   | détecte / skippe si absent      |
| `gosearch`       | CLI externe   | détecte / skippe si absent      |
| `httpx_probe`    | CLI externe   | détecte / skippe si absent      |
