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
        <span className="mt-1 block text-sm font-bold text-yellow">{share ? "One task, for someone else" : "On this phone"}</span>
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
        <span className="hidden text-right text-sm font-bold text-card/80 sm:block">
          Fix
          <span className="text-yellow"> · </span>
          Renew
          <span className="text-yellow"> · </span>
          Call
        </span>
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
          <h2 className="text-lg font-bold">Protect yourself before calling</h2>
          <p className="mt-2 text-base leading-snug">
            Use the organisation’s official website or an account you already trust. Do not rely on a number in an unexpected text or letter.
          </p>
        </div>
      </div>
    </aside>
  );
}

export function OfficialPanel({ href }: { href: string | null }) {
  return (
    <aside className="overflow-hidden rounded-2xl bg-official text-sea">
      <div className="flex">
        <div className="w-2 shrink-0 bg-sea" aria-hidden />
        <div className="p-4">
          <h2 className="text-lg font-bold">Check the official process</h2>
          <p className="mt-2 text-base leading-snug text-navy">
            Check the official page before applying. You can usually apply online; Post Office help is optional.
          </p>
          {href ? (
            <a href={href} target="_blank" rel="noreferrer" className="mt-3 inline-flex min-h-11 items-center gap-1 text-base font-bold text-sea underline">
              Open trusted starting point
              <span aria-hidden>↗</span>
            </a>
          ) : (
            <p className="mt-3 text-base text-navy">Use the account or letter you already have. Don’t follow a link from an unexpected text.</p>
          )}
        </div>
      </div>
    </aside>
  );
}

export function HoldUpCard({
  task,
  eyebrow,
}: {
  task: Pick<SortedTask, "title" | "party" | "contact" | "dueAt" | "dueEnd" | "reference" | "item" | "fault" | "promise" | "renewing" | "expiry">;
  eyebrow: string;
}) {
  const who = task.party || task.contact || task.title;
  return (
    <section className="docket">
      <div className="docket-head">
        <div>
          <p className="text-sm font-bold tracking-[0.14em] text-yellow">{eyebrow}</p>
          <h2 className="mt-2 font-display text-4xl leading-none text-balance">{who}</h2>
        </div>
        <p className="stamp">{task.reference ? task.reference : "No ref"}</p>
      </div>
      <div className="h-3 bg-peach" aria-hidden />
      <div className="docket-body">
        <p className="text-xl font-bold text-navy">{formatWhen(task.dueAt, task.dueEnd)}</p>
        {task.promise ? <p className="mt-2 text-lg">They said {task.promise}</p> : null}
        {task.item || task.fault ? (
          <p className="mt-3 text-lg text-ink">
            {task.item}
            {task.item && task.fault ? " · " : ""}
            {task.fault}
          </p>
        ) : null}
        {task.renewing ? (
          <p className="mt-3 text-lg">
            {task.renewing}
            {task.expiry ? ` · ${task.expiry}` : ""}
          </p>
        ) : null}
      </div>
    </section>
  );
}
