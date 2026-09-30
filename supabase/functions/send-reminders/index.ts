import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

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
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// A plain, well-formed service email: short intro, one button, the link written out, and who sends it.
function html(heading: string, intro: string, button: string, link: string, footer: string): string {
  return `<!doctype html><html><body style="margin:0;padding:0;background:#F6F3EC"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F6F3EC"><tr><td align="center" style="padding:24px 12px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#FFFFFF;border-radius:8px"><tr><td style="padding:28px 28px 8px;font-family:Arial,Helvetica,sans-serif;color:#1B1B1F"><p style="margin:0 0 18px;font-size:22px;font-weight:bold">sorted<span style="color:#2A3990">.</span></p><p style="margin:0 0 10px;font-size:18px;font-weight:bold">${esc(heading)}</p><p style="margin:0 0 22px;font-size:16px;line-height:1.5">${esc(intro)}</p><a href="${esc(link)}" style="display:inline-block;background:#2A3990;color:#FFFFFF;text-decoration:none;font-size:16px;font-weight:bold;padding:12px 22px;border-radius:6px">${esc(button)}</a><p style="margin:22px 0 0;font-size:13px;line-height:1.5;color:#55565C">Or copy this link: ${esc(link)}</p></td></tr><tr><td style="padding:18px 28px 26px;font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.5;color:#6B6C72">${footer}</td></tr></table></td></tr></table></body></html>`;
}

async function send(key: string, from: string, to: string, subject: string, text: string, htmlBody: string, headers?: Record<string, string>): Promise<{ ok: boolean; id?: string; err?: string }> {
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from, to: [to], subject, text, html: htmlBody, headers }),
  });
  const body = await res.text();
  if (!res.ok) { console.log("resend error", res.status, body); return { ok: false, err: `${res.status} ${body.slice(0, 200)}` }; }
  let id: string | undefined; try { id = JSON.parse(body).id; } catch { /* ignore */ }
  console.log("resend ok", id);
  return { ok: true, id };
}

// Wording for each kind of reminder. "Move" = something the person said they would do; otherwise it is someone else's promise.
function copy(kind: string, move: boolean) {
  if (move) {
    if (kind === "start") return { subject: "Your Sorted reminder: due tomorrow", heading: "Something you planned to do is due tomorrow", intro: "One of your tasks in Sorted has something for you to do by tomorrow. Open it to see what, and mark it done when you have." };
    if (kind === "after") return { subject: "Your Sorted task: did you get it done?", heading: "Did you get it done?", intro: "The time you set for one of your tasks has passed. Open it and mark it done, or pick a new time." };
    return { subject: "Your Sorted reminder", heading: "Something you planned to do is due", intro: "One of your tasks in Sorted has something for you to do. Open it to see what, and mark it done when you have." };
  }
  if (kind === "after") return { subject: "Your Sorted task: did it happen?", heading: "Did it happen?", intro: "The time for one of your tasks has passed. Open it and tell Sorted what happened, so it knows what to do next." };
  return { subject: "Your Sorted reminder", heading: "Something you're waiting on is coming up", intro: "One of your tasks in Sorted is due soon. Open it to see the details and what to have ready." };
}

