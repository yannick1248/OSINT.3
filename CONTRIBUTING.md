# Contribuer à OSINT OMÉGA AI

## Règles d'or

1. **Clean Architecture** : pas d'import du bas vers le haut. `domain` ne
   dépend de rien ; `application` dépend de `domain` ; `infrastructure` et
   `presentation` dépendent de `application` et `domain`.
2. **TDD** : chaque fonction métier est couverte par un test unitaire.
   `pytest --cov=app` doit rester vert et la couverture ne doit pas régresser.
3. **Sécurité** : aucune clé ni secret dans le code. Toute valeur sensible
   passe par une variable d'environnement documentée dans `.env.example`.
4. **Éthique** : tout nouveau module OSINT journalise ses exécutions via
   le sink d'audit (`AuditSink`) et porte un `description` explicite.

## Ajouter un module OSINT

1. Créer le module sous `backend/app/infrastructure/modules/<name>.py` en
   étendant `OsintModule[TParams, TOutput]`.
2. Déclarer `name`, `description`, `input_schema`, `output_schema`.
3. Implémenter `validate_input` et `execute`.
4. Enregistrer le module dans `build_default_registry()`
   (`backend/app/infrastructure/modules/__init__.py`).
5. Ajouter des tests sous `backend/tests/test_<name>.py`.

Un gabarit minimal :

```python
from typing import ClassVar
from pydantic import BaseModel
from app.domain.modules.base import (
    ConfidenceLevel, OsintModule, OsintResult, OsintResultStatus,
)

class MyParams(BaseModel):
    query: str

class MyOutput(BaseModel):
    hits: list[str]

class MyModule(OsintModule[MyParams, MyOutput]):
    name: ClassVar[str] = "my_module"
    description: ClassVar[str] = "Décrit ce que fait le module."
    input_schema: ClassVar[type[BaseModel]] = MyParams
    output_schema: ClassVar[type[BaseModel]] = MyOutput

    async def validate_input(self, params: MyParams) -> bool:
        return bool(params.query.strip())

    async def execute(self, params: MyParams) -> OsintResult[MyOutput]:
        data = MyOutput(hits=[])
        return OsintResult[MyOutput](
            module=self.name,
            status=OsintResultStatus.SUCCESS,
            confidence=ConfidenceLevel.MEDIUM,
            data=data,
        )
```

## Commandes utiles

```bash
# Backend
cd backend && pytest && ruff check .

# Frontend
cd frontend && npm run type-check && npm run build

# Stack complète
docker compose up --build
```
