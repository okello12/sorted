// v142: the service worker turns Android's share POST into /#new=… (the words only ever in the # part), leaves every
// other request alone, and caches nothing. Run: node tests/fn/sw_share_check.mjs
import fs from "node:fs";
const src = fs.readFileSync(new URL("../../public/sw.js", import.meta.url), "utf8");
const L = {}; const self = { addEventListener: (k, f) => { L[k] = f; }, location: { origin: "https://sorted-pilot.vercel.app" }, registration: {}, clients: {}, skipWaiting() {} };
new Function("self", src)(self);
const fails = []; let n = 0;
const ok = (c, m) => { n++; console.log((c ? "PASS " : "FAIL ") + m); if (!c) fails.push(m); };
async function fire(req) { let res = null; const e = { request: req, respondWith: (p) => { res = p; } }; L.fetch(e); return res ? await res : null; }
const fd = new FormData(); fd.append("st", "Evri"); fd.append("sx", "Your parcel will arrive by Friday"); fd.append("su", "https://evri.com/track/H01");
let r = await fire(new Request("https://sorted-pilot.vercel.app/share-target", { method: "POST", body: fd }));
const loc = r && r.headers.get("location") || "";
ok(r && r.status === 303 && loc.startsWith("https://sorted-pilot.vercel.app/#new=") && decodeURIComponent(loc.split("#new=")[1]) === "Evri\nYour parcel will arrive by Friday\nhttps://evri.com/track/H01", "a share becomes /#new=<the words>, in the # part only: " + loc.slice(0, 80));
ok(!/[?&]sx=/.test(loc) && loc.indexOf("?") < 0, "nothing shared is in the address the server sees");
r = await fire(new Request("https://sorted-pilot.vercel.app/share-target", { method: "POST", body: new FormData() }));
ok(r && (r.headers.get("location") || "").endsWith("/#start"), "an empty share lands on Home");
ok((await fire(new Request("https://sorted-pilot.vercel.app/", { method: "GET" }))) === null, "an ordinary page load is left to the network");
ok((await fire(new Request("https://evil.example/share-target", { method: "POST", body: fd }))) === null, "a POST to another site is left alone");
ok(!/caches\./.test(src), "the service worker caches nothing");
console.log("ERRORS []"); console.log("FAILS", JSON.stringify(fails));
