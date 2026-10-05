// Web Push for Sorted (v133): the message encryption of RFC 8291 (aes128gcm) and the VAPID signature of RFC 8292,
// written with WebCrypto only, so it runs the same in Supabase's Deno and in Node (tests/webpush_check.mjs checks it
// against the RFC 8291 example). The push service sees only an encrypted blob, and the blob holds no case details.

const enc = new TextEncoder();
const subtle = globalThis.crypto.subtle;

export function b64u(buf: ArrayBuffer | Uint8Array): string {
  const b = buf instanceof Uint8Array ? buf : new Uint8Array(buf);
  let s = "";
  for (let i = 0; i < b.length; i++) s += String.fromCharCode(b[i]);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
export function unb64u(s: string): Uint8Array {
  const t = s.replace(/-/g, "+").replace(/_/g, "/") + "===".slice((s.length + 3) % 4);
  const bin = atob(t);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
function cat(...parts: Uint8Array[]): Uint8Array {
  let n = 0;
  for (const p of parts) n += p.length;
  const out = new Uint8Array(n);
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}
async function hmac(key: Uint8Array, data: Uint8Array): Promise<Uint8Array> {
  const k = await subtle.importKey("raw", key, { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return new Uint8Array(await subtle.sign("HMAC", k, data));
}

// Encrypts one push message. `opts.salt` and `opts.asKeys` exist only so the RFC example can be reproduced.
export async function encryptPayload(
  payload: Uint8Array,
  uaPublic: Uint8Array,
  authSecret: Uint8Array,
  opts: { salt?: Uint8Array; asKeys?: CryptoKeyPair } = {},
): Promise<Uint8Array> {
  const asKeys = opts.asKeys || (await subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"])) as CryptoKeyPair;
  const asPublic = new Uint8Array(await subtle.exportKey("raw", asKeys.publicKey));
  const uaKey = await subtle.importKey("raw", uaPublic, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const ecdh = new Uint8Array(await subtle.deriveBits({ name: "ECDH", public: uaKey }, asKeys.privateKey, 256));
  const prkKey = await hmac(authSecret, ecdh);
  const keyInfo = cat(enc.encode("WebPush: info\0"), uaPublic, asPublic, new Uint8Array([1]));
  const ikm = await hmac(prkKey, keyInfo);
  const salt = opts.salt || globalThis.crypto.getRandomValues(new Uint8Array(16));
  const prk = await hmac(salt, ikm);
  const cek = (await hmac(prk, cat(enc.encode("Content-Encoding: aes128gcm\0"), new Uint8Array([1])))).slice(0, 16);
  const nonce = (await hmac(prk, cat(enc.encode("Content-Encoding: nonce\0"), new Uint8Array([1])))).slice(0, 12);
  const key = await subtle.importKey("raw", cek, { name: "AES-GCM" }, false, ["encrypt"]);
  const ct = new Uint8Array(await subtle.encrypt({ name: "AES-GCM", iv: nonce }, key, cat(payload, new Uint8Array([2]))));
  const rs = new Uint8Array([0, 0, 16, 0]); // 4096
  return cat(salt, rs, new Uint8Array([asPublic.length]), asPublic, ct);
}

// The VAPID header for one push service. `jwk` is the private key as a JWK (kty EC, crv P-256, d, x, y).
export async function vapidHeader(endpoint: string, jwk: JsonWebKey, subject: string): Promise<string> {
  const aud = new URL(endpoint).origin;
  const head = b64u(enc.encode(JSON.stringify({ typ: "JWT", alg: "ES256" })));
  const body = b64u(enc.encode(JSON.stringify({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: subject })));
  const key = await subtle.importKey("jwk", { ...jwk, key_ops: ["sign"], ext: true }, { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"]);
  const sig = new Uint8Array(await subtle.sign({ name: "ECDSA", hash: "SHA-256" }, key, enc.encode(head + "." + body)));
  const pub = cat(new Uint8Array([4]), unb64u(jwk.x as string), unb64u(jwk.y as string));
  return `vapid t=${head}.${body}.${b64u(sig)}, k=${b64u(pub)}`;
}

export type Sub = { endpoint: string; p256dh: string; auth: string };

// Sends one message. Returns the push service's status: 201 accepted; 404 or 410 means the subscription is gone.
export async function sendPush(sub: Sub, message: unknown, jwk: JsonWebKey, subject: string, ttl = 86400): Promise<number> {
  const body = await encryptPayload(enc.encode(JSON.stringify(message)), unb64u(sub.p256dh), unb64u(sub.auth));
  const res = await fetch(sub.endpoint, {
    method: "POST",
    headers: {
      Authorization: await vapidHeader(sub.endpoint, jwk, subject),
      "Content-Encoding": "aes128gcm",
      "Content-Type": "application/octet-stream",
      TTL: String(ttl),
      Urgency: "normal",
    },
    body,
  });
  try { await res.arrayBuffer(); } catch { /* ignore */ }
  return res.status;
}
