const fs=require('fs'),c=require('crypto');const h=b=>c.createHash('sha1').update(b).digest('hex');
let s=fs.readFileSync('public/index.html','utf8');
if(h(s)!=='a67be56623578140247bee3124bd1a657b7b2158')throw new Error('base mismatch '+h(s));
function R(a,b,n){n=n||1;const k=s.split(a).length-1;if(k!==n)throw new Error('match '+k+': '+a.slice(0,60));s=s.split(a).join(b)}
// ---- v108: Moving home for all four nations. A fifth question (where is the new home?); the official links for the
// licence, voting, the GP and the council chosen by nation (MV_NAT, mvLink), every one read by hand; Northern Ireland
// tells LPS about rates instead of the council about council tax; a move with no nation yet is asked once. ----
R("var MV_CHECKED=\"3 Oct 2026\";",
  "/* v108: the nation the new home is in decides the official links. GOV.UK's driving licence service is for Great Britain\n   (Northern Ireland uses DVA on nidirect); GOV.UK's register to vote is for England, Scotland and Wales (Northern Ireland\n   registers with EONI); the V5C service and \"find your council\" cover all four; GP registration is NHS England, NHS 111\n   Wales, NHS inform or nidirect; Northern Ireland has rates, not council tax, so that step tells LPS instead. */\nvar MV_NATIONS=[[\"en\",\"England\"],[\"wa\",\"Wales\"],[\"sc\",\"Scotland\"],[\"ni\",\"Northern Ireland\"]];\nvar MV_NAT={\n  wa:{gp:[\"https://111.wales.nhs.uk/localservices/gpfaq/\",\"How to register, on NHS 111 Wales\"]},\n  sc:{gp:[\"https://www.nhsinform.scot/care-support-and-rights/nhs-services/doctors/registering-with-a-gp-practice/\",\"How to register, on NHS inform\"]},\n  ni:{gp:[\"https://www.nidirect.gov.uk/articles/your-local-doctor-gp\",\"How to register, on nidirect\"],licence:[\"https://www.nidirect.gov.uk/services/change-address-your-driving-licence-online\",\"Change it on nidirect\"],vote:[\"https://www.eoni.org.uk/register-to-vote/electoral-registration/\",\"Register with the Electoral Office for Northern Ireland\"],council:[\"https://www.nidirect.gov.uk/services/create-or-update-your-rate-account\",\"Update your rate account on nidirect\"]}\n};\nfunction mvLink(it,a){var n=(a&&a.nation)||\"en\";return (MV_NAT[n]&&MV_NAT[n][it.link])||MV_LINK[it.link]||null}\nfunction mvNation(a){var n=(a&&a.nation)||\"\";for(var i=0;i<MV_NATIONS.length;i++)if(MV_NATIONS[i][0]===n)return MV_NATIONS[i][1];return \"\"}\nfunction momSub(it,a){return typeof it.sub===\"function\"?it.sub(a||{}):(it.sub||\"\")}\nvar MV_CHECKED=\"4 Oct 2026\";");
R("  {k:\"council\",l:function(a){return a.council===\"new\"?\"Tell your old and new council\":\"Tell your council about the move\"},own:1,start:0,link:\"council\",sub:\"For council tax at both addresses.\"},",
  "  {k:\"council\",l:function(a){return a.nation===\"ni\"?\"Tell Land & Property Services you’ve moved\":a.council===\"new\"?\"Tell your old and new council\":\"Tell your council about the move\"},own:1,start:0,link:\"council\",sub:function(a){return a.nation===\"ni\"?\"For rates at both addresses. Northern Ireland has rates, not council tax.\":\"For council tax at both addresses.\"}},");
R("  {k:\"licence\",l:\"Change the address on your driving licence\",own:1,start:0,link:\"licence\",on:function(a){return a.car===\"yes\"},sub:\"It’s free. DVLA can fine you up to £1,000 if you don’t tell them.\"},",
  "  {k:\"licence\",l:\"Change the address on your driving licence\",own:1,start:0,link:\"licence\",on:function(a){return a.car===\"yes\"},sub:function(a){return \"It’s free. \"+(a.nation===\"ni\"?\"DVA\":\"DVLA\")+\" can fine you up to £1,000 if you don’t tell them.\"}},");
R("function momLinkA(it,cls){return it.link&&MV_LINK[it.link]?'<a class=\"'+cls+'\" href=\"'+MV_LINK[it.link][0]+'\" target=\"_blank\" rel=\"noopener\">'+esc(MV_LINK[it.link][1])+'</a>':''}",
  "function momLinkA(it,cls,a){var L=it.link?mvLink(it,a):null;return L?'<a class=\"'+cls+'\" href=\"'+L[0]+'\" target=\"_blank\" rel=\"noopener\">'+esc(L[1])+'</a>':''}");
