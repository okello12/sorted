# Adversarial language corpus for Sorted's promise reader (2 October 2026).
# The rule: no commitment from another party, no promise card. Instructions, information, conditionals, maybes,
# questions, your own plans and your own requests are not commitments.
# NOT = must give no card. YES = must give a card. MSG_* = whole pasted messages.
import itertools, datetime
from dates import ahead

PARTIES = ["Currys", "British Gas", "Amazon", "EE", "Sky", "the landlord", "the council", "DPD", "Royal Mail", "Argos",
           "John Lewis", "Octopus", "Thames Water", "BT", "Vodafone", "Aviva", "my letting agent", "the plumber"]
F = ahead(16)['dm']                     # a future date like "18 October"
DAYS = ["tomorrow", "on Friday", "next Tuesday", "on " + F, "on Thursday morning"]
VERBS = ["come", "send someone", "fix it", "deliver it", "pay the refund", "call back"]

def cyc(templates, n_per):
    out = []
    pi = itertools.cycle(PARTIES); di = itertools.cycle(DAYS); vi = itertools.cycle(VERBS)
    for t in templates:
        for _ in range(n_per):
            p = next(pi); out.append(t.format(P=p, Pc=p[0].upper() + p[1:], D=next(di), V=next(vi), F=F))
    return out

NOT_GROUPS = {
  "your own plan": cyc([
    "I'll call {P} {D}.", "I need to chase {P} {D}.", "I'm going to email {P} {D}.", "My plan is to ring {P} {D}.",
    "I promised myself I'd sort {P} out {D}.", "I told {P} I'd send the photos {D}.", "I said I'd be in {D} for {P}.",
    "I have to call {P} again {D}.", "I should ring {P} {D}.", "I want to complain to {P} {D}.",
  ], 3),
  "maybe": cyc([
    "{Pc} said they might {V} {D}.", "{Pc} said maybe they'll {V} {D}.", "{Pc} said they could possibly {V} {D}.",
    "{Pc} said hopefully they'll {V} {D}.", "{Pc} said they'll try to {V} {D}.", "{Pc} said they'd probably {V} {D}.",
    "{Pc} said they would aim to {V} {D}.", "{Pc} said it should be sorted {D}.", "{Pc} said they may be able to {V} {D}.",
    "{Pc} said they're not sure, perhaps {D}.",
  ], 3),
  "condition": cyc([
    "{Pc} said if the part arrives they'll {V} {D}.", "{Pc} said they'll {V} {D} as long as I send the receipt.",
    "{Pc} said they'll {V} {D} provided the claim is approved.", "{Pc} said they'll {V} {D} unless they're busy.",
    "{Pc} said subject to approval they'll {V} {D}.", "{Pc} said once the claim is approved they'll {V} {D}.",
    "{Pc} said assuming the stock comes in they'll {V} {D}.", "{Pc} said depending on the engineer they'll {V} {D}.",
  ], 3),
  "information": cyc([
    "{Pc} said they're open {D} from 9 to 5.", "{Pc} said the next available slot is {D}.",
    "{Pc} said engineers are available {D}.", "{Pc} said the office closes at 5 {D}.",
    "{Pc} said refunds usually take 5 working days.", "{Pc} said it can take up to 10 days.",
    "{Pc} said delivery normally takes 3 days.", "{Pc} said the sale ends {D}.", "{Pc} said the offer expires {D}.",
    "{Pc} said their lines are open {D}.", "{Pc} said refunds take 3 to 5 days.", "{Pc} said they'll be open {D}.",
  ], 3),
  "instruction": cyc([
    "{Pc} said to call back {D}.", "{Pc} told me to ring again {D}.", "{Pc} asked me to send photos {D}.",
    "{Pc} said please email them {D}.", "{Pc} said I should check the app {D}.", "{Pc} said call again {D} if nothing arrives.",
    "{Pc} said check back {D}.", "{Pc} said I need to be home {D}.", "{Pc} said ring them {D}.", "{Pc} said try again {D}.",
  ], 3),
  "refusal or no date": cyc([
    "{Pc} wouldn't promise anything for {D}.", "{Pc} refused to give a date.", "{Pc} couldn't confirm a date.",
    "{Pc} said they can't guarantee {D}.", "{Pc} didn't say when.", "Nobody from {P} has said when.",
    "{Pc} still hasn't given me a date.", "{Pc} said they don't know when.", "{Pc} said there's no date yet.",
    "{Pc} promised nothing.", "{Pc} won't commit to a date.",
  ], 3),
  "question": cyc([
    "Will {P} {V} {D}?", "Did {P} say they'd {V} {D}?", "Can {P} {V} {D}?", "Should I expect {P} {D}?",
    "Is {P} coming {D}?",
  ], 3),
  "your own request": cyc([
    "I asked {P} to {V} {D}.", "I've requested a callback from {P} {D}.", "I want {P} to {V} {D}.",
    "I'd like {P} to {V} {D}.", "I've asked {P} to confirm {D}.",
  ], 3),
  "general claim": cyc([
    "My neighbour said {P} usually comes {D}.", "Apparently {P} refunds take 5 days.",
    "The website says {P} delivers {D}.", "The email says to contact {P} {D}.", "Someone online said {P} takes weeks.",
  ], 2),
}
NOT_HAND = [
  "They said if the part arrives, the engineer may come tomorrow.", "They promised nothing and told me to call tomorrow.",
  "Currys said the shop closes tomorrow at 6pm.", "British Gas said appointments are available tomorrow.",
  "They said please call tomorrow.", "They said check back tomorrow.", "They said we'll be open tomorrow.",
  "The engineer will come at 5", "They said someone would be in touch at some point.",
  "They said they'll look into it.", "They said they'll get back to me.", "They said soon.",
  "Currys said they'd see what they can do.", "The landlord said he'll think about it.",
  "No one has promised anything. I want to call Currys tomorrow.", "They never promised a date.",
  "There is no guarantee the refund arrives tomorrow.", "They wouldn't give me a date for the engineer",
]

