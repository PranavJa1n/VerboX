import type { Contradiction, FeedRow, FleetRow, HitlCard, Stats } from './types';

export const BASE_STATS: Stats = { blocks: 412, saved: 14200, flags: 89, review: 18, pending: 18 };

export const INITIAL_FEED: FeedRow[] = [
  {
    id: 'seed-1', time: '10:22:02 UTC', trace: 'run_8f21ac', agent: 'support_agent_v2', tool: 'issue_refund',
    rule: 'max_refund_without_confirmation', decision: 'blocked', severity: 1.0,
  },
  {
    id: 'seed-2', time: '10:21:45 UTC', trace: 'run_3d91be', agent: 'remediation_engineer', tool: 'scale_k8s_deployment',
    rule: 'max_replicas_threshold', decision: 'failsafe', severity: 0.82,
  },
  {
    id: 'seed-3', time: '10:20:11 UTC', trace: 'run_1a44ef', agent: 'pixos_triage_supervisor', tool: 'get_weather',
    rule: 'allow_low_risk_lookup', decision: 'allowed', severity: 0.0,
  },
];

export const INITIAL_CONTRADICTIONS: Contradiction[] = [
  {
    id: 'c_0007',
    text: 'Verifier Agent ("Delivered") vs Support Agent ("Never delivered").',
    sim: '0.31',
  },
];

export const INITIAL_HITL: HitlCard[] = [
  {
    id: 'v_00042',
    reasoning: 'Irreversible refund issued without resolving delivery contradiction.',
    confidence: 74,
  },
];

export const FLEETS: FleetRow[] = [
  { agent: 'support_agent_v2', version: 'v3.1.0', clean: 82, flagged: 18, trust: '0.82', flaggedTone: 'amber' },
  { agent: 'pixos_triage_supervisor', version: 'v1.4.2', clean: 210, flagged: 4, trust: '0.98', flaggedTone: 'muted' },
  { agent: 'remediation_engineer', version: 'v2.0.1', clean: 95, flagged: 12, trust: '0.88', flaggedTone: 'terracotta' },
];

export const BENCHMARKS = [
  { label: 'Prompt Injection Resistance', value: '99.4%', tone: 'text-sage', note: 'Passed 500 red-team vectors' },
  { label: 'Reckless Remediation Guard', value: '100%', tone: 'text-sage', note: 'Zero unauthorized prod writes' },
  { label: 'Infinite Loop Prevention', value: '96.8%', tone: 'text-charcoal', note: 'Avg 2.1 retries before halt' },
  { label: 'Prompt Drift Score', value: 'Stable', tone: 'text-terracotta', note: 'v3 prompt version baseline' },
];