R("(it.sub?' · '+esc(it.sub):'')+'</p><div class=\"cap99-acts\">'+momLinkA(it,\"link\")+",
  "(momSub(it,m.ans)?' · '+esc(momSub(it,m.ans)):'')+'</p><div class=\"cap99-acts\">'+momLinkA(it,\"link\",m.ans)+");
R("  if(it.sub)h+='<p class=\"cap99-s\">'+esc(it.sub)+'</p>';",
  "  if(momSub(it,m.ans))h+='<p class=\"cap99-s\">'+esc(momSub(it,m.ans))+'</p>';");
R("+(inTouch?\"They’ve told me more\":\"I’ve contacted them\")+'</button>'+momLinkA(it,\"link\")+",
  "+(inTouch?\"They’ve told me more\":\"I’ve contacted them\")+'</button>'+momLinkA(it,\"link\",m.ans)+");
R("<p class=\"muted\" style=\"margin:0\">Four quick questions, so Sorted only shows what applies to you. Nothing is saved until you press the button.</p>",
  "<p class=\"muted\" style=\"margin:0\">Five quick questions, so Sorted only shows what applies to you, with the right official links. Nothing is saved until you press the button.</p>");
R("  h+='<div class=\"stack-s\"><p class=\"h3\" style=\"margin:0\">Are you taking your broadband with you?</p>'+momChips(\"mv-bb\",[[\"yes\",\"Yes\"],[\"no\",\"No, or not sure\"]],a.bb||\"no\")+'</div>';",
  "  h+='<div class=\"stack-s\"><p class=\"h3\" style=\"margin:0\">Are you taking your broadband with you?</p>'+momChips(\"mv-bb\",[[\"yes\",\"Yes\"],[\"no\",\"No, or not sure\"]],a.bb||\"no\")+'</div>';\n  h+='<div class=\"stack-s\"><p class=\"h3\" style=\"margin:0\">Where is the new home?</p><p class=\"muted\" style=\"margin:0;font-size:15px\">The official pages for your licence, voting, the GP and the council differ between the four nations.</p>'+momChips(\"mv-nation\",MV_NATIONS,a.nation||\"\")+'</div>';");
R("    var ans={tenure:pick(\"mv-tenure\")||\"other\",council:pick(\"mv-council\")||\"unsure\",car:pick(\"mv-car\")||\"no\",bb:pick(\"mv-bb\")||\"no\"},mex=S.view.id?momOf(S.view.id):null;",
  "    var ans={tenure:pick(\"mv-tenure\")||\"other\",council:pick(\"mv-council\")||\"unsure\",car:pick(\"mv-car\")||\"no\",bb:pick(\"mv-bb\")||\"no\"},mex=S.view.id?momOf(S.view.id):null;if(pick(\"mv-nation\"))ans.nation=pick(\"mv-nation\");");
R("    track(\"moment_created\",nm,{type:\"moving\",tenure:ans.tenure,council:ans.council,car:ans.car,bb:ans.bb,days:",
  "    track(\"moment_created\",nm,{type:\"moving\",tenure:ans.tenure,council:ans.council,car:ans.car,bb:ans.bb,nation:ans.nation||\"\",days:");
R("  h+='<section class=\"stack-s\"><p class=\"eyebrow\">Life moment</p><h1 class=\"h1\">'+esc(m.title)+'</h1><p class=\"cap99-date\">'+esc(pkDayLabel(m.date))+' · '+esc(momWhen(m))+'</p><p class=\"muted\" style=\"margin:0\">Your own steps have the official link.",
  "  h+='<section class=\"stack-s\"><p class=\"eyebrow\">Life moment</p><h1 class=\"h1\">'+esc(m.title)+'</h1><p class=\"cap99-date\">'+esc(pkDayLabel(m.date))+' · '+esc(momWhen(m))+(mvNation(m.ans)?' · '+esc(mvNation(m.ans)):'')+'</p>'+(mvNation(m.ans)?'':'<p class=\"note cap108-nation\" style=\"margin:0\">Which nation is the new home in? The official links differ. <button class=\"link\" data-a=\"mom-edit\" style=\"display:inline;min-height:0;padding:0\">Say where</button></p>')+'<p class=\"muted\" style=\"margin:0\">Your own steps have the official link.");
R(".cap103-said textarea{width:100%}",
  ".cap103-said textarea{width:100%}\n:root[data-theme=\"dark\"] .case56-overline{color:#CFCBFF}\n@media (prefers-color-scheme:dark){:root:not([data-theme=\"light\"]) .case56-overline{color:#CFCBFF}}\n.cap95-wrap .cap95-chip,.cap98-mchip{min-height:44px}");
R(".case75-email-slim .link{min-height:36px;padding:4px 0;flex:none}",
  ".case75-email-slim .link{min-height:44px;padding:4px 0;flex:none}");
fs.writeFileSync('public/index.html',s);
const EXPECT='2e17dc4b6bf3856520a65bc200e8ebbcb978ddba';
if(EXPECT&&h(s)!==EXPECT)throw new Error('output mismatch '+h(s));
console.log('v108 ok',h(s),s.length);
