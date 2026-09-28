import { Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Frame, TicketStack } from "@/components/sorted/brand";
import { formatWhen, prepareState, type Mode, type SortedTask } from "@/lib/sorted/model";
import { useSorted } from "@/lib/sorted/store";

type CaseBucket = "needs" | "waiting" | "done";
type ComposerStep = "situation" | "baseline";

export function HomeScreen() {
  const navigate = useNavigate();
  const tasks = useSorted((state) => state.tasks);
  const ready = useSorted((state) => state.ready);
  const markReady = useSorted((state) => state.markReady);
  const addTask = useSorted((state) => state.addTask);
  const [composerOpen, setComposerOpen] = useState(false);
  const [step, setStep] = useState<ComposerStep>("situation");
  const [situation, setSituation] = useState("");
  const [baseline, setBaseline] = useState("");
  const [error, setError] = useState("");
  const now = new Date();

  useEffect(() => {
    if (ready) return;
    void Promise.resolve(useSorted.persist.rehydrate()).finally(() => markReady());
  }, [ready, markReady]);

  const groups = useMemo(() => {
    const result: Record<CaseBucket, SortedTask[]> = { needs: [], waiting: [], done: [] };
    for (const task of tasks) result[bucketFor(task, now)].push(task);
    return result;
  }, [tasks, now]);

  const openCount = groups.needs.length + groups.waiting.length;
  const nothingNeedsYou = openCount > 0 && groups.needs.length === 0;

  function resetComposer() {
    setStep("situation");
    setSituation("");
    setBaseline("");
    setError("");
    setComposerOpen(false);
  }

  function createCase() {
    if (baseline.trim().length < 2) {
      setError("Write what you were going to do next, even if the answer was ‘nothing yet’. ");
      return;
    }

    const mode = inferMode(situation);
    const id = addTask({
      mode,
      title: situation.trim(),
      baseline: baseline.trim(),
      item: "",
      fault: mode === "fix" ? situation.trim() : "",
      bought: "",
      retailer: "",
      renewing: mode === "renew" ? situation.trim() : "",
      expiry: "",
      contact: "",
      ask: "",
    });
    resetComposer();
    void navigate({ to: "/tasks/$id", params: { id }, search: { share: false } });
  }

  return (
    <Frame>
      {!ready ? <p className="text-muted">Opening your cases…</p> : null}

      {ready && openCount === 0 ? (
        <section className="overflow-hidden rounded-3xl bg-navy px-5 pt-6 pb-5 text-card shadow-[6px_6px_0_#f0c14a]">
          <p className="text-xs font-bold tracking-[0.16em] text-yellow">ONE CASE, THE WHOLE WAY</p>
          <h1 className="mt-3 max-w-sm font-display text-4xl leading-tight text-balance">
            They said Tuesday.
            <span className="mt-1 block text-yellow">Sorted remembers Tuesday.</span>
          </h1>
          <p className="mt-3 max-w-sm text-base leading-relaxed text-card/90">
            Tell Sorted what is happening. Keep the promise, the reference and the next move on the same case until it is genuinely finished.
          </p>
          <TicketStack />
        </section>
      ) : null}

      {ready && nothingNeedsYou ? (
        <section className="mb-5 overflow-hidden rounded-3xl bg-butter px-5 py-5 text-ink shadow-[4px_4px_0_#e4d7c4]">
          <p className="text-sm font-bold tracking-[0.12em] text-amber">SORTED IS HOLDING THESE</p>
          <h1 className="mt-2 font-display text-4xl leading-tight">Nothing needs you right now.</h1>
          <p className="mt-2 text-base text-ink/75">You can put these down until the other party’s clock says otherwise.</p>
        </section>
      ) : null}

      {ready && openCount > 0 ? (
        <div className="flex flex-col gap-6">
          {groups.needs.length > 0 ? (
            <CaseSection title="Needs you" count={groups.needs.length}>
              {groups.needs.map((task) => (
                <CaseCard key={task.id} task={task} now={now} bucket="needs" />
              ))}
            </CaseSection>
          ) : null}

          {groups.waiting.length > 0 ? (
            <CaseSection title="Waiting" count={groups.waiting.length}>
              {groups.waiting.map((task) => (
                <CaseCard key={task.id} task={task} now={now} bucket="waiting" />
              ))}
            </CaseSection>
          ) : null}

          {groups.done.length > 0 ? (
            <details className="rounded-3xl bg-card px-4 py-3 shadow-[0_0_0_1px_rgba(16,24,43,0.06)]">
              <summary className="cursor-pointer text-base font-bold text-muted">Done · {groups.done.length}</summary>
              <ul className="mt-3 flex flex-col gap-2">
                {groups.done.map((task) => (
                  <li key={task.id}>
                    <Link
                      to="/tasks/$id"
                      params={{ id: task.id }}
                      search={{ share: false }}
                      className="block rounded-2xl bg-paper px-4 py-3 text-ink no-underline"
                    >
                      <span className="block font-bold">{task.title}</span>
                      <span className="mt-1 block text-sm text-muted">{task.outcome || "Finished"}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            </details>
          ) : null}
        </div>
      ) : null}

      {ready ? (
        <section className={`${openCount > 0 ? "sticky bottom-3 z-10 mt-6" : "mt-5"}`}>
          {openCount > 0 && !composerOpen ? (
            <button
              type="button"
              className="btn btn-yellow shadow-[4px_4px_0_#10182b]"
              onClick={() => setComposerOpen(true)}
            >
              + Sort something else
            </button>
          ) : (
            <div className="rounded-3xl bg-card p-4 shadow-[4px_4px_0_#10182b]">
              {step === "situation" ? (
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    if (situation.trim().length < 3) {
                      setError("Tell Sorted the situation in one sentence.");
                      return;
                    }
                    setError("");
                    setStep("baseline");
                  }}
                >
                  <label className="field">
                    What do you need to sort out?
                    <span className="hint">One unfinished situation. No category to choose.</span>
                    <textarea
                      rows={3}
                      value={situation}
                      onChange={(event) => setSituation(event.target.value)}
                      placeholder="My washing machine stopped draining."
                    />
                  </label>
                  {error ? <p className="mt-2 text-base text-brown">{error}</p> : null}
                  <button type="submit" className="btn btn-navy mt-4">Start</button>
                  {openCount > 0 ? (
                    <button type="button" className="mt-3 min-h-11 w-full text-sm font-bold text-muted" onClick={resetComposer}>
                      Cancel
                    </button>
                  ) : null}
                </form>
              ) : (
                <form
                  onSubmit={(event) => {
                    event.preventDefault();
                    createCase();
                  }}
                >
                  <p className="text-sm font-bold text-muted">{situation}</p>
                  <label className="field mt-3">
                    What were you going to do next?
                    <span className="hint">Your plan first, before Sorted suggests anything.</span>
                    <textarea
                      rows={3}
                      value={baseline}
                      onChange={(event) => setBaseline(event.target.value)}
                      placeholder="I was going to call the shop."
                    />
                  </label>
                  {error ? <p className="mt-2 text-base text-brown">{error}</p> : null}
                  <button type="submit" className="btn btn-navy mt-4">Open this case</button>
                  <button type="button" className="mt-3 min-h-11 w-full text-sm font-bold text-muted" onClick={() => setStep("situation")}>
                    Back
                  </button>
                </form>
              )}
            </div>
          )}
        </section>
      ) : null}

      <p className="mt-8 text-center text-sm text-muted">The case stays open until the situation is actually finished.</p>
    </Frame>
  );
}

function CaseSection({ title, count, children }: { title: string; count: number; children: React.ReactNode }) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-display text-3xl text-ink">{title}</h2>
        <span className="rounded-full bg-navy px-3 py-1 text-sm font-bold text-yellow">{count}</span>
      </div>
      <ul className="flex flex-col gap-3">{children}</ul>
    </section>
  );
}

