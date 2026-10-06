import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
import { sendPush } from "./webpush.ts";

// v12 (Sorted v141): an Idempotency-Key per reminder for Resend; a push already sent for a reminder is not repeated; only
// a refused subscription (400, 401, 403, 413) counts towards removing it; push TTL 6 hours before, a day after; the
// footer links to Settings to stop all reminder emails.
// v11 (Sorted v133): each reminder also goes to the phones that switched on "Get reminders on this phone" (Web Push,
// push_subs, the private key `vapid_private_jwk` in Vault). The notification never says what the case is: fixed text,
// the case link and, after the time, the answer buttons. A guest with no email gets reminders this way. A phone the push
// service no longer knows (404 or 410) is removed. The "after" email also offers Later and New date.
// v10 (Sorted v116): records when each reminder is handed to Resend (submitted_at) before the call, and Resend's
// acceptance (sent_at, provider_id) after it; delivery and bounces arrive later through resend-events.
// v9 (Sorted v71): an "after" reminder for a promise or your own step has two answer links, Yes and No. They open the
// case, which records the answer once it has loaded and offers Undo. Still no case details in the email.
// v8: claims reminders and helper invites in the database before sending (needs the reliability fixes of 2 Oct 2026).
// Called every 10 minutes by pg_cron (and straight away after a helper invite).
// Emails never contain task details: only a link.
const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, { auth: { persistSession: false } });
const SITE = "https://sorted-pilot.vercel.app";
const FN = "https://boxrwcuhxmimayaxzywu.supabase.co/functions/v1";
const FRESH_MS = 30 * 60 * 1000; // a reminder more than 30 minutes late is not sent

async function secret(name: string): Promise<string | null> {
  const { data } = await sb.rpc("sorted_secret", { p_name: name });
  return (data as string) || null;
}
async function stopToken(u: string, cron: string): Promise<string> {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(cron), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const s = new Uint8Array(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode("stop:" + u)));
  return Array.from(s).map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
function eq(a: string, b: string) { if (a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// A plain, well-formed service email: short intro, one button, the link written out, and who sends it.
function html(heading: string, intro: string, button: string, link: string, footer: string, second?: { button: string; link: string; note: string }, more?: { label: string; link: string }[]): string {
  const extra = more && more.length ? `<p style="margin:18px 0 0;font-size:15px;line-height:1.7">${more.map((m) => `<a href="${esc(m.link)}" style="color:#2A3990">${esc(m.label)}</a>`).join("<br>")}</p>` : "";
  const two = second ? `<a href="${esc(second.link)}" style="display:inline-block;margin:10px 0 0;background:#FFFFFF;color:#2A3990;border:2px solid #2A3990;text-decoration:none;font-size:16px;font-weight:bold;padding:10px 20px;border-radius:6px">${esc(second.button)}</a><p style="margin:16px 0 0;font-size:14px;line-height:1.5;color:#55565C">${esc(second.note)}</p>` : "";
  return `<!doctype html><html><body style="margin:0;padding:0;background:#F6F3EC"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F6F3EC"><tr><td align="center" style="padding:24px 12px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#FFFFFF;border-radius:8px"><tr><td style="padding:28px 28px 8px;font-family:Arial,Helvetica,sans-serif;color:#1B1B1F"><p style="margin:0 0 18px;font-size:22px;font-weight:bold">sorted<span style="color:#2A3990">.</span></p><p style="margin:0 0 10px;font-size:18px;font-weight:bold">${esc(heading)}</p><p style="margin:0 0 22px;font-size:16px;line-height:1.5">${esc(intro)}</p><a href="${esc(link)}" style="display:inline-block;background:#2A3990;color:#FFFFFF;text-decoration:none;font-size:16px;font-weight:bold;padding:12px 22px;border-radius:6px;margin-right:8px">${esc(button)}</a>${two}${extra}${second ? "" : `<p style="margin:22px 0 0;font-size:13px;line-height:1.5;color:#55565C">Or copy this link: ${esc(link)}</p>`}</td></tr><tr><td style="padding:18px 28px 26px;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:#6B6C72">${footer}</td></tr></table></td></tr></table></body></html>`;
}

async function send(key: string, from: string, to: string, subject: string, text: string, htmlBody: string, headers?: Record<string, string>, idem?: string): Promise<{ ok: boolean; id?: string; err?: string }> {
  // v141: an idempotency key per reminder, so a retry after a lost response never sends the same email twice.
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json", ...(idem ? { "Idempotency-Key": idem } : {}) },
    body: JSON.stringify({ from, to: [to], subject, text, html: htmlBody, headers }),
  });
  const body = await res.text();
  if (!res.ok) { console.log("resend error", res.status); return { ok: false, err: String(res.status) }; }  // status only: the body can contain the address
  let id: string | undefined; try { id = JSON.parse(body).id; } catch { /* ignore */ }
  console.log("resend ok", id);
  return { ok: true, id };
}

