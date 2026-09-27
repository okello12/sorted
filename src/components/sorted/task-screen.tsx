import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Frame, ModeIcon, OfficialPanel, ProtectPanel, SafetyPanel } from "@/components/sorted/brand";
import {
  BOARDS,
  boardLabel,
  combineLocal,
  formatWhen,
  modeTitle,
  officialUrl,
  prepareState,
  prepareTitle,
} from "@/lib/sorted/model";
import { useSorted, useTask } from "@/lib/sorted/store";

export function TaskScreen({ id, share }: { id: string; share: boolean }) {
  const task = useTask(id);
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

  useEffect(() => {
    if (ready) return;
    void Promise.resolve(useSorted.persist.rehydrate()).finally(() => markReady());
  }, [ready, markReady]);

  if (!ready) {
    return (
      <Frame share={share}>
        <p className="text-muted">Opening…</p>
      </Frame>
    );
  }

  if (!task) {
    return (
      <Frame share={share}>
        <p className="text-lg">That task isn’t on this phone.</p>
        {share ? null : (
          <Link to="/" className="mt-4 inline-block text-navy underline">
            All tasks
          </Link>
        )}
      </Frame>
    );
  }

  const state = prepareState(task, now);

  return (
    <Frame share={share}>
      {share ? (
        <p className="mb-4 text-base text-muted">Just this task. The rest of the list stays private.</p>
      ) : (
        <Link to="/" className="mb-4 inline-flex items-center gap-1 text-base font-bold text-navy no-underline">
          <span aria-hidden>←</span> All tasks
        </Link>
      )}

      <article className="rounded-3xl bg-card p-4">
        <div className="flex items-center gap-3">
          <ModeIcon mode={task.mode} />
          <div>
            <p className="text-sm font-bold text-muted">{modeTitle(task.mode)}</p>
            <h1 className="text-2xl font-bold leading-tight text-ink">{task.title}</h1>
          </div>
        </div>

        <ol className="mt-4 flex flex-wrap gap-2" aria-label="Board">
          {BOARDS.map((item) => (
            <li
              key={item.id}
              className={`rounded-full px-3 py-1 text-sm ${item.id === task.board ? "bg-navy font-bold text-card" : "bg-paper text-muted"}`}
            >
              {item.label}
            </li>
          ))}
        </ol>

        <p className="mt-4 text-base text-muted">You were about to: {task.baseline}</p>

        <dl className="mt-4 flex flex-col gap-2 text-base">
          {task.item ? <Row k="What it is" v={task.item} /> : null}
          {task.fault ? <Row k="What’s happening" v={task.fault} /> : null}
          {task.bought ? <Row k="Bought" v={task.bought} /> : null}
          {task.retailer ? <Row k="Sold by" v={task.retailer} /> : null}
          {task.renewing ? <Row k="Renewing" v={task.renewing} /> : null}
          {task.expiry ? <Row k="Expiry" v={task.expiry} /> : null}
          {task.contact ? <Row k="Contact" v={task.contact} /> : null}
          {task.ask ? <Row k="Ask for" v={task.ask} /> : null}
        </dl>

        <div className="mt-4">
          {task.mode === "fix" ? <SafetyPanel /> : null}
          {task.mode === "renew" ? <OfficialPanel href={officialUrl(task.renewing)} /> : null}
          {task.mode === "call" || task.callAdded ? <ProtectPanel /> : null}
        </div>
      </article>

      {task.promise ? (
        <section className={`mt-4 overflow-hidden rounded-3xl ${state ? "bg-peach" : "bg-card"}`}>
          <div className="flex">
            {state ? <div className="w-2 shrink-0 bg-orange" aria-hidden /> : null}
            <div className="p-4">
              <h2 className="font-display text-3xl text-brown">
                {state ? prepareTitle(task, now, state) : "They promised"}
              </h2>
              <p className="mt-2 text-lg font-bold">{task.party || task.contact || "Them"}</p>
              <p className="text-lg">{formatWhen(task.dueAt, task.dueEnd)}</p>
              <p className="text-lg">{task.reference ? `Ref ${task.reference}` : "No reference given"}</p>
              <p className="mt-2 text-lg">{task.promise}</p>
              {state && !share ? (
                <div className="mt-4 flex flex-col gap-2">
                  <button type="button" className="min-h-12 rounded-2xl bg-navy text-lg font-bold text-card" onClick={() => setShowCard(true)}>
                    Show this
                  </button>
                  <button type="button" className="min-h-12 rounded-2xl bg-card text-lg font-bold text-navy" onClick={() => setShowDone(true)}>
                    It happened
                  </button>
                  <button type="button" className="min-h-12 text-lg text-navy underline" onClick={() => markMissed(task.id)}>
                    It didn’t happen
                  </button>
                </div>
              ) : null}
              {!state && task.board === "waiting" ? (
                <p className="mt-3 text-base text-muted">The orange card appears 24 hours before this. Not before.</p>
              ) : null}
            </div>
          </div>
        </section>
      ) : null}

      {showCard ? (
        <section className="mt-4 rounded-3xl border border-line bg-card p-5">
          <p className="text-sm font-bold tracking-wide text-muted">HOLD THIS UP</p>
          <p className="mt-2 font-display text-4xl text-ink">{task.party || task.contact || task.title}</p>
          <p className="mt-2 text-xl">{formatWhen(task.dueAt, task.dueEnd)}</p>
          <p className="text-xl font-bold">{task.reference ? `Ref ${task.reference}` : "No reference given"}</p>
          {task.item || task.fault ? (
            <p className="mt-4 text-lg">
              {task.item}
              {task.item && task.fault ? " · " : ""}
              {task.fault}
            </p>
          ) : null}
          <p className="mt-2 text-lg">They said {task.promise}</p>
        </section>
      ) : null}

      {task.events.length > 0 ? (
        <section className="mt-4">
          <h2 className="text-lg font-bold">The thread</h2>
          <ol className="mt-2 flex flex-col gap-2">
            {task.events.map((item) => (
              <li key={item.id} className="rounded-2xl bg-card px-4 py-3 text-base">
                {item.label}
              </li>
            ))}
          </ol>
        </section>
      ) : null}

      {share || task.board === "done" ? null : (
        <section className="mt-5 flex flex-col gap-3">
          {task.board === "to_sort" ? (
            <button type="button" className="min-h-12 rounded-full bg-navy px-5 text-lg font-bold text-card" onClick={() => setBoard(task.id, "your_move", "Moved to your move.")}>
              This is my next step
            </button>
          ) : null}
          {task.mode === "fix" && !task.callAdded ? (
            <button type="button" className="min-h-12 rounded-full bg-sky px-5 text-lg font-bold text-navy" onClick={() => setShowCall((open) => !open)}>
              This needs a call
            </button>
          ) : null}
          {task.board !== "waiting" ? (
            <button type="button" className="min-h-12 rounded-full bg-card px-5 text-lg font-bold text-navy" onClick={() => setShowPromise((open) => !open)}>
              Log what they promised
            </button>
          ) : null}
          <button type="button" className="min-h-12 text-lg font-bold text-navy underline" onClick={() => setShowDone((open) => !open)}>
            It’s finished
          </button>
        </section>
      )}

      {showCall && !share ? (
        <CallForm
          onSave={(contact, ask) => {
            attachCall(task.id, contact, ask);
            setShowCall(false);
          }}
        />
      ) : null}
      {showPromise && !share ? (
        <PromiseForm
          party={task.party || task.contact}
          onSave={(patch) => {
            logPromise(task.id, patch);
            setShowPromise(false);
          }}
        />
      ) : null}
      {showDone && !share ? (
        <DoneForm
          onSave={(outcome) => {
            markDone(task.id, outcome);
            setShowDone(false);
          }}
        />
      ) : null}

      {task.board === "done" && task.outcome ? (
        <p className="mt-4 text-lg">Finished. {task.outcome}</p>
      ) : null}

      {share ? null : (
        <button
          type="button"
          className="mt-6 text-base text-navy underline"
          onClick={() => {
            const url = `${window.location.origin}/tasks/${task.id}?share=1`;
            void navigator.clipboard.writeText(url).then(() => {
              setCopied(true);
              window.setTimeout(() => setCopied(false), 2000);
            });
          }}
        >
          {copied ? "Link copied" : "Copy a view-only link"}
        </button>
      )}
      <p className="mt-2 text-sm text-muted">{boardLabel(task.board)} · one task, not the whole list.</p>
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
      <h2 className="text-xl font-bold">Add the call to this task</h2>
      <label className="field">
        Who
        <input value={contact} onChange={(event) => setContact(event.target.value)} />
      </label>
      <label className="field">
        What you need to ask
        <textarea value={ask} onChange={(event) => setAsk(event.target.value)} />
      </label>
      <ProtectPanel />
      <button type="submit" className="min-h-12 rounded-full bg-navy px-5 text-lg font-bold text-card">
        Keep it on this task
      </button>
    </form>
  );
}

function PromiseForm({
  party,
  onSave,
}: {
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
      <label className="field">
        They said
        <textarea value={promise} onChange={(event) => setPromise(event.target.value)} />
      </label>
      <label className="field">
        Who
        <input value={who} onChange={(event) => setWho(event.target.value)} />
      </label>
      <label className="field">
        Date
        <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
      </label>
      <label className="field">
        Start
        <input type="time" value={start} onChange={(event) => setStart(event.target.value)} />
      </label>
      <label className="field">
        End, if there’s a slot
        <input type="time" value={end} onChange={(event) => setEnd(event.target.value)} />
      </label>
      <label className="field">
        Reference
        <input value={reference} onChange={(event) => setReference(event.target.value)} />
      </label>
      {error ? <p className="text-brown">{error}</p> : null}
      <button type="submit" className="min-h-12 rounded-full bg-navy px-5 text-lg font-bold text-card">
        Save the promise
      </button>
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
      <label className="field">
        What happened?
        <textarea value={outcome} onChange={(event) => setOutcome(event.target.value)} />
      </label>
      <button type="submit" className="mt-3 min-h-12 rounded-full bg-navy px-5 text-lg font-bold text-card">
        Mark done
      </button>
    </form>
  );
}
