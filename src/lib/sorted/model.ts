export type Mode = "fix" | "renew" | "call";
export type Board = "to_sort" | "your_move" | "waiting" | "done";
export type FilterId = "all" | Board;

export type ThreadEvent = {
  id: string;
  at: string;
  label: string;
};

export type SortedTask = {
  id: string;
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
  phone: string;
  callAdded: boolean;
  promise: string;
  dueAt: string | null;
  dueEnd: string | null;
  reference: string;
  party: string;
  outcome: string;
  events: ThreadEvent[];
};

export const FILTERS: { id: FilterId; label: string }[] = [
  { id: "all", label: "All" },
  { id: "to_sort", label: "To sort" },
  { id: "your_move", label: "Your move" },
  { id: "waiting", label: "Waiting" },
  { id: "done", label: "Done" },
];

export const BOARDS: { id: Board; label: string }[] = [
  { id: "to_sort", label: "To sort" },
  { id: "your_move", label: "Your move" },
  { id: "waiting", label: "Waiting" },
  { id: "done", label: "Done" },
];

export const MODES: { id: Mode; title: string; hint: string }[] = [
  { id: "fix", title: "Fix something", hint: "Find a safe next step" },
  { id: "renew", title: "Renew something", hint: "Know what to do and when" },
  { id: "call", title: "Make a call", hint: "Get ready and note the outcome" },
];

export const RENEW_KINDS = [
  "UK passport",
  "Driving licence",
  "MOT",
  "Car tax",
  "Home insurance",
  "Warranty",
  "TV licence",
  "Something else",
] as const;

const OFFICIAL: Record<string, string> = {
  "UK passport": "https://www.gov.uk/renew-adult-passport",
  "Driving licence": "https://www.gov.uk/renew-driving-licence",
  MOT: "https://www.gov.uk/getting-an-mot",
  "Car tax": "https://www.gov.uk/vehicle-tax",
  "TV licence": "https://www.tvlicensing.co.uk/",
};

export function officialUrl(kind: string): string | null {
  return OFFICIAL[kind] ?? null;
}

export function isMode(value: string): value is Mode {
  return value === "fix" || value === "renew" || value === "call";
}

export function boardLabel(board: Board): string {
  return BOARDS.find((item) => item.id === board)?.label ?? board;
}

export function modeTitle(mode: Mode): string {
  return MODES.find((item) => item.id === mode)?.title ?? mode;
}

export type PrepareState = "prepare" | "missed" | null;

export function prepareState(task: SortedTask, now: Date): PrepareState {
  if (task.board !== "waiting" || !task.dueAt) return null;
  const due = new Date(task.dueAt).getTime();
  if (Number.isNaN(due)) return null;
  if (now.getTime() >= due) return "missed";
  if (now.getTime() >= due - 24 * 60 * 60 * 1000) return "prepare";
  return null;
}

export function prepareTitle(task: SortedTask, now: Date, state: PrepareState): string {
  if (state === "missed") return "Check outcome";
  const due = task.dueAt ? new Date(task.dueAt) : null;
  if (!due) return "Due";
  const sameDay = startOfDay(now).getTime() === startOfDay(due).getTime();
  return sameDay ? "Due today" : "Due tomorrow";
}

export function formatWhen(dueAt: string | null, dueEnd: string | null): string {
  if (!dueAt) return "No time set";
  const due = new Date(dueAt);
  const date = due.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" });
  const start = clock(due);
  if (!dueEnd) return `${date}  ${start}`;
  const end = new Date(dueEnd);
  return `${date}  ${start}–${clock(end)}`;
}

export function listMeta(task: SortedTask, now: Date): string {
  const state = prepareState(task, now);
  if (state === "prepare" && task.dueAt) return `${prepareTitle(task, now, state)} · ${clock(new Date(task.dueAt))}`;
  if (state === "missed") return "Check outcome";
  if (task.board === "done") return task.outcome || "Finished";
  if (task.board === "waiting" && task.dueAt) return formatWhen(task.dueAt, task.dueEnd);
  if (task.expiry) return `Expires ${task.expiry}`;
  return boardLabel(task.board);
}

export function matchesFilter(task: SortedTask, filter: FilterId): boolean {
  if (filter === "all") return true;
  return task.board === filter;
}

export function combineLocal(date: string, time: string): string | null {
  if (!date || !time) return null;
  const [year, month, day] = date.split("-").map(Number);
  const [hours, minutes] = time.split(":").map(Number);
  if (!year || !month || !day || Number.isNaN(hours) || Number.isNaN(minutes)) return null;
  return new Date(year, month - 1, day, hours, minutes, 0, 0).toISOString();
}

function clock(date: Date): string {
  return date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
}

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function at(now: Date, dayOffset: number, hours: number, minutes: number): string {
  const date = new Date(now);
  date.setDate(date.getDate() + dayOffset);
  date.setHours(hours, minutes, 0, 0);
  return date.toISOString();
}

function event(label: string, hoursAgo = 0): ThreadEvent {
  return { id: `${label.slice(0, 12)}-${hoursAgo}`, at: new Date(Date.now() - hoursAgo * 3600000).toISOString(), label };
}

export function buildSeed(now: Date): SortedTask[] {
  const due = at(now, 1, 8, 0);
  const end = at(now, 1, 13, 0);
  return [
    {
      id: "heat",
      mode: "fix",
      title: "Heating",
      baseline: "I was going to call the letting agent again.",
      board: "your_move",
      item: "Boiler and radiators",
      fault: "No heating",
      bought: "",
      retailer: "",
      renewing: "",
      expiry: "",
      contact: "Oakridge Lettings",
      ask: "Confirm when an engineer is coming.",
      phone: "",
      callAdded: true,
      promise: "",
      dueAt: null,
      dueEnd: null,
      reference: "",
      party: "Oakridge Lettings",
      outcome: "",
      events: [event("You recorded that the heating is still not working.", 2)],
    },
    {
      id: "wash",
      mode: "fix",
      title: "Washing machine",
      baseline: "I was going to call the retailer.",
      board: "waiting",
      item: "Bosch washing machine",
      fault: "Won’t drain",
      bought: "Mar 2023",
      retailer: "John Lewis",
      renewing: "",
      expiry: "",
      contact: "John Lewis",
      ask: "Send an engineer. It’s still under warranty.",
      phone: "",
      callAdded: true,
      promise: "Engineer visit",
      dueAt: due,
      dueEnd: end,
      reference: "OL-55821",
      party: "John Lewis",
      outcome: "",
      events: [
        event("You recorded the washing machine fault.", 30),
        event("You called John Lewis and asked for an engineer.", 26),
        event("They promised an engineer visit and gave reference OL-55821.", 20),
      ],
    },
  ];
}
