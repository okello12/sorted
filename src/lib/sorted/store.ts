import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { buildSeed, type Board, type Mode, type SortedTask } from "@/lib/sorted/model";

type Draft = {
  mode: Mode;
  title: string;
  baseline: string;
  item: string;
  fault: string;
  bought: string;
  retailer: string;
  renewing: string;
  expiry: string;
  contact: string;
  ask: string;
};

type SortedStore = {
  tasks: SortedTask[];
  ready: boolean;
  markReady: () => void;
  addTask: (draft: Draft) => string;
  setBoard: (id: string, board: Board, label: string) => void;
  attachCall: (id: string, contact: string, ask: string) => void;
  logPromise: (
    id: string,
    patch: { promise: string; dueAt: string; dueEnd: string | null; reference: string; party: string },
  ) => void;
  markDone: (id: string, outcome: string) => void;
  markMissed: (id: string) => void;
  resetExamples: () => void;
};

function mapTask(tasks: SortedTask[], id: string, fn: (task: SortedTask) => SortedTask) {
  return tasks.map((task) => (task.id === id ? fn(task) : task));
}

function stamp(label: string): SortedTask["events"][number] {
  return { id: crypto.randomUUID(), at: new Date().toISOString(), label };
}

export const useSorted = create<SortedStore>()(
  persist(
    (set) => ({
      tasks: buildSeed(new Date()),
      ready: false,
      markReady: () => set({ ready: true }),
      addTask: (draft) => {
        const id = crypto.randomUUID();
        const task: SortedTask = {
          id,
          mode: draft.mode,
          title: draft.title.trim(),
          baseline: draft.baseline.trim(),
          board: "to_sort",
          item: draft.item.trim(),
          fault: draft.fault.trim(),
          bought: draft.bought.trim(),
          retailer: draft.retailer.trim(),
          renewing: draft.renewing.trim(),
          expiry: draft.expiry.trim(),
          contact: draft.contact.trim(),
          ask: draft.ask.trim(),
          phone: "",
          callAdded: draft.mode === "call",
          promise: "",
          dueAt: null,
          dueEnd: null,
          reference: "",
          party: draft.contact.trim(),
          outcome: "",
          events: [stamp("Task created. Waiting for the first real step.")],
        };
        set((state) => ({ tasks: [task, ...state.tasks] }));
        return id;
      },
      setBoard: (id, board, label) =>
        set((state) => ({
          tasks: mapTask(state.tasks, id, (task) => ({
            ...task,
            board,
            events: [...task.events, stamp(label)],
          })),
        })),
      attachCall: (id, contact, ask) =>
        set((state) => ({
          tasks: mapTask(state.tasks, id, (task) => ({
            ...task,
            contact: contact.trim(),
            ask: ask.trim(),
            party: task.party || contact.trim(),
            callAdded: true,
            board: task.board === "to_sort" ? "your_move" : task.board,
            events: [...task.events, stamp(`Call added: ${contact.trim()}. ${ask.trim()}`)],
          })),
        })),
      logPromise: (id, patch) =>
        set((state) => ({
          tasks: mapTask(state.tasks, id, (task) => ({
            ...task,
            ...patch,
            board: "waiting",
            events: [...task.events, stamp(`They promised: ${patch.promise}`)],
          })),
        })),
      markDone: (id, outcome) =>
        set((state) => ({
          tasks: mapTask(state.tasks, id, (task) => ({
            ...task,
            board: "done",
            outcome: outcome.trim(),
            events: [...task.events, stamp(`Finished. ${outcome.trim()}`)],
          })),
        })),
      markMissed: (id) =>
        set((state) => ({
          tasks: mapTask(state.tasks, id, (task) => ({
            ...task,
            board: "your_move",
            events: [...task.events, stamp("Nothing happened. Back to your move.")],
          })),
        })),
      resetExamples: () => set({ tasks: buildSeed(new Date()) }),
    }),
    {
      name: "sorted.v1",
      storage: createJSONStorage(() => localStorage),
      skipHydration: true,
      partialize: (state) => ({ tasks: state.tasks }),
    },
  ),
);

export function useTask(id: string): SortedTask | undefined {
  return useSorted((state) => state.tasks.find((task) => task.id === id));
}
