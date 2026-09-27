import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";

export function Mark() {
  return (
    <span className="grid size-11 place-items-center rounded-xl bg-yellow text-navy" aria-hidden>
      <svg viewBox="0 0 24 24" className="size-6" fill="none">
        <path d="M5 12.5 10 17.5 19 7.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  );
}

export function AppHeader({ share = false }: { share?: boolean }) {
  return (
    <header className="bg-navy text-card">
      <div className="mx-auto flex w-full max-w-lg items-center justify-between px-4 py-3.5">
        {share ? (
          <span className="flex items-center gap-3">
            <Mark />
            <span className="text-3xl font-bold tracking-tight">sorted.</span>
          </span>
        ) : (
          <Link to="/" className="flex items-center gap-3 text-card no-underline">
            <Mark />
            <span className="text-3xl font-bold tracking-tight">sorted.</span>
          </Link>
        )}
        <span className="grid size-9 place-items-center text-card/80" title="This list stays on this phone">
          <svg viewBox="0 0 24 24" className="size-6" fill="none" aria-hidden>
            <path d="M12 3 5 6v6c0 4.2 2.8 7.4 7 9 4.2-1.6 7-4.8 7-9V6l-7-3Z" stroke="currentColor" strokeWidth="1.7" />
            <path d="m9 12 2 2 4-4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
          </svg>
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
    <div className="min-h-screen bg-paper">
      <AppHeader share={share} />
      <main className="mx-auto w-full max-w-lg px-4 py-5">{children}</main>
    </div>
  );
}

export function ModeIcon({ mode }: { mode: "fix" | "renew" | "call" }) {
  const bg = mode === "fix" ? "bg-lilac" : mode === "renew" ? "bg-butter" : "bg-sky";
  return (
    <span className={`grid size-12 shrink-0 place-items-center rounded-2xl ${bg} text-navy`} aria-hidden>
      {mode === "fix" ? (
        <svg viewBox="0 0 24 24" className="size-6" fill="none">
          <path d="M14.5 5.5a4 4 0 0 0-5.6 5.6L4 16.1 7.9 20l4.9-4.9a4 4 0 0 0 5.6-5.6l-2.3 2.3-2.1-2.1 2.3-2.2Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
        </svg>
      ) : mode === "renew" ? (
        <svg viewBox="0 0 24 24" className="size-6" fill="none">
          <rect x="4" y="5" width="16" height="15" rx="2" stroke="currentColor" strokeWidth="1.7" />
          <path d="M8 3.5v3M16 3.5v3M4 10h16" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" className="size-6" fill="none">
          <path d="M8 5.5c.4 2.4.2 4.2-1.2 6.2-1.6 2.2-1.5 3.6.2 5.2 1.6 1.6 3 1.8 5.2.2 2-1.4 3.8-1.6 6.2-1.2l.8 2.2c-3.2.6-5.6.2-8.2-2.4-2.6-2.6-3-5-2.4-8.2L8 5.5Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
        </svg>
      )}
    </span>
  );
}

export function SafetyPanel() {
  return (
    <aside className="overflow-hidden rounded-2xl bg-peach text-brown">
      <div className="flex">
        <div className="w-1.5 shrink-0 bg-orange" aria-hidden />
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
        <div className="w-1.5 shrink-0 bg-orange" aria-hidden />
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
    <aside className="rounded-2xl bg-official p-4 text-navy">
      <h2 className="text-lg font-bold">Check the official process</h2>
      <p className="mt-2 text-base leading-snug">
        Check the official page before applying. You can usually apply online; Post Office help is optional.
      </p>
      {href ? (
        <a href={href} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-base font-bold text-navy underline">
          Open trusted starting point
          <span aria-hidden>↗</span>
        </a>
      ) : (
        <p className="mt-3 text-base">Use the account or letter you already have. Don’t follow a link from an unexpected text.</p>
      )}
    </aside>
  );
}
