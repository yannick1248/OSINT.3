# Synthèse opérationnelle — Service SMS « 939 GE », listes AVS CdC, APIs juridiques/OSINT (mise à jour 29 avril 2026)

## Cadre méthodologique (8 phases OSINT)
- **Objectif**: établir l’état historique et actuel de deux dispositifs suisses (Index Auto GE et listes AVS CdC), puis proposer un workflow légal de corrélation OSINT.
- **Collecte**: prioritairement sources primaires (ge.ch, zas.admin.ch, APIs officielles), puis médias secondaires.
- **Pivots**: plaque -> détenteur (cadre légal), NAVS inactif/annulé -> réidentification via UPI.
- **Recoupement**: chaque point fort confirmé sur >=2 sources quand possible.
- **Hiérarchie de preuve**: primaire > secondaire > communautaire.
- **Confiance**: LOW/MEDIUM/HIGH par finding.
- **Tests croisés**: signalement explicite des zones paywall/archives incomplètes.
- **Output structuré**: résumé actionnable + limites + prochains pivots.

---

## PARTIE 1 — Service SMS « 939 GE »

### 1.1 Fonctionnement original (historique)
**État constaté**:
- Le service genevois permettait d’obtenir des informations de détenteur via SMS pour une plaque GE (format mentionné historiquement: « GE + numéro de plaque » vers le **939**).
- La documentation de presse historique (Le Temps 23.05.2008 + TDG/20 Minutes) confirme l’existence du service et les controverses d’usage.

**Confiance**: MEDIUM (sources médias, certaines sous paywall).

### 1.2 Raisons de restriction
- Les sources de presse de 2013 rapportent des usages abusifs (notamment dans des scénarios de vols/ciblage), ce qui a alimenté la polémique.
- Le canton a progressivement restreint l’accès pour encadrer l’usage et réduire les abus.

**Confiance**: MEDIUM.

### 1.3 État actuel (2026)
Source primaire cantonale: page officielle GE « Répertoire des détenteurs de plaques (Index Auto) ».
- L’accès SMS n’est plus grand public.
- L’accès se fait via **demande d’autorisation** (formulaire) adressée à l’OCV.
- Mention explicite: certaines lignes business ne sont pas compatibles avec les SMS surtaxés.

**Confiance**: HIGH.

### 1.4 Archives Wayback / récupération historique
- Point d’entrée demandé: `http://web.archive.org/web/*/https://www.ge.ch/repertoire-detenteurs-plaques-index-auto`
- Méthode:
  1) Lister les captures (2008–2013).
  2) Ouvrir les snapshots proches des dates de polémiques.
  3) Capturer les sections « accès », « tarif », « public visé » et mentions CGU.
- Note: des pages intermédiaires ont pu changer d’URL; pivoter via captures du domaine `ge.ch` et recherche texte interne "index auto", "SMS", "939".

**Confiance**: HIGH pour la méthode, MEDIUM pour l’exhaustivité archive sans scraping massif.

---

## PARTIE 2 — Listes AVS inactivés/annulés (CdC)

### 2.1 Page officielle analysée
- URL: https://www.zas.admin.ch/fr/numeros-inactives-ou-annules
- La CdC publie explicitement:
  - **Liste A**: NAVS inactivé + NAVS actif correspondant (2 colonnes séparées par espace).
  - **Liste B**: NAVS annulés (1 NAVS par ligne).

### 2.2 URL exactes des fichiers
Les liens directs sont dynamiques sur la page, mais les artefacts sont publiés sous ces noms:
- `NAVSInact.YYYYMM` (mensuel, ZIP)
- `NAVSAnnul.YYYYMM` (mensuel, ZIP)
- archives annuelles `navsinact_YYYY`, `navsannul_YYYY`.

Exemples visibles au 29.04.2026:
- `NAVSInact.202603`, `NAVSInact.202602`, `NAVSInact.202601`
- `NAVSAnnul.202603`, `NAVSAnnul.202602`, `NAVSAnnul.202601`

Si URL directe introuvable: cliquer les liens depuis la page officielle (ou utiliser UPIServices si vous êtes utilisateur systématique reconnu).

### 2.3 Format, volumétrie, fréquence
- **Format livré**: ZIP contenant fichiers texte structurés ligne par ligne.
- **Liste A**: « ancien NAVS inactif » + « NAVS actif de référence ».
- **Liste B**: NAVS annulé seul.
- **Fréquence**: mensuelle + archives annuelles.

**Confiance**: HIGH.

### 2.4 Cadre légal (pratique)
- Accès/publication encadrés par la CdC et par le régime d’utilisation systématique du NAVS13.
- Réidentification opérationnelle: via **UPIViewer/UPIServices** pour organismes autorisés.
- Vigilance juridique: secret professionnel (art. 321 CP selon contexte métier), LPD, finalité, minimisation et traçabilité.

**Confiance**: MEDIUM-HIGH (sur principes); valider article par article avec un juriste pour cas d’usage précis.

### 2.5 Copies/miroirs
- Internet Archive: présence forte des pages CdC; vérifier snapshot par année pour versions historiques.
- Opendata.swiss: pas de preuve robuste d’un dataset miroir officiel complet de ces listes.

**Confiance**: MEDIUM.

---

## PARTIE 3 — TRI API Juridique vs OSINT (2026)

