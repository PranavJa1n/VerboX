import type { Decision } from './types';

export const BADGES: Record<Decision, { label: string; cls: string; sev: string }> = {
  blocked: { label: 'BLOCKED', cls: 'bg-terracotta-light text-terracotta border-terracotta/30', sev: 'text-terracotta' },
  failsafe: { label: 'FAIL-SAFE', cls: 'bg-amber-light text-amber border-amber/30', sev: 'text-amber' },
  halted: { label: 'HALTED', cls: 'bg-amber-light text-amber border-amber/30', sev: 'text-amber' },
  paused: { label: 'PAUSED', cls: 'bg-amber-light text-amber border-amber/30', sev: 'text-amber' },
  cached: { label: 'CACHE HIT', cls: 'bg-sage-light text-sage border-sage/30', sev: 'text-sage' },
  allowed: { label: 'ALLOWED', cls: 'bg-sage-light text-sage border-sage/30', sev: 'text-sage' },
};