// Wording for each kind of reminder. "Move" = something the person said they would do; otherwise it is someone else's promise.
function copy(kind: string, move: boolean) {
  if (move) {
    if (kind === "start") return { push: "Something you planned to do is due tomorrow.", subject: "Your Sorted reminder: due tomorrow", heading: "Something you planned to do is due tomorrow", intro: "One of your cases in Sorted has something for you to do by tomorrow. Open it to see what, and mark it done when you have." };
    if (kind === "after") return { push: "Did you get it done? Tap to answer.", subject: "Your Sorted case: did you get it done?", heading: "Did you get it done?", intro: "The time you set for one of your cases has passed. Tap Yes and Sorted will mark it done, or Not yet to pick a new time." };
    return { push: "Something you planned to do is due.", subject: "Your Sorted reminder", heading: "Something you planned to do is due", intro: "One of your cases in Sorted has something for you to do. Open it to see what, and mark it done when you have." };
  }
  if (kind === "after") return { push: "Did it happen? Tap to answer.", subject: "Your Sorted case: did it happen?", heading: "Did it happen?", intro: "The time for one of your cases has passed. Tap an answer and Sorted will record it in that case. If it didn't happen, your chase will be ready." };
  return { push: "Something you’re waiting on is due soon.", subject: "Your Sorted reminder", heading: "Something you're waiting on is coming up", intro: "One of your cases in Sorted is due soon. Open it to see the details and what to have ready." };
}

