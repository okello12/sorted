// Unit tests for the product modules (docs/PRODUCT_PHASE1.md). Run: node tests/product/units.mjs
import { load, ok, eq, done } from './load.mjs';
const P = load(), R = P.record, I = P.intake, S = P.safety, M = P.makers, RT = P.route;
const NOW = new Date(2026, 9, 10, 12, 0).getTime();

// ---------- identification ----------
let r = I.readLabel('BOSCH\nSerie 6\nWashing machine\nE-Nr. WGG244ZCGB/01\nFD 1234 56789\nS/N: 123456789\n220-240V 50Hz 2300W');
eq([r.brand, r.category, r.model, r.modelHow, r.serial], ['Bosch', 'washing_machine', 'WGG244ZCGB', 'labelled', '123456789'], 'clear Bosch label');
r = I.readLabel('Model No: WMB71643PTE\nSerial No. 22-401234-10\nBeko');
eq([r.brand, r.model, r.serial], ['Beko', 'WMB71643PTE', '22-401234-10'], 'Beko label with Model No and Serial No.');
r = I.readLabel('BOSCH Washing machine E-Nr. WGG244ZCGB/01 SIN: 123456789 220-240V 50Hz');
eq([r.model, r.serial], ['WGG244ZCGB', '123456789'], 'OCR’s usual misreading of S/N as SIN still reads the serial');
r = I.readLabel('~~ ;; .. ,, ~');
eq(r.quality, 'failed', 'a blurred read fails');
eq([r.brand, r.model, r.serial], ['', '', ''], 'a failed read proposes nothing');
r = I.readLabel('');
eq(r.quality, 'failed', 'an empty read fails');
r = I.readLabel('Miele\nW1 Classic\n230V');
eq([r.brand, r.model, r.serial], ['Miele', '', ''], 'brand only: no model or serial');
r = I.readLabel('Type: WAN28281GB  Serial 4500123');
eq([r.brand, r.model, r.serial], ['', 'WAN28281GB', '4500123'], 'no brand: the labelled model and serial still read');
r = I.readLabel('Model: WGG244ZCGB\nModel: WAN28100GB\nBosch');
eq([r.model, r.models], ['', ['WGG244ZCGB', 'WAN28100GB']], 'two model numbers: none proposed, both offered');
r = I.readLabel('Bosch WGG244ZCGB serial: 123456789');
eq([r.brand, r.model, r.modelHow, r.serial], ['Bosch', 'WGG244ZCGB', 'unlabelled', '123456789'], 'an unlabelled model is marked unlabelled');
r = I.readLabel('Dyson V11 SV14 serial: AB1-UK-HBA1234');
eq([r.brand, r.model, r.serial], ['Dyson', '', 'AB1-UK-HBA1234'], 'short unlabelled tokens are not guessed as a model');
r = I.readLabel('A Bosch washing machine on a kitchen floor');
eq([r.brand, r.category, r.model], ['Bosch', 'washing_machine', ''], 'a product photo gives brand and kind, never a model');
r = I.readLabel('Model: 230V');
eq(r.model, '', 'a voltage is not a model');
r = I.readLabel('Model: WGG244ZCGB S/N: WGG244ZCGB');
ok(r.model !== r.serial || !r.model, 'a model and serial are never the same value');
r = I.readLabel('snack 12345 service 99999 Model: ABC1234');
eq([r.serial, r.model], ['', 'ABC1234'], '"snack" and "service" are not serial labels');
r = I.readLabel('Samsung WW90T534DAW serial number 0B7H5ABR800123');
eq([r.brand, r.serial], ['Samsung', '0B7H5ABR800123'], 'a maker known by name only is still read as the brand');

