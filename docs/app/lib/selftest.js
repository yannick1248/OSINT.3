// Anti-regression self-test. Runs detection, gate, and a sample of network tools
// against innocuous public targets. Intended to be run by the user from the UI.
import { detectTargetType, TargetType } from "./detect.js";
import { evaluateGate } from "./gate.js";
import { TOOLS } from "./tools.js";

const SAMPLES = {
  domain: "example.com",
  email: "test@example.com",
  username: "torvalds",
  ip: "8.8.8.8",
  url: "https://example.com/?utm_source=test",
  hash: "5d41402abc4b2a76b9719d911017c592",
  phone: "+41791234567",
  onion: "abcdef1234.onion",
  person: "Ada Lovelace",
};

const expected = {
  "example.com": "domain",
  "test@example.com": "email",
  "torvalds": "username",
  "8.8.8.8": "ip",
  "https://example.com/?utm_source=test": "url",
  "5d41402abc4b2a76b9719d911017c592": "hash",
  "+41791234567": "phone",
  "abcdef1234.onion": "onion",
  "Ada Lovelace": "person",
};

export async function runSelfTest(onLine) {
  const log = (label, status, detail) => onLine?.({ label, status, detail });
  let pass = 0, fail = 0, warn = 0;

  // 1. Detection
  for (const [val, want] of Object.entries(expected)) {
    const got = detectTargetType(val);
    if (got.type === want) { log(`detect("${val}")`, "pass", `→ ${got.type}`); pass++; }
    else { log(`detect("${val}")`, "fail", `expected ${want}, got ${got.type}`); fail++; }
  }

  // 2. Gate — LEGALLY_RESTRICTED must always block
  {
    const t = detectTargetType("example.com");
    const d = evaluateGate(t, "LEGALLY_RESTRICTED");
    if (!d.allowed) { log("gate(LEGALLY_RESTRICTED)", "pass", "blocks correctly"); pass++; }
    else { log("gate(LEGALLY_RESTRICTED)", "fail", "should block"); fail++; }
  }
  {
    const t = detectTargetType("alice@example.com");
    const d = evaluateGate(t, "PUBLIC_INTEREST_RESEARCH");
    if (d.allowed && d.restricted) { log("gate(EMAIL+PUBLIC_INTEREST)", "pass", "restricted note set"); pass++; }
    else { log("gate(EMAIL+PUBLIC_INTEREST)", "fail", JSON.stringify(d)); fail++; }
  }

  // 3. Local tools always run
  const local = TOOLS.filter(t => t.kind === "local");
  for (const tool of local) {
    const sample = SAMPLES[tool.targets[0]] || "example.com";
    try {
      const r = await tool.run(sample);
      if (r.status === "success") { log(`tool[${tool.id}]`, "pass", `confidence=${r.confidence}`); pass++; }
      else { log(`tool[${tool.id}]`, "warn", r.error || `status=${r.status}`); warn++; }
    } catch (e) {
      log(`tool[${tool.id}]`, "fail", e.message);
      fail++;
    }
  }

  // 4. Sample network tools (best-effort, may legitimately fail offline)
  const netSample = ["dns_google", "crt_sh", "rdap"];
  for (const id of netSample) {
    const tool = TOOLS.find(t => t.id === id);
    if (!tool) continue;
    const sample = SAMPLES[tool.targets[0]] || "example.com";
    try {
      const r = await tool.run(sample);
      if (r.status === "success") { log(`net[${tool.id}]`, "pass", "OK"); pass++; }
      else if (r.status === "partial") { log(`net[${tool.id}]`, "warn", r.error || "partial"); warn++; }
      else { log(`net[${tool.id}]`, "warn", r.error || "fail"); warn++; }
    } catch (e) {
      log(`net[${tool.id}]`, "warn", e.message);
      warn++;
    }
  }

  return { pass, fail, warn };
}

export { TargetType };
