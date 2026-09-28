import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Frame, ModeIcon, TicketStack } from "@/components/sorted/brand";
import {
  FILTERS,
  boardLabel,
  listMeta,
  matchesFilter,
  modeTitle,
  type FilterId,
  type Mode,
} from "@/lib/sorted/model";
import { useSorted } from "@/lib/sorted/store";

const STARTS: { mode: Mode; title: string; hint: string; face: string }[] = [
  { mode: "fix", title: "Fix something", hint: "Find a safe next step", face: "bg-lilac" },
  { mode: "renew", title: "Renew something", hint: "Know what to do and when", face: "bg-butter" },
  { mode: "call", title: "Make a call", hint: "Get ready and note the outcome", face: "bg-sky" },
];

const SPINE: Record<Mode, string> = {
  fix: "bg-plum",
  renew: "bg-amber",
  call: "bg-sea",
};

export function HomeScreen() {
  const tasks = useSorted((state) => state.tasks);
  const ready = useSorted((state) => state.ready);
  const markReady = useSorted((state) => state.markReady);
  const [filter, setFilter] = useState<FilterId>("all");
  const now = new Date();

  useEffect(() => {
    if (ready) return;
    void Promise.resolve(useSorted.persist.rehydrate()).finally(() => markReady());
  }, [ready, markReady]);

  const visible = tasks.filter((task) => matchesFilter(task, filter));

  return (
    <Frame>
      <section className="overflow-hidden rounded-3xl bg-navy px-5 pt-6 pb-5 text-card shadow-[6px_6px_0_#f0c14a]">
        <p className="text-xs font-bold tracking-[0.16em] text-yellow">ONE TASK, THE WHOLE WAY</p>
        <h1 className="mt-3 max-w-xs font-display text-4xl leading-tight text-balance">
          Life gets messy.
          <span className="mt-1 block text-yellow">Sorted keeps up.</span>
        </h1>
        <p className="mt-3 max-w-sm text-base leading-relaxed text-card/90">
          Start with what you were about to do. The call and what they promised stay on that same task — and come back when they’re due.
        </p>
        <TicketStack />
      </section>

      <ul className="mt-5 flex flex-col gap-3">
        {STARTS.map((item) => (
          <li key={item.mode}>
            <Link
              to="/new/$mode"
              params={{ mode: item.mode }}
              className={`flex items-center gap-3 rounded-3xl ${item.face} px-3 py-3 text-ink no-underline shadow-[4px_4px_0_#10182b]`}
            >
              <ModeIcon mode={item.mode} large />
              <span className="min-w-0 flex-1">
                <span className="block text-xl font-bold">{item.title}</span>
                <span className="block text-base text-ink/75">{item.hint}</span>
              </span>
              <span className="grid size-11 place-items-center rounded-full bg-navy text-sm font-bold text-card">Start</span>
            </Link>
          </li>
        ))}
      </ul>

      <div className="mt-8 flex items-end justify-between gap-3">
        <h2 className="font-display text-3xl text-ink">Your tasks</h2>
        <span className="mb-1 rounded-full bg-navy px-3 py-1 text-sm font-bold text-yellow">{tasks.length}</span>
      </div>

      <div className="mt-3 flex gap-2 overflow-x-auto rounded-full bg-card p-1 shadow-[0_0_0_1px_rgba(16,24,43,0.06)]" role="tablist" aria-label="Task states">
        {FILTERS.map((item) => {
          const on = filter === item.id;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={on}
              className={`min-h-11 shrink-0 rounded-full px-4 text-base ${on ? "bg-yellow font-bold text-navy" : "text-muted"}`}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {!ready ? <p className="mt-6 text-muted">Opening your tasks…</p> : null}

      {ready && visible.length === 0 ? (
        <div className="mt-4 rounded-3xl bg-card px-6 py-12 text-center shadow-[4px_4px_0_#e4d7c4]">
          <p className="font-display text-3xl text-ink">Your list starts here</p>
          <p className="mt-2 text-base text-muted">Start with the job you need to sort.</p>
        </div>
      ) : null}

      {ready && visible.length > 0 ? (
        <ul className="mt-4 flex flex-col gap-3">
          {visible.map((task) => (
            <li key={task.id}>
              <Link
                to="/tasks/$id"
                params={{ id: task.id }}
                search={{ share: false }}
                className="flex overflow-hidden rounded-3xl bg-card text-ink no-underline shadow-[0_0_0_1px_rgba(16,24,43,0.06),4px_4px_0_#e4d7c4]"
              >
                <span className={`w-2 shrink-0 ${SPINE[task.mode]}`} aria-hidden />
                <span className="flex min-w-0 gap-3 px-4 py-4">
                  <ModeIcon mode={task.mode} />
                  <span className="min-w-0">
                    <span className="block text-lg font-bold leading-snug">{task.title}</span>
                    <span className="mt-1 block text-base font-bold text-navy">{listMeta(task, now)}</span>
                    <span className="block text-sm text-muted">
                      {modeTitle(task.mode)} · {boardLabel(task.board)}
                    </span>
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}

      <p className="mt-8 text-center text-sm text-muted">One task, from the first question to the promise that’s due.</p>
    </Frame>
  );
}