| Outil | URL | Accès | Ce que ça déverrouille | Usage avancé |
|---|---|---|---|---|
| INPI API | https://data.inpi.fr/ | freemium | entreprises FR, bénéficiaires, actes | graphe UBO + dirigeants transfrontaliers |
| OpenCorporates API | https://api.opencorporates.com/ | freemium/payant | entités multi-pays | résolution d’entités + fusions |
| Judilibre | https://www.courdecassation.fr/open-data | gratuit | jurisprudence FR | extraction de patterns de litiges |
| Pappers API | https://developers.pappers.fr/ | freemium | Kbis, dirigeants, bénéficiaires | scoring réseau sociétés-personnes |
| OpenSanctions API | https://www.opensanctions.org/ | gratuit/freemium | sanctions/PEP/entities | screening compliance multi-source |
| Wikidata SPARQL | https://query.wikidata.org/ | gratuit | graphes entités publics | pivot alias multilingue |
| Registre poursuites CH | cantonal | payant/justif. | état poursuites local | due diligence légitime |
| UPI/UPIServices | https://www.zas.admin.ch/fr/interface-upiservices | réglementé | mutations NAVS13 | correction d’identité à grande échelle légale |
| Shodan API | https://developer.shodan.io/ | payant | exposition services internet | surface d’attaque org + historique |
| Censys API | https://search.censys.io/api | freemium/payant | certificats, hosts | corrélation cert->infra->ASN |
| OpenSky API | https://opensky-network.org/ | gratuit/freemium | trafic aérien ADS-B | corrélation aéronef-opérateur |
| VesselFinder/AISHub | https://www.vesselfinder.com/ / https://www.aishub.net/ | freemium/payant | AIS maritime | suivi flotte/escales |
| Intelligence X API | https://intelx.io/ | payant | leaks, historiques web | pivot email/téléphone/doc hash |
| HIBP API | https://haveibeenpwned.com/API/v3 | payant | exposition email/domain | surveillance domaine org |
| Telegram API | https://core.telegram.org/api | gratuit (conditions) | métadonnées publiques | veille canaux/OSINT communautaire |
| Maltego | https://www.maltego.com/ | freemium/payant | graphe multi-connecteurs | chainage automatisé de pivots |

Nouveaux axes depuis 2025: renforcer la couche "entity resolution" + surveillance réglementaire (sanctions, registres nationaux, marchés publics numériques).

---

## PARTIE 4 — Croisements puissants (workflow légal)

### 4.1 Workflow nominal (nom -> adresse -> véhicule -> société -> fuite -> Telegram)
1) **Nom** -> registres entreprise / presse / décisions ouvertes.
2) **Adresse/entreprise** -> registres commerce + bénéficiaires + sanctions.
3) **Véhicule (cadre pro autorisé)** -> index cantonal autorisé (ex GE).
4) **Email/domain** -> HIBP/IntelX (défensif).
5) **Alias pseudo** -> graph social public.
6) **Telegram** -> canaux publics / usernames publiquement liés.

### 4.2 Automatisation
- **Maltego**: transforms sur entreprises, domaines, personnes, sanctions, leaks.
- **Python async**: orchestrateur API + rate-limit + cache + journal d’audit (qui a cherché quoi, quand, pourquoi).

### 4.3 Intégration 939 + NAVS
- **939 historique**: source contextuelle de risque, pas base de scraping.
- **NAVS inactifs/annulés**: contrôle d’identité et nettoyage de collisions d’identifiants dans SI autorisés.
- Croiser ensuite avec registre commerce/sanctions pour un dossier de conformité robuste.

---

## PARTIE 5 — Recherches complémentaires

### 5.1 Équivalents 939 en autres cantons
- Forte hétérogénéité cantonale (accès web, guichet, intérêt légitime, professions autorisées).
- Action: matrice cantonale VD/BE/ZH avec: canal, prix, SLA, base légale.

### 5.2 Bots/APIs “type plaques”
- Existence possible d’apps tierces; risque juridique/qualité élevé.
- Recommandation: n’intégrer que sources officielles ou partenaires contractuels.

### 5.3 Nouveaux registres ouverts depuis 2025
- Pivots à surveiller: bénéficiaires effectifs, marchés publics, registres fonciers numérisés (selon juridiction).

### 5.4 Veille Perplexity (requêtes récurrentes)
- Quotidien: "site:ge.ch index auto plaques détenteur mise à jour"
- Hebdo: "site:zas.admin.ch NAVSInact NAVSAnnul publication"
- Hebdo: "LPD Suisse jurisprudence données personnelles annuaires scraping"
- Mensuel: "site:opendata.swiss registre bénéficiaires effectifs suisse"

---

## Mise en garde juridique (obligatoire)
- **Interdiction**: scraping massif d’annuaires personnes sans base légale/contractuelle.
- **Principe**: minimisation, finalité, proportionnalité, journalisation.
- **Professionnels**: privilégier accès autorisés, API sous contrat, et avis juridique local.

## Sources principales (consultées le 29 avril 2026)
- GE Index Auto: https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
- Wayback endpoint demandé: http://web.archive.org/web/*/https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
- CdC numéros inactivés/annulés: https://www.zas.admin.ch/fr/numeros-inactives-ou-annules
- CdC UPIServices: https://www.zas.admin.ch/fr/interface-upiservices
- TDG (archive index, article 2013 mentionné): https://www.tdg.ch/geneve/2013/04/22
