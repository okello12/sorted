import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { formatWhen, type Mode, type SortedTask } from "@/lib/sorted/model";

export function Mark() {
  return (
    <span className="grid size-12 place-items-center rounded-2xl bg-yellow text-navy shadow-[4px_4px_0_#c4891a]" aria-hidden>
      <svg viewBox="0 0 24 24" className="size-7" fill="none">
        <path d="M5 12.5 10 17.5 19 7.5" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}

export function AppHeader({ share = false }: { share?: boolean }) {
  const word = (
    <span className="flex items-center gap-3">
      <Mark />
      <span>
        <span className="block text-3xl font-bold leading-none tracking-tight">sorted.</span>
        <span className="mt-1 block text-sm font-bold text-yellow">{share ? "One case, for someone else" : "One case, all the way"}</span>
      </span>
    </span>
  );
  return (
    <header className="bg-navy text-card">
      <div className="h-1.5 bg-yellow" />
      <div className="mx-auto flex w-full max-w-lg items-center justify-between px-4 py-4">
        {share ? word : (
          <Link to="/" className="text-card no-underline">
            {word}
          </Link>
        )}
        <span className="hidden text-right text-sm font-bold text-card/70 sm:block">The situation stays together.</span>
      </div>
    </header>
  );
}

export function Frame({
  children,
  share = false,
}: {
  children: ReactNode;
  share?: boolean;
}) {
  return (
    <div className="min-h-screen">
      <AppHeader share={share} />
      <main className="mx-auto w-full max-w-lg px-4 py-5">{children}</main>
    </div>
  );
}

const MODE_FACE: Record<Mode, string> = {
  fix: "bg-lilac text-plum",
  renew: "bg-butter text-amber",
  call: "bg-sky text-sea",
};

export function ModeIcon({ mode, large = false }: { mode: Mode; large?: boolean }) {
  return (
    <span className={`grid shrink-0 place-items-center rounded-2xl ${MODE_FACE[mode]} ${large ? "size-16" : "size-12"}`} aria-hidden>
      <ModeGlyph mode={mode} />
    </span>
  );
}

function ModeGlyph({ mode }: { mode: Mode }) {
  if (mode === "fix") {
    return (
      <svg viewBox="0 0 48 48" className="size-8" fill="none">
        <rect x="6" y="18" width="22" height="16" rx="3" fill="currentColor" />
        <path d="M28 22h8l4 6v6h-12V22Z" fill="currentColor" opacity="0.55" />
        <circle cx="16" cy="36" r="3" fill="#fffdf8" />
        <circle cx="34" cy="36" r="3" fill="#fffdf8" />
        <path d="M14 18V12h8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
      </svg>
    );
  }
  if (mode === "renew") {
    return (
      <svg viewBox="0 0 48 48" className="size-8" fill="none">
        <rect x="10" y="8" width="22" height="30" rx="3" fill="currentColor" />
        <rect x="16" y="12" width="16" height="22" rx="2" fill="#fffdf8" />
        <circle cx="32" cy="30" r="7" fill="#e15a28" />
        <path d="m29 30 2 2 4-4" stroke="#fffdf8" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 48 48" className="size-8" fill="none">
      <path d="M16 10c1 8 0 12-4 16-3 3-2 6 1 9 4 4 8 4 13 1 4-3 8-4 14-3l2 6c-8 2-14 1-20-5-6-6-7-13-6-20l0-4Z" fill="currentColor" />
      <circle cx="34" cy="16" r="6" fill="#f0c14a" />
    </svg>
  );
}

export function TicketStack() {
  return (
    <div className="relative h-28 w-full" aria-hidden>
      <span className="absolute top-2 right-6 h-20 w-28 rotate-6 rounded-2xl bg-sky shadow-[4px_4px_0_#0d4f73]" />
      <span className="absolute top-4 right-14 h-20 w-28 -rotate-6 rounded-2xl bg-lilac shadow-[4px_4px_0_#3c2a78]" />
      <span className="absolute top-1 right-10 grid h-20 w-32 place-items-center rounded-2xl bg-yellow text-navy shadow-[4px_4px_0_#c4891a]">
        <svg viewBox="0 0 24 24" className="size-10" fill="none">
          <path d="M5 12.5 10 17.5 19 7.5" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </span>
    </div>
  );
}

export function SafetyPanel() {
  return (
    <aside className="overflow-hidden rounded-2xl bg-peach text-brown">
      <div className="flex">
        <div className="w-2 shrink-0 bg-orange" aria-hidden />
        <div className="p-4">
          <h2 className="text-lg font-bold">Stop if it seems unsafe</h2>
          <p className="mt-2 text-base leading-snug">
            If you smell burning, see damaged wiring or have water near electrical parts, switch off only if safe and seek qualified help. Do not open electrical or gas components.
          </p>
        </div>
      </div>
    </aside>
  );
}

export function ProtectPanel() {
  return (
    <aside className="overflow-hidden rounded-2xl bg-peach text-brown">
      <div className="flex">
        <div className="w-2 shrink-0 bg-orange" aria-hidden />
        <div className="p-4">
          <h2 className="text-lg font-bold">Use a number you trust</h2>
          <p className="mt-2 text-base leading-snug">
            Prefer the number on the organisation’s official website, your statement or a number you already use. Be cautious with numbers in unexpected texts or emails.
          </p>
        </div>
      </div>
    </aside>
  );
}

export function OfficialPanel({ href }: { href: string | null }) {
  return (
    <aside className="overflow-hidden rounded-2xl bg-sky text-sea">
      <div className="flex">
        <div className="w-2 shrink-0 bg-sea" aria-hidden />
        <div className="p-4">
          <h2 className="text-lg font-bold">Official route first</h2>
          <p className="mt-2 text-base leading-snug">Use the official service rather than a sponsored result or a link from an unexpected message.</p>
          {href ? (
            <a href={href} target="_blank" rel="noreferrer" className="mt-3 inline-flex min-h-11 items-center font-bold text-sea underline">
              Open the official page
            </a>
          ) : null}
        </div>
      </div>
    </aside>
  );
}

export function HoldUpCard({ task, eyebrow }: { task: SortedTask; eyebrow: string }) {
  return (
    <section className="overflow-hidden rounded-3xl bg-card shadow-[6px_6px_0_#10182b]">
      <div className="bg-navy px-4 py-3 text-card">
        <p className="text-sm font-bold tracking-[0.14em] text-yellow">{eyebrow}</p>
        <h2 className="mt-1 font-display text-3xl leading-tight">{task.title}</h2>
      </div>
      <div className="p-4">
        <dl className="grid gap-3 text-base">
          {task.item ? <InfoRow label="What" value={task.item} /> : null}
          {task.fault ? <InfoRow label="Problem" value={task.fault} /> : null}
          {task.contact ? <InfoRow label="Who" value={task.contact} /> : null}
          {task.ask ? <InfoRow label="Ask" value={task.ask} /> : null}
          {task.promise ? <InfoRow label="They promised" value={task.promise} /> : null}
          {task.dueAt ? <InfoRow label="When" value={formatWhen(task.dueAt, task.dueEnd)} /> : null}
          {task.reference ? <InfoRow label="Reference" value={task.reference} /> : null}
        </dl>
      </div>
    </section>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-sm font-bold uppercase tracking-[0.08em] text-muted">{label}</dt>
      <dd className="mt-1 text-lg text-ink">{value}</dd>
    </div>
  );
}