// ---------- receipts ----------
let rc = I.readReceipt('CURRYS PC WORLD\n14/02/2026 13:22\nBosch washer £499.00', NOW);
eq([rc.retailer, rc.bought, rc.dates], ['Currys', '2026-02-14', ['2026-02-14']], 'a correct receipt');
rc = I.readReceipt('Argos\nOrder date 3 March 2025\nDelivered 7 March 2025', NOW);
eq([rc.bought, rc.dates], ['', ['2025-03-03', '2025-03-07']], 'two dates: none proposed, both offered');
rc = I.readReceipt('AO.com 02/14/2026', NOW);
eq([rc.bought, rc.odd], ['', true], 'a month-first date is never read, and flagged');
rc = I.readReceipt('John Lewis 14/02/2027', NOW);
eq([rc.retailer, rc.bought], ['John Lewis', ''], 'a future date is dropped');
rc = I.readReceipt('Corner shop ltd 14/02/2026', NOW);
eq([rc.retailer, rc.bought], ['', '2026-02-14'], 'an unknown shop is not invented');

// ---------- the record ----------
let rec = R.make('p1', NOW);
ok(R.propose(rec, 'brand', 'Bosch', 'label_photo', NOW), 'a reading is proposed');
eq([R.value(rec, 'brand'), R.candidate(rec, 'brand'), R.status(rec, 'brand')], ['', 'Bosch', 'candidate'], 'OCR is a candidate, never a fact');
ok(R.confirm(rec, 'brand', NOW + 1), 'Looks right confirms');
eq([R.value(rec, 'brand'), R.status(rec, 'brand')], ['Bosch', 'confirmed'], 'confirmed');
ok(!R.propose(rec, 'brand', 'Beko', 'label_photo', NOW + 2), 'a later reading never overwrites a fact');
R.propose(rec, 'model', 'WGG244ZCG8', 'label_photo', NOW);
R.set(rec, 'model', 'wgg244zcgb', NOW + 3);
eq([R.value(rec, 'model'), R.status(rec, 'model')], ['WGG244ZCGB', 'corrected'], 'a correction is the value, marked corrected');
eq(R.field(rec, 'model').was.map(w => [w.v, w.st]), [['WGG244ZCG8', 'candidate']], 'the wrong reading is kept in history');
R.propose(rec, 'serial', '123456789', 'label_photo', NOW);
R.set(rec, 'serial', '123456780', NOW + 4);
eq(R.field(rec, 'serial').was.map(w => w.v), ['••••6789'], 'a replaced serial is kept masked, never in full');
eq(R.mask('123456789'), '••••6789', 'mask shows the last four');
eq(R.mask('AB12'), '••••12', 'a short serial shows two');
R.propose(rec, 'serial', '999999999', 'label_photo', NOW + 5);
eq(R.value(rec, 'serial'), '123456780', 'a reading never replaces a typed serial');
let rec2 = R.make('p2', NOW);
R.propose(rec2, 'serial', '555566667777', 'label_photo', NOW);
R.reject(rec2, 'serial', NOW + 1);
eq([R.status(rec2, 'serial'), R.field(rec2, 'serial').v], ['rejected', '••••7777'], 'a rejected serial is kept masked');
ok(!R.propose(rec2, 'retailer', 'Currys', 'nowhere', NOW), 'an unknown source is refused');
R.set(rec, 'category', 'washing_machine', NOW);
eq(R.label(rec), 'Bosch washing machine', 'label from facts');
const safe = R.safeCopy(rec);
ok(JSON.stringify(safe).indexOf('123456780') < 0, 'safeCopy carries no full serial');
eq(R.scrub(rec, 'Serial 123456780 please'), 'Serial ••••6780 please', 'scrub masks the serial in text');
// purchase facts and the repair engine
let rp = R.make('p3', NOW);
R.propose(rp, 'retailer', 'Currys', 'receipt', NOW); R.propose(rp, 'bought', '2026-02-14', 'receipt', NOW);
eq(R.forFix(rp, NOW), {}, 'unconfirmed purchase details reach nothing');
R.confirm(rp, 'retailer', NOW); R.confirm(rp, 'bought', NOW);
eq(R.forFix(rp, NOW), { seller: 'Currys', age: 'lt1' }, 'confirmed purchase details reach the repair engine');
ok(!R.set(rp, 'bought', '2026-02-41', NOW), 'an impossible date is refused');
eq(R.value(rp, 'bought'), '2026-02-14', 'and the confirmed date stays');
R.set(rp, 'bought', '2019-01-01', NOW);
eq(R.ageBand(rp, NOW), 'gt6', 'over six years');
eq(R.ready(rec, false).map(x => x.v), ['Bosch WGG244ZCGB, washing machine', 'Serial ••••6780'], 'ready rows mask the serial');
eq(R.ready(rec, true)[1].v, 'Serial 123456780', 'the full serial only when asked');

