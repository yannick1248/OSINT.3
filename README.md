# OSINT.3
Service de l’information mondiale

## Vision produit : CRM/IDE d’investigation humain ↔ machine

Objectif : créer un **cockpit unifié** où un analyste humain et des agents machine coopèrent en temps réel pour la recherche, l’enquête et la qualification des signaux critiques.

### 1) Architecture de symbiose (synergie complète)

- **Fenêtre Humaine (IDE)** : éditeur de requêtes, notes d’enquête, chronologie, et panneau d’hypothèses.
- **Fenêtre Machine (CRM IA)** : agents spécialisés (collecte, recoupement, scoring de fiabilité, résumé).
- **Bus d’orchestration** : toute action machine est traçable, rejouable, et validable par l’humain.
- **Mémoire de cas (CRM)** : contacts, entités, événements, pièces, liens, statut, actions suivantes.

### 2) Modules clés du CRM/IDE

1. **Intake multi-source**
   - Email, documents, exports CSV, API, transcriptions.
2. **Graph d’enquête**
   - Personnes, organisations, lieux, transactions, horodatage.
3. **Copilote de recherche**
   - Propose pistes, contre-hypothèses, manques de preuves.
4. **Salle de décision**
   - Validation humaine obligatoire avant publication/escalade.
5. **Audit & conformité**
   - Journal signé, versionné, avec chaîne de responsabilité.

### 3) Boucle opérationnelle humain-machine

1. L’humain formule une question d’enquête.
2. La machine collecte et structure les indices.
3. L’humain corrige, invalide ou confirme.
4. La machine raffine la recherche et met à jour le score de confiance.
5. Le système produit un rapport vérifiable avec sources, limites et recommandations.

### 4) Principes de sûreté

- **Vérifiable avant action** : pas de conclusion sans preuve liée.
- **Humain dans la boucle** : l’IA assiste, ne décide pas seule.
- **Mode dégradé hors-ligne** : continuité locale si réseau indisponible.
- **Séparation des rôles** : collecte, analyse, validation, décision.

### 5) MVP recommandé

- Frontend : TypeScript + Vite
- Data locale : IndexedDB + chiffrement AES-GCM
- Orchestration : workers agents + file d’événements
- Visualisation : timeline + graphe + workspace de preuves
- Qualité : tests unitaires (moteur), e2e (workflow analyste)

### 6) Résultat attendu

Un **CRM/IDE d’investigation** qui augmente la capacité humaine : plus rapide, plus traçable, plus robuste, sans perdre l’esprit critique ni la responsabilité.