YES_TEMPLATES = [
  "{Pc} said the engineer will come {D}.", "{Pc} promised a refund {D}.", "{Pc} confirmed delivery {D}.",
  "{Pc} told me the parcel will arrive {D}.", "{Pc} agreed to send a replacement {D}.",
  "{Pc} assured me the money will be back within 5 working days.", "{Pc} guaranteed it would be fixed {D}.",
  "{Pc} said they'll call me back {D}.", "{Pc} confirmed my refund will be processed within 3 days.",
  "{Pc} promised to ring me {D} at 10am.", "{Pc} said someone will come {D} between 8 and 12.",
  "{Pc} has booked the repair for {D}.", "{Pc} said the refund will be paid {D}.", "{Pc} said they will {V} {D}.",
]
YES = cyc(YES_TEMPLATES, 6) + [
  "The engineer is booked for tomorrow between 8 and 12, ref BG-4471.", "Currys promised a refund by tomorrow, order 445566",
  "The landlord promised the boiler will be fixed by " + F, "BA promised the refund within 10 working days",
  "Vodafone confirmed the credit will show by Friday", "The letting agent said the plumber will come on Thursday at 10am",
  "Aviva said they will call me back tomorrow afternoon", "John Lewis promised a replacement tomorrow",
]

MSG_YES = [
  "Hi Baldwin,\nThanks for your patience. Your engineer visit is confirmed for " + ahead(5)['long'] + " between 8am and 12pm. Your reference is BG-77120.\nBritish Gas",
  "Your refund of £89.99 has been processed. Please allow up to 5 working days for it to reach your account. Order 551234.",
  "Good news! Your replacement is on its way and will be delivered on " + ahead(3)['long'] + ". Track it in the app.",
  "Dear customer, we will call you back on " + ahead(2)['long'] + " between 2pm and 4pm about case 88213. Kind regards, EE",
  "Please note your engineer will arrive on " + ahead(6)['long'] + " between 12pm and 6pm. Reference SKY-55120.",
]
MSG_NOT = [
  "Our opening hours are Monday to Friday 9am to 5pm. If you still need help, call us on 0800 000 000.",
  "Don't miss our autumn sale! Offers end " + ahead(4)['long'] + ". Shop now.",
  "Thanks for contacting us. We'll look into this and get back to you as soon as we can.",
  "Refunds usually take 3 to 5 working days once approved. You can track your refund in your account.",
  "If the part arrives on time, we may be able to send an engineer on " + ahead(3)['long'] + ". We'll let you know.",
  "Please call us on " + ahead(2)['long'] + " to arrange a new appointment. Lines are open 8am to 8pm.",
  "We're sorry, we can't give you a date for the repair yet. We'll be in touch.",
]

def not_all():
    out = [(g, s) for g, xs in NOT_GROUPS.items() for s in xs]
    return out + [("hand-written", s) for s in NOT_HAND]

