// Phase 1.5 audit: dangerous and safe descriptions, written the way people write, through the product safety rules.
// Every dangerous one must stop (STOP_USE or PROFESSIONAL_ONLY); every safe one must not be STOP_USE.
import { load, ok, done } from './load.mjs';
const S = load().safety, NOW = Date.UTC(2026, 9, 10);
const STOP = [
  ['washing_machine', 'theres sparks coming from the back'], ['washing_machine', 'saw a spark when I plugged it in'],
  ['tumble_dryer', 'smells like something is burning'], ['tumble_dryer', 'burnt smell from the drum'], ['tumble_dryer', 'there was a flash and a bang'],
  ['dishwasher', 'smoke coming out the bottom'], ['dishwasher', 'its smoking'], ['coffee', 'the plug is scorched'],
  ['coffee', 'the cable got really hot and melted a bit'], ['vacuum', 'battery is swollen'], ['vacuum', 'the battery pack has puffed up'],
  ['vacuum', 'the battery is bulging out of the case'], ['printer', 'the lead is frayed'], ['printer', 'wires are showing on the cable'],
  ['router', 'the power adapter is too hot to touch'], ['washing_machine', 'water leaking onto the plug socket'],
  ['washing_machine', 'the socket behind it is wet'], ['fridge_freezer', 'it trips the electrics every time'], ['fridge_freezer', 'keeps tripping the fuse box'],
  ['oven', 'I can smell gas'], ['oven', 'gas smell in the kitchen'], ['boiler', 'carbon monoxide alarm is going off'],
  ['microwave', 'sparking inside when it runs'], ['microwave', 'flames inside'], ['other', 'I got an electric shock off it'],
  ['other', 'it tingles when I touch the metal'], ['other', 'it is overheating badly'], ['coffee', 'melted plastic smell'],
  ['tumble_dryer', 'caught fire'], ['washing_machine', 'the plug has burn marks'], ['vacuum', 'the charger smells of burning'],
  ['other', 'there is exposed copper wire'], ['dishwasher', 'water dripping into the plug'], ['other', 'it blew the fuse'],
];
const PRO = [
  ['boiler', 'no hot water'], ['boiler', 'the pressure keeps dropping'], ['other', 'my combi boiler is showing an error'],
  ['oven', 'the gas hob wont light'], ['other', 'the pilot light keeps going out'], ['car', 'the brakes are squealing'],
  ['car', 'steering feels loose'], ['car', 'airbag light is on'], ['car', 'smell of petrol'], ['washing_machine', 'should I take the back off'],
  ['oven', 'I need to replace the heating element'], ['microwave', 'can I replace the magnetron'], ['washing_machine', 'the motor needs changing, can I change the motor myself'],
];
const SAFE = [
  ['washing_machine', 'it wont drain'], ['washing_machine', 'it stopped mid cycle'], ['washing_machine', 'no smoke or burning smell, it just wont spin'],
  ['dishwasher', 'not cleaning properly'], ['tumble_dryer', 'clothes still damp after drying'], ['vacuum', 'lost suction'],
  ['printer', 'paper jam'], ['printer', 'it says the ink is empty'], ['router', 'the wifi keeps dropping'], ['coffee', 'water not coming through'],
  ['washing_machine', 'error code E18'], ['dishwasher', 'there is water left in the bottom'], ['washing_machine', 'it leaks from the door seal onto the floor'],
  ['washing_machine', 'nothing is sparking, it just beeps'], ['vacuum', 'the battery runs out quickly'], ['tumble_dryer', 'it is noisy'],
];
const strong = r => r === 'STOP_USE' || r === 'PROFESSIONAL_ONLY';
STOP.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(d.result === 'STOP_USE', 'STOP: "' + w + '" (' + c + ') got ' + d.result + ' ' + d.matched_rules); });
PRO.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(strong(d.result), 'PROFESSIONAL: "' + w + '" (' + c + ') got ' + d.result); });
SAFE.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(d.result !== 'STOP_USE', 'SAFE: "' + w + '" (' + c + ') got ' + d.result + ' ' + d.matched_rules); });
done('safety corpus');
