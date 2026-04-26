# État de l’art 2026 — API & outils d’accès légal au « web profond » (juridique/gouvernemental vs OSINT)

> **Note préalable** : la ressource indiquée est `"[LIEN]"` (placeholder), sans URL exploitable. Je ne peux donc pas extraire *les outils cités dans cette ressource précise*. Le présent livrable est une synthèse opérationnelle **améliorée** fondée sur des sources officielles et l’état du marché en avril 2026.

## 1) Tri juridique — registres/API officiels qui cassent les verrous d’accès

### 1.1 Entreprises, bénéficiaires effectifs, identité légale

| Outil/API | URL | Déverrouille quoi (difficile d’accès) | Usage avancé | Coût |
|---|---|---|---|---|
| **OpenCorporates API** | https://api.opencorporates.com/documentation/API-Reference | Registres d’entreprises multi-juridictions, souvent fragmentés par pays/interface | Détection de structures en chaîne (multi-pays), recoupée avec sanctions et litiges | Freemium + plans payants |
| **GLEIF LEI API** | https://www.gleif.org/lei-data/gleif-lei-look-up-api/access-the-api | Entités légales globales (LEI), liens de propriété directs/ultimes (Level 2) | Résolution d’identité cross-border (LEI ↔ ISIN/BIC quand mappé) pour KYC/KYB | Gratuit |
| **Companies House API (UK)** | https://developer.company-information.service.gov.uk/overview/ | Données sociétés UK via API au lieu d’UI/formulaires web | Monitoring événementiel (changement dirigeants, PSC) + alerting | Gratuit (clé API) |
| **BORIS (UE, interconnexion BO)** | https://e-justice.europa.eu/topics/registers-business-insolvency-land/beneficial-ownership-registers-interconnection-system-boris_en | Interconnexion des registres bénéficiaires effectifs nationaux (accès variable selon base légale) | Requête transfrontalière ciblée sur UBO dans analyses AML | Accès dépend pays/règles |
| **OpenOwnership Register** | https://www.openownership.org/en/ | Données BO consolidées open-data (zones couvertes) | Pré-filtrage de cibles avant requêtes officielles nationales | Gratuit |

### 1.2 Jurisprudence, dossiers judiciaires, législation

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **CourtListener REST API** | https://www.courtlistener.com/help/api/rest/ | Opinions, dockets, métadonnées judiciaires US en API | Graphe de citations + alerte sur nouveaux filings par partie/juge | Gratuit (quota) |
| **RECAP (CourtListener/PACER bridge)** | https://www.courtlistener.com/help/api/rest/recap/ | Une partie des docs PACER (sinon payants/peu accessibles) | Réduction coût PACER via mutualisation RECAP + enrichissement pipeline litige | Mixte (selon cas) |
| **Légifrance API (PISTE)** | https://www.data.gouv.fr/dataservices/legifrance | Jurisprudence, codes, textes consolidés FR en accès machine | Veille réglementaire FR automatisée par thème + diff temporel | Gratuit (inscription) |
| **EUR-Lex / CELLAR (web services)** | https://eur-lex.europa.eu/content/help/data-reuse/reuse-contents-eurlex-details.html | Corpus législatif UE (métadonnées + extraction machine-readable) | Pipeline de conformité UE (règlements/directives + historique versions) | Gratuit |
| **SEC EDGAR APIs (data.sec.gov)** | https://www.sec.gov/edgar/sec-api-documentation | Dépôts réglementaires US (10-K/10-Q/8-K etc.) via JSON | Détection signaux faibles (risques, contentieux, related parties) en NLP | Gratuit |

### 1.3 Sanctions, listes de surveillance, export controls

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **OFAC Sanctions List Service (SLS)** | https://ofac.treasury.gov/sanctions-list-service | Listes OFAC à jour + endpoints de récupération | Screening incrémental quotidien avec hash checking des fichiers | Gratuit |
| **UK Sanctions List (source unique depuis 28/01/2026)** | https://www.gov.uk/government/publications/the-uk-sanctions-list | Liste UK unifiée (individus/entités/navires) | Migration des moteurs de filtrage OFSI Group ID → UKSL Unique ID | Gratuit |
| **OpenSanctions API** | https://api.opensanctions.org/ | Agrégation sanctions/PEP/watchlists multi-sources | Normalisation d’alias + translittérations pour fuzzy matching mondial | Freemium / payant |

