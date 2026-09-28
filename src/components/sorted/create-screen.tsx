import { Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Frame, ModeIcon, OfficialPanel, ProtectPanel, SafetyPanel } from "@/components/sorted/brand";
import { RENEW_KINDS, modeTitle, officialUrl, type Mode } from "@/lib/sorted/model";
import { useSorted } from "@/lib/sorted/store";

export function CreateScreen({ mode }: { mode: Mode }) {
  const navigate = useNavigate();
  const addTask = useSorted((state) => state.addTask);
  const [step, setStep] = useState<"baseline" | "form">("baseline");
  const [baseline, setBaseline] = useState("");
  const [title, setTitle] = useState("");
  const [item, setItem] = useState("");
  const [fault, setFault] = useState("");
  const [bought, setBought] = useState("");
  const [retailer, setRetailer] = useState("");
  const [renewing, setRenewing] = useState("UK passport");
  const [expiry, setExpiry] = useState("");
  const [contact, setContact] = useState("");
  const [ask, setAsk] = useState("");
  const [error, setError] = useState("");

  return (
    <Frame>
      <Link to="/" className="mb-4 inline-flex items-center gap-1 text-base font-bold text-navy no-underline">
        <span aria-hidden>←</span> All tasks
      </Link>
      <section className="overflow-hidden rounded-3xl bg-card shadow-[4px_4px_0_#10182b]">
        <div className={`flex items-center gap-3 px-4 py-4 ${mode === "fix" ? "bg-lilac" : mode === "renew" ? "bg-butter" : "bg-sky"}`}>
          <ModeIcon mode={mode} large />
          <div>
            <p className="text-sm font-bold tracking-wide text-navy">{step === "baseline" ? "First, your plan" : "Then the facts"}</p>
            <h1 className="font-display text-3xl leading-none text-ink">{modeTitle(mode)}</h1>
          </div>
        </div>
        <div className="p-4">

        {step === "baseline" ? (
          <form
            className="mt-5"
            onSubmit={(event) => {
              event.preventDefault();
              if (baseline.trim().length < 3) {
                setError("Write what you were about to do, even if it was “leave it”.");
                return;
              }
              setError("");
              setStep("form");
            }}
          >
            <label className="field">
              What were you about to do?
              <span className="hint">Asked before any guidance, so this is your plan — not ours.</span>
              <textarea value={baseline} onChange={(event) => setBaseline(event.target.value)} rows={3} />
            </label>
            {error ? <p className="mt-3 text-base text-brown">{error}</p> : null}
            <button type="submit" className="btn btn-yellow mt-5">
              Continue
            </button>
          </form>
        ) : (
          <form
            className="mt-5 flex flex-col gap-4"
            onSubmit={(event) => {
              event.preventDefault();
              if (!title.trim()) {
                setError("Give it a name you would recognise later.");
                return;
              }
              const id = addTask({
                mode,
                title,
                baseline,
                item,
                fault,
                bought,
                retailer,
                renewing: mode === "renew" ? renewing : "",
                expiry: mode === "renew" ? expiry : "",
                contact: mode === "call" ? contact : "",
                ask: mode === "call" ? ask : "",
              });
              void navigate({ to: "/tasks/$id", params: { id }, search: { share: false } });
            }}
          >
            <label className="field">
              What are you sorting out?
              <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder={placeholder(mode)} />
            </label>
            {mode === "fix" ? (
              <>
                <label className="field">
                  What is it?
                  <span className="hint">Brand and model if you have them</span>
                  <input value={item} onChange={(event) => setItem(event.target.value)} />
                </label>
                <label className="field">
                  What is happening?
                  <textarea value={fault} onChange={(event) => setFault(event.target.value)} placeholder="Describe the fault or error code" />
                </label>
                <label className="field">
                  When did you buy it?
                  <input value={bought} onChange={(event) => setBought(event.target.value)} />
                </label>
                <label className="field">
                  Who sold it to you?
                  <input value={retailer} onChange={(event) => setRetailer(event.target.value)} placeholder="Retailer, if known" />
                </label>
                <SafetyPanel />
              </>
            ) : null}
            {mode === "renew" ? (
              <>
                <label className="field">
                  What needs renewing?
                  <select value={renewing} onChange={(event) => setRenewing(event.target.value)}>
                    {RENEW_KINDS.map((kind) => (
                      <option key={kind}>{kind}</option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  Expiry or renewal date
                  <input value={expiry} onChange={(event) => setExpiry(event.target.value)} placeholder="For example, 12 Dec 2026" />
                </label>
                <OfficialPanel href={officialUrl(renewing)} />
              </>
            ) : null}
            {mode === "call" ? (
              <>
                <label className="field">
                  Who do you need to contact?
                  <input value={contact} onChange={(event) => setContact(event.target.value)} placeholder="The account you already trust" />
                </label>
                <label className="field">
                  What do you need to ask for?
                  <textarea value={ask} onChange={(event) => setAsk(event.target.value)} placeholder="Explain the bill and confirm the correct amount" />
                </label>
                <ProtectPanel />
              </>
            ) : null}
            {error ? <p className="text-base text-brown">{error}</p> : null}
            <button type="submit" className="btn btn-navy w-fit">
              Create task
            </button>
          </form>
        )}
        </div>
      </section>
    </Frame>
  );
}

function placeholder(mode: Mode): string {
  if (mode === "fix") return "Washing machine won’t drain";
  if (mode === "renew") return "Renew my passport";
  return "Call about the energy bill";
}
