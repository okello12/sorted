/* src/product/product.js (Phase 1 of the product-photo specification, docs/PRODUCT_PHASE1.md)
   The product record that lives on a repair case as t.prod. Pure: no DOM, no saving, no clock of its own (every
   function that records a time takes `now`, a number of milliseconds).

   A field is {v, st, src, at, was:[…]}:
     st   candidate (read by Sorted, not yet accepted), confirmed (accepted as read), corrected (the person typed a
          different value), unknown (the person said they don't know), rejected (the person turned a reading down);
     src  user, label_photo, receipt, barcode, official_source;
     was  the earlier values, oldest first, each {v, st, src, at}. A serial number is kept there masked, never in full.
   Only confirmed and corrected values are facts. Everything else is a suggestion that must not change anything. */
var ProductRecord = (function () {
  var FIELDS = ["category", "brand", "model", "serial", "retailer", "bought"];
  var SOURCES = ["user", "label_photo", "receipt", "barcode", "official_source"];
  var CATS = [
    ["washing_machine", "Washing machine"], ["dishwasher", "Dishwasher"], ["tumble_dryer", "Tumble dryer"],
    ["fridge_freezer", "Fridge or freezer"], ["vacuum", "Vacuum cleaner"], ["printer", "Printer"], ["router", "Router"],
    ["coffee", "Coffee machine"], ["oven", "Oven or cooker"], ["microwave", "Microwave"],
    ["boiler", "Boiler or heating"], ["car", "Car or van"], ["other", "Something else"]
  ];
  var FACT = { confirmed: 1, corrected: 1 };

  function catName(k) { for (var i = 0; i < CATS.length; i++) if (CATS[i][0] === k) return CATS[i][1]; return ""; }
  function catKey(name) {
    var x = String(name || "").toLowerCase();
    for (var i = 0; i < CATS.length; i++) if (CATS[i][1].toLowerCase() === x || CATS[i][0] === x) return CATS[i][0];
    return "";
  }
  function clean(k, v) {
    v = String(v == null ? "" : v).replace(/\s+/g, " ").trim().slice(0, 80);
    if (k === "model" || k === "serial") v = v.replace(/\s+/g, "").toUpperCase();
    return v;
  }
  /* "••••6789": the last four characters, or the last two of a short one. Never more. */
  function mask(s) {
    s = String(s || "").replace(/\s+/g, "");
    if (!s) return "";
    return "••••" + s.slice(s.length >= 8 ? -4 : -2);
  }
  function okDate(x) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(x || "")); if (!m) return false;
    var d = new Date(+m[1], +m[2] - 1, +m[3]);
    return d.getFullYear() === +m[1] && d.getMonth() === +m[2] - 1 && d.getDate() === +m[3];
  }
  function keep(k, v) { return k === "serial" ? mask(v) : v; }

  function make(id, now) { return { v: 1, id: String(id || ""), f: {}, safety: null, at: now, up: now }; }
  function field(rec, k) { return rec && rec.f && rec.f[k] || null; }
  function isFact(fl) { return !!(fl && FACT[fl.st]); }
  /* The value only if it is a fact. */
  function value(rec, k) { var fl = field(rec, k); return isFact(fl) ? fl.v : ""; }
  function candidate(rec, k) { var fl = field(rec, k); return fl && fl.st === "candidate" ? fl.v : ""; }
  function status(rec, k) { var fl = field(rec, k); return fl ? fl.st : "unknown"; }
  function put(rec, k, v, st, src, now) {
    var fl = rec.f[k] || (rec.f[k] = { v: "", st: "unknown", src: "", at: now, was: [] });
    if (fl.v || fl.st !== "unknown") { var old = { v: keep(k, fl.v), st: fl.st, src: fl.src, at: fl.at }; (fl.was = fl.was || []).push(old); }
    fl.v = v; fl.st = st; fl.src = src; fl.at = now; rec.up = now;
    return fl;
  }

  /* A reading. It never touches a fact: a confirmed or corrected value stays, and the reading is ignored. */
  function propose(rec, k, v, src, now) {
    if (FIELDS.indexOf(k) < 0 || SOURCES.indexOf(src) < 0) return false;
    v = clean(k, v); if (!v) return false;
    if (k === "bought" && !okDate(v)) return false;
    var fl = field(rec, k);
    if (isFact(fl)) return false;
    if (fl && fl.st === "rejected" && fl.v === v) return false;
    if (fl && fl.st === "candidate" && fl.v === v && fl.src === src) return false;
    put(rec, k, v, "candidate", src, now);
    return true;
  }
  /* The person accepts the reading as it is. */
  function confirm(rec, k, now) {
    var fl = field(rec, k);
    if (!fl || fl.st !== "candidate" || !fl.v) return false;
    put(rec, k, fl.v, "confirmed", fl.src, now);
    return true;
  }
  /* The person types a value. Equal to the reading: confirmed. Different: corrected, the reading kept in `was`. */
  function set(rec, k, v, now) {
    if (FIELDS.indexOf(k) < 0) return false;
    v = clean(k, v);
    var fl = field(rec, k);
    if (!v) return forget(rec, k, now);
    if (k === "bought" && !okDate(v)) return false;
    if (fl && fl.v === v && isFact(fl)) return false;
    var st = fl && fl.v === v && fl.st === "candidate" ? "confirmed" : (fl && fl.v ? "corrected" : "confirmed");
    put(rec, k, v, st, "user", now);
    return true;
  }
  function reject(rec, k, now) {
    var fl = field(rec, k);
    if (!fl || fl.st !== "candidate") return false;
    put(rec, k, fl.v, "rejected", fl.src, now);
    rec.f[k].v = keep(k, fl.v);
    return true;
  }
  function forget(rec, k, now) {
    var fl = field(rec, k);
    if (fl && fl.st === "unknown" && !fl.v) return false;
    put(rec, k, "", "unknown", "user", now);
    return true;
  }

  /* "Bosch washing machine", "Bosch", "Washing machine", from facts only. */
  function label(rec) {
    var b = value(rec, "brand"), c = catName(value(rec, "category"));
    if (c === "Something else") c = "";
    if (b && c) return b + " " + c.charAt(0).toLowerCase() + c.slice(1);
    return b || c || "";
  }
  function months(fromIso, now) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(fromIso || ""));
    if (!m || !okDate(fromIso)) return null;
    var a = new Date(+m[1], +m[2] - 1, +m[3]), b = new Date(now);
    var n = (b.getFullYear() - a.getFullYear()) * 12 + (b.getMonth() - a.getMonth()) - (b.getDate() < a.getDate() ? 1 : 0);
    return n < 0 ? null : n;
  }
  /* The repair engine's age band (AGE in the page): lt1, 1to2, 2to6, gt6. Empty when the date isn't a fact. */
  function ageBand(rec, now) {
    var n = months(value(rec, "bought"), now);
    if (n == null) return "";
    return n < 12 ? "lt1" : n < 24 ? "1to2" : n < 72 ? "2to6" : "gt6";
  }
  /* What the repair engine should read, from facts only. The one direction: t.prod → t.fix. */
  function forFix(rec, now) {
    var o = {}, c = value(rec, "category"), b = value(rec, "brand"), m = value(rec, "model"), r = value(rec, "retailer");
    if (c && c !== "other") o.item = catName(c);
    if (b || m) o.model = [b, m].filter(Boolean).join(" ");
    if (r) o.seller = r;
    var a = ageBand(rec, now); if (a) o.age = a;
    return o;
  }
  /* Rows for "Have these ready" and the contact. The serial is masked unless `full` is true. */
  function ready(rec, full) {
    var out = [], b = value(rec, "brand"), m = value(rec, "model"), c = catName(value(rec, "category")), s = value(rec, "serial");
    if (b || m || c) out.push({ k: "product", v: [b, m].filter(Boolean).join(" ") + (c && c !== "Something else" ? (b || m ? ", " : "") + c.toLowerCase() : "") });
    if (s) out.push({ k: "serial", v: "Serial " + (full ? s : mask(s)) });
    var r = value(rec, "retailer"), d = value(rec, "bought");
    if (r) out.push({ k: "retailer", v: "Bought from " + r });
    if (d) out.push({ k: "bought", v: d });
    return out;
  }
  /* A copy safe to show or send anywhere: the serial masked in the value and in every earlier value. */
  function safeCopy(rec) {
    var c = JSON.parse(JSON.stringify(rec || {}));
    if (c.f && c.f.serial) { c.f.serial.v = mask(c.f.serial.v); (c.f.serial.was || []).forEach(function (w) { w.v = mask(w.v); }); }
    return c;
  }
  /* Every place a full serial could be: used to strip it from text before it leaves the case. */
  function scrub(rec, text) {
    var s = String(text == null ? "" : text), v = field(rec, "serial");
    var all = [];
    if (v && v.v && v.v.indexOf("•") < 0) all.push(v.v);
    all.forEach(function (x) { if (x.length >= 4) s = s.split(x).join(mask(x)); });
    return s;
  }
  return {
    FIELDS: FIELDS, SOURCES: SOURCES, CATS: CATS, catName: catName, catKey: catKey, mask: mask, make: make,
    field: field, value: value, candidate: candidate, status: status, isFact: isFact, propose: propose,
    confirm: confirm, set: set, reject: reject, forget: forget, label: label, months: months, ageBand: ageBand,
    forFix: forFix, okDate: okDate, ready: ready, safeCopy: safeCopy, scrub: scrub
  };
})();