Deno.serve(async (req: Request) => {
  const cron = await secret("sorted_cron_secret");
  if (!cron || req.headers.get("x-cron-secret") !== cron) return new Response("forbidden", { status: 403 });

  const nowMs = Date.now();
  const now = new Date(nowMs).toISOString();
  const staleBefore = new Date(nowMs - FRESH_MS).toISOString();

  const { data: stale } = await sb.from("reminders")
    .update({ cancelled_at: now, cancel_reason: "stale" })
    .is("sent_at", null).is("cancelled_at", null).lt("send_at", staleBefore)
    .select("id");

  const key = await secret("resend_api_key");
  const from = await secret("reminder_from");
  if (!key || !from || !from.includes("@")) {
    return Response.json({ skipped: "sending not configured (needs resend_api_key and reminder_from)", stale: stale?.length ?? 0 });
  }

  // 1. Helper invitations (double opt-in). Sent once; only within a day of the request.
  let invites = 0;
  const { data: pend } = await sb.from("helpers").select("task_id,email,inviter_name,token,invited_at")
    .eq("status", "pending").is("invite_sent_at", null).gte("invited_at", new Date(nowMs - 86400000).toISOString()).limit(20);
  for (const h of pend ?? []) {
    const yes = `${SITE}/?helper=yes&h=${h.token}`;
    const intro = `${h.inviter_name} is using Sorted to keep track of something they're waiting on, and has already sent you a link to it. They'd like Sorted to email you a short nudge when it's due, so you can check in with them.`;
    const text = `Hello,\n\n${intro}\n\nIf that's fine, say yes here: ${yes}\n\nIf you don't click, Sorted won't email you again. The nudges never say what the task is, and you can stop them at any time.\n\nIf you don't know ${h.inviter_name}, ignore this email.\n\nSorted is a small research pilot run by Baldwin Thompson-Addo.`;
    const hb = html(`${h.inviter_name} asked Sorted to keep you in the loop`, intro, "Yes, nudge me", yes, `If you don't click, Sorted won't email you again. The nudges never say what the task is, and you can stop them at any time. If you don't know ${esc(h.inviter_name)}, ignore this email.<br><br>Sorted is a small research pilot run by Baldwin Thompson-Addo.`);
    const r = await send(key, from, h.email, `${h.inviter_name} asked Sorted to keep you in the loop`, text, hb);
    if (r.ok) { await sb.from("helpers").update({ invite_sent_at: new Date().toISOString() }).eq("task_id", h.task_id).eq("token", h.token); invites++; }
  }

  // 2. Due reminders.
  const { data: due, error } = await sb.from("reminders")
    .select("id,task_id,user_id,kind,promise_id,send_at")
    .is("sent_at", null).is("cancelled_at", null)
    .gte("send_at", staleBefore).lte("send_at", now)
    .order("send_at").limit(50);
  if (error) return Response.json({ error: error.message }, { status: 500 });

  let sent = 0, cancelled = 0, failed = 0, nudged = 0;
  for (const r of due ?? []) {
    const cancel = async (reason: string) => { await sb.from("reminders").update({ cancelled_at: new Date().toISOString(), cancel_reason: reason }).eq("id", r.id); cancelled++; };
    const { data: opt } = await sb.from("email_optouts").select("user_id").eq("user_id", r.user_id).maybeSingle();
    if (opt) { await cancel("unsubscribed"); continue; }
    const { data: row } = await sb.from("tasks").select("data").eq("id", r.task_id).maybeSingle();
    const t: any = row?.data;
    if (!t) { await cancel("task gone"); continue; }
    if (t.board === "done") { await cancel("task done"); continue; }
    if (t.emailRemind === false) { await cancel("switched off"); continue; }
    const open = (t.promises || []).slice().reverse().find((p: any) => p.status === "open");
    const openMv = (t.moves || []).slice().reverse().find((m: any) => m.status === "open");
    const isMove = !!(r.promise_id && openMv && openMv.id === r.promise_id);
    const valid = r.promise_id ? ((open && open.id === r.promise_id) || isMove) : !(t.renew && t.renew.applied) && !open;
    if (!valid) { await cancel("superseded"); continue; }
    const { data: u } = await sb.auth.admin.getUserById(r.user_id);
    const email = u?.user?.email;
    if (!email) { await cancel("no email"); continue; }
    const link = `${SITE}/?task=${encodeURIComponent(r.task_id)}&src=email`;
    const c = copy(r.kind, isMove);
    const stop = `${FN}/email-stop?u=${r.user_id}&t=${await stopToken(r.user_id, cron)}`;
    const text = `${c.heading}\n\n${c.intro}\n\nOpen your task: ${link}\n\nYou're getting this because you use Sorted and have email reminders on for this task. The details stay in the app, not in this email. To stop them, open the task and turn email reminders off.\n\nSorted is a small research pilot run by Baldwin Thompson-Addo.`;
    const hb = html(c.heading, c.intro, "Open your task", link, `You're getting this because you use Sorted and have email reminders on for this task. The details stay in the app, not in this email. To stop them, open the task and turn email reminders off.<br><br>Sorted is a small research pilot run by Baldwin Thompson-Addo.`);
    const res = await send(key, from, email, c.subject, text, hb, { "List-Unsubscribe": `<${stop}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" });
    if (!res.ok) { failed++; await sb.from("reminders").update({ cancel_reason: `send failed: ${res.err}` }).eq("id", r.id); continue; }
    await sb.from("reminders").update({ sent_at: new Date().toISOString(), provider_id: res.id ?? null }).eq("id", r.id);
    sent++;

    // 3. Nudge a confirmed helper, using the share link they already have.
    if (r.kind === "before" || r.kind === "start") {
      const { data: h } = await sb.from("helpers").select("email,inviter_name,token,status").eq("task_id", r.task_id).maybeSingle();
      const { data: sh } = await sb.from("shares").select("token").eq("task_id", r.task_id).maybeSingle();
      if (h && h.status === "confirmed" && sh?.token) {
        const hstop = `${SITE}/?helper=stop&h=${h.token}`;
        const hlink = `${SITE}/?share=${sh.token}`;
        const hintro = isMove ? `Something ${h.inviter_name} planned to do is due soon. You said you'd like a nudge so you can check in with them.` : `Something ${h.inviter_name} is waiting on is due soon. You said you'd like a nudge so you can check in with them.`;
        const htext = `${hintro}\n\nSee it here: ${hlink}\n\nTo stop these nudges: ${hstop}\n\nSorted is a small research pilot run by Baldwin Thompson-Addo.`;
        const hhtml = html(`A nudge about ${h.inviter_name}`, hintro, "See it", hlink, `To stop these nudges: <a href="${esc(hstop)}" style="color:#2A3990">stop them here</a>.<br><br>Sorted is a small research pilot run by Baldwin Thompson-Addo.`);
        const hr = await send(key, from, h.email, `A nudge about ${h.inviter_name}`, htext, hhtml, { "List-Unsubscribe": `<${hstop}>` });
        if (hr.ok) { await sb.from("reminders").update({ helper_sent_at: new Date().toISOString() }).eq("id", r.id); nudged++; }
      }
    }
  }
  return Response.json({ due: due?.length ?? 0, sent, cancelled, failed, stale: stale?.length ?? 0, invites, nudged });
});
