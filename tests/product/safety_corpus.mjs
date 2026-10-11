// Phase 1.5 audit, extended by the external audit of 11 October 2026 (ps-3): dangerous and safe descriptions, written the way people write, through the product safety rules.
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
  // ps-3 (external audit, 11 Oct 2026): hedged, past, paused and mixed descriptions must never clear a real warning
  ['washing_machine', "I don't think it is smoking, but it smells strange"], ['washing_machine', "I don't think it's smoking but there's a burning smell"],
  ['tumble_dryer', "no smoke but it smells of burning"], ['washing_machine', "no sparks, but the plug is hot"],
  ['washing_machine', "it's not sparking any more but it did earlier"], ['washing_machine', "it isn't smoking now but it was last night"],
  ['washing_machine', "didn't see any sparks but heard crackling from the socket"], ['coffee', "not burning, but there is a strange electrical smell"],
  ['coffee', 'smells like fish or hot plastic'], ['other', "there's a fishy smell from the socket"], ['router', 'the adapter is buzzing and smells funny'],
  ['vacuum', 'battery got hot and hissed'], ['vacuum', 'the battery is leaking'], ['other', 'e-bike battery is smoking'],
  ['other', 'lithium battery on the scooter got really hot while charging'], ['washing_machine', 'water came out and now the lights flicker and the socket clicks'],
  ['other', 'the light switch is warm and buzzing'], ['other', 'socket is discoloured brown'], ['other', 'the extension lead is melting'],
  ['washing_machine', 'the cable is cut but not touching anything'], ['other', 'lights dim and there is a crackle in the fuse box'],
  ['boiler', "I can't tell if that's gas I'm smelling"], ['boiler', "I don't smell gas but the CO alarm is beeping"],
  ['boiler', "no gas smell, but the flame is yellow and there's soot"], ['boiler', 'black marks around the boiler and I feel dizzy'],
  ['oven', "the hob clicks and there's a smell of rotten eggs"], ['fridge_freezer', 'the back of the fridge is too hot and smells'],
  ['microwave', 'it sparks and bangs when it runs'], ['tumble_dryer', "it doesn't smoke, it just catches fire sometimes"],
  ['dishwasher', 'nothing wrong apart from smoke coming out'], ['washing_machine', 'not leaking from the door, but water is pooling round the plug'],
];
const PRO = [
  ['boiler', 'no hot water'], ['boiler', 'the pressure keeps dropping'], ['other', 'my combi boiler is showing an error'],
  ['oven', 'the gas hob wont light'], ['other', 'the pilot light keeps going out'], ['car', 'the brakes are squealing'],
  ['car', 'steering feels loose'], ['car', 'airbag light is on'], ['car', 'smell of petrol'], ['washing_machine', 'should I take the back off'],
  ['oven', 'I need to replace the heating element'], ['microwave', 'can I replace the magnetron'], ['washing_machine', 'the motor needs changing, can I change the motor myself'],
  ['car', "the brakes don't feel right"], ['car', 'brake pedal goes to the floor'], ['car', 'tyre has a bulge'], ['car', 'ABS light on'],
  ['car', 'I can smell fuel in the car'], ['car', 'the EV battery warning is on'], ['car', "seatbelt won't latch"], ['other', 'the consumer unit keeps tripping'],
  ['boiler', "I don't think it's gas but the boiler is making a banging noise"],
];
const SAFE = [
  ['washing_machine', 'it wont drain'], ['washing_machine', 'it stopped mid cycle'], ['washing_machine', 'no smoke or burning smell, it just wont spin'],
  ['dishwasher', 'not cleaning properly'], ['tumble_dryer', 'clothes still damp after drying'], ['vacuum', 'lost suction'],
  ['printer', 'paper jam'], ['printer', 'it says the ink is empty'], ['router', 'the wifi keeps dropping'], ['coffee', 'water not coming through'],
  ['washing_machine', 'error code E18'], ['dishwasher', 'there is water left in the bottom'], ['washing_machine', 'it leaks from the door seal onto the floor'],
  ['washing_machine', 'nothing is sparking, it just beeps'], ['vacuum', 'the battery runs out quickly'], ['tumble_dryer', 'it is noisy'],
  ['washing_machine', 'it smells bad inside the drum'], ['dishwasher', 'it smells of fish'], ['washing_machine', 'the drum is noisy and clicks'],
  ['coffee', 'the switch clicks off too early'], ['vacuum', 'the battery light flashes'], ['other', 'my phone gets warm while charging'],
  ['washing_machine', 'brown water comes out'], ['fridge_freezer', 'it hums loudly'], ['washing_machine', "it was fine before, now it won't drain"],
  ['tumble_dryer', 'not drying, no burning smell, nothing hot'], ['washing_machine', 'no sparks, no smoke, nothing strange'],
];
const strong = r => r === 'STOP_USE' || r === 'PROFESSIONAL_ONLY';
STOP.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(d.result === 'STOP_USE', 'STOP: "' + w + '" (' + c + ') got ' + d.result + ' ' + d.matched_rules); });
PRO.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(strong(d.result), 'PROFESSIONAL: "' + w + '" (' + c + ') got ' + d.result); });
SAFE.forEach(([c, w]) => { const d = S.decide({ category: c, words: w }, NOW); ok(d.result !== 'STOP_USE', 'SAFE: "' + w + '" (' + c + ') got ' + d.result + ' ' + d.matched_rules); });
done('safety corpus');