---

## 2) Tri OSINT — API/techniques pour données ouvertes non indexées

### 2.1 IoT / Surface d’exposition Internet

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **Shodan API** | https://developer.shodan.io/api | Services exposés, bannières, ports, métadonnées devices | Attack-surface mapping d’un groupe + dérive de config dans le temps | Freemium / payant |
| **Censys Platform API** | https://docs.censys.com/docs/platform-api | Inventaire certs/TLS/services, recherche Internet-wide | Pivot certif TLS → infrastructures liées (hébergement, clones, phishing) | Freemium / payant |
| **ZoomEye API** | https://www.zoomeye.hk/doc | Exposition cyber globale (alternative asiatique) | Cross-validation de découverte d’actifs hors couverture occidentale | Freemium / payant |

### 2.2 Maritime / Aérien / mobilité

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **OpenSky API** | https://opensky-network.org/data/api | Traces ADS-B ouvertes (recherche/non-commercial) | Corrélation vols atypiques ↔ événements corporate/géopolitiques | Gratuit (limites) |
| **ADS-B Exchange API** | https://www.adsbexchange.com/products/enterprise-api/ | Données vol très granulaires, faible latence | Détection pattern de flotte (business jets, routes récurrentes) | Payant (Enterprise) |
| **MarineTraffic API** | https://servicedocs.marinetraffic.com/ | AIS navires (positions, voyages, escales) | Détection transbordement suspect via gap AIS + escales corrélées | Payant |
| **AISHub** | https://www.aishub.net/api | Flux AIS communautaires | Enrichissement low-cost en complément fournisseurs premium | Gratuit / freemium |

### 2.3 Leaks, breaches, traces publiques difficiles

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **Have I Been Pwned API v3** | https://haveibeenpwned.com/API/v3 | Exposition comptes/domaines dans violations publiques | Due diligence cyber d’un domaine avant M&A / onboarding fournisseur | Payant (API key) |
| **AlienVault OTX API** | https://otx.alienvault.com/api | IoCs et pulses communautaires | Pivot IOC → campagnes apparentées (enrichissement CTI) | Gratuit |
| **Wayback CDX API** | https://archive.org/help/wayback_api.php | Historique web non indexé actuel | Preuve d’antériorité (pages supprimées, mentions légales modifiées) | Gratuit |

### 2.4 Réseaux sociaux & graphes ouverts

| Outil/API | URL | Déverrouille quoi | Usage avancé | Coût |
|---|---|---|---|---|
| **Wikidata SPARQL** | https://query.wikidata.org/sparql | Graphe entités/relations, multi-langues | Résolution d’entités + alias multilingues avant matching juridique | Gratuit |
| **CrowdTangle (historique)** | https://www.crowdtangle.com/ | Données publiques FB/IG (accès restreint selon éligibilité) | Analyse propagation narrative par pages/groupes | Limité / sur dossier |
| **Social Links API** | https://social-link.net/api-documentation | Agrégation profils sociaux/messageries | Enquête KYC renforcée (traces publiques corrélées) | Payant |

---

## 3) Croisements puissants (playbooks pratiques)

### Playbook A — « KYB investigatif » entreprise à risque
1. **OpenCorporates + GLEIF + registre national** pour identité légale robuste.
2. **OpenSanctions/OFAC/UKSL** pour screening sanctions des entités et dirigeants.
3. **CourtListener + EDGAR** pour litiges et signaux réglementaires.
4. **Shodan/Censys/HIBP** pour posture cyber et incidents d’exposition.
5. Score composite (juridique + cyber + réputation) dans un graphe (Neo4j/Maltego).

### Playbook B — « Navire/avion → société → bénéficiaire effectif »
1. Identifiant mobile (IMO/MMSI/hex ICAO) via **MarineTraffic/OpenSky/ADSBx**.
2. Lien opérateur/owner (registre maritime/aérien + OpenCorporates).
3. Mapping des dirigeants/UBO (GLEIF, BO registers, sources nationales).
4. Contrôle sanctions et contentieux.

### Playbook C — « Preuve d’antériorité réglementaire »
1. Snapshot historique via **Wayback CDX**.
2. Texte officiel via **EUR-Lex/Légifrance** (versioning).
3. Dossier probant horodaté (hash + PDF + URL source).