// ---------- safety ----------
const dec = (words, cat, ans) => S.decide({ category: cat || 'washing_machine', words, answers: ans }, NOW);
const res = (w, c, a) => dec(w, c, a).result;
[['It is sparking at the back', 'sparking'], ['there is a burning smell', 'burning'], ['smoke came out', 'smoke'],
 ['I can smell gas', 'gas_fumes'], ['the battery is swollen', 'battery'], ['the cable is frayed and exposed', 'wiring'],
 ['water is pooling near the plug socket', 'water_electrics'], ['it is overheating', 'overheating'],
 ['the plug gets really hot', 'overheating'], ['it keeps tripping the electrics', 'tripping'], ['I got a shock off it', 'shock'],
 ['scorch marks on the back', 'burning'], ['the battery is bulging', 'battery'], ['bare wires showing', 'wiring']].forEach(([w, id]) => {
  const d = dec(w); ok(d.result === 'STOP_USE' && d.matched_rules.indexOf(id) >= 0, 'STOP_USE for "' + w + '" by ' + id + ' (got ' + d.result + ' ' + d.matched_rules + ')');
});
eq(res('my brakes are squealing', 'car'), 'PROFESSIONAL_ONLY', 'a brake problem is professional only');
eq(res('the steering is heavy', 'car'), 'PROFESSIONAL_ONLY', 'steering');
eq(res('no hot water', 'boiler'), 'PROFESSIONAL_ONLY', 'a boiler problem is professional only');
eq(res('the boiler pressure is low', 'other'), 'PROFESSIONAL_ONLY', 'a boiler named in words, any category');
eq(res('should I take the back off to look', 'washing_machine'), 'PROFESSIONAL_ONLY', 'opening the casing is professional only');
eq(res('the heating element needs replacing, can I replace the element', 'oven'), 'PROFESSIONAL_ONLY', 'replacing an element');
eq(res('the wipers stopped', 'car'), 'OFFICIAL_INFORMATION_ONLY', 'a car otherwise: official information only');
eq(res('not cold', 'fridge_freezer'), 'OFFICIAL_INFORMATION_ONLY', 'a fridge: official information only');
eq(res('turntable stopped', 'microwave'), 'OFFICIAL_INFORMATION_ONLY', 'a microwave: official information only');
eq(res('it does something', 'other'), 'OFFICIAL_INFORMATION_ONLY', 'unknown: official information only');
eq(res('it won’t drain, water sitting in the drum'), 'SAFE_EXTERNAL_CHECKS', 'a washing machine that won’t drain');
eq(res('no smoke or burning smell, it just won’t spin'), 'SAFE_EXTERNAL_CHECKS', 'negated danger words clear');
eq(res('I can’t smell gas'), 'SAFE_EXTERNAL_CHECKS', 'can’t smell gas clears');
eq(res('nothing is sparking'), 'SAFE_EXTERNAL_CHECKS', 'nothing is sparking clears');
eq(res('there’s no smoke but it smells of burning'), 'STOP_USE', 'a negation clears only what it governs');
eq(res('no water near the plug'), 'SAFE_EXTERNAL_CHECKS', 'no water near the plug clears');
eq(res('leaking when I switch it on'), 'SAFE_EXTERNAL_CHECKS', 'a leak with a switch is not water on electrics');
eq(res('fine', 'washing_machine', { unsafe: true }), 'STOP_USE', 'the person saying it is unsafe stops');
eq(S.decide({ category: 'printer', words: 'paper jam', legacyDanger: true }, NOW).result, 'STOP_USE', 'the page’s own danger words stop too');
const d1 = dec('sparking');
eq([d1.rule_version, d1.created_at, d1.product_class], [S.RULE_VERSION, NOW, 'washing_machine'], 'the decision records its version, time and class');
ok(!S.allows(d1).supportLink && S.allows(d1).stop, 'STOP_USE allows no support link presented as a fix');
ok(!S.allows(dec('paper jam', 'printer')).checks === false, 'external checks allowed only by the class');

