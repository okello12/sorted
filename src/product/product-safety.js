/* src/product/product-safety.js
   The safety gate. Deterministic rules, never a model. It runs before Sorted offers anything about a product, and its
   decision is stored on the case with the rules that matched and RULE_VERSION. False positives are acceptable; false
   negatives are not, so a negation only clears the danger words it directly governs ("no smoke or burning smell").

   Results, strongest first:
     STOP_USE                   stop using it now; the safety screen; no checks of any kind
     PROFESSIONAL_ONLY          only a qualified person should go near it (gas, internal mains, a car's safety systems)
     OFFICIAL_INFORMATION_ONLY  official information and contact only, never checks (cars otherwise, fridges, unknown)
     SAFE_EXTERNAL_CHECKS       a later phase may offer the maker's own outside checks; Phase 1 offers none */
var ProductSafety = (function () {
  var RULE_VERSION = "ps-2";  /* ps-2 (Phase 1.5 audit): a flash with a bang; a smell of petrol, diesel or fuel */
  var ORDER = ["SAFE_EXTERNAL_CHECKS", "OFFICIAL_INFORMATION_ONLY", "PROFESSIONAL_ONLY", "STOP_USE"];
  var D = "spark(?:s|ing|ed|y)?|arc(?:s|ing)?|smok(?:e|es|ing|y)|burn(?:ing|t|ed|s)?(?:\\s+smell)?|scorch(?:ed|ing|es|marks?)?|fire|flames?|fumes?|gas(?:\\s+smell)?|smell(?:s|ing)?(?:\\s+of)?\\s+(?:gas|burning)|melt(?:ed|ing)?|shocks?|tingl(?:e|es|ing)|overheat(?:s|ing|ed)?|hot|water|wet|leak(?:s|ing)?|exposed\\s+wires?|wires?|cables?";
  var NEG = new RegExp("\\b(?:no|not|never|without|nothing(?:'s|\\s+is)?|isn't|aren't|wasn't|can't|cannot|couldn't|don't|doesn't|didn't|won't)\\b(?:\\s+(?:any|signs?|of|smell(?:s|ing)?|see|seen|hear|a|an|the|it|is|been|there|anything|sign|evidence|smoke\\s+or))*\\s+(?:" + D + ")(?:\\s*(?:,|or|nor|and)\\s*(?:any\\s+|no\\s+)?(?:" + D + "))*", "gi");
  var RULES = [
    { id: "sparking", res: "STOP_USE", re: /\bspark(?:s|ing|ed|y)?\b|\barc(?:s|ing)\b|\bflash(?:es|ing|ed)?\b[^.]{0,20}\b(?:plug|socket|inside|behind)\b/i },
    { id: "smoke", res: "STOP_USE", re: /\bsmok(?:e|es|ing|ed|y)\b/i },
    { id: "burning", res: "STOP_USE", re: /\bburn(?:ing|t|ed|s)?\b|\bscorch(?:ed|ing|es|\s+marks?)?\b|\bchar(?:red|ring)\b|\bmelt(?:ed|ing|s)?\b|\bfire\b|\bflames?\b/i },
    { id: "gas_fumes", res: "STOP_USE", re: /\bsmell(?:s|ing)?\s+(?:of\s+)?gas\b|\bgas\s+(?:smell|leak|leaking)\b|\bleak(?:ing)?\s+gas\b|\bfumes?\b|\bcarbon\s+monoxide\b|\bco\s+(?:alarm|detector)\b|\bsmell(?:s|ing)?\s+(?:of\s+|like\s+)?(?:petrol|diesel|fuel)\b|\b(?:petrol|diesel|fuel)\s+smell\b/i },
    { id: "battery", res: "STOP_USE", re: /\b(?:swollen|swelling|swell(?:ed|s)?|bulg(?:e|es|ing|ed)|puff(?:ed|y|ing)(?:\s+up)?|expanded|bloated)\b[^.]{0,30}\bbatter(?:y|ies)\b|\bbatter(?:y|ies)\b[^.]{0,30}\b(?:swollen|swelling|swelled|bulg\w*|puff\w*|expanded|bloated|leak\w*|hiss\w*|hot)\b/i },
    { id: "wiring", res: "STOP_USE", re: /\b(?:exposed|bare|frayed|damaged|cut|chewed|split|melted|broken|cracked|loose)\b[^.]{0,20}\b(?:wires?|wiring|cables?|cords?|leads?|flex|plug|sockets?)\b|\b(?:wires?|wiring|cables?|cords?|leads?|flex)\b[^.]{0,20}\b(?:exposed|showing|frayed|damaged|split|melted|sticking\s+out|hanging\s+out)\b|\bcopper\b/i },
    { id: "shock", res: "STOP_USE", re: /\b(?:electric\s+)?shock(?:s|ed)?\b(?!\s+absorb)|\btingl(?:e|es|ing)\b|\belectrocut\w*/i },
    { id: "overheating", res: "STOP_USE", re: /\boverheat\w*|\btoo\s+hot\s+to\s+touch\b|\b(?:very|really|extremely|dangerously|red|boiling)\s+hot\b|\bhot\s+to\s+the\s+touch\b|\b(?:plug|socket|cable|lead|cord|casing)\b[^.]{0,20}\b(?:hot|warm)\b/i },
    { id: "water_electrics", res: "STOP_USE", re: /\b(?:water|leak\w*|wet|damp)\b[^.]{0,40}\b(?:plug|socket|electrics?|electrical|wiring|fuse\s*box|consumer\s+unit|light\s+fitting|extension\s+lead)\b|\b(?:plug|socket|electrics|wiring|extension\s+lead|consumer\s+unit)\b[^.]{0,40}\b(?:wet|water|damp)\b/i },
    { id: "tripping", res: "STOP_USE", re: /\btrip(?:s|ping|ped)?\b[^.]{0,30}\b(?:electric\w*|fuse|breaker|rcd|power|switch)\b|\bblows?\s+(?:the\s+)?fuse\b|\bblew\s+(?:the\s+)?fuse\b/i },
    { id: "explosion", res: "STOP_USE", re: /\bexplod\w*|\bexplosion\b|\bbang\b[^.]{0,20}\b(?:smoke|smell|flash|spark)\w*|\bflash(?:es|ed)?\b[^.]{0,30}\bbang(?:s|ed)?\b/i },
    { id: "said_unsafe", res: "STOP_USE", ans: "unsafe" },
    { id: "gas_appliance", res: "PROFESSIONAL_ONLY", re: /\bboiler\b|\bcombi\b|\bgas\s+(?:hob|cooker|oven|fire|heater|appliance|supply|meter|pipe)\b|\bpilot\s+light\b|\bflue\b/i, cats: ["boiler"] },
    { id: "internal_mains", res: "PROFESSIONAL_ONLY", re: /\b(?:open(?:ing)?|take|taking|took|remove|removing)\b[^.]{0,15}\b(?:back|casing|cover|panel|lid)\s+off\b|\b(?:open(?:ing)?\s+(?:it|up|the\s+(?:back|casing|case|cover|panel)))\b|\binside\s+the\s+(?:casing|machine|unit|case|plug)\b|\b(?:replace|replacing|change|changing|fix|fixing|rewire|rewiring)\b[^.]{0,15}\b(?:motor|element|heating\s+element|pcb|circuit\s+board|control\s+board|main\s+board|capacitor|thermostat|wiring|fuse\s+inside)\b|\bhigh[- ]voltage\b|\bcapacitor\b|\bmagnetron\b/i },
    { id: "car_safety", res: "PROFESSIONAL_ONLY", re: /\bbrak(?:e|es|ing)\b|\bsteering\b|\bair\s*bags?\b|\bfuel\s+(?:leak|smell|line|pump|tank)\b|\bpetrol\s+(?:leak|smell)\b|\bdiesel\s+(?:leak|smell)\b|\bunder(?:neath)?\s+the\s+(?:car|van|vehicle)\b|\bjack(?:ed|ing)?\s+(?:it\s+)?up\b|\bsuspension\b|\btyres?\s+(?:blew|blown|burst|bulge)\b|\bseat\s*belts?\b|\b(?:ev|hybrid|traction)\s+batter(?:y|ies)\b/i },
    { id: "class_microwave", res: "OFFICIAL_INFORMATION_ONLY", cats: ["microwave"] },
    { id: "class_car", res: "OFFICIAL_INFORMATION_ONLY", cats: ["car"] },
    { id: "class_fridge", res: "OFFICIAL_INFORMATION_ONLY", cats: ["fridge_freezer"] },
    { id: "class_oven", res: "OFFICIAL_INFORMATION_ONLY", cats: ["oven"] },
    { id: "class_unknown", res: "OFFICIAL_INFORMATION_ONLY", cats: ["other", ""] }
  ];
  var EXTERNAL = ["washing_machine", "dishwasher", "tumble_dryer", "vacuum", "printer", "router", "coffee"];
  var WHY = {
    STOP_USE: "What you described could be dangerous. Stop using it.",
    PROFESSIONAL_ONLY: "Only a qualified person should work on this. Sorted won’t suggest any checks.",
    OFFICIAL_INFORMATION_ONLY: "Sorted will point you to official information and help to contact them, not checks you do yourself.",
    SAFE_EXTERNAL_CHECKS: "Nothing you’ve said sounds dangerous. If anything changes, stop using it."
  };
  function norm(s) { return " " + String(s || "").replace(/[’‘]/g, "'").replace(/\s+/g, " ") + " "; }
  /* Words with their negated danger phrases removed. */
  function unNegated(s) { return norm(s).replace(NEG, " "); }
  function stronger(a, b) { return ORDER.indexOf(a) >= ORDER.indexOf(b) ? a : b; }
  /* decide({category, words, answers:{unsafe:true}}, now) → SafetyDecision. `words` is everything the person said
     about the problem (one string or a list). */
  function decide(inp, now) {
    inp = inp || {};
    var cat = String(inp.category || ""), said = [].concat(inp.words || []).join(". "), x = unNegated(said), ans = inp.answers || {};
    var res = EXTERNAL.indexOf(cat) >= 0 ? "SAFE_EXTERNAL_CHECKS" : "OFFICIAL_INFORMATION_ONLY", hit = [];
    RULES.forEach(function (r) {
      var on = false;
      if (r.ans) on = !!ans[r.ans];
      if (!on && r.re) on = r.re.test(x);
      if (!on && r.cats) on = r.cats.indexOf(cat) >= 0;
      if (on) { hit.push(r.id); res = stronger(res, r.res); }
    });
    if (inp.legacyDanger) { hit.push("page_danger"); res = "STOP_USE"; }
    return { product_class: cat || "other", matched_rules: hit, result: res, reason: WHY[res], rule_version: RULE_VERSION, created_at: now };
  }
  /* What the result allows. Phase 1 never offers checks; these say what later phases may do. */
  function allows(dec) {
    var r = dec && dec.result;
    return { checks: r === "SAFE_EXTERNAL_CHECKS", supportLink: r !== "STOP_USE", contact: true, stop: r === "STOP_USE", pro: r === "PROFESSIONAL_ONLY" };
  }
  return { RULE_VERSION: RULE_VERSION, ORDER: ORDER, RULES: RULES, decide: decide, allows: allows, unNegated: unNegated, WHY: WHY };
})();
