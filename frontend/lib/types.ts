export type TabId = 'overview' | 'policy' | 'swarm' | 'benchmarks' | 'hitl';

export type Decision = 'blocked' | 'failsafe' | 'halted' | 'paused' | 'cached' | 'allowed';

export interface FeedRow {
  id: string;
  time: string;
  trace: string;
  agent: string;
  tool: string;
  rule: string;
  decision: Decision;
  severity: number;
  isNew?: boolean;
}

export interface Contradiction {
  id: string;
  text: string;
  sim: string;
  isNew?: boolean;
}

export interface HitlCard {
  id: string;
  reasoning: string;
  confidence: number;
  label?: string;
  isNew?: boolean;
}

export interface Stats {
  blocks: number;
  saved: number;
  flags: number;
  review: number;
  pending: number;
}
export type StatKey = keyof Stats;

export interface FleetRow {
  agent: string;
  version: string;
  clean: number;
  flagged: number;
  trust: string;
  flaggedTone: 'amber' | 'terracotta' | 'muted';
}

export type StageId = 'agent' | 'sdk' | 'tier1' | 'cache' | 'stream' | 'tier2' | 'hitl' | 'ui';
export type LogKind = 'info' | 'ok' | 'warn' | 'block' | 'sys';

export interface DashboardActions {
  bump(key: StatKey, n: number): void;
  addFeedRow(row: Omit<FeedRow, 'id' | 'time' | 'isNew'>): void;
  addContradiction(c: { id: string; text: string; sim: string }): void;
  addHitl(h: { id: string; reasoning: string; confidence: number }): void;
}

export interface ScenarioCtx {
  trace: string;
  cid: string;
  vid: string;
}

export interface ScenarioStep {
  stage: StageId;
  tag: string;
  kind: LogKind;
  text: string;
  fx?: (ctx: ScenarioCtx, api: DashboardActions) => void;
}

export interface Scenario {
  title: string;
  fix: string;
  flaw: string;
  steps: ScenarioStep[];
}
