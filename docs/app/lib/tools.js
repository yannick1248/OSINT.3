// Integrated tools — each `run()` performs a REAL query.
// Sources chosen for CORS compatibility from static origins.
import { TargetType } from "./detect.js";

const t0 = () => performance.now();
const elapsed = (start) => Math.round(performance.now() - start);

function ok(source, data, confidence = "MEDIUM", meta = {}) {
  return { source, status: "success", confidence, data, ...meta };
}
function partial(source, data, error, confidence = "LOW") {
  return { source, status: "partial", confidence, data, error };
}
function fail(source, error) {
  return { source, status: "failed", confidence: "LOW", error };
}

async function fetchJson(url, opts = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), opts.timeout || 15000);
  try {
    const r = await fetch(url, { signal: ctrl.signal, headers: opts.headers || {} });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } finally {
    clearTimeout(timer);
  }
}

async function fetchText(url, opts = {}) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), opts.timeout || 15000);
  try {
    const r = await fetch(url, { signal: ctrl.signal, headers: opts.headers || {} });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.text();
  } finally {
    clearTimeout(timer);
  }
}

// ------------------- DOMAIN -------------------

const domainSyntax = {
  id: "domain_syntax",
  label: "Analyse syntaxique",
  description: "Décompose TLD, longueur, IDN, caractères suspects. Local, aucune requête réseau.",
  kind: "local",
  targets: [TargetType.DOMAIN],
  async run(value) {
    const domain = value.toLowerCase();
    const parts = domain.split(".");
    const tld = parts.at(-1);
    const sld = parts.slice(-2).join(".");
    const isIdn = /[^\x00-\x7F]/.test(domain) || domain.startsWith("xn--");
    const hasHyphens = domain.includes("-");
    const digits = (domain.match(/\d/g) || []).length;
    return ok(this.id, {
      domain, tld, sld,
      labels: parts.length,
      length: domain.length,
      is_idn: isIdn,
      has_hyphens: hasHyphens,
      digit_count: digits,
      looks_suspicious: domain.length > 25 || digits > 3 || parts.length > 4,
    }, "HIGH");
  },
};

const crtsh = {
  id: "crt_sh",
  label: "Sous-domaines (crt.sh)",
  description: "Énumère les sous-domaines via les Certificate Transparency logs. CORS ouvert.",
  kind: "api",
  targets: [TargetType.DOMAIN],
  async run(value) {
    const start = t0();
    try {
      const data = await fetchJson(`https://crt.sh/?q=${encodeURIComponent("%." + value)}&output=json`, { timeout: 20000 });
      const subs = new Set();
      for (const row of data) {
        for (const name of String(row.name_value || "").split("\n")) {
          const clean = name.trim().toLowerCase();
          if (clean && !clean.startsWith("*")) subs.add(clean);
        }
      }
      const list = [...subs].sort();
      return ok(this.id, {
        domain: value,
        count: list.length,
        subdomains: list.slice(0, 200),
        truncated: list.length > 200,
        elapsed_ms: elapsed(start),
      }, list.length > 0 ? "HIGH" : "MEDIUM");
    } catch (e) {
      return fail(this.id, `crt.sh: ${e.message}`);
    }
  },
};

const dnsGoogle = {
  id: "dns_google",
  label: "Résolution DNS (Google)",
  description: "Enregistrements A/AAAA/MX/NS/TXT via Google DNS-over-HTTPS (dns.google).",
  kind: "api",
  targets: [TargetType.DOMAIN],
  async run(value) {
    const types = ["A", "AAAA", "MX", "NS", "TXT"];
    const out = {};
    const errors = [];
    await Promise.all(types.map(async (type) => {
      try {
        const d = await fetchJson(`https://dns.google/resolve?name=${encodeURIComponent(value)}&type=${type}`);
        out[type] = (d.Answer || []).map(a => ({ name: a.name, ttl: a.TTL, data: a.data }));
      } catch (e) {
        errors.push(`${type}: ${e.message}`);
        out[type] = [];
      }
    }));
    const total = Object.values(out).reduce((a, b) => a + b.length, 0);
    if (total === 0) return partial(this.id, out, errors.join("; ") || "aucun enregistrement");
    return ok(this.id, out, total >= 3 ? "HIGH" : "MEDIUM");
  },
};

