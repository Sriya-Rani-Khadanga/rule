import { create } from "zustand";

export interface TaalEvent {
  id: string;
  name: string;
  date: string;
  startTime: string;
  endTime: string;
  priority: number;
  category: string;
}

export interface Conflict {
  eventA: TaalEvent;
  eventB: TaalEvent;
  overlapMinutes: number;
  intensity: number; // 0-1
}

export interface ResolvedEvent extends TaalEvent {
  originalStartTime: string;
  originalEndTime: string;
  wasShifted: boolean;
}

export interface ResolutionResult {
  resolvedEvents: ResolvedEvent[];
  conflicts: Conflict[];
  explanations: string[];
  metrics: {
    totalEvents: number;
    conflictsResolved: number;
    efficiency: number;
    freeTimeHours: number;
    satisfactionScore: number;
    fairnessScore: number;
  };
}

interface StoreState {
  // Events
  events: TaalEvent[];
  addEvent: (event: Omit<TaalEvent, "id">) => void;
  removeEvent: (id: string) => void;
  updateEvent: (id: string, updates: Partial<TaalEvent>) => void;
  setEvents: (events: TaalEvent[]) => void;
  clearEvents: () => void;

  // Resolution
  resolution: ResolutionResult | null;
  setResolution: (result: ResolutionResult) => void;
  isResolving: boolean;
  setIsResolving: (v: boolean) => void;

  // Scroll tracking for parallax
  scrollY: number;
  setScrollY: (y: number) => void;
}

export const useStore = create<StoreState>((set) => ({
  events: [],
  addEvent: (event) =>
    set((state) => ({
      events: [...state.events, { ...event, id: crypto.randomUUID() }],
    })),
  removeEvent: (id) =>
    set((state) => ({ events: state.events.filter((e) => e.id !== id) })),
  updateEvent: (id, updates) =>
    set((state) => ({
      events: state.events.map((e) => (e.id === id ? { ...e, ...updates } : e)),
    })),
  setEvents: (events) => set({ events }),
  clearEvents: () => set({ events: [], resolution: null }),

  resolution: null,
  setResolution: (result) => set({ resolution: result }),
  isResolving: false,
  setIsResolving: (v) => set({ isResolving: v }),

  scrollY: 0,
  setScrollY: (y) => set({ scrollY: y }),
}));