// ---------- the registry ----------
ok(M.MAKERS.length >= 5, 'makers listed');
M.MAKERS.forEach(e => ['support', 'repair', 'contact'].forEach(k => { if (e[k]) ok(M.isOfficial(e[k], e), e.name + ' ' + k + ' is on its own domain'); }));
M.SHOPS.forEach(e => { if (e.help) ok(M.isOfficial(e.help, e), e.name + ' help is on its own domain'); });
const bosch = M.makerByName('Bosch');
ok(!M.isOfficial('https://bosch-manuals.example.com/wgg244', bosch), 'a look-alike domain is not official');
ok(!M.isOfficial('https://www.bosch-home.co.uk.evil.com/x', bosch), 'a suffix trick is not official');
ok(!M.isOfficial('http://www.bosch-home.co.uk/customer-service', bosch), 'http is not official');
ok(!M.isOfficial('https://www.lg.com/us/support/', M.makerByName('LG')), 'LG’s US pages are not LG UK');
ok(M.isOfficial('https://www.lg.com/uk/support/contact-us/', M.makerByName('LG')), 'LG UK is');
eq(M.brandIn('made by BOSCH for Bosch'), 'Bosch', 'brand by alias, any case');
eq(M.makerByName('Acme'), null, 'an unknown maker has no entry');
['Samsung', 'Hotpoint', 'Indesit', 'Hoover', 'AEG', 'Electrolux', 'Philips', 'HP', 'Epson', 'Canon'].forEach(n => {
  const e = M.makerByName(n); ok(e && M.link(e, 'support'), n + ' has a checked UK support link');
});
eq(M.makerByName('Whirlpool'), null, 'Whirlpool has no entry: its UK repair site names no owner');
eq(M.brandIn('Whirlpool FFB 8448'), 'Whirlpool', 'Whirlpool is still recognised by name');
eq(M.brandIn('Motor 1.5 HP 230V'), '', 'horsepower on a motor label is not HP');
eq(M.brandIn('HP DeskJet 2720e'), 'HP', 'HP on a printer label is HP');
ok(!M.isOfficial('https://www.samsung.com/us/support/', M.makerByName('Samsung')), 'Samsung’s US pages are not Samsung UK');
ok(!M.isOfficial('https://indesitservice.co.uk/repair', M.makerByName('Indesit')), 'Indesit’s unnamed repair domain is not linked');
ok(/^\d{1,2} [A-Z][a-z]{2} \d{4}$/.test(M.CHECKED), 'the registry carries the date it was checked');