const rdap = {
  id: "rdap",
  label: "RDAP / WHOIS (rdap.org)",
  description: "Métadonnées d'enregistrement via RDAP public (CORS ouvert).",
  kind: "api",
  targets: [TargetType.DOMAIN, TargetType.IP],
  async run(value) {
    try {
      const d = await fetchJson(`https://rdap.org/${value.includes("@") ? "entity" : (/^\d/.test(value) ? "ip" : "domain")}/${encodeURIComponent(value)}`);
      const summary = {
        handle: d.handle,
        ldh: d.ldhName,
        status: d.status,
        registrar: d.entities?.find(e => e.roles?.includes("registrar"))?.vcardArray?.[1]?.find(v => v[0] === "fn")?.[3],
        events: (d.events || []).map(e => ({ action: e.eventAction, date: e.eventDate })),
        nameservers: (d.nameservers || []).map(n => n.ldhName),
      };
      return ok(this.id, summary, "HIGH");
    } catch (e) {
      return fail(this.id, `RDAP: ${e.message}`);
    }
  },
};

const waybackDomain = {
  id: "wayback",
  label: "Historique Wayback Machine",
  description: "Nombre de snapshots + premier/dernier via l'API CDX d'archive.org.",
  kind: "api",
  targets: [TargetType.DOMAIN, TargetType.URL],
  async run(value) {
    try {
      const url = `https://web.archive.org/cdx/search/cdx?url=${encodeURIComponent(value)}&limit=5&fl=timestamp,original&output=json&collapse=timestamp:6`;
      const d = await fetchJson(url);
      const rows = Array.isArray(d) ? d.slice(1) : [];
      return ok(this.id, {
        target: value,
        snapshot_count_sample: rows.length,
        recent_snapshots: rows.map(r => ({ ts: r[0], url: r[1] })),
        view_calendar: `https://web.archive.org/web/*/${value}`,
      }, rows.length > 0 ? "HIGH" : "LOW");
    } catch (e) {
      return fail(this.id, `Wayback: ${e.message}`);
    }
  },
};

// ------------------- IP -------------------

const ipInfo = {
  id: "ipapi",
  label: "Geo-IP (ipapi.co)",
  description: "Géolocalisation, ASN, organisation. API publique avec CORS.",
  kind: "api",
  targets: [TargetType.IP],
  async run(value) {
    try {
      const d = await fetchJson(`https://ipapi.co/${encodeURIComponent(value)}/json/`);
      if (d.error) return fail(this.id, d.reason || "ipapi error");
      return ok(this.id, {
        ip: d.ip,
        country: d.country_name,
        region: d.region,
        city: d.city,
        org: d.org,
        asn: d.asn,
        latitude: d.latitude,
        longitude: d.longitude,
        timezone: d.timezone,
      }, "HIGH");
    } catch (e) {
      return fail(this.id, `ipapi: ${e.message}`);
    }
  },
};

// ------------------- EMAIL -------------------

const emailSyntax = {
  id: "email_syntax",
  label: "Analyse email local",
  description: "Valide la syntaxe, extrait le domaine, détecte les alias + et les fournisseurs jetables connus.",
  kind: "local",
  targets: [TargetType.EMAIL],
  async run(value) {
    const [local, domain] = value.split("@");
    const disposable = [
      "mailinator.com", "tempmail.io", "guerrillamail.com", "10minutemail.com",
      "yopmail.com", "throwawaymail.com", "trashmail.com", "maildrop.cc",
    ];
    const plusTag = local.includes("+") ? local.split("+")[1] : null;
    return ok(this.id, {
      email: value,
      local, domain,
      plus_tag: plusTag,
      is_disposable_domain: disposable.includes(domain),
      gravatar_url: `https://www.gravatar.com/avatar/${await sha256(value.toLowerCase())}?d=404`,
    }, "HIGH");
  },
};

