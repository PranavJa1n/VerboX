'use client';

import { createContext, useContext, useMemo, useReducer, type ReactNode } from 'react';
import { BASE_STATS, INITIAL_CONTRADICTIONS, INITIAL_FEED, INITIAL_HITL } from './initial-data';
import type { Contradiction, DashboardActions, FeedRow, HitlCard, StatKey, Stats } from './types';

interface State {
  stats: Stats;
  feed: FeedRow[];
  contradictions: Contradiction[];
  hitl: HitlCard[];
}

type Action =
  | { type: 'bump'; key: StatKey; n: number }
  | { type: 'feed'; row: FeedRow }
  | { type: 'contradiction'; item: Contradiction }
  | { type: 'hitl'; item: HitlCard }
  | { type: 'label'; id: string; label: string }
  | { type: 'resetStats' };

const FEED_LIMIT = 14;

const initialState: State = {
  stats: BASE_STATS,
  feed: INITIAL_FEED,
  contradictions: INITIAL_CONTRADICTIONS,
  hitl: INITIAL_HITL,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'bump':
      return { ...state, stats: { ...state.stats, [action.key]: state.stats[action.key] + action.n } };
    case 'feed':
      return { ...state, feed: [action.row, ...state.feed].slice(0, FEED_LIMIT) };
    case 'contradiction':
      return { ...state, contradictions: [action.item, ...state.contradictions] };
    case 'hitl':
      return { ...state, hitl: [action.item, ...state.hitl] };
    case 'label': {
      const target = state.hitl.find((h) => h.id === action.id);
      if (!target || target.label) return state;
      return {
        ...state,
        hitl: state.hitl.map((h) => (h.id === action.id ? { ...h, label: action.label } : h)),
        stats: {
          ...state.stats,
          pending: Math.max(0, state.stats.pending - 1),
          review: Math.max(0, state.stats.review - 1),
        },
      };
    }
    case 'resetStats':
      return { ...state, stats: BASE_STATS };
    default:
      return state;
  }
}

const uid = () => Math.random().toString(36).slice(2, 10);

interface DashboardContextValue extends DashboardActions {
  state: State;
  label(id: string, label: string): void;
  resetStats(): void;
}

const DashboardContext = createContext<DashboardContextValue | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  // dispatch is stable, so the action object is created once and safe to call from async code.
  const actions = useMemo<DashboardActions & { label(id: string, label: string): void; resetStats(): void }>(
    () => ({
      bump: (key, n) => dispatch({ type: 'bump', key, n }),
      addFeedRow: (row) =>
        dispatch({
          type: 'feed',
          row: { ...row, id: uid(), time: new Date().toISOString().slice(11, 19) + ' UTC', isNew: true },
        }),
      addContradiction: (c) => dispatch({ type: 'contradiction', item: { ...c, isNew: true } }),
      addHitl: (h) => dispatch({ type: 'hitl', item: { ...h, isNew: true } }),
      label: (id, label) => dispatch({ type: 'label', id, label }),
      resetStats: () => dispatch({ type: 'resetStats' }),
    }),
    [],
  );

  const value = useMemo(() => ({ state, ...actions }), [state, actions]);
  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard(): DashboardContextValue {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error('useDashboard must be used inside <DashboardProvider>');
  return ctx;
}
