/* src/product/resolution-route.js
   "Best next step": one recommended route with its reason and the others beneath it, worked out from facts only
   (confirmed or corrected values in the product record, the safety decision, who is responsible). A candidate
   (an OCR reading not yet accepted) never changes the route. No legal conclusions: a reason states what Sorted
   knows and, where it leans on outside advice, names the source. Pure; depends on ProductRecord and ProductMakers. */
var ProductRoute = (function () {
  var R = ProductRecord, M = ProductMakers;
  var KEYS = ["RETAILER", "MANUFACTURER", "QUALIFIED_REPAIR", "OFFICIAL_SERVICE_CENTRE", "SELF_RESOLVED", "OTHER"];
  function fmt(isoD) {
    var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(isoD || ""); if (!m) return "";
    var mo = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][+m[2] - 1];
    return (+m[3]) + " " + mo + " " + m[1];
  }
  function ago(n) {
    if (n == null) return "";
    if (n < 1) return "less than a month ago";
    if (n < 12) return n + (n === 1 ? " month" : " months") + " ago";
    var y = Math.floor(n / 12); return "about " + y + (y === 1 ? " year" : " years") + " ago";
  }
  function opt(key, who, why, url) { return { key: key, who: who || "", why: why || "", url: url || "" }; }
  /* route({rec, safety, responsible, fixed, party, partyResp}, now) */
  function route(inp, now) {
    inp = inp || {};
    var rec = inp.rec || R.make("", now), dec = inp.safety || null, res = dec ? dec.result : "";
    var brand = R.value(rec, "brand"), shopN = R.value(rec, "retailer"), bought = R.value(rec, "bought");
    var mk = brand ? M.makerByName(brand) : null, sh = shopN ? M.shopByName(shopN) : null;
    var n = R.months(bought, now), cat = R.value(rec, "category");
    var makerUrl = mk ? (M.link(mk, "repair") || M.link(mk, "contact") || M.link(mk, "support")) : "";
    var shopUrl = sh ? M.link(sh, "help") : "";
    var basis = [], alt = [], best;
    var bWho = brand || "the maker", sWho = shopN || "the shop";
    if (inp.fixed) return { key: "SELF_RESOLVED", who: "", reason: "You said it’s working again.", alt: [], basis: [] };
    if (inp.responsible && inp.responsible !== "me") {
      return { key: "OTHER", who: inp.party || "", reason: "You said it’s " + (inp.partyResp || "someone else") + "’s job to fix it, so the request goes to them.", alt: [], basis: [] };
    }
    if (res === "PROFESSIONAL_ONLY" && (cat === "boiler" || (dec.matched_rules || []).indexOf("gas_appliance") >= 0)) {
      basis.push(M.SOURCES.hse_gas);
      best = opt("QUALIFIED_REPAIR", "a Gas Safe registered engineer", "Work on gas appliances must be done by a Gas Safe registered engineer.", M.SOURCES.hse_gas.url);
      if (mk) alt.push(opt("MANUFACTURER", mk.name, "Their own engineers may cover it.", makerUrl));
      return { key: best.key, who: best.who, reason: best.why, url: best.url, alt: alt, basis: basis };
    }
    if (res === "PROFESSIONAL_ONLY" && cat === "car") {
      best = opt("QUALIFIED_REPAIR", "a garage", "This needs a qualified mechanic. Don’t drive it if you’re unsure it’s safe.");
      return { key: best.key, who: best.who, reason: best.why, url: "", alt: alt, basis: basis };
    }
    var stop = res === "STOP_USE" ? "Keep it switched off. " : "";
    if (shopN && (n == null || n < 72)) {
      basis.push(M.SOURCES.ca_retailer);
      var when = bought ? " on " + fmt(bought) + ", " + ago(n) : "";
      best = opt("RETAILER", shopN, stop + "You bought it from " + shopN + when + ". Citizens Advice says the shop that sold it should help you sort out a fault." + (bought ? "" : " Sorted doesn’t know when you bought it."), shopUrl);
      if (mk) alt.push(opt("MANUFACTURER", mk.name, "If " + shopN + " can’t help, " + mk.name + " can tell you its repair options.", makerUrl));
      alt.push(opt("QUALIFIED_REPAIR", "a local repairer", "A paid repair, if you’d rather not wait."));
    } else if (mk) {
      var why = shopN ? "You bought it " + ago(n) + ". " + mk.name + " can tell you its repair options." :
        "Sorted doesn’t know where or when you bought it. " + mk.name + " can tell you its repair options.";
      best = opt("MANUFACTURER", mk.name, stop + why, makerUrl);
      if (shopN) alt.push(opt("RETAILER", shopN, "You can still ask the shop that sold it.", shopUrl));
      else alt.push(opt("RETAILER", "the shop you bought it from", "If you remember where you bought it, add it. The shop may be the place to start."));
      alt.push(opt("QUALIFIED_REPAIR", "a local repairer", "A paid repair from someone local."));
    } else {
      var why2 = brand ? "Sorted doesn’t have a checked support page for " + brand + " yet." : "Sorted doesn’t know who made it yet.";
      best = opt("QUALIFIED_REPAIR", "a local repairer", stop + why2 + " A local repairer can quote for a repair.");
      if (shopN) alt.push(opt("RETAILER", shopN, "You can ask the shop that sold it.", shopUrl));
      if (brand) alt.push(opt("MANUFACTURER", brand, "Look up " + brand + "’s own UK support page."));
      else alt.push(opt("RETAILER", "the shop you bought it from", "If you remember where you bought it, add it."));
    }
    return { key: best.key, who: best.who, reason: best.why, url: best.url, alt: alt, basis: basis };
  }
  return { KEYS: KEYS, route: route, fmt: fmt, ago: ago };
})();
