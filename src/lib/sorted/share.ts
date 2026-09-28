import type { Board, Mode, SortedTask } from "@/lib/sorted/model";

export type ShareCard = {
  v: 1;
  mode: Mode;
  title: string;
  baseline: string;
  board: Board;
  item: string;
  fault: string;
  bought: string;
  retailer: string;
  renewing: string;
  expiry: string;
  contact: string;
  ask: string;
  promise: string;
  dueAt: string | null;
  dueEnd: string | null;
  reference: string;
  party: string;
  outcome: string;
};

const MODES = new Set<Mode>(["fix", "renew", "call"]);
const BOARDS = new Set<Board>(["to_sort", "your_move", "waiting", "done"]);

export function encodeShare(task: SortedTask): string {
  const card: ShareCard = {
    v: 1,
    mode: task.mode,
    title: task.title,
    baseline: task.baseline,
    board: task.board,
    item: task.item,
    fault: task.fault,
    bought: task.bought,
    retailer: task.retailer,
    renewing: task.renewing,
    expiry: task.expiry,
    contact: task.contact,
    ask: task.ask,
    promise: task.promise,
    dueAt: task.dueAt,
    dueEnd: task.dueEnd,
    reference: task.reference,
    party: task.party,
    outcome: task.outcome,
  };
  const bytes = new TextEncoder().encode(JSON.stringify(card));
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replace(/=+$/, "");
}

export function decodeShare(raw: string): ShareCard | null {
  if (!raw) return null;
  try {
    const padded = raw.replaceAll("-", "+").replaceAll("_", "/") + "===".slice((raw.length + 3) % 4);
    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
    const parsed = JSON.parse(new TextDecoder().decode(bytes)) as Partial<ShareCard>;
    if (parsed.v !== 1 || !parsed.mode || !MODES.has(parsed.mode)) return null;
    if (!parsed.board || !BOARDS.has(parsed.board) || !parsed.title) return null;
    return {
      v: 1,
      mode: parsed.mode,
      title: String(parsed.title),
      baseline: String(parsed.baseline ?? ""),
      board: parsed.board,
      item: String(parsed.item ?? ""),
      fault: String(parsed.fault ?? ""),
      bought: String(parsed.bought ?? ""),
      retailer: String(parsed.retailer ?? ""),
      renewing: String(parsed.renewing ?? ""),
      expiry: String(parsed.expiry ?? ""),
      contact: String(parsed.contact ?? ""),
      ask: String(parsed.ask ?? ""),
      promise: String(parsed.promise ?? ""),
      dueAt: parsed.dueAt ? String(parsed.dueAt) : null,
      dueEnd: parsed.dueEnd ? String(parsed.dueEnd) : null,
      reference: String(parsed.reference ?? ""),
      party: String(parsed.party ?? ""),
      outcome: String(parsed.outcome ?? ""),
    };
  } catch {
    return null;
  }
}

export function cardToTask(card: ShareCard, id: string): SortedTask {
  return {
    id,
    mode: card.mode,
    title: card.title,
    baseline: card.baseline,
    board: card.board,
    item: card.item,
    fault: card.fault,
    bought: card.bought,
    retailer: card.retailer,
    renewing: card.renewing,
    expiry: card.expiry,
    contact: card.contact,
    ask: card.ask,
    phone: "",
    callAdded: card.mode === "call" || Boolean(card.contact && card.ask),
    promise: card.promise,
    dueAt: card.dueAt,
    dueEnd: card.dueEnd,
    reference: card.reference,
    party: card.party,
    outcome: card.outcome,
    events: [],
  };
}
