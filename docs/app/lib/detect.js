// Client-side target type detection — mirrors osint_omega.engine.detect_target_type
export const TargetType = Object.freeze({
  EMAIL: "email",
  DOMAIN: "domain",
  USERNAME: "username",
  PHONE: "phone",
  IP: "ip",
  ONION: "onion",
  URL: "url",
  HASH: "hash",
  FREE_TEXT: "free_text",
  PERSON: "person",
});

const RE = {
  email:  /^[\w.!#$%&'*+/=?^`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$/,
  ipv4:   /^(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})$/,
  ipv6:   /^[0-9a-fA-F:]+$/,
  onion:  /\.onion$/i,
  url:    /^https?:\/\//i,
  phone:  /^\+?\d[\d\s().-]{6,}\d$/,
  domain: /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/,
  hashMd5:    /^[A-Fa-f0-9]{32}$/,
  hashSha1:   /^[A-Fa-f0-9]{40}$/,
  hashSha256: /^[A-Fa-f0-9]{64}$/,
  username: /^@?[A-Za-z0-9_.-]{2,64}$/,
};

export function detectTargetType(raw) {
  const value = String(raw || "").trim();
  if (!value) return { value, type: TargetType.FREE_TEXT };

  if (RE.url.test(value)) {
    try {
      const u = new URL(value);
      if (u.hostname.endsWith(".onion")) return { value, type: TargetType.ONION };
      return { value, type: TargetType.URL };
    } catch { /* fallthrough */ }
  }
  if (RE.onion.test(value)) return { value, type: TargetType.ONION };
  if (RE.email.test(value)) return { value: value.toLowerCase(), type: TargetType.EMAIL };
  if (RE.ipv4.test(value)) return { value, type: TargetType.IP };
  if (RE.hashSha256.test(value) || RE.hashSha1.test(value) || RE.hashMd5.test(value)) {
    return { value: value.toLowerCase(), type: TargetType.HASH };
  }
  const digits = value.replace(/[^\d+]/g, "");
  if (RE.phone.test(value) && digits.replace(/^\+/, "").length >= 7) {
    return { value: digits, type: TargetType.PHONE };
  }
  if (RE.domain.test(value)) return { value: value.toLowerCase(), type: TargetType.DOMAIN };
  if (value.includes(" ")) return { value, type: TargetType.PERSON };
  if (RE.username.test(value)) return { value: value.replace(/^@/, ""), type: TargetType.USERNAME };
  return { value, type: TargetType.FREE_TEXT };
}
