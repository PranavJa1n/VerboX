'use client';

import StatCard from '@/components/StatCard';
import { useDashboard } from '@/lib/dashboard-store';
import { FLEETS } from '@/lib/initial-data';

const flaggedTone = {
  amber: 'text-amber font-medium',
  terracotta: 'text-terracotta font-medium',
  muted: 'text-charcoal-muted',
} as const;

export default function Overview() {
  const { state } = useDashboard();
  const { stats } = state;

  return (
    <div className="space-y-8">
      <div className="space-y-1.5 border-b border-cream-border pb-6">
        <h1 className="font-serif text-3xl font-normal tracking-tight text-charcoal italic">
          Autonomous agent governance at wire speed.
        </h1>
        <p className="text-xs font-mono text-charcoal-muted tracking-wide">
          Real-time telemetry, deterministic YAML gating, and zero-hallucination verification.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label="Fleet Trust Score"
          value="0.88"
          suffix={<span className="text-xs font-mono text-sage font-medium">+0.04</span>}
          footnote="Across 12 active agent versions"
        />
        <StatCard
          label="Compute / Cost Saved"
          value={(stats.saved / 1000).toFixed(1) + 'k'}
          valueClass="text-terracotta"
          suffix={<span className="text-xs font-mono text-charcoal-muted">calls</span>}
          footnote={<>Via Redis shared result cache (${Math.round(stats.saved * 0.02408)})</>}
          flashOn={stats.saved}
        />
        <StatCard
          label="Tier 1 Blocks"
          value={stats.blocks}
          suffix={<span className="text-xs font-mono text-charcoal-muted">YAML rules</span>}
          footnote="Executed in < 2.1 milliseconds"
          flashOn={stats.blocks}
        />
        <StatCard
          label="Auditor Flags"
          value={stats.flags}
          suffix={<span className="text-xs font-mono text-amber font-medium">{stats.review} review</span>}
          footnote="LLM-as-a-Judge trace inspection"
          flashOn={`${stats.flags}-${stats.review}`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-cream-surface border border-cream-border rounded-[4px] p-6 space-y-5 shadow-sm">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">Active Agent Fleets</h2>
            <span className="text-[11px] font-mono text-sage flex items-center space-x-1.5 font-medium">
              <span className="w-2 h-2 rounded-full bg-sage" />
              <span>Live telemetry syncing</span>
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-cream-border text-charcoal-muted bg-cream-warm/50">
                  {['AGENT ID', 'VERSION', 'CLEAN', 'FLAGGED', 'TRUST'].map((h) => (
                    <th key={h} className="py-2.5 px-3 font-normal">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-border text-charcoal">
                {FLEETS.map((f) => (
                  <tr key={f.agent} className="hover:bg-cream-warm/40 transition-colors">
                    <td className="py-3 px-3 font-medium">{f.agent}</td>
                    <td className="py-3 px-3 text-charcoal-muted">{f.version}</td>
                    <td className="py-3 px-3 text-sage font-medium">{f.clean}</td>
                    <td className={'py-3 px-3 ' + flaggedTone[f.flaggedTone]}>{f.flagged}</td>
                    <td className="py-3 px-3 font-semibold">{f.trust}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-cream-surface border border-cream-border rounded-[4px] p-6 flex flex-col justify-between space-y-6 shadow-sm">
          <div className="space-y-4">
            <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">Governance Controls</h2>
            <div className="space-y-2.5 font-mono text-xs">
              <button type="button" className="w-full text-left px-4 py-3 rounded-[4px] bg-cream-warm hover:bg-cream-border/50 border border-cream-border text-charcoal transition flex items-center justify-between font-medium">
                <span>Deploy YAML Policy Bundle</span>
                <span className="text-terracotta font-bold">sync →</span>
              </button>
              <button type="button" className="w-full text-left px-4 py-3 rounded-[4px] bg-cream-warm hover:bg-cream-border/50 border border-cream-border text-charcoal transition flex items-center justify-between">
                <span>Export Audit Compliance PDF</span>
                <span className="text-charcoal-muted">report</span>
              </button>
              <button type="button" className="w-full text-left px-4 py-3 rounded-[4px] bg-cream-warm hover:bg-cream-border/50 border border-cream-border text-charcoal transition flex items-center justify-between">
                <span>Purge Redis Execution Cache</span>
                <span className="text-terracotta">flush</span>
              </button>
            </div>
          </div>
          <div className="pt-4 border-t border-cream-border text-xs font-mono text-charcoal-muted flex justify-between">
            <span>Governance Engine</span>
            <span className="text-charcoal font-medium">LangGraph + OPA</span>
          </div>
        </div>
      </div>
    </div>
  );
}
