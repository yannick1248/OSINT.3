// Functional OSINT link tree — every URL performs a real search/query.
// Organized by target type, then by investigation category.
import { TargetType } from "./detect.js";

const enc = encodeURIComponent;

const LINK_TREE = {
  [TargetType.DOMAIN]: [
    {
      title: "Recon DNS / Infra",
      links: [
        { label: "Shodan host search", description: "Services, ports, bannières exposés.", tag: "api",
          url: (v) => `https://www.shodan.io/search?query=hostname:${enc(v)}` },
        { label: "Censys search", description: "Certificats + hôtes.", tag: "api",
          url: (v) => `https://search.censys.io/search?resource=hosts&q=${enc(v)}` },
        { label: "crt.sh", description: "Certificate Transparency logs.", tag: "api",
          url: (v) => `https://crt.sh/?q=${enc("%." + v)}` },
        { label: "SecurityTrails", description: "Historique DNS + sous-domaines.", tag: "api",
          url: (v) => `https://securitytrails.com/domain/${enc(v)}/history/a` },
        { label: "DNSDumpster", description: "Cartographie DNS visuelle.", tag: "api",
          url: (v) => `https://dnsdumpster.com/?q=${enc(v)}` },
        { label: "URLScan", description: "Scan + screenshot + IOCs.", tag: "api",
          url: (v) => `https://urlscan.io/search/#domain:${enc(v)}` },
      ],
    },
    {
      title: "WHOIS / Registre",
      links: [
        { label: "WHOIS ICANN", description: "Données d'enregistrement officielles.", tag: "registry",
          url: (v) => `https://lookup.icann.org/en/lookup?q=${enc(v)}` },
        { label: "DomainTools", description: "Historique WHOIS.", tag: "registry",
          url: (v) => `https://whois.domaintools.com/${enc(v)}` },
        { label: "ViewDNS", description: "WHOIS + reverse IP.", tag: "registry",
          url: (v) => `https://viewdns.info/whois/?domain=${enc(v)}` },
      ],
    },
    {
      title: "Archives & historique",
      links: [
        { label: "Wayback Machine", description: "Calendrier des snapshots.", tag: "archive",
          url: (v) => `https://web.archive.org/web/*/${enc(v)}` },
        { label: "Google Cache", description: "Dernier cache Google.", tag: "cache",
          url: (v) => `https://www.google.com/search?q=cache:${enc(v)}` },
        { label: "Common Crawl", description: "Index web public.", tag: "archive",
          url: (v) => `https://index.commoncrawl.org/CC-MAIN-2024-33-index?url=${enc(v)}/*&output=json` },
      ],
    },
    {
      title: "Menaces / réputation",
      links: [
        { label: "VirusTotal", description: "Antivirus + passive DNS.", tag: "threat",
          url: (v) => `https://www.virustotal.com/gui/domain/${enc(v)}` },
        { label: "AbuseIPDB (reverse)", description: "Réputation IP associée.", tag: "threat",
          url: (v) => `https://www.abuseipdb.com/check/${enc(v)}` },
        { label: "AlienVault OTX", description: "Pulses & indicateurs.", tag: "threat",
          url: (v) => `https://otx.alienvault.com/indicator/domain/${enc(v)}` },
        { label: "ThreatMiner", description: "Aggrégateur IOC.", tag: "threat",
          url: (v) => `https://www.threatminer.org/domain.php?q=${enc(v)}` },
      ],
    },
    {
      title: "Google Dorks",
      links: [
        { label: "site:", description: "Toutes les pages indexées.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=site:${enc(v)}` },
        { label: "site: -www", description: "Sous-domaines autres que www.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=site:${enc(v)}+-inurl:www` },
        { label: "Fichiers sensibles", description: "PDF/XLS/DOC indexés.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=site:${enc(v)}+(filetype:pdf+OR+filetype:xls+OR+filetype:doc)` },
        { label: "Pages de login", description: "Portails d'authentification.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=site:${enc(v)}+(inurl:login+OR+inurl:admin+OR+inurl:signin)` },
        { label: "Exposés .env/.git", description: "Configuration / secrets potentiels.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=site:${enc(v)}+(ext:env+OR+ext:git+OR+ext:sql)` },
      ],
    },
  ],

  [TargetType.EMAIL]: [
    {
      title: "Fuites / breaches",
      links: [
        { label: "HIBP (Have I Been Pwned)", description: "Base de breaches.", tag: "breach",
          url: (v) => `https://haveibeenpwned.com/account/${enc(v)}` },
        { label: "Dehashed", description: "Moteur de breaches (payant).", tag: "breach",
          url: (v) => `https://dehashed.com/search?query=${enc(v)}` },
        { label: "IntelligenceX", description: "Archives + fuites.", tag: "breach",
          url: (v) => `https://intelx.io/?s=${enc(v)}` },
        { label: "LeakCheck", description: "Moteur breaches privé.", tag: "breach",
          url: (v) => `https://leakcheck.io/?search=${enc(v)}` },
      ],
    },
    {
      title: "Réputation / validation",
      links: [
        { label: "EmailRep", description: "Score de réputation.", tag: "api",
          url: (v) => `https://emailrep.io/${enc(v)}` },
        { label: "MXToolbox SuperTool", description: "MX, blacklist, SPF.", tag: "api",
          url: (v) => `https://mxtoolbox.com/SuperTool.aspx?action=mx:${enc(v.split("@")[1] || v)}` },
        { label: "Hunter.io (verify)", description: "Vérification de délivrabilité.", tag: "api",
          url: (v) => `https://hunter.io/email-verifier/${enc(v)}` },
        { label: "Gravatar profile", description: "Profil public éventuel.", tag: "profile",
          url: (v) => `https://gravatar.com/${enc(v)}` },
      ],
    },
    {
      title: "Présence plateformes",
      links: [
        { label: "Holehe (CLI local)", description: "Ouvre la doc; à lancer via osint_omega CLI.", tag: "doc",
          url: () => `https://github.com/megadose/holehe` },
        { label: "Epieos", description: "Présence Google + plateformes.", tag: "api",
          url: (v) => `https://tools.epieos.com/email.php?email=${enc(v)}` },
      ],
    },
    {
      title: "Google Dorks",
      links: [
        { label: "Tout web", description: "Recherche exacte.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22` },
        { label: "Pastebin leaks", description: "Mentions sur pastebin & miroirs.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+(site:pastebin.com+OR+site:ghostbin.com+OR+site:throwbin.com)` },
        { label: "LinkedIn", description: "Profil éventuel.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+site:linkedin.com` },
      ],
    },
  ],

  [TargetType.USERNAME]: [
    {
      title: "Vérifications multi-plateformes",
      links: [
        { label: "WhatsMyName", description: "400+ sites testés via navigateur.", tag: "multi",
          url: (v) => `https://whatsmyname.app/?q=${enc(v)}` },
        { label: "Sherlock (local)", description: "CLI Python — 400+ plateformes.", tag: "doc",
          url: () => `https://github.com/sherlock-project/sherlock` },
        { label: "Namechk", description: "Disponibilité sur 100+ sites.", tag: "multi",
          url: (v) => `https://namechk.com/namechk/username/${enc(v)}` },
        { label: "Instant Username Search", description: "Rapide, multi-sites.", tag: "multi",
          url: (v) => `https://instantusername.com/#/${enc(v)}` },
      ],
    },
    {
      title: "Profils directs",
      links: [
        { label: "GitHub", description: "Profil + repos.", tag: "profile",
          url: (v) => `https://github.com/${enc(v)}` },
        { label: "GitLab", description: "Profil + projets.", tag: "profile",
          url: (v) => `https://gitlab.com/${enc(v)}` },
        { label: "Reddit", description: "Historique commentaires.", tag: "profile",
          url: (v) => `https://www.reddit.com/user/${enc(v)}` },
        { label: "Twitter/X", description: "Compte éventuel.", tag: "profile",
          url: (v) => `https://twitter.com/${enc(v)}` },
        { label: "Instagram", description: "Profil public.", tag: "profile",
          url: (v) => `https://www.instagram.com/${enc(v)}` },
        { label: "TikTok", description: "Profil + vidéos.", tag: "profile",
          url: (v) => `https://www.tiktok.com/@${enc(v)}` },
        { label: "Mastodon (search)", description: "Découverte fédivers.", tag: "profile",
          url: (v) => `https://mastodon.social/@${enc(v)}` },
        { label: "Keybase", description: "Identité cryptographique.", tag: "profile",
          url: (v) => `https://keybase.io/${enc(v)}` },
      ],
    },
    {
      title: "Fuites & réputation",
      links: [
        { label: "HIBP (breach search)", description: "Recherche breaches par pseudo.", tag: "breach",
          url: (v) => `https://haveibeenpwned.com/unifiedsearch/${enc(v)}` },
        { label: "IntelligenceX", description: "Archives + fuites.", tag: "breach",
          url: (v) => `https://intelx.io/?s=${enc(v)}` },
      ],
    },
    {
      title: "Google Dorks",
      links: [
        { label: "Exact match", description: "Toutes les occurrences.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22` },
        { label: "Forums / profils", description: "profile/user URLs.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+(inurl:profile+OR+inurl:user+OR+inurl:member)` },
      ],
    },
  ],

  [TargetType.IP]: [
    {
      title: "Geo & ASN",
      links: [
        { label: "Shodan host", description: "Services ouverts.", tag: "api",
          url: (v) => `https://www.shodan.io/host/${enc(v)}` },
        { label: "Censys host", description: "Vue détaillée.", tag: "api",
          url: (v) => `https://search.censys.io/hosts/${enc(v)}` },
        { label: "ipinfo.io", description: "Geo, ASN, organisation.", tag: "api",
          url: (v) => `https://ipinfo.io/${enc(v)}` },
        { label: "ipapi.co", description: "Geo + détails JSON.", tag: "api",
          url: (v) => `https://ipapi.co/${enc(v)}/` },
        { label: "BGPView", description: "Routage BGP / préfixes.", tag: "api",
          url: (v) => `https://bgpview.io/ip/${enc(v)}` },
      ],
    },
    {
      title: "Réputation / abus",
      links: [
        { label: "AbuseIPDB", description: "Score d'abus.", tag: "threat",
          url: (v) => `https://www.abuseipdb.com/check/${enc(v)}` },
        { label: "VirusTotal", description: "Réputation + passive DNS.", tag: "threat",
          url: (v) => `https://www.virustotal.com/gui/ip-address/${enc(v)}` },
        { label: "GreyNoise", description: "Activité scanners Internet.", tag: "threat",
          url: (v) => `https://viz.greynoise.io/ip/${enc(v)}` },
        { label: "AlienVault OTX", description: "Indicateurs associés.", tag: "threat",
          url: (v) => `https://otx.alienvault.com/indicator/ip/${enc(v)}` },
        { label: "Spur.us", description: "Détection VPN/résidentiel.", tag: "threat",
          url: (v) => `https://spur.us/context/${enc(v)}` },
      ],
    },
    {
      title: "Reverse / DNS",
      links: [
        { label: "ViewDNS reverse IP", description: "Domaines hébergés sur l'IP.", tag: "recon",
          url: (v) => `https://viewdns.info/reverseip/?host=${enc(v)}&t=1` },
        { label: "SecurityTrails reverse", description: "Historique DNS associé.", tag: "recon",
          url: (v) => `https://securitytrails.com/list/ip/${enc(v)}` },
      ],
    },
  ],

  [TargetType.PHONE]: [
    {
      title: "Moteurs spécialisés",
      links: [
        { label: "PhoneInfoga (doc)", description: "CLI OSINT téléphone.", tag: "doc",
          url: () => `https://github.com/sundowndev/phoneinfoga` },
        { label: "Numverify", description: "Validation + opérateur.", tag: "api",
          url: (v) => `https://numverify.com/dashboard?search=${enc(v)}` },
        { label: "Truecaller (recherche)", description: "Annuaire communautaire.", tag: "search",
          url: (v) => `https://www.truecaller.com/search/ch/${enc(v)}` },
        { label: "Sync.me", description: "Identité associée.", tag: "search",
          url: (v) => `https://sync.me/search/?number=${enc(v)}` },
      ],
    },
    {
      title: "Google Dorks",
      links: [
        { label: "Recherche exacte", description: "Toutes mentions.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22` },
        { label: "Leaks / dumps", description: "Mentions sur pastebin & cie.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+(site:pastebin.com+OR+ext:txt)` },
      ],
    },
  ],

  [TargetType.PERSON]: [
    {
      title: "Recherches nominatives",
      links: [
        { label: "Google exact", description: "Nom entre guillemets.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22` },
        { label: "LinkedIn", description: "Profils professionnels.", tag: "social",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+site:linkedin.com` },
        { label: "Twitter/X", description: "Comptes + mentions.", tag: "social",
          url: (v) => `https://twitter.com/search?q=${enc(v)}` },
        { label: "Facebook", description: "Profils + mentions.", tag: "social",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22+site:facebook.com` },
      ],
    },
    {
      title: "Registres / public records",
      links: [
        { label: "OpenCorporates", description: "Registres d'entreprises mondiaux.", tag: "registry",
          url: (v) => `https://opencorporates.com/officers?q=${enc(v)}&utf8=%E2%9C%93` },
        { label: "CH Zefix", description: "Registre du commerce suisse.", tag: "registry",
          url: (v) => `https://www.zefix.ch/fr/search/entity/list?name=${enc(v)}` },
        { label: "FR Pappers", description: "Registre SIRENE + dirigeants.", tag: "registry",
          url: (v) => `https://www.pappers.fr/recherche?q=${enc(v)}` },
        { label: "OFAC sanctions", description: "Liste sanctions US.", tag: "sanctions",
          url: (v) => `https://sanctionssearch.ofac.treas.gov/Details.aspx?id=0&name=${enc(v)}` },
        { label: "EU sanctions map", description: "Sanctions européennes.", tag: "sanctions",
          url: (v) => `https://www.sanctionsmap.eu/#/main?search=${enc(v)}` },
      ],
    },
    {
      title: "Images & vidéos",
      links: [
        { label: "Google Images", description: "Recherche visuelle.", tag: "image",
          url: (v) => `https://www.google.com/search?q=${enc(v)}&tbm=isch` },
        { label: "Yandex Images", description: "Bonne reverse image.", tag: "image",
          url: (v) => `https://yandex.com/images/search?text=${enc(v)}` },
        { label: "Bing Images", description: "Alternative.", tag: "image",
          url: (v) => `https://www.bing.com/images/search?q=${enc(v)}` },
      ],
    },
  ],

  [TargetType.URL]: [
    {
      title: "Analyse sécurité",
      links: [
        { label: "URLScan", description: "Scan live + screenshot.", tag: "api",
          url: (v) => `https://urlscan.io/search/#${enc("page.url:\"" + v + "\"")}` },
        { label: "VirusTotal", description: "Scanners + réputation.", tag: "api",
          url: (v) => `https://www.virustotal.com/gui/search/${enc(v)}` },
        { label: "Hybrid Analysis", description: "Sandbox + IOCs.", tag: "api",
          url: () => `https://www.hybrid-analysis.com/` },
        { label: "Sucuri SiteCheck", description: "Malware + blacklist.", tag: "api",
          url: (v) => `https://sitecheck.sucuri.net/results/${enc(v)}` },
      ],
    },
    {
      title: "Archives",
      links: [
        { label: "Wayback Machine", description: "Calendrier des snapshots.", tag: "archive",
          url: (v) => `https://web.archive.org/web/*/${enc(v)}` },
        { label: "Archive.today", description: "Archive alternative.", tag: "archive",
          url: (v) => `https://archive.ph/${enc(v)}` },
        { label: "Google Cache", description: "Dernier cache.", tag: "cache",
          url: (v) => `https://www.google.com/search?q=cache:${enc(v)}` },
      ],
    },
  ],

  [TargetType.HASH]: [
    {
      title: "Malware / IOC",
      links: [
        { label: "VirusTotal", description: "AV multi-moteur.", tag: "threat",
          url: (v) => `https://www.virustotal.com/gui/file/${enc(v)}` },
        { label: "MalwareBazaar", description: "Échantillons publics.", tag: "threat",
          url: (v) => `https://bazaar.abuse.ch/browse.php?search=sha256%3A${enc(v)}` },
        { label: "Hybrid Analysis", description: "Sandbox.", tag: "threat",
          url: (v) => `https://www.hybrid-analysis.com/search?query=${enc(v)}` },
        { label: "ThreatFox", description: "IOCs récents.", tag: "threat",
          url: (v) => `https://threatfox.abuse.ch/browse.php?search=ioc%3A${enc(v)}` },
      ],
    },
  ],

  [TargetType.ONION]: [
    {
      title: "Index & sécurité",
      links: [
        { label: "Ahmia (clearnet)", description: "Index .onion clearweb.", tag: "dir",
          url: (v) => `https://ahmia.fi/search/?q=${enc(v)}` },
        { label: "Tor.taxi (guide)", description: "Répertoire curated.", tag: "dir",
          url: () => `https://tor.taxi/` },
        { label: "OnionScan (doc)", description: "Outil audit .onion.", tag: "doc",
          url: () => `https://onionscan.org/` },
      ],
    },
  ],

  [TargetType.FREE_TEXT]: [
    {
      title: "Recherche générique",
      links: [
        { label: "Google exact", description: "Recherche litérale.", tag: "dork",
          url: (v) => `https://www.google.com/search?q=%22${enc(v)}%22` },
        { label: "DuckDuckGo", description: "Sans suivi.", tag: "search",
          url: (v) => `https://duckduckgo.com/?q=${enc(v)}` },
        { label: "Yandex", description: "Index complémentaire.", tag: "search",
          url: (v) => `https://yandex.com/search/?text=${enc(v)}` },
        { label: "Bing", description: "Alternative.", tag: "search",
          url: (v) => `https://www.bing.com/search?q=${enc(v)}` },
      ],
    },
  ],
};

export { LINK_TREE };
