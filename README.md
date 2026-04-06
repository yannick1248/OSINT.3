# OSINT.3

Cadre d’investigation OSINT orienté **agents**, **nœuds** et **réseaux** pour produire des analyses robustes par recroisement systématique.

## 1) Audit complet de l’existant

### Constat
- Dépôt initialement quasi vide (pas d’architecture, pas de protocole d’exécution).
- Aucune cartographie d’API, de dépendances, de blocs de code ou d’outils.
- Aucun mécanisme d’autocorrection/autotest.

### Risques
- Conclusions non traçables.
- Dépendances cachées et attaques de supply chain non détectées.
- Couverture d’investigation incomplète.

### Exigence projet
Implémenter un standard **structuré, synthétique, fonctionnel, exigeant, professionnel**, avec boucle d’**autocorrection** et d’**autotest**.

---

## 2) Modèle conceptuel normatif (obligatoire)

### Définitions
- **Option** : hypothèse, piste, action ou décision candidate.
- **Nœud** : unité élémentaire de connaissance/action.
- **Agent** : entité autonome de collecte/analyse/contrôle.
- **Réseau de neurones opérationnel** : groupe de 3 nœuds minimum.
- **Réseau d’agents** : groupe de 3 agents minimum.

### Règles de composition
1. **Toute option est un nœud.**
2. **Tout agent crée des nœuds et des options après consultation des autres agents.**
3. **Tout groupe de plus de 2 neurones (nœuds) est un nœud composite et un réseau de neurones.**
4. **Tout réseau de neurones crée des agents spécialisés.**
5. **Tout groupe de plus de 2 agents est un réseau d’agents et un nœud de coordination.**

Objectif: maximiser le recroisement multi-niveaux (option ↔ nœud ↔ agent ↔ réseau).

---

## 3) Workflow d’investigation exigeant

1. **Cadrage** : objectif, périmètre, contraintes légales/éthiques, horizon temporel.
2. **Exploration multi-agents** : collecte parallèle, consultation croisée obligatoire.
3. **Recroisement** : matrice `source x affirmation x agent x confiance`.
4. **Contre-enquête** : réfutation active des hypothèses centrales.
5. **Décision** : priorisation impact/coût/risque/délai/confiance.
6. **Capitalisation** : archivage des patterns et erreurs.

---

## 4) Demande de toutes les API (cadre de recherche)

### 4.1 Typologie des API à inventorier
- **API OSINT générales** : moteurs, actualités, archives web, WHOIS/RDAP.
- **API réseaux sociaux** (selon conformité légale et TOS).
- **API géospatiales** : géocodage, cartographie, imagerie satellite.
- **API cybersécurité** : IOC, réputation IP/domaines, vulnérabilités.
- **API données publiques** : open data nationaux, statistiques officielles.
- **API internes** : services maison, SIEM, data-lake, bus événementiel.

### 4.2 Fiche standard API (obligatoire)
Pour chaque API:
- Nom / propriétaire / URL / version.
- Méthodes et endpoints.
- Authentification (clé, OAuth2, mTLS).
- Quotas, latence, SLA, coût.
- Formats (JSON/CSV/XML), pagination, limites.
- Données sensibles traitées (PII, géolocalisation, etc.).
- Journalisation, conformité, dépendances transverses.

### 4.3 Score de criticité API
`Criticité = Impact métier x Sensibilité données x Risque indisponibilité x Coût`.

---

## 5) Recherche de toute dépendance possible

### 5.1 Dépendances techniques
- **Runtime** (Python/Node/Go/Rust/JVM, etc.).
- **Packages directs** (requirements.txt, package.json, Cargo.toml, etc.).
- **Transitives** (arbre complet + versions verrouillées).
- **Système** (binaires Linux, bibliothèques dynamiques, services externes).
- **Infra** (DB, cache, files, observabilité, IAM).

### 5.2 Commandes Linux de base (audit dépendances)
```bash
# Python
pip freeze

# Node
npm ls --all

# Rust
cargo tree

# Binaire + libs dynamiques
ldd <binary>

# Processus et sockets
ps aux
ss -tulpen
```

