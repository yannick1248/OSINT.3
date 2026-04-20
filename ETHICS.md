# Charte éthique et légale

OSINT OMÉGA AI est conçu pour l'investigation **légale et éthique**. En
utilisant ou en contribuant à ce projet, vous vous engagez à respecter les
principes suivants.

## Cadre d'usage autorisé

- Journalisme d'investigation
- Enquêtes privées agréées dans le cadre légal applicable
- Équipes cybersécurité défensive (blue team, threat intel, IR)
- Recherche académique
- Forces de l'ordre dans le cadre de procédures légales

## Interdits

- Harcèlement, doxing, stalking ou intimidation
- Collecte de données sur mineurs hors cadre judiciaire explicite
- Contournement de mesures techniques de protection
- Usage offensif (intrusion, exfiltration, sabotage)
- Toute activité violant le RGPD, le CCPA ou les lois locales applicables

## Garanties techniques

- **Audit trail** : chaque exécution de module émet un `AuditEvent`
  (acteur, module, paramètres, issue) via `AuditSink`.
- **Disclaimer UI** : chaque vue d'investigation affiche un rappel légal.
- **Scopes/RBAC** : analyst / investigator / admin, limitant les actions
  destructrices ou sensibles.
- **Pas de stockage de secrets** : toutes les clés API passent par
  l'environnement, jamais par le dépôt.

## Signaler un abus

Ouvrir une issue privée ou contacter les mainteneurs. Les modules
malveillants ou manifestement offensifs seront refusés et retirés.
