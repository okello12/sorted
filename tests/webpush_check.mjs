// Checks supabase/functions/send-reminders/webpush.ts against the worked example in RFC 8291 (Appendix A), and that a
// VAPID header verifies with its own public key. Run: node --experimental-strip-types tests/webpush_check.mjs
import { copyFileSync } from "node:fs";
copyFileSync(new URL("../supabase/functions/send-reminders/webpush.ts", import.meta.url), new URL("./out/webpush.mts", import.meta.url));
const { encryptPayload, vapidHeader, b64u, unb64u } = await import("./out/webpush.mts");
const subtle = globalThis.crypto.subtle, fails = [];
const ok = (c, m) => { console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); };
const asPub = unb64u("BP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A8");
const jwk = (d, pub) => ({ kty: "EC", crv: "P-256", d, x: b64u(pub.slice(1, 33)), y: b64u(pub.slice(33, 65)) });
const priv = await subtle.importKey("jwk", jwk("yfWPiYE-n46HLnH0KqZOF1fJJU3MYrct3AELtAQ-oRw", asPub), { name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
const pub = await subtle.importKey("raw", asPub, { name: "ECDH", namedCurve: "P-256" }, true, []);
const body = await encryptPayload(new TextEncoder().encode("When I grow up, I want to be a watermelon"),
  unb64u("BCVxsr7N_eNgVRqvHtD0zTZsEc6-VV-JvLexhqUzORcxaOzi6-AYWXvTBHm4bjyPjs7Vd8pZGH6SRpkNtoIAiw4"), unb64u("BTBZMqHH6r4Tts7J_aSIgg"),
  { salt: unb64u("DGv6ra1nlYgDCS1FRnbzlw"), asKeys: { privateKey: priv, publicKey: pub } });
ok(b64u(body) === "DGv6ra1nlYgDCS1FRnbzlwAAEABBBP4z9KsN6nGRTbVYI_c7VJSPQTBtkgcy27mlmlMoZIIgDll6e3vCYLocInmYWAmS6TlzAC8wEqKK6PBru3jl7A_yl95bQpu6cVPTpK4Mqgkf1CXztLVBSt2Ks3oZwbuwXPXLWyouBWLVWGNWQexSgSxsj_Qulcy4a-fN", "the encrypted body matches RFC 8291 Appendix A");
const kp = await subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
const vj = await subtle.exportKey("jwk", kp.privateKey);
const h = await vapidHeader("https://fcm.googleapis.com/fcm/send/abc", vj, "mailto:test@example.com");
const m = /^vapid t=([^.]+)\.([^.]+)\.([^,]+), k=(.+)$/.exec(h);
const claims = JSON.parse(Buffer.from(m[2], "base64url").toString());
const ver = await subtle.verify({ name: "ECDSA", hash: "SHA-256" }, kp.publicKey, unb64u(m[3]), new TextEncoder().encode(m[1] + "." + m[2]));
ok(m && ver && claims.aud === "https://fcm.googleapis.com" && claims.sub === "mailto:test@example.com" && claims.exp > Date.now() / 1000, "the VAPID token verifies, with the push service as its audience");
ok(b64u(new Uint8Array(await subtle.exportKey("raw", kp.publicKey))) === m[4], "the VAPID header carries the matching public key");
console.log("FAILS", JSON.stringify(fails));