### Outils d’agrégation/relation utiles
- **Maltego** (transforms & link analysis): https://www.maltego.com/
- **SpiderFoot** (automatisation OSINT): https://www.spiderfoot.net/
- **MISP** (partage IoC): https://www.misp-project.org/
- **Neo4j + scripts Python** (matching entités, score de confiance).

---

## 4) Points d’attention juridiques (strictement légal vs zone grise)

### Clairement légal (si respect des CGU + lois locales)
- Requêtes via API officielles/documentées.
- Données open-data/public records sans contournement technique.
- Archiver des pages publiques (Wayback) sans intrusion.
- Matching/fuzzy sous base légitime (compliance, anti-fraude, intérêt légitime documenté).

### Zone grise / à encadrer fortement
- **Contournement actif** de paywall, CAPTCHA, géoblocage ou restrictions contractuelles.
- Scraping agressif malgré interdiction explicite (ToS, robots, clauses anti-automatisation).
- Ré-identification de personnes à partir de datasets pseudo-anonymisés.
- Croisement massif pouvant produire profilage sensible sans base légale (RGPD/LPD/CCPA selon juridiction).

### Risques juridiques récurrents
- Violation contractuelle (ToS/API terms) même si donnée « publique ».
- Protection des bases de données (UE), droit d’auteur sur structuration/annotation.
- Données personnelles sensibles, transferts transfrontaliers, conservation excessive.

---

## 5) Limites actuelles & axes de recherche à creuser

### Limites
- Fragmentation mondiale des registres BO (accès hétérogène, parfois restreint).
- Qualité variable des entités (alias, translittération, homonymie).
- Coûts élevés pour données premium (maritime, social, due diligence enrichie).
- Dépendance aux quotas/rate limits et à la stabilité des APIs.

### Axes de recherche prioritaires
1. **Entity Resolution avancée** : modèles probabilistes + graph matching supervisé.
2. **Traçabilité juridique** : logs de collecte, preuve d’intégrité (hash, horodatage qualifié).
3. **OSINT multimodal** : corrélation texte + mobilité + cyber + documents légaux.
4. **Veille sanctions temps réel** : pipelines événementiels (webhooks, diff de listes).
5. **Conformité by-design** : minimisation, séparation PII, politiques de rétention.

---

## Perplexity Power Play

Copie/colle ces prompts dans Perplexity pour prolonger efficacement ta recherche :

1. **Sanctions quotidiennes**
   - « Liste-moi les mises à jour OFAC et UK Sanctions List des 7 derniers jours, avec liens officiels et IDs des entrées modifiées. »
2. **Due diligence entreprise**
   - « Fais un profil KYB de *[Entreprise X]* : registre officiel, dirigeants, UBO, litiges, sanctions, incidents cyber, avec sources primaires uniquement. »
3. **Réglementaire UE/FR**
   - « Donne-moi les textes EUR-Lex et Légifrance applicables à *[secteur]*, version en vigueur + modifications depuis 24 mois. »
4. **SEC ciblé**
   - « Récupère les derniers 8-K/10-K/10-Q de *[Company]* via data.sec.gov et signale les passages risque/contenieux/changement gouvernance. »
5. **Maritime/aérien investigatif**
   - « Pour IMO *[numéro]* et hex ICAO *[code]*, donne trajectoires, opérateurs, liens corporate et éventuelles correspondances sanctions. »
6. **Validation juridique collecte**
   - « Classe mes sources (API X, scraping Y, archive Z) en ‘légal clair / à valider / zone grise’ avec justification RGPD + ToS + droit des bases. »
7. **Plan technique prêt-prod**
   - « Conçois une architecture OSINT/KYB legal-safe (ETL, entity resolution, scoring, audit log, retention), avec stack open-source et coûts mensuels estimés. »

---

## Mini-checklist opérationnelle (48h)

- Construire une **matrice sources** (officielles vs OSINT) avec base légale et ToS.
- Implémenter 3 connecteurs robustes : **EDGAR**, **OFAC/UKSL**, **OpenCorporates/GLEIF**.
- Monter un graphe entités minimal (société, personne, navire, avion, sanction, litige).
- Ajouter scoring confiance + piste d’audit (qui/quoi/quand/source).
- Documenter un protocole « stop/go juridique » avant toute extension scraping.