const emailDnsMx = {
  id: "email_mx",
  label: "Vérification MX du domaine",
  description: "Interroge Google DNS pour lister les MX records du domaine de l'email.",
  kind: "api",
  targets: [TargetType.EMAIL],
  async run(value) {
    const domain = value.split("@")[1];
    try {
      const d = await fetchJson(`https://dns.google/resolve?name=${encodeURIComponent(domain)}&type=MX`);
      const mx = (d.Answer || []).map(a => a.data).sort();
      return ok(this.id, {
        domain,
        mx,
        count: mx.length,
        deliverable_likely: mx.length > 0,
      }, mx.length > 0 ? "HIGH" : "LOW");
    } catch (e) {
      return fail(this.id, `DNS MX: ${e.message}`);
    }
  },
};

// ------------------- USERNAME -------------------

const usernameProbe = {
  id: "username_probe",
  label: "Sondage pseudo (multi-plateformes)",
  description: "Vérifie par HEAD/GET l'existence du pseudo sur ~15 plateformes publiques.",
  kind: "api",
  targets: [TargetType.USERNAME],
  async run(value) {
    const u = encodeURIComponent(value);
    const probes = [
      { site: "GitHub",     url: `https://api.github.com/users/${u}`, check: (r) => r.ok },
      { site: "Reddit",     url: `https://www.reddit.com/user/${u}/about.json`, check: (r) => r.ok },
      { site: "HackerNews", url: `https://hacker-news.firebaseio.com/v0/user/${u}.json`, check: async (r) => { const t = await r.text(); return r.ok && t !== "null"; } },
      { site: "GitLab",     url: `https://gitlab.com/api/v4/users?username=${u}`, check: async (r) => { try { return r.ok && (await r.json()).length > 0; } catch { return false; } } },
      { site: "Bitbucket",  url: `https://bitbucket.org/${u}/`, check: (r) => r.status === 200, mode: "opaque" },
      { site: "Pastebin",   url: `https://pastebin.com/u/${u}`, check: (r) => r.status === 200, mode: "opaque" },
      { site: "Keybase",    url: `https://keybase.io/_/api/1.0/user/lookup.json?username=${u}`, check: async (r) => { try { return r.ok && (await r.json()).status?.code === 0; } catch { return false; } } },
      { site: "Docker Hub", url: `https://hub.docker.com/v2/users/${u}/`, check: (r) => r.ok },
      { site: "NPM",        url: `https://registry.npmjs.org/-/user/org.couchdb.user:${u}`, check: (r) => r.ok },
      { site: "PyPI",       url: `https://pypi.org/user/${u}/`, check: (r) => r.status === 200, mode: "opaque" },
    ];

    const hits = [];
    const misses = [];
    await Promise.all(probes.map(async (p) => {
      try {
        const opts = p.mode === "opaque" ? { mode: "no-cors" } : {};
        const r = await fetch(p.url, opts);
        if (p.mode === "opaque") {
          // opaque responses can't be inspected; we can only trust that fetch did not throw
          misses.push({ site: p.site, url: p.url, note: "opaque (vérification manuelle requise)" });
          return;
        }
        const hit = await p.check(r);
        (hit ? hits : misses).push({ site: p.site, url: p.url });
      } catch (e) {
        misses.push({ site: p.site, url: p.url, error: e.message });
      }
    }));

    return ok(this.id, {
      username: value,
      found: hits,
      not_found_or_unknown: misses,
      total_checked: probes.length,
      hit_count: hits.length,
    }, hits.length >= 3 ? "HIGH" : hits.length > 0 ? "MEDIUM" : "LOW");
  },
};