### 5.3 Contrôles sécurité
- Inventaire SBOM.
- CVE connues par version.
- Politique de mise à jour et rollback.

---

## 6) Recherche de tous les blocs possibles de code

### 6.1 Classification des blocs
- Acquisition/collecte.
- Normalisation/nettoyage.
- Corrélation/fusion.
- Scoring/prise de décision.
- Export/reporting.
- QA/autotest.

### 6.2 Méthode de découverte rapide
```bash
# Lister les fichiers code
rg --files

# Repérer les points d’entrée
rg "main\(|if __name__ == '__main__'|cli|argparse|click|cobra|commander"

# Repérer appels API/HTTP
rg "requests\.|httpx\.|fetch\(|axios|curl|urllib|aiohttp"

# Repérer SQL/stockage
rg "SELECT |INSERT |UPDATE |DELETE |sqlite|postgres|mysql|redis"
```

### 6.3 Matrice bloc ↔ dépendance ↔ API
Chaque bloc doit référencer:
- dépendances utilisées,
- API consommées,
- données d’entrée/sortie,
- risque et niveau de test.

---

## 7) Recherche de toutes les données statistiques

### 7.1 Familles de statistiques
- Volumétrie sources (par type et période).
- Taux de corroboration inter-sources.
- Taux de contradiction et temps de résolution.
- Latence par API et coût unitaire.
- Précision des hypothèses (validées/rejetées/incertaines).

### 7.2 KPIs minimum
- **Coverage Score**: % conclusions avec >=2 sources indépendantes.
- **Contradiction Handling Time**: délai moyen d’arbitrage.
- **Confidence Drift**: variation moyenne des scores après autocorrection.
- **API Reliability**: disponibilité/erreur/timeout.

### 7.3 Format statistique recommandé
- Table temporelle journalière.
- Agrégations hebdo/mensuelles.
- Tableau de bord décisionnel avec seuils d’alerte.

---

## 8) Outils d’investigation Linux disponibles (catalogue de référence)

### 8.1 Réseau & renseignement technique
- `whois`, `dig`, `nslookup`, `host`, `curl`, `wget`, `nmap`, `amass`, `theHarvester`.

### 8.2 Analyse web & contenu
- `lynx`, `jq`, `htmlq`, `wget --mirror`, `waybackpack`.

### 8.3 Forensic & metadata
- `exiftool`, `binwalk`, `strings`, `file`, `xxd`, `pdfinfo`.

### 8.4 Système & corrélation
- `rg`, `fd`, `find`, `awk`, `sed`, `sort`, `uniq`, `comm`, `parallel`.

### 8.5 Vérification sécurité
- `trivy`, `grype`, `syft`, `gitleaks`, `semgrep`.

> Note: utiliser uniquement les outils autorisés par la politique légale/contractuelle locale.

---

## 9) Protocole d’autocorrection

- Double validation par agents distincts sur chaque assertion critique.
- Journal d’erreurs (source faible, biais, datation, surinterprétation).
- Recalcul des scores de confiance après correction.
- Blocage automatique de conclusion si contradiction non arbitrée.

---

## 10) Protocole d’autotest (gate qualité)

### Tests critiques
1. Couverture: conclusion liée à >=2 sources.
2. Contradiction: au moins une tentative de réfutation par hypothèse clé.
3. Traçabilité: décision reliée à ses nœuds et agents contributifs.
4. Robustesse: retrait d’une source majeure sans effondrement complet.
5. Fraîcheur: date de validité explicite pour données volatiles.

### Statut
- **PASS**: tous tests critiques OK.
- **WARN**: 1 test non critique KO.
- **FAIL**: 1 test critique KO (publication interdite).

---

## 11) Plan d’implémentation immédiat

- [ ] Créer un schéma `node/agent/network/option` en JSON/YAML.
- [ ] Ajouter un registre `apis.yaml` et un registre `dependencies.yaml`.
- [ ] Générer une matrice automatique `blocks x deps x apis`.
- [ ] Mettre en place un pipeline d’autotest en CI.
- [ ] Publier un tableau de bord statistique versionné.