// ---------- routes ----------
const confirmed = (o) => { const x = R.make('r', NOW); Object.keys(o).forEach(k => R.set(x, k, o[k], NOW)); return x; };
const safeDec = S.decide({ category: 'washing_machine', words: 'won’t drain' }, NOW);
let rt = RT.route({ rec: confirmed({ brand: 'Bosch', category: 'washing_machine', retailer: 'Argos', bought: '2026-02-14' }), safety: safeDec }, NOW);
eq([rt.key, rt.who], ['RETAILER', 'Argos'], 'retailer route from confirmed purchase');
ok(/14 February 2026/.test(rt.reason) && /Citizens Advice/.test(rt.reason) && rt.basis.length === 1, 'reason states the facts and names its source');
ok(/^https:\/\/help\.argos\.co\.uk\//.test(rt.url), 'the retailer’s checked help page');
eq(rt.alt.map(a => a.key), ['MANUFACTURER', 'QUALIFIED_REPAIR'], 'the others beneath');
let un = R.make('u', NOW); R.set(un, 'brand', 'Bosch', NOW); R.propose(un, 'retailer', 'Argos', 'receipt', NOW); R.propose(un, 'bought', '2026-02-14', 'receipt', NOW);
rt = RT.route({ rec: un, safety: safeDec }, NOW);
eq([rt.key, rt.who], ['MANUFACTURER', 'Bosch'], 'unconfirmed purchase details never drive the route');
ok(/doesn’t know where or when/.test(rt.reason), 'unknown purchase details are said to be unknown');
rt = RT.route({ rec: confirmed({ brand: 'Bosch', retailer: 'Argos', bought: '2018-01-01' }), safety: safeDec }, NOW);
eq(rt.key, 'MANUFACTURER', 'over six years: the maker first');
rt = RT.route({ rec: confirmed({ brand: 'Samsung', category: 'washing_machine' }), safety: safeDec }, NOW);
eq([rt.key, rt.url], ['MANUFACTURER', 'https://www.samsung.com/uk/support/repair/'], 'Samsung with no purchase details: Samsung UK’s repair page');
rt = RT.route({ rec: confirmed({ brand: 'Acme', category: 'printer' }), safety: safeDec }, NOW);
eq(rt.key, 'QUALIFIED_REPAIR', 'no registry entry: a repairer');
ok(/doesn’t have a checked support page for Acme/.test(rt.reason), 'and says so');
rt = RT.route({ rec: confirmed({ brand: 'Bosch', category: 'boiler' }), safety: S.decide({ category: 'boiler', words: 'no heat' }, NOW) }, NOW);
eq([rt.key, rt.basis.length], ['QUALIFIED_REPAIR', 1], 'a boiler: a Gas Safe engineer, with the HSE source');
rt = RT.route({ rec: confirmed({ category: 'car' }), safety: S.decide({ category: 'car', words: 'brakes grinding' }, NOW) }, NOW);
eq(rt.key, 'QUALIFIED_REPAIR', 'a car’s brakes: a garage');
rt = RT.route({ rec: confirmed({ brand: 'Bosch', retailer: 'Argos', bought: '2026-02-14' }), safety: dec('sparking') }, NOW);
ok(/^Keep it switched off\./.test(rt.reason), 'a stopped product is told to stay off');
rt = RT.route({ rec: confirmed({ brand: 'Bosch' }), safety: safeDec, responsible: 'landlord', party: 'My landlord', partyResp: 'your landlord' }, NOW);
eq(rt.key, 'OTHER', 'someone else’s job: OTHER');
rt = RT.route({ rec: confirmed({ brand: 'Bosch' }), safety: safeDec, fixed: true }, NOW);
eq(rt.key, 'SELF_RESOLVED', 'fixed');
// a route never leaks a serial
rt = RT.route({ rec: confirmed({ brand: 'Bosch', serial: '123456789', retailer: 'Argos' }), safety: safeDec }, NOW);
ok(JSON.stringify(rt).indexOf('123456789') < 0, 'a route carries no serial');

// ---------- doubt about a model read from a photo (external audit, 11 Oct 2026; the readings are the audit's own) ----------
r = I.readLabel('BOSCH E-Nr. WGG244ZCGB/01 S/N: 123456789', { conf: 90 });
eq([r.model, r.doubt, r.withheld], ['WGG244ZCGB', [], []], 'a clear photo: the model with no doubt');
r = I.readLabel('BOSCH E-Nr. WGG244zc6p/9, S/N: 123456789', { conf: 71 });
eq([r.model, r.doubt], ['WGG244ZC6P', ['photo', 'case']], 'tilted: offered, with doubt (photo, lower case inside)');
r = I.readLabel('BOSCH E-Nr. WGG244ZCGBI0L', { conf: 76 });
eq(r.doubt, ['photo', 'confusable'], 'low resolution: doubt (an I beside a 0)');
r = I.readLabel('BOSCH E-Nr. WGG2442CGBO1', { conf: 84 });
eq(r.doubt, ['photo', 'confusable'], 'blurred: doubt (an O beside a 1)');
r = I.readLabel('BOSCH E-Nr. WGG2A4ZCORITL S/N: 123456789', { conf: 21 });
eq([r.model, r.models, r.withheld, r.doubt, r.brand, r.serial], ['', [], ['WGG2A4ZCORITL'], ['unclear'], 'Bosch', '123456789'], 'too unclear: no model offered, the make and serial still read');
r = I.readLabel('Samsung WW90T534DAW serial number 0B7H5ABR800123');
eq([r.model, r.doubt], ['WW90T534DAW', []], 'no confidence given (typed or pasted text): no doubt from the photo');
eq(I.modelDoubt('WGG244zCGB', 86), ['case'], 'a correct read with a lower-case letter is still doubted (a warning, not a refusal)');

done('product units');