const githubProfile = {
  id: "github_profile",
  label: "Profil GitHub détaillé",
  description: "Récupère bio, repos publics, followers via api.github.com.",
  kind: "api",
  targets: [TargetType.USERNAME],
  async run(value) {
    try {
      const d = await fetchJson(`https://api.github.com/users/${encodeURIComponent(value)}`);
      return ok(this.id, {
        login: d.login, name: d.name, company: d.company, blog: d.blog,
        location: d.location, email: d.email, bio: d.bio,
        public_repos: d.public_repos, followers: d.followers, following: d.following,
        created_at: d.created_at, updated_at: d.updated_at, html_url: d.html_url,
      }, "HIGH");
    } catch (e) {
      return fail(this.id, `GitHub: ${e.message}`);
    }
  },
};

// ------------------- HASH -------------------

const hashLookup = {
  id: "hash_lookup",
  label: "Classification hash",
  description: "Détecte l'algorithme probable par longueur. Local.",
  kind: "local",
  targets: [TargetType.HASH],
  async run(value) {
    const len = value.length;
    const algo = { 32: "MD5", 40: "SHA-1", 64: "SHA-256", 96: "SHA-384", 128: "SHA-512" }[len] || "inconnu";
    return ok(this.id, {
      hash: value,
      length: len,
      algorithm_guess: algo,
    }, "HIGH");
  },
};

// ------------------- URL -------------------

const urlDecompose = {
  id: "url_decompose",
  label: "Décomposition URL",
  description: "Parse scheme/host/path/query. Détecte les trackers UTM. Local.",
  kind: "local",
  targets: [TargetType.URL],
  async run(value) {
    try {
      const u = new URL(value);
      const params = {};
      const trackers = [];
      for (const [k, v] of u.searchParams) {
        params[k] = v;
        if (/^(utm_|fbclid|gclid|mc_cid|mc_eid|yclid|igshid)/i.test(k)) trackers.push(k);
      }
      return ok(this.id, {
        scheme: u.protocol.replace(":", ""),
        host: u.hostname,
        port: u.port || null,
        path: u.pathname,
        query_params: params,
        fragment: u.hash || null,
        trackers_detected: trackers,
      }, "HIGH");
    } catch (e) {
      return fail(this.id, `URL parse: ${e.message}`);
    }
  },
};

// ------------------- PHONE -------------------

const phoneParse = {
  id: "phone_parse",
  label: "Analyse téléphone",
  description: "Détection du préfixe pays (E.164). Local.",
  kind: "local",
  targets: [TargetType.PHONE],
  async run(value) {
    const normalized = value.replace(/\D/g, "");
    const countryGuesses = guessCountry(normalized);
    return ok(this.id, {
      input: value,
      digits_only: normalized,
      length: normalized.length,
      possible_countries: countryGuesses,
    }, countryGuesses.length ? "MEDIUM" : "LOW");
  },
};

// ------------------- helpers -------------------

async function sha256(s) {
  const data = new TextEncoder().encode(s);
  const buf = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function guessCountry(digits) {
  const prefixes = {
    "1": "US/CA", "33": "FR", "41": "CH", "44": "GB", "49": "DE",
    "39": "IT", "34": "ES", "32": "BE", "31": "NL", "351": "PT",
    "352": "LU", "43": "AT", "7": "RU", "86": "CN", "81": "JP",
    "82": "KR", "91": "IN", "61": "AU", "55": "BR", "212": "MA",
    "213": "DZ", "216": "TN", "221": "SN",
  };
  const hits = [];
  for (const [p, c] of Object.entries(prefixes)) {
    if (digits.startsWith(p)) hits.push({ prefix: `+${p}`, country: c });
  }
  return hits;
}

// ------------------- export -------------------

export const TOOLS = [
  domainSyntax, crtsh, dnsGoogle, rdap, waybackDomain,
  ipInfo,
  emailSyntax, emailDnsMx,
  usernameProbe, githubProfile,
  hashLookup,
  urlDecompose,
  phoneParse,
];
