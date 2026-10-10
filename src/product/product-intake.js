/* src/product/product-intake.js
   Reads candidates from text that on-device OCR got from a rating label or a receipt. It only ever proposes: every
   value it returns is a candidate the person must accept. It never guesses a model from what a product looks like,
   and a model it finds without a "Model" (or similar) label beside it is marked unlabelled, so the page says Sorted
   isn't sure. Pure; depends on ProductMakers and ProductRecord. */
var ProductIntake = (function () {
  var MODEL_LBL = /\b(?:model(?:\s*(?:no|number|nr|code))?|mod\.?|type(?:\s*(?:no|nr))?|e-?nr|product\s*(?:code|no|number)|prod\.?\s*no|m\/?n)(?![a-z])\s*[.:#]?\s*([A-Z0-9][A-Z0-9\-\/.]{2,24})/gi;
  var SERIAL_LBL = /\b(?:s[\/|il1]?n|ser(?:ial)?(?:\s*(?:no|number|nr))?|serial)(?![a-z])\s*[.:#]?\s*([A-Z0-9][A-Z0-9\-]{3,30})/gi;
  /* A label-less token shaped like a model: letters and digits mixed, 6 to 20 long. */
  var MODEL_BARE = /\b(?=[A-Z0-9\-\/]{6,20}\b)(?=[A-Z0-9\-\/]*[A-Z])(?=[A-Z0-9\-\/]*\d)[A-Z][A-Z0-9]*(?:[\-\/][A-Z0-9]+)*\b/g;
  var NOT_MODEL = /^(?:\d{1,4}(?:V|W|HZ|KW|KG|A|MM|CM|L)|IPX\d|IP\d\d|CE\d*|WEEE|UKCA|\d+[-\/]\d+(?:V|HZ))$/i;
  var CAT_WORDS = [
    [/\bwasher[- ]?dryer\b|\bwashing\s*machine\b|\bwasher\b/i, "washing_machine"], [/\bdish\s*washer\b/i, "dishwasher"],
    [/\btumble\s*dryer\b|\b(?:condenser|vented|heat pump)\s*dryer\b|\bdryer\b/i, "tumble_dryer"],
    [/\bfridge|\bfreezer\b|\brefrigerat/i, "fridge_freezer"], [/\bvacuum\b|\bhoover\b(?!\s+(?:ltd|limited))/i, "vacuum"],
    [/\bprinter\b|\ball[- ]in[- ]one\b|\binkjet\b|\blaser\s*jet\b/i, "printer"], [/\brouter\b|\bhub\b|\bwi-?fi\b/i, "router"],
    [/\bcoffee\b|\bespresso\b|\bbean[- ]to[- ]cup\b/i, "coffee"], [/\bmicrowave\b/i, "microwave"],
    [/\boven\b|\bcooker\b|\bhob\b|\brange\b/i, "oven"], [/\bboiler\b|\bcombi\b|\bgas\s*fire\b/i, "boiler"]
  ];
  function up(s) { return String(s || "").toUpperCase(); }
  function trimTok(v) { return up(v).replace(/[.\-\/]+$/, ""); }
  function plausibleModel(v) { return v.length >= 3 && /\d/.test(v) && /[A-Z]/.test(v) && !NOT_MODEL.test(v); }
  function plausibleSerial(v) { return v.length >= 5 && /\d/.test(v); }
  function category(text) { for (var i = 0; i < CAT_WORDS.length; i++) if (CAT_WORDS[i][0].test(text)) return CAT_WORDS[i][1]; return ""; }
  /* Is the read worth showing at all? Too little text, or mostly noise, is a failed read. */
  function quality(text) {
    var t = String(text || ""), toks = t.split(/\s+/).filter(Boolean);
    var alnum = (t.match(/[A-Za-z0-9]/g) || []).length;
    if (alnum < 6 || !toks.length) return "failed";
    var junk = toks.filter(function (x) { return !/[A-Za-z0-9]{2,}/.test(x); }).length;
    return junk / toks.length > 0.6 ? "failed" : "ok";
  }
  /* From a rating label: {quality, brand, category, model, models[], modelHow (labelled | unlabelled), serial}. */
  function readLabel(text) {
    var t = String(text || "").replace(/[’‘]/g, "'").replace(/\r/g, "");
    var out = { quality: quality(t), brand: "", category: "", model: "", models: [], modelHow: "", serial: "" };
    if (out.quality === "failed") return out;
    out.brand = ProductMakers.brandIn(t);
    out.category = category(t);
    var m, serials = [];
    SERIAL_LBL.lastIndex = 0;
    while ((m = SERIAL_LBL.exec(t))) { var s = trimTok(m[1]); if (plausibleSerial(s) && serials.indexOf(s) < 0) serials.push(s); }
    out.serial = serials[0] || "";
    var labelled = [];
    MODEL_LBL.lastIndex = 0;
    while ((m = MODEL_LBL.exec(t))) {
      var v = trimTok(m[1]).replace(/\/\d{1,2}$/, "");
      if (plausibleModel(v) && serials.indexOf(v) < 0 && labelled.indexOf(v) < 0) labelled.push(v);
    }
    if (labelled.length) { out.models = labelled; out.modelHow = "labelled"; }
    else if (out.brand) {
      var bare = [], u = up(t).replace(SERIAL_LBL, " ");
      MODEL_BARE.lastIndex = 0;
      while ((m = MODEL_BARE.exec(u))) { var b = trimTok(m[0]); if (plausibleModel(b) && serials.indexOf(b) < 0 && bare.indexOf(b) < 0 && b !== up(out.brand)) bare.push(b); }
      if (bare.length) { out.models = bare.slice(0, 3); out.modelHow = "unlabelled"; }
    }
    /* Two different models: Sorted asks which, and proposes neither. */
    out.model = out.models.length === 1 ? out.models[0] : "";
    return out;
  }
  var MON = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, sept: 9, oct: 10, nov: 11, dec: 12 };
  function iso(y, mo, d) {
    if (y < 100) y += 2000;
    var dt = new Date(y, mo - 1, d);
    if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return "";
    return y + "-" + (mo < 10 ? "0" : "") + mo + "-" + (d < 10 ? "0" : "") + d;
  }
  /* Dates on a receipt, day first as in the UK. Future dates and dates over 20 years old are dropped. */
  function dates(text, now) {
    var t = String(text || ""), out = [], m, odd = false;
    var re1 = /\b(\d{1,2})[\/.\-](\d{1,2})[\/.\-](\d{2}|\d{4})\b/g;
    while ((m = re1.exec(t))) { var a = iso(+m[3], +m[2], +m[1]); if (a) out.push(a); else if (iso(+m[3], +m[1], +m[2])) odd = true; }
    var re2 = /\b(\d{1,2})(?:st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)[a-z]*\.?,?\s+(\d{4})\b/gi;
    while ((m = re2.exec(t))) { var b = iso(+m[3], MON[m[2].toLowerCase()], +m[1]); if (b) out.push(b); }
    var re3 = /\b(\d{4})-(\d{2})-(\d{2})\b/g;
    while ((m = re3.exec(t))) { var c = iso(+m[1], +m[2], +m[3]); if (c) out.push(c); }
    var today = new Date(now), lim = new Date(now); lim.setFullYear(lim.getFullYear() - 20);
    var tIso = iso(today.getFullYear(), today.getMonth() + 1, today.getDate()), lIso = iso(lim.getFullYear(), lim.getMonth() + 1, lim.getDate());
    var uniq = [];
    out.forEach(function (d) { if (d <= tIso && d >= lIso && uniq.indexOf(d) < 0) uniq.push(d); });
    return { list: uniq, odd: odd };
  }
  /* From a receipt or order confirmation: {quality, retailer, bought, dates[], odd}. One date is proposed; several are
     offered as a choice; a date that only works month-first is never read and `odd` is set so the page can say so. */
  function readReceipt(text, now) {
    var t = String(text || "");
    var out = { quality: quality(t), retailer: "", bought: "", dates: [], odd: false };
    if (out.quality === "failed") return out;
    var s = ProductMakers.shop(t); out.retailer = s ? s.name : "";
    var d = dates(t, now); out.dates = d.list; out.odd = d.odd;
    out.bought = d.list.length === 1 ? d.list[0] : "";
    return out;
  }
  return { readLabel: readLabel, readReceipt: readReceipt, quality: quality, category: category, dates: dates };
})();
