// Auto-complete suggestions for the target input.
// Generates plausible expansions based on what the user has typed.
import { detectTargetType, TargetType } from "./detect.js";

export function suggestionsFor(raw) {
  const value = String(raw || "").trim();
  if (!value) return [];
  const out = new Set();

  if (value.includes("@") && !value.endsWith("@")) {
    // looks like email — suggest dorks
    out.add(value);
    out.add(`"${value}"`);
  } else if (/^[A-Za-z0-9._-]+$/.test(value) && !value.includes(".")) {
    // bare label — could be a username; suggest common email/domain expansions
    out.add(`@${value}`);
    out.add(`${value}@gmail.com`);
    out.add(`${value}@protonmail.com`);
    out.add(`${value}.com`);
    out.add(`${value}.io`);
    out.add(`${value}.org`);
  } else if (/^\d{1,3}(?:\.\d{1,3}){0,3}$/.test(value)) {
    // partial IPv4 — keep
    out.add(value);
  } else if (/^https?:\/\//i.test(value)) {
    try {
      const u = new URL(value);
      out.add(u.hostname);
      out.add(value);
    } catch { /* ignore */ }
  } else if (value.includes(".") && !value.includes(" ")) {
    out.add(value);
    out.add(`www.${value}`);
  } else if (value.includes(" ")) {
    out.add(value);
    out.add(`"${value}"`);
  } else {
    out.add(value);
  }

  return [...out].slice(0, 8).map(v => {
    const t = detectTargetType(v);
    return { value: v, type: t.type };
  });
}

export { TargetType };
