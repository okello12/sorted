import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Frame, HoldUpCard, OfficialPanel, ProtectPanel, SafetyPanel } from "@/components/sorted/brand";
import { combineLocal, formatWhen, officialUrl, prepareState, type SortedTask } from "@/lib/sorted/model";
import { cardToTask, decodeShare, encodeShare } from "@/lib/sorted/share";
import { useSorted, useTask } from "@/lib/sorted/store";

export function TaskScreen({ id, share }: { id: string; share: boolean }) {
  const live = useTask(id);
  const ready = useSorted((state) => state.ready);
  const markReady = useSorted((state) => state.markReady);
  const setBoard = useSorted((state) => state.setBoard);
  const attachCall = useSorted((state) => state.attachCall);
  const logPromise = useSorted((state) => state.logPromise);
  const markDone = useSorted((state) => state.markDone);
  const markMissed = useSorted((state) => state.markMissed);
  const [now] = useState(() => new Date());
  const [showCall, setShowCall] = useState(false);
  const [showPromise, setShowPromise] = useState(false);
  const [showDone, setShowDone] = useState(false);
  const [showCard, setShowCard] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copiedChase, setCopiedChase] = useState(false);
  const [snapshot] = useState(() => {
    if (!share || typeof window === "undefined") return null;
    const card = decodeShare(window.location.hash.replace(/^#/, ""));
    return card ? cardToTask(card, id) : null;
  });

  useEffect(() => {
    if (ready) return;
    void Promise.resolve(useSorted.persist.rehydrate()).finally(() => markReady());
  }, [ready, markReady]);

  const task = share && snapshot ? snapshot : live;
  const fromLink = Boolean(share && snapshot);

  if (!ready && !fromLink) {
    return (
      <Frame share={share}>
        <p className="text-muted">Opening…</p>
      </Frame>
    );
  }

  if (!task) {
    return (
      <Frame share={share}>
        <p className="text-lg">That case isn’t on this phone.</p>
        {share ? <p className="mt-2 text-base text-muted">The link did not include a case to read.</p> : (
          <Link to="/" className="mt-4 inline-block text-navy underline">All cases</Link>
        )}
      </Frame>
    );
  }

  const state = prepareState(task, now);
  const missedRecorded = task.board === "your_move" && Boolean(task.promise) && task.events.some((item) => item.label.includes("Nothing happened"));
  const status = caseStatus(task, state);
  const rail = status === "Waiting on them" ? "bg-amber" : status === "Check outcome" ? "bg-orange" : status === "Done" ? "bg-sea" : "bg-lilac";

  return (
    <Frame share={share}>
      {share ? (
        <div className="mb-4">
          <HoldUpCard task={task} eyebrow={fromLink ? "SHARED CASE" : "ONE CASE"} />
          <p className="mt-3 text-base text-muted">Just this case. Everything else stays private.</p>
        </div>
      ) : (
        <Link to="/" className="mb-4 inline-flex items-center gap-1 text-base font-bold text-navy no-underline">
          <span aria-hidden>←</span> All cases
        </Link>
      )}

      <article className="overflow-hidden rounded-3xl bg-card shadow-[4px_4px_0_#e4d7c4]">
        <div className={`h-2 ${rail}`} />
        <div className="p-4">
          <p className="text-sm font-bold uppercase tracking-[0.1em] text-muted">{status}</p>
          <h1 className="mt-1 font-display text-3xl leading-tight text-ink">{task.title}</h1>
          <p className="mt-4 text-base text-muted"><strong className="text-ink">You recorded:</strong> {task.baseline}</p>

          <dl className="mt-4 flex flex-col gap-2 text-base">
            {task.item ? <Row k="What it is" v={task.item} /> : null}
            {task.fault && task.fault !== task.title ? <Row k="What’s happening" v={task.fault} /> : null}
            {task.bought ? <Row k="Bought" v={task.bought} /> : null}
            {task.retailer ? <Row k="Sold by" v={task.retailer} /> : null}
            {task.expiry ? <Row k="Expiry" v={task.expiry} /> : null}
            {task.contact ? <Row k="Who" v={task.contact} /> : null}
            {task.ask ? <Row k="What you need" v={task.ask} /> : null}
          </dl>

          <div className="mt-4">
            {task.mode === "fix" ? <SafetyPanel /> : null}
            {task.mode === "renew" ? <OfficialPanel href={officialUrl(task.renewing)} /> : null}
            {task.mode === "call" || task.callAdded ? <ProtectPanel /> : null}
          </div>
        </div>
      </article>

      {task.promise && !share ? (
        <section className={`docket mt-4 ${state === "missed" ? "bg-peach" : state === "prepare" ? "bg-butter" : ""}`}>
          <div className={`docket-head ${state === "missed" ? "bg-orange" : ""}`}>
            <div>
              <p className={`text-sm font-bold tracking-[0.14em] ${state === "missed" ? "text-card" : "text-yellow"}`}>
                {state === "missed" ? "CHECK OUTCOME" : state === "prepare" ? "COMING UP" : "THEY SAID"}
              </p>
              <h2 className="mt-1 font-display text-4xl leading-none">
                {state === "missed" ? "Did it happen?" : state === "prepare" ? "Get ready" : "Waiting"}
              </h2>
            </div>
            <p className={`stamp ${state === "missed" ? "border-card text-card" : ""}`}>{task.reference || "No ref"}</p>
          </div>
          <div className="docket-body">
            <p className="text-sm font-bold uppercase tracking-[0.08em] text-muted">They said</p>
            <p className="mt-1 text-lg font-bold">{task.party || task.contact || "Them"}</p>
            <p className="text-lg">{formatWhen(task.dueAt, task.dueEnd)}</p>
            <p className="mt-2 text-lg">{task.promise}</p>

            {state === "missed" ? (
              <div className="mt-4 flex flex-col gap-3">
                <button type="button" className="btn btn-navy" onClick={() => setShowDone(true)}>They came</button>
                <button type="button" className="btn btn-paper" onClick={() => markMissed(task.id)}>Nobody came</button>
                <button type="button" className="btn btn-paper" onClick={() => setShowPromise(true)}>They rescheduled</button>
              </div>
            ) : state === "prepare" ? (
              <div className="mt-4">
                <p className="text-base text-muted">Nothing to chase yet. Have the reference and any useful details ready.</p>
                <button type="button" className="btn btn-paper mt-3" onClick={() => setShowCard(true)}>Show this</button>
              </div>
            ) : (
              <p className="mt-3 text-base text-muted">You can put this down until the agreed time.</p>
            )}
          </div>
        </section>
      ) : null}

      {missedRecorded && !share ? (
        <section className="mt-4 overflow-hidden rounded-3xl bg-card shadow-[4px_4px_0_#e4d7c4]">
          <div className="border-l-8 border-orange p-4">
            <p className="text-sm font-bold uppercase tracking-[0.1em] text-brown">Your move</p>
            <h2 className="mt-1 font-display text-3xl text-ink">They missed it. Chase it up.</h2>
            <p className="mt-2 text-base text-muted">The next line is already written from this case.</p>
            <div className="mt-3 rounded-2xl bg-paper p-4 text-base leading-relaxed text-ink">{chaseMessage(task)}</div>
            <button
              type="button"
              className="btn btn-navy mt-3"
              onClick={() => {
                void navigator.clipboard.writeText(chaseMessage(task)).then(() => {
                  setCopiedChase(true);
                  window.setTimeout(() => setCopiedChase(false), 1800);
                });
              }}
            >
              {copiedChase ? "Copied" : "Copy chase message"}
            </button>
          </div>
        </section>
      ) : null}

      {showCard && !share ? (
        <div className="mt-4"><HoldUpCard task={task} eyebrow="SHOW THIS" /></div>
      ) : null}

      {task.events.length > 0 ? (
        <section className="mt-4">
          <h2 className="text-lg font-bold">The thread</h2>
          <ol className="mt-2 border-l-4 border-yellow pl-3">
            {task.events.map((item) => (
              <li key={item.id} className="mb-2 rounded-2xl bg-card px-4 py-3 text-base shadow-[3px_3px_0_#e4d7c4]">
                <span className="mb-1 block text-xs font-bold uppercase tracking-[0.1em] text-muted">{provenance(item.label)}</span>
                {item.label}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      {share || task.board === "done" ? null : (
        <section className="mt-5 flex flex-col gap-3">
          {task.board === "to_sort" ? (
            <button type="button" className="btn btn-navy" onClick={() => setBoard(task.id, "your_move", "You chose this as the next move.")}>This is my next step</button>
          ) : null}
          {task.mode === "fix" && !task.callAdded ? (
            <button type="button" className="btn btn-paper bg-sky" onClick={() => setShowCall((open) => !open)}>This needs a call</button>
          ) : null}
          {task.board !== "waiting" ? (
            <button type="button" className="btn btn-yellow" onClick={() => setShowPromise((open) => !open)}>Log what they promised</button>
          ) : null}
          <button type="button" className="min-h-12 text-lg font-bold text-navy underline" onClick={() => setShowDone((open) => !open)}>It’s finished</button>
        </section>
      )}

      {showCall && !share ? (
        <CallForm onSave={(contact, ask) => { attachCall(task.id, contact, ask); setShowCall(false); }} />
      ) : null}
      {showPromise && !share ? (
        <PromiseForm
          party={task.party || task.contact}
          onSave={(patch) => { logPromise(task.id, patch); setShowPromise(false); }}
        />
      ) : null}
      {showDone && !share ? (
        <DoneForm onSave={(outcome) => { markDone(task.id, outcome); setShowDone(false); }} />
      ) : null}

      {task.board === "done" && task.outcome ? (
        <section className="mt-4 rounded-3xl bg-butter p-4 shadow-[4px_4px_0_#e4d7c4]">
          <p className="text-sm font-bold uppercase tracking-[0.1em] text-amber">Done</p>
          <h2 className="mt-1 font-display text-3xl text-ink">This one is finished.</h2>
          <p className="mt-2 text-lg text-ink">{task.outcome}</p>
        </section>
      ) : null}

      {share ? null : (
        <button type="button" className="btn btn-yellow mt-6" onClick={() => {
          const url = `${window.location.origin}/tasks/${task.id}?share=1#${encodeShare(task)}`;
          void navigator.clipboard.writeText(url).then(() => {
            setCopied(true);
            window.setTimeout(() => setCopied(false), 2000);
          });
        }}>
          {copied ? "Link copied — send that" : "Share this case"}
        </button>
      )}
      <p className="mt-2 text-sm text-muted">Sharing carries this case only. It does not expose the rest of your cases.</p>
    </Frame>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex gap-3">
      <dt className="w-28 shrink-0 text-muted">{k}</dt>
      <dd>{v}</dd>
    </div>
  );
}

function CallForm({ onSave }: { onSave: (contact: string, ask: string) => void }) {
  const [contact, setContact] = useState("");
  const [ask, setAsk] = useState("");
  return (
    <form
      className="mt-4 flex flex-col gap-3 rounded-3xl bg-sky p-4"
      onSubmit={(event) => {
        event.preventDefault();
        if (!contact.trim() || !ask.trim()) return;
        onSave(contact, ask);
      }}
    >
      <h2 className="text-xl font-bold">Add the call to this case</h2>
      <label className="field">Who<input value={contact} onChange={(event) => setContact(event.target.value)} /></label>
      <label className="field">What you need to ask<textarea value={ask} onChange={(event) => setAsk(event.target.value)} /></label>
      <ProtectPanel />
      <button type="submit" className="btn btn-navy">Keep it on this case</button>
    </form>
  );
}

function PromiseForm({ party, onSave }: {
  party: string;
  onSave: (patch: { promise: string; dueAt: string; dueEnd: string | null; reference: string; party: string }) => void;
}) {
  const [promise, setPromise] = useState("");
  const [who, setWho] = useState(party);
  const [date, setDate] = useState("");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [reference, setReference] = useState("");
  const [error, setError] = useState("");
  return (
    <form
      className="mt-4 flex flex-col gap-3 rounded-3xl bg-card p-4"
      onSubmit={(event) => {
        event.preventDefault();
        const dueAt = combineLocal(date, start);
        if (!promise.trim() || !dueAt) {
          setError("Write what they said, and when.");
          return;
        }
        let dueEnd = end ? combineLocal(date, end) : null;
        if (dueEnd && new Date(dueEnd) <= new Date(dueAt)) dueEnd = null;
        onSave({ promise: promise.trim(), dueAt, dueEnd, reference: reference.trim(), party: who.trim() });
      }}
    >
      <h2 className="text-xl font-bold">What did they promise?</h2>
      <p className="text-sm text-muted">Nothing becomes case fact until you save it here.</p>
      <label className="field">They said<textarea value={promise} onChange={(event) => setPromise(event.target.value)} /></label>
      <label className="field">Who<input value={who} onChange={(event) => setWho(event.target.value)} /></label>
      <label className="field">Date<input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
      <label className="field">Start<input type="time" value={start} onChange={(event) => setStart(event.target.value)} /></label>
      <label className="field">End, if there’s a slot<input type="time" value={end} onChange={(event) => setEnd(event.target.value)} /></label>
      <label className="field">Reference<input value={reference} onChange={(event) => setReference(event.target.value)} /></label>
      {error ? <p className="text-brown">{error}</p> : null}
      <button type="submit" className="btn btn-navy">Save the promise</button>
    </form>
  );
}

function DoneForm({ onSave }: { onSave: (outcome: string) => void }) {
  const [outcome, setOutcome] = useState("");
  return (
    <form
      className="mt-4 rounded-3xl bg-card p-4"
      onSubmit={(event) => {
        event.preventDefault();
        if (!outcome.trim()) return;
        onSave(outcome);
      }}
    >
      <label className="field">What finally happened?<textarea value={outcome} onChange={(event) => setOutcome(event.target.value)} /></label>
      <button type="submit" className="btn btn-navy mt-3">Finish this case</button>
    </form>
  );
}

function caseStatus(task: SortedTask, state: ReturnType<typeof prepareState>): string {
  if (task.board === "done") return "Done";
  if (task.board === "waiting" && state === "missed") return "Check outcome";
  if (task.board === "waiting") return "Waiting on them";
  return "Your move";
}

function provenance(label: string): "They said" | "You" | "Sorted" {
  if (/they promised|they said/i.test(label)) return "They said";
  if (/due|remind|sorted|suggest/i.test(label)) return "Sorted";
  return "You";
}

function chaseMessage(task: SortedTask): string {
  const who = task.party || task.contact || "you";
  const ref = task.reference ? ` reference ${task.reference}` : "";
  const when = task.dueAt ? ` for ${formatWhen(task.dueAt, task.dueEnd)}` : "";
  const promised = task.promise ? ` You said: “${task.promise}.”` : "";
  return `Hi, I’m following up with ${who} about${ref}${when}.${promised} It didn’t happen as agreed. Please can you confirm what happens next and the new arrangement?`;
}