Deno.serve(async (req: Request) => {
  const cron = await secret("sorted_cron_secret");
  if (!cron || !eq(req.headers.get("x-cron-secret") || "", cron)) return new Response("forbidden", { status: 403 });

  const nowMs = Date.now();
  const now = new Date(nowMs).toISOString();
  const staleBefore = new Date(nowMs - FRESH_MS).toISOString();

  const { data: stale } = await sb.from("reminders")
    .update({ cancelled_at: now, cancel_reason: "stale" })
    .is("sent_at", null).is("cancelled_at", null).lt("send_at", staleBefore)
    .select("id");

  const key = await secret("resend_api_key");
  const from = await secret("reminder_from");
  const emailOn = !!(key && from && from.includes("@"));
  let vapid: JsonWebKey | null = null;
  try { const v = await secret("vapid_private_jwk"); vapid = v ? JSON.parse(v) : null; } catch { vapid = null; }
  const subject = (await secret("vapid_subject")) || "mailto:kofiniiakwei@gmail.com";
  if (!emailOn && !vapid) {
    return Response.json({ skipped: "sending not configured (needs resend_api_key and reminder_from, or vapid_private_jwk)", stale: stale?.length ?? 0 });
  }

  // 1. Helper invitations (double opt-in). Sent once; only within a day of the request.
  let invites = 0;
  if (emailOn) {
  // Claimed in the database first (invite_sent_at set), so two runs at once can't send the same invite.
  const { data: pend } = await sb.rpc("claim_helper_invites", { p_limit: 20 });
  for (const h of (pend ?? []) as any[]) {
    const yes = `${SITE}/?helper=yes&h=${h.token}`;
    const intro = `${h.inviter_name} is using Sorted to keep track of something they're waiting on, and has already sent you a link to it. They'd like Sorted to email you a short nudge when it's due, so you can check in with them.`;
    const text = `Hello,\n\n${intro}\n\nIf that's fine, say yes here: ${yes}\n\nIf you don't click, Sorted won't email you again. The nudges never say what the case is, and you can stop them at any time.\n\nIf you don't know ${h.inviter_name}, ignore this email.\n\nSorted is a small UK service run by Baldwin Thompson-Addo.`;
    const hb = html(`${h.inviter_name} asked Sorted to keep you in the loop`, intro, "Yes, nudge me", yes, `If you don't click, Sorted won't email you again. The nudges never say what the case is, and you can stop them at any time. If you don't know ${esc(h.inviter_name)}, ignore this email.<br><br>Sorted is a small UK service run by Baldwin Thompson-Addo.`);
    const r = await send(key, from, h.email, `${h.inviter_name} asked Sorted to keep you in the loop`, text, hb);
    if (r.ok) invites++;
    else await sb.from("helpers").update({ invite_sent_at: null }).eq("task_id", h.task_id).eq("token", h.token);  // try again next run
  }
  }

  // 2. Due reminders.
  // Claimed first (claimed_at set) so two runs at once can't send the same email. An unfinished claim can be
  // taken again after 5 minutes, so a failed send is retried while it is still fresh.
  const { data: due, error } = await sb.rpc("claim_due_reminders", { p_limit: 50 });
  if (error) return Response.json({ error: "claim failed" }, { status: 500 });

  let sent = 0, cancelled = 0, failed = 0, nudged = 0, pushed = 0;
  for (const r of (due ?? []) as any[]) {
    const cancel = async (reason: string) => { await sb.from("reminders").update({ cancelled_at: new Date().toISOString(), cancel_reason: reason }).eq("id", r.id); cancelled++; };
    const { data: opt } = await sb.from("email_optouts").select("user_id").eq("user_id", r.user_id).maybeSingle();
    const { data: row } = await sb.from("tasks").select("data").eq("id", r.task_id).maybeSingle();
    const t: any = row?.data;
    if (!t) { await cancel("task gone"); continue; }
    if (t.board === "done") { await cancel("task done"); continue; }
    const open = (t.promises || []).slice().reverse().find((p: any) => p.status === "open");
    const openMv = (t.moves || []).slice().reverse().find((m: any) => m.status === "open");
    const isMove = !!(r.promise_id && openMv && openMv.id === r.promise_id);
    const valid = r.promise_id ? ((open && open.id === r.promise_id) || isMove) : !(t.renew && t.renew.applied) && !open;
    if (!valid) { await cancel("superseded"); continue; }
    const { data: u } = await sb.auth.admin.getUserById(r.user_id);
    const email = u?.user?.email;
    const wantEmail = !!(emailOn && email && !opt && t.emailRemind !== false);
    const { data: subs } = vapid ? await sb.from("push_subs").select("id,endpoint,p256dh,auth,fails").eq("user_id", r.user_id) : { data: [] as any[] };
    const wantPush = !!(vapid && subs && subs.length);
    if (!wantEmail && !wantPush) { await cancel(!email ? "no email" : opt ? "unsubscribed" : t.emailRemind === false ? "switched off" : "no channel"); continue; }
    const link = `${SITE}/?task=${encodeURIComponent(r.task_id)}&src=email`;
    const c = copy(r.kind, isMove);
    // Answer links only after the time has passed, only for the promise or step this reminder is about, never for parking.
    const target = isMove ? openMv : open;
    const ask = r.kind === "after" && r.promise_id && target && target.id === r.promise_id && target.src !== "parking";
    const ans = (a: string) => `${link}&ans=${a}&p=${encodeURIComponent(r.promise_id)}`;
    const stop = `${FN}/email-stop?u=${r.user_id}&t=${await stopToken(r.user_id, cron)}`;
    const settings = `${SITE}/#more-settings`;
    const yesL = isMove ? "Yes, done" : "Yes, it happened", noL = isMove ? "Not yet" : "No, it didn't";
    const more = ask ? [{ label: "Can’t deal with it now? Choose when Sorted reminds you", link: ans("later") }].concat(isMove ? [] : [{ label: "They gave a new date? Add it", link: ans("date") }]) : [];
    const text = `${c.heading}\n\n${c.intro}\n\n` + (ask ? `${yesL}: ${ans("yes")}\n${noL}: ${ans("no")}\n` + more.map((m) => `${m.label}: ${m.link}`).join("\n") + `\n\nSorted opens the case so you can check, and you can undo it.\n\n` : `Open your case: ${link}\n\n`) + `You're getting this because you use Sorted and have email reminders on for this case. The details stay in the app, not in this email. To stop all reminder emails, turn them off in Settings: ${settings}\nTo stop them for this case only, open the case and turn its email reminders off.\n\nSorted is a small UK service run by Baldwin Thompson-Addo.`;
    const hb = html(c.heading, c.intro, ask ? yesL : "Open your case", ask ? ans("yes") : link, `You're getting this because you use Sorted and have email reminders on for this case. The details stay in the app, not in this email. To stop all reminder emails, <a href="${esc(settings)}" style="color:#2A3990">turn them off in Settings</a>. To stop them for this case only, open the case and turn its email reminders off.<br><br>Sorted is a small UK service run by Baldwin Thompson-Addo.`, ask ? { button: noL, link: ans("no"), note: "Sorted opens the case so you can check, and you can undo it." } : undefined, more);
    // The phone first: fixed words, the case link, and after the time the answer buttons. Never what the case is.
    let pushOk = 0, pushTried = 0;
    // v141: a push already delivered for this reminder (a run cut short before the email) is not sent again.
    if (wantPush && (r as any).push_sent_at) pushOk = 1;
    else if (wantPush) {
      const rel = `/?task=${encodeURIComponent(r.task_id)}&src=push`;
      const relAns = (a: string) => `${rel}&ans=${a}&p=${encodeURIComponent(r.promise_id)}`;
      const msg: any = { t: "Sorted", b: c.push, u: rel, g: "case-" + String(r.task_id).slice(0, 40) };
      if (ask) { msg.x = [["yes", isMove ? "Done" : "Yes"], ["no", "Not yet"]]; msg.a = { yes: relAns("yes"), no: relAns("no") }; }
      for (const s of (subs ?? []) as any[]) {
        pushTried++;
        let st = 0;
        try { st = await sendPush({ endpoint: s.endpoint, p256dh: s.p256dh, auth: s.auth }, msg, vapid!, subject, r.kind === "after" ? 86400 : 21600); } catch { st = 0; }
        if (st >= 200 && st < 300) { pushOk++; await sb.from("push_subs").update({ last_ok_at: new Date().toISOString(), fails: 0 }).eq("id", s.id); }
        else if (st === 404 || st === 410) await sb.from("push_subs").delete().eq("id", s.id);
        // v141: only a refusal of the subscription itself counts towards removing it; an outage (429, 5xx, no answer) doesn't.
        else if (st === 400 || st === 401 || st === 403 || st === 413) { await sb.from("push_subs").update({ fails: (s.fails || 0) + 1 }).eq("id", s.id); if ((s.fails || 0) + 1 >= 5) await sb.from("push_subs").delete().eq("id", s.id); }
      }
      await sb.from("reminders").update({ push_sent_at: pushOk ? new Date().toISOString() : null, push_detail: `${pushOk} of ${pushTried}` }).eq("id", r.id);
      if (pushOk) pushed++;
    }
    if (!wantEmail) {
      if (pushOk) { await sb.from("reminders").update({ sent_at: new Date().toISOString() }).eq("id", r.id); sent++; }
      else { failed++; await sb.from("reminders").update({ cancel_reason: "push failed" }).eq("id", r.id); }
      continue;
    }
    await sb.from("reminders").update({ submitted_at: new Date().toISOString() }).eq("id", r.id);
    const res = await send(key!, from!, email!, c.subject, text, hb, { "List-Unsubscribe": `<${stop}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" }, `rem-${r.id}`);
    if (!res.ok) { failed++; await sb.from("reminders").update({ cancel_reason: `send failed: ${res.err}` }).eq("id", r.id); if (pushOk) await sb.from("reminders").update({ sent_at: new Date().toISOString() }).eq("id", r.id); continue; }
    await sb.from("reminders").update({ sent_at: new Date().toISOString(), provider_id: res.id ?? null }).eq("id", r.id);
    sent++;

    // 3. Nudge a confirmed helper, using the share link they already have.
    if (emailOn && (r.kind === "before" || r.kind === "start")) {
      const { data: h } = await sb.from("helpers").select("email,inviter_name,token,status").eq("task_id", r.task_id).maybeSingle();
      const { data: sh } = await sb.from("shares").select("token").eq("task_id", r.task_id).maybeSingle();
      if (h && h.status === "confirmed" && sh?.token) {
        const hstop = `${SITE}/?helper=stop&h=${h.token}`;
        const hlink = `${SITE}/?share=${sh.token}`;
        const hintro = isMove ? `Something ${h.inviter_name} planned to do is due soon. You said you'd like a nudge so you can check in with them.` : `Something ${h.inviter_name} is waiting on is due soon. You said you'd like a nudge so you can check in with them.`;
        const htext = `${hintro}\n\nSee it here: ${hlink}\n\nTo stop these nudges: ${hstop}\n\nSorted is a small UK service run by Baldwin Thompson-Addo.`;
        const hhtml = html(`A nudge about ${h.inviter_name}`, hintro, "See it", hlink, `To stop these nudges: <a href="${esc(hstop)}" style="color:#2A3990">stop them here</a>.<br><br>Sorted is a small UK service run by Baldwin Thompson-Addo.`);
        const hr = await send(key, from, h.email, `A nudge about ${h.inviter_name}`, htext, hhtml, { "List-Unsubscribe": `<${hstop}>` });
        if (hr.ok) { await sb.from("reminders").update({ helper_sent_at: new Date().toISOString() }).eq("id", r.id); nudged++; }
      }
    }
  }
  return Response.json({ due: due?.length ?? 0, sent, pushed, cancelled, failed, stale: stale?.length ?? 0, invites, nudged });
});