function CaseCard({ task, now, bucket }: { task: SortedTask; now: Date; bucket: Exclude<CaseBucket, "done"> }) {
  const state = prepareState(task, now);
  const missed = state === "missed";
  const rail = bucket === "waiting" ? "bg-amber" : missed ? "bg-orange" : "bg-lilac";
  const face = bucket === "waiting" ? "bg-butter" : "bg-card";

  return (
    <li>
      <Link
        to="/tasks/$id"
        params={{ id: task.id }}
        search={{ share: false }}
        className={`flex overflow-hidden rounded-3xl ${face} text-ink no-underline shadow-[0_0_0_1px_rgba(16,24,43,0.06),4px_4px_0_#e4d7c4]`}
      >
        <span className={`w-2 shrink-0 ${rail}`} aria-hidden />
        <span className="min-w-0 flex-1 px-4 py-4">
          <span className="block text-xl font-bold leading-snug">{task.title}</span>
          {missed ? (
            <>
              <span className="mt-1 block text-base font-bold text-brown">Visit window ended · Did they come?</span>
              <span className="mt-1 block text-sm text-muted">Open the same case to record the outcome.</span>
            </>
          ) : bucket === "waiting" ? (
            <>
              <span className="mt-1 block text-base font-bold text-navy">Waiting on {task.party || task.contact || "them"}</span>
              {task.dueAt ? <span className="mt-1 block text-sm text-ink/80">{formatWhen(task.dueAt, task.dueEnd)}{task.reference ? ` · ${task.reference}` : ""}</span> : null}
              {task.dueAt ? <span className="mt-1 block text-sm text-muted">You can put this down until {waitUntil(task)}.</span> : null}
            </>
          ) : (
            <>
              <span className="mt-1 block text-base font-bold text-navy">Your move</span>
              <span className="mt-1 block text-sm text-muted">{task.ask || task.baseline || "Open the case for the next useful step."}</span>
            </>
          )}
        </span>
        <span className="grid w-12 shrink-0 place-items-center text-2xl text-navy" aria-hidden>›</span>
      </Link>
    </li>
  );
}

function bucketFor(task: SortedTask, now: Date): CaseBucket {
  if (task.board === "done") return "done";
  if (task.board === "waiting" && prepareState(task, now) !== "missed") return "waiting";
  return "needs";
}

function waitUntil(task: SortedTask): string {
  const value = task.dueEnd || task.dueAt;
  if (!value) return "the agreed time";
  return new Date(value).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

function inferMode(text: string): Mode {
  const value = text.toLowerCase();
  if (/renew|licen[cs]e|passport|mot|tax|insurance|warranty|expire/.test(value)) return "renew";
  if (/broken|fault|leak|drain|heating|boiler|washer|washing|fridge|oven|repair|not working|stopped/.test(value)) return "fix";
  return "call";
}
