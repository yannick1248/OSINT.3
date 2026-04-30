# Synthèse opérationnelle — Genève 939 / AVS inactivés-annulés / APIs (mise à jour 29 avril 2026)

## Partie 1 — Service SMS « 939 GE »
- **Fonctionnement historique (2008)** : le service genevois permettait l’envoi d’un SMS avec format `GE + numéro de plaque` au **939** pour obtenir l’identité/adresse du détenteur, avec facturation par requête et délai court de réponse.
- **Restriction progressive** : après polémiques d’usage abusif (notamment médiatisation 2013), accès durci et encadrement légal renforcé.
- **État actuel (source officielle ge.ch)** : la page « Répertoire des détenteurs de plaques (Index Auto) » indique un accès encadré, avec **prix de renseignement CHF 2.-** et procédure administrative (dont mention d’un versement préalable de **CHF 10.-** pour demande écrite).
- **Archives Wayback** :
  - Capture index des snapshots : http://web.archive.org/web/*/https://www.ge.ch/repertoire-detenteurs-plaques-index-auto
  - Variante utile : http://web.archive.org/web/*/https://ge.ch/repertoire-detenteurs-plaques-index-auto
  - Méthode : ouvrir la frise annuelle 2008–2013, extraire les captures des pages « modalités », formulaires PDF, et captures d’écran horodatées.

## Partie 2 — Listes AVS inactivés/annulés (CdC/ZAS)
- **Page officielle** : https://www.zas.admin.ch/fr/numeros-inactives-ou-annules (publié le **5 mars 2026**).
- **Structure documentée officiellement** :
  - **Liste A** : NAVS inactivé + NAVS actif correspondant (2 valeurs séparées par espace).
  - **Liste B** : NAVS annulés (1 NAVS par ligne).
- **Diffusion** : fichiers ZIP mensuels et annuels (ex. `NAVSInact.202602`, `NAVSAnnul.202602`, `navsinact_2025`).
- **Obtention des liens directs** : via inspection du code source HTML de la page ZAS, rubrique téléchargements; sinon via UPIViewer/UPIServices ou contact support registre UPI.
- **Cadre légal (à vérifier sur textes consolidés)** : traitement strictement finalisé/proportionné (LPD), secret professionnel (art. 321 CP) selon rôle, et contraintes AVS/UPI pour usages systématiques.

## Partie 3 — Tri APIs juridiques vs OSINT (2026)
### Juridique / gouvernemental
| Outil | URL | Accès | Valeur difficile | Exemple avancé |
|---|---|---|---|---|
| Judilibre | https://www.courdecassation.fr/acces-rapide-judilibre | Gratuit/API | Jurisprudence structurée | Similarité de motifs + réseau d’avocats/cabinets |
| OpenSanctions | https://www.opensanctions.org/ | Freemium | Entités sanctions/PEP consolidées | Screening multi-juridictions + résolution d’entités |
| Wikidata SPARQL | https://query.wikidata.org/ | Gratuit | Graphe public interconnecté | Pivot personne→société→mandats→pays |
| UPIServices (CH) | https://www.zas.admin.ch/ | Réglementé | Vérif. NAVS sous conditions | Contrôles d’identité en processus métier autorisé |

### OSINT / investigation
| Outil | URL | Accès | Valeur difficile | Exemple avancé |
|---|---|---|---|---|
| Shodan | https://www.shodan.io/ | Payant/freemium | Exposition services internet | Détection surface d’attaque fournisseur |
| Censys | https://search.censys.io/ | Freemium | Certificats + hôtes | Pivot certif → sous-domaines oubliés |
| OpenSky Network | https://opensky-network.org/ | Freemium | Données vol | Corrélation trafic aérien/événement |
| HIBP (domain search) | https://haveibeenpwned.com/API | Payant | Breaches par domaine | Prioriser remédiation des identifiants exposés |
| Intelligence X | https://intelx.io/ | Payant | Archives/fuites indexées | Validation défensive d’empreintes d’exposition |

## Partie 4 — Workflow de croisement (strictement légal)
1. Entrée: nom/téléphone/email/société.
2. Validation source primaire (registre officiel ou source propriétaire autorisée).
3. Enrichissement entité (entreprises, sanctions, presse, réseaux publics).
4. Pivot véhicules **uniquement** via canaux autorisés (ex. régimes cantonaux pro, quand base légale).
5. Pivot AVS inactivé/annulé **uniquement** en contexte habilité (UPI).
6. Recoupement à 2+ sources indépendantes avant conclusion.
7. Sortie: findings avec niveau de confiance LOW/MEDIUM/HIGH + contradictions.

## Partie 5 — Axes à creuser
- Cartographie par canton des services type Auto-Index (VD confirmé; BE/ZH à inventorier).
- Veille CGU/search policy (search.ch/local.ch) mensuelle.
- Veille PFPDT/EDÖB sur jurisprudence données personnelles.
- Veille opendata.swiss sur nouveaux jeux « registres publics » (marchés, corporate, foncier selon base légale cantonale).

## Avertissement juridique
Ce document est une synthèse OSINT défensive et conformité. **Aucun scraping de masse ni contournement de protections techniques** n’est recommandé. Toute consultation de données personnelles doit reposer sur une base légale, une finalité explicite et la proportionnalité.