# Messy real-world writing (v50). Each YES item carries what the card must say: weekday, hour, past.
MESSY_YES = [
  ("british gas said engineer coming tmrw 8-12", {"days": 1, "hour": 8}),
  ("currys promised refund by fri", {"weekday": "Friday"}),
  ("landlord said hes sending someone thurs", {"weekday": "Thursday"}),
  ("They said they'd come on Tuesday, then changed it to Thursday", {"weekday": "Thursday"}),
  ("Amazon: Your package will arrive tomorrow by 9pm.", {"days": 1, "hour": 21}),
  ("engineer was meant to come yesterday but never showed", {"past": True}),
  ("Sky said engineer booked for 14/10 between 8 and 1", {"hour": 8}),
  ("THEY PROMISED THE REFUND BY MONDAY", {"weekday": "Monday", "party": ""}),
  ("the council said someone will inspect the damp within 10 working days", {}),
  ("DPD said redelivery is tomorrow", {"days": 1}),
  ("Octopus confirmed the smart meter install is on the 20th", {"dom": 20}),
  ("Argos said refund in 3-5 working days", {}),
  ("---------- Forwarded message ---------\nFrom: Currys <help@currys.co.uk>\nYour refund of £129 will be paid within 5 working days. Order 77412.", {}),
  ("On Mon, John Lewis wrote:\n> Your engineer will visit on Thursday.\nUpdate: we have moved your visit to Saturday between 8am and 1pm.", {"weekday": "Saturday", "hour": 8}),
  ("plumber said hell pop round after lunch tomorrow", {"days": 1}),
  ("Virgin said an engineer would come out sometime next week", {}),
  ("The insurer told me they'd pay out by the end of the month", {}),
  ("BT said the fault will be fixed by 11:59pm on Friday", {"weekday": "Friday", "hour": 23}),
]
MESSY_NOT = [
  "they said they'd maybe come tmrw idk", "need to ring currys tmrw", "can u call back tmrw", "ring us back tmrw x",
  "Landlord said he would sort the boiler asap", "Currys said they'd refund me but didn't say when",
  "currys said to ring back fri", "they said engineers r available thurs", "BT said maybe next week",
  "landlord said he'll come thurs if he can", "sky said call em tmrw lol",
]

# Case names (v55). A message gets a clear name; a short typed sentence keeps its own words.
TITLES = [
  ("Amazon: your replacement kettle will arrive on 9 October.", "Amazon replacement kettle"),
  ("Your engineer visit is confirmed for Friday between 8am and 12pm. Reference BG-77120. British Gas", "British Gas engineer visit · BG-77120"),
  ("DPD: your parcel will be delivered tomorrow between 10:00 and 11:00", "DPD delivery"),
  ("Hi Baldwin, thanks for your patience. We will call you back on Monday about case 88213. Kind regards, EE", "EE callback · 88213"),
  ("Sky said engineer booked for 14/10 between 8 and 1", "Sky engineer visit"),
  ("Council tax bill is wrong", "Council tax bill is wrong"),
  ("Aviva still hasn't paid my claim", "Aviva still hasn't paid my claim"),
  ("Royal Mail lost my parcel", "Royal Mail lost my parcel"),
  ("GP surgery won't give me an appointment", "GP surgery won't give me an appointment"),
  ("Currys refund hasn't arrived, order 445566", "Currys refund · 445566"),
]

