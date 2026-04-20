# Prompts multi-agent forensiques

`system_prompt.xml` est le prompt système à injecter dans un LLM (Claude,
GPT, etc.) agissant comme **OMEGA_ORCHESTRATOR**. Il impose :

- une gouvernance de périmètre (SANDBOX_TEST / OWNED_ASSETS /
  CLIENT_AUTHORIZED_SCOPE / PUBLIC_INTEREST_RESEARCH / INTERNAL_AUDIT /
  LEGALLY_RESTRICTED),
- un modèle de confiance 4 niveaux (VERY_HIGH / HIGH / MEDIUM / LOW) aligné
  avec `osint_omega.types.Confidence`,
- un pipeline en 7 étapes (QUALIFY_REQUEST → REPORT),
- des règles forensiques (séparation faits / inférences / hypothèses),
- un protocole de sortie structuré,
- des garde-fous de sécurité (refus de doxxing, stalking, surveillance non
  mandatée, etc.).

## Chargement programmatique

```python
from osint_omega.agents import load_system_prompt

system_prompt = load_system_prompt()
# → à passer comme `system` à l'API Claude / OpenAI
```

Le moteur `osint_omega.engine.Engine` incarne côté code les gates et le modèle
de confiance décrits ici ; le prompt fournit la couche raisonnement.
