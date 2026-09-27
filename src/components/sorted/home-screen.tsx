import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Frame, ModeIcon } from "@/components/sorted/brand";
import {
  FILTERS,
  boardLabel,
  listMeta,
  matchesFilter,
  modeTitle,
  type FilterId,
} from "@/lib/sorted/model";
import { useSorted } from "@/lib/sorted/store";

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
      <section className="overflow-hidden rounded-3xl bg-navy px-5 py-6 text-card">
        <p className="text-xs font-bold tracking-[0.16em] text-yellow">YOUR EVERYDAY ACTION SPACE</p>
        <h1 className="mt-3 font-display text-4xl leading-tight text-balance">
          Life gets messy.
          <span className="mt-1 block text-yellow">Sorted keeps up.</span>
        </h1>
        <p className="mt-3 max-w-sm text-base leading-relaxed text-card/85">
          Fix it. Renew it. Make the call. Keep the whole story — including what they promised — in one place.
        </p>
      </section>

      <ul className="mt-4 flex flex-col gap-3">
        {(
          [
            ["fix", "Fix something", "Find a safe next step", "bg-lilac"],
            ["renew", "Renew something", "Know what to do and when", "bg-butter"],
            ["call", "Make a call", "Get ready and note the outcome", "bg-sky"],
          ] as const
        ).map(([mode, title, hint, bg]) => (
          <li key={mode}>
            <Link
              to="/new/$mode"
              params={{ mode }}
              className={`flex items-center gap-3 rounded-3xl ${bg} px-3 py-3 text-ink no-underline`}
            >
              <ModeIcon mode={mode} />
              <span className="min-w-0 flex-1">
                <span className="block text-xl font-bold">{title}</span>
                <span className="block text-base text-muted">{hint}</span>
              </span>
              <span className="pr-2 text-base font-bold text-navy">Start →</span>
            </Link>
          </li>
        ))}
      </ul>

      <div className="mt-8 flex items-center gap-2">
        <h2 className="text-2xl font-bold text-ink">Your tasks</h2>
        <span className="grid min-w-7 place-items-center rounded-full bg-line px-2 text-sm font-bold text-muted">{tasks.length}</span>
      </div>

      <div className="mt-3 flex gap-2 overflow-x-auto pb-1" role="tablist" aria-label="Task states">
        {FILTERS.map((item) => {
          const on = filter === item.id;
          return (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={on}
              className={`min-h-11 shrink-0 rounded-full px-4 text-base ${on ? "bg-navy font-bold text-card" : "text-muted"}`}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {!ready ? <p className="mt-6 text-muted">Opening your tasks…</p> : null}

      {ready && visible.length === 0 ? (
        <div className="mt-4 rounded-3xl border border-dashed border-line bg-card px-6 py-12 text-center">
          <p className="text-xl font-bold text-ink">Your list starts here</p>
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
                className="flex gap-3 rounded-3xl bg-card px-4 py-4 text-ink no-underline shadow-[0_1px_0_rgba(16,24,43,0.04)]"
              >
                <ModeIcon mode={task.mode} />
                <span className="min-w-0">
                  <span className="block text-lg font-bold leading-snug">{task.title}</span>
                  <span className="mt-1 block text-base text-navy">{listMeta(task, now)}</span>
                  <span className="block text-sm text-muted">
                    {modeTitle(task.mode)} · {boardLabel(task.board)}
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}

      <p className="mt-8 text-center text-sm text-muted">Sorted · One task, from first question to finished.</p>
    </Frame>
  );
}