# Parking notices (v60). Each must give exactly these facts; anything not listed must be absent or match.
PCN_NOTICES = [
  ("""LONDON BOROUGH OF SOUTHWARK
PENALTY CHARGE NOTICE
PCN Number: SK12345678
Vehicle Registration Mark: AB12 CDE
Date of contravention: 02/10/2026
Time: 10:14
Location: Lordship Lane SE22
Contravention code: 12 Parked in a residents' or shared use parking place without clearly displaying a permit.
The penalty charge is £130. If paid within 14 days of the date of this notice, the penalty charge is reduced by 50% to £65.""",
   {"kind": "council", "issuer": "Southwark Council", "ref": "SK12345678", "vrm": "AB12 CDE", "when": "2 Oct 2026", "time": "10:14",
    "place": "Lordship Lane SE22", "amount": "£130", "discount": "£65 if paid within 14 days", "title": "Southwark PCN · SK12345678"}),
  ("Camden Council PENALTY CHARGE NOTICE PCN number: CU98765432 Vehicle registration: LK70 XYZ Date of contravention: 28 September 2026 Time: 14.32 Location: Camden High Street Code: 01 Parked in a restricted street during prescribed hours. Penalty charge: £160 reduced to £80 if paid within 14 days.",
   {"kind": "council", "issuer": "Camden Council", "ref": "CU98765432", "vrm": "LK70 XYZ", "when": "28 Sep 2026", "time": "14:32",
    "amount": "£160", "discount": "£80 if paid within 14 days", "title": "Camden PCN · CU98765432"}),
  ("ParkingEye Ltd PARKING CHARGE NOTICE Notice to Keeper Protection of Freedoms Act 2012 Reference number: 1234567 Vehicle registration: YT19 ABC Car park: Aldi Lewisham Date of event: 14/09/2026 Parking charge amount: £100. Reduced to £60 if paid within 14 days. If you wish to appeal you can do so via POPLA.",
   {"kind": "private", "issuer": "ParkingEye", "ref": "1234567", "vrm": "YT19 ABC", "when": "14 Sep 2026", "place": "Aldi Lewisham",
    "amount": "£100", "discount": "£60 if paid within 14 days", "title": "ParkingEye parking charge · 1234567"}),
  ("Royal Borough of Kensington and Chelsea NOTICE TO OWNER PCN: KC22334455 Vehicle: BD51 SMR Date of notice: 30/09/2026 Date of contravention: 01/09/2026 The penalty charge of £160 remains unpaid. You must pay or make representations within 28 days of the date of service.",
   {"kind": "council", "issuer": "Kensington and Chelsea Council", "ref": "KC22334455", "vrm": "BD51 SMR", "issued": "30 Sep 2026",
    "when": "1 Sep 2026", "amount": "£160", "title": "Kensington and Chelsea PCN · KC22334455"}),
  ("Transport for London Penalty Charge Notice - Bus Lane. PCN number: LB12345678 Vehicle registration mark: GF23 KLM Date: 12 September 2026 Time: 08:03 Location: Old Kent Road. Penalty charge £160, discounted amount £80 if paid within 21 days of the date of service. Pay by 3 October 2026.",
   {"kind": "council", "issuer": "Transport for London", "ref": "LB12345678", "vrm": "GF23 KLM", "when": "12 Sep 2026", "time": "08:03",
    "place": "Old Kent Road", "amount": "£160", "discount": "£80 if paid within 21 days", "payby": "3 Oct 2026", "title": "TfL PCN · LB12345678"}),
  ("Got a parking ticket from Hackney Council, PCN HK11223344, £130, says I wasn't in a bay",
   {"kind": "council", "issuer": "Hackney Council", "ref": "HK11223344", "amount": "£130", "title": "Hackney PCN · HK11223344"}),
  ("Euro Car Parks parking charge notice. Charge number: 98765432. Vehicle: KM68 PLO. Site: Westfield Stratford. Date of event: 20/09/2026. Amount due: £100, reduced to £60 if paid within 14 days. Appeals: IAS.",
   {"kind": "private", "issuer": "Euro Car Parks", "ref": "98765432", "vrm": "KM68 PLO", "when": "20 Sep 2026", "place": "Westfield Stratford",
    "amount": "£100", "discount": "£60 if paid within 14 days", "title": "Euro Car Parks parking charge · 98765432"}),
]
PCN_NOT = [
  "Currys promised a refund of £130 by Friday, order 445566", "Fixed Penalty Notice for littering, £150, Lambeth Council",
  "Council tax bill is wrong, account 12345678", "The parking at the hospital is terrible",
  "British Gas said the engineer will come on Friday, ref BG-4471", "Southwark Council said they'll fix the pothole by Friday",
  "My parking permit renewal is due next month", "Thames Water charge of £84 is wrong",
  "Landlord says I owe £130 for a parking space", "I need to pay the congestion charge tomorrow",
]
PCN_NOTICES.append(("CAMDEN COUNCIL PENALTY CHARGE NOTICE PCN Number: CU98765432 Vehicle registration: LK70 XYZ Date of contravention: 28/09/2026 Time: 14:32 Location: Camden High Street Penalty charge: £160, reduced to £80 if paid within 14 days.",
   {"kind": "council", "issuer": "Camden Council", "ref": "CU98765432", "vrm": "LK70 XYZ", "when": "28 Sep 2026", "amount": "£160", "title": "Camden PCN · CU98765432"}))
PCN_NOTICES.append(("WEST BERKSHIRE COUNCIL PENALTY CHARGE NOTICE PCN: WB12345678 Vehicle: AB12 CDE Penalty charge: £70",
   {"kind": "council", "issuer": "West Berkshire Council", "ref": "WB12345678", "title": "West Berkshire PCN · WB12345678"}))
PCN_NOTICES.append(("London Borough of Southwark PENALTY CHARGE NOTICE PCN Number: SK12345678 Location: Lordship Lane SE22 The penalty charge is £130.",
   {"kind": "council", "ref": "SK12345678", "place": "Lordship Lane SE22", "amount": "£130"}))

# Hand-offs (v66): the case is with Currys; who does the message say has it now?
HO_YES = [
  ("Hi, we've passed your case to DPD, who will contact you about the redelivery.", "DPD"),
  ("This is the manufacturer's responsibility, not ours.", "the manufacturer"),
  ("You will need to contact Samsung directly about the repair.", "Samsung"),
  ("Your complaint has been transferred to our partner Knowhow Repairs.", "Knowhow Repairs"),
  ("It's now a matter for the courier.", "the courier"),
  ("Please get in touch with Evri directly about the missing parcel.", "Evri"),
]
HO_NOT = [
  "Please contact us directly if you have any questions.", "We have passed your feedback to the team.",
  "Your refund will be paid by Friday.", "It's not our responsibility to collect it.",
  "We've passed this to Currys' returns team.", "Please speak to your bank.",
]
