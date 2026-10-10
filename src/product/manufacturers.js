/* src/product/manufacturers.js
   The controlled registry. A maker or shop is here only with pages a person opened and read on CHECKED; a link is
   shown only when its host is one of the entry's official domains (isOfficial). Phase 1 links to support and
   contact pages only. Sorted has not read any troubleshooting instructions on them, and must never say it has.
   Recheck every link before changing CHECKED (release gate G8: within 90 days). Never generated.
   10 Oct 2026: Bosch, Beko, Miele, LG, Dyson; then Samsung, Hotpoint, Indesit, Hoover, AEG, Electrolux, Philips, HP, Epson
   and Canon, each page fetched twice by separate checks. Whirlpool is left out: its UK repair site names no owner. Indesit's
   repair booking site (indesitservice.co.uk) is a separate domain naming no owner, so only indesit.co.uk is linked. */
var ProductMakers = (function () {
  var CHECKED = "10 Oct 2026";
  var MAKERS = [
    { id: "bosch", name: "Bosch", al: ["bosch"], regions: ["GB"], domains: ["bosch-home.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave", "coffee", "vacuum"],
      support: "https://www.bosch-home.co.uk/customer-service", supportTitle: "Bosch Customer Service (UK)",
      repair: "https://www.bosch-home.co.uk/customer-service/repair-service",
      contact: "https://www.bosch-home.co.uk/customer-service/contact-us" },
    { id: "beko", name: "Beko", al: ["beko"], regions: ["GB"], domains: ["beko.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave"],
      support: "https://www.beko.co.uk/support", supportTitle: "Beko Support & Appliance Aftercare (UK)",
      contact: "https://www.beko.co.uk/support" },
    { id: "miele", name: "Miele", al: ["miele"], regions: ["GB"], domains: ["miele.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave", "coffee", "vacuum"],
      support: "https://www.miele.co.uk/c/service-10.htm", supportTitle: "Miele Service (UK)",
      repair: "https://www.miele.co.uk/c/repair-26.htm" },
    { id: "lg", name: "LG", al: ["lg", "lg electronics"], regions: ["GB"], domains: ["lg.com"], path: "/uk/",
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "microwave", "vacuum"],
      support: "https://www.lg.com/uk/support/contact-us/", supportTitle: "LG UK Support: contact us",
      contact: "https://www.lg.com/uk/support/contact-us/" },
    { id: "samsung", name: "Samsung", al: ["samsung"], regions: ["GB"], domains: ["samsung.com"], path: "/uk/",
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave", "vacuum"],
      support: "https://www.samsung.com/uk/support/", supportTitle: "Samsung UK: Product Help & Support",
      repair: "https://www.samsung.com/uk/support/repair/" },
    { id: "hotpoint", name: "Hotpoint", al: ["hotpoint"], regions: ["GB"], domains: ["hotpoint.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave"],
      support: "https://www.hotpoint.co.uk/service", supportTitle: "Hotpoint UK: Service and repair",
      repair: "https://www.hotpoint.co.uk/service/repair" },
    { id: "indesit", name: "Indesit", al: ["indesit"], regions: ["GB"], domains: ["indesit.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven"],
      support: "https://www.indesit.co.uk/support", supportTitle: "Indesit UK: Support" },
    { id: "hoover", name: "Hoover", al: ["hoover"], regions: ["GB"], domains: ["hoover-home.com"], path: "/en_GB/",
      cats: ["vacuum", "washing_machine", "tumble_dryer", "dishwasher", "fridge_freezer", "oven"],
      support: "https://www.hoover-home.com/en_GB/pages/contact-us", supportTitle: "Hoover UK: Contact customer support",
      contact: "https://www.hoover-home.com/en_GB/pages/contact-us" },
    { id: "aeg", name: "AEG", al: ["aeg"], regions: ["GB"], domains: ["aeg.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave", "vacuum"],
      support: "https://www.aeg.co.uk/support/services", supportTitle: "AEG UK: Services",
      repair: "https://support.aeg.co.uk/repairs/information" },
    { id: "electrolux", name: "Electrolux", al: ["electrolux"], regions: ["GB"], domains: ["electrolux.co.uk"],
      cats: ["washing_machine", "dishwasher", "tumble_dryer", "fridge_freezer", "oven", "microwave", "vacuum"],
      support: "https://support.electrolux.co.uk/repairs/information", supportTitle: "Electrolux UK: Book a repair",
      repair: "https://support.electrolux.co.uk/repairs/information" },
    { id: "philips", name: "Philips", al: ["philips"], regions: ["GB"], domains: ["philips.co.uk"],
      cats: ["coffee", "vacuum"],
      support: "https://www.philips.co.uk/c-w/support-home/support-contact-form", supportTitle: "Philips UK: Contact support",
      contact: "https://www.philips.co.uk/c-w/support-home/support-contact-form" },
    { id: "hp", name: "HP", al: ["hp", "hewlett packard", "hewlett-packard"], regions: ["GB"], domains: ["hp.com"], path: "/gb-en/",
      cats: ["printer"],
      support: "https://www.hp.com/gb-en/contact-hp/contact.html", supportTitle: "HP UK: Contact HP",
      contact: "https://www.hp.com/gb-en/contact-hp/contact.html" },
    { id: "epson", name: "Epson", al: ["epson"], regions: ["GB"], domains: ["epson.co.uk"], path: "/en_GB/",
      cats: ["printer"],
      support: "https://www.epson.co.uk/en_GB/support", supportTitle: "Epson UK: Support",
      contact: "https://www.epson.co.uk/en_GB/contactus" },
    { id: "canon", name: "Canon", al: ["canon"], regions: ["GB"], domains: ["canon.co.uk"],
      cats: ["printer"],
      support: "https://www.canon.co.uk/support/", supportTitle: "Canon UK: Consumer product support" },
    { id: "dyson", name: "Dyson", al: ["dyson"], regions: ["GB"], domains: ["dyson.co.uk"],
      cats: ["vacuum"],
      support: "https://www.dyson.co.uk/support/email-request", supportTitle: "Dyson UK: contact us",
      contact: "https://www.dyson.co.uk/support/email-request" }
  ];
  /* Makers Sorted recognises on a label but has no checked page for yet. Named, never linked. */
  var KNOWN = ["Whirlpool", "Candy", "Zanussi",
    "Siemens", "Neff", "Haier", "Grundig", "Smeg", "Panasonic", "Sharp", "Russell Hobbs", "Breville", "De'Longhi",
    "Nespresso", "Shark", "Vax", "Henry", "Numatic", "Brother", "Kodak", "TP-Link", "Netgear",
    "BT", "Sky", "Virgin Media", "Belling", "Stoves", "Montpellier", "Logik", "Tefal",
    "Sage", "Krups", "Kenwood", "Morphy Richards", "Ninja", "iRobot", "Gtech"];
  var SHOPS = [
    { id: "argos", name: "Argos", al: ["argos"], domains: ["help.argos.co.uk", "argos.co.uk"],
      help: "https://help.argos.co.uk/help/refunds-&-returns/my-items-faulty-what-should-i-do", helpTitle: "Argos: my item’s faulty, what should I do?" },
    { id: "ao", name: "AO", al: ["ao", "ao.com", "appliances online"], domains: ["ao.com"],
      help: "https://ao.com/help-and-advice/my-ao/contact-us", helpTitle: "AO: contact us" },
    { id: "currys", name: "Currys", al: ["currys", "currys pc world", "pc world"], domains: [] },
    { id: "johnlewis", name: "John Lewis", al: ["john lewis", "john lewis & partners", "john lewis and partners"], domains: [] },
    { id: "amazon", name: "Amazon", al: ["amazon", "amazon.co.uk"], domains: [] },
    { id: "very", name: "Very", al: ["very.co.uk"], domains: [] },
    { id: "richersounds", name: "Richer Sounds", al: ["richer sounds"], domains: [] },
    { id: "appliancesdirect", name: "Appliances Direct", al: ["appliances direct"], domains: [] },
    { id: "ebay", name: "eBay", al: ["ebay"], domains: [] }
  ];
  var SOURCES = {
    ca_retailer: { title: "Citizens Advice: shoppers stuck with faulty electrical items urged to use their consumer rights",
      url: "https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/shoppers-urged-to-use-their-consumer-rights/" },
    ca_faulty: { title: "Citizens Advice: return faulty goods",
      url: "https://www.citizensadvice.org.uk/consumer/somethings-gone-wrong-with-a-purchase/return-faulty-goods/" },
    hse_gas: { title: "HSE: check an engineer is Gas Safe registered", url: "https://www.hse.gov.uk/gas/gas-safe-register-check.htm" }
  };

  function words(s) { return " " + String(s || "").toLowerCase().replace(/[’‘]/g, "'").replace(/[^a-z0-9'&.]+/g, " ") + " "; }
  function hit(w, a) { return w.indexOf(" " + a + " ") >= 0; }
  /* The first entry (by position in the text) whose name appears as whole words. */
  function findIn(list, text) {
    var w = words(text), best = null, at = 1e9;
    list.forEach(function (e) {
      (e.al || [e.name.toLowerCase()]).forEach(function (a) {
        var i = w.indexOf(" " + a + " ");
        if (i >= 0 && i < at) { at = i; best = e; }
      });
    });
    return best;
  }
  function maker(text) { return findIn(MAKERS, text); }
  function shop(text) { return findIn(SHOPS, text); }
  /* A brand name found on a label: a registry maker, or one Sorted knows by name only. */
  function brandIn(text) {
    text = String(text || "").replace(/\b\d+(?:\.\d+)?\s*hp\b/gi, " ");  /* horsepower on a motor label is not HP */
    var m = maker(text), w = words(text), k = null, at = 1e9;
    KNOWN.forEach(function (n) { var i = w.indexOf(" " + n.toLowerCase() + " "); if (i >= 0 && i < at) { at = i; k = n; } });
    if (m) { var mi = 1e9; m.al.forEach(function (a) { var i = w.indexOf(" " + a + " "); if (i >= 0 && i < mi) mi = i; }); if (mi <= at) return m.name; }
    return k || "";
  }
  function byName(list, name) {
    var x = String(name || "").toLowerCase().trim();
    for (var i = 0; i < list.length; i++) {
      if (list[i].name.toLowerCase() === x || (list[i].al || []).indexOf(x) >= 0) return list[i];
    }
    return null;
  }
  function host(url) { var m = /^https:\/\/([^\/?#]+)(\/[^?#]*)?/.exec(String(url || "")); return m ? { h: m[1].toLowerCase(), p: m[2] || "/" } : null; }
  /* Only a link whose host is one of the entry's own domains (or a sub-domain of one), and inside its UK path when
     it has one, is official. A search result calling itself "Bosch manual" is not. */
  function isOfficial(url, e) {
    var u = host(url);
    if (!u || !e) return false;
    var ok = (e.domains || []).some(function (d) { return u.h === d || u.h === "www." + d || u.h.slice(-(d.length + 1)) === "." + d; });
    return ok && (!e.path || u.p.indexOf(e.path) === 0);
  }
  function link(e, which) { var u = e && e[which]; return u && isOfficial(u, e) ? u : ""; }
  return { CHECKED: CHECKED, MAKERS: MAKERS, SHOPS: SHOPS, KNOWN: KNOWN, SOURCES: SOURCES, maker: maker, shop: shop,
    brandIn: brandIn, makerByName: function (n) { return byName(MAKERS, n); }, shopByName: function (n) { return byName(SHOPS, n); },
    isOfficial: isOfficial, link: link };
})();
