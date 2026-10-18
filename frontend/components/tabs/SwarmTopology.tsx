'use client';

import { useDashboard } from '@/lib/dashboard-store';

const NODE = 'px-4 py-2.5 bg-cream-surface border border-cream-border rounded-[4px] text-charcoal font-medium shadow-sm';

export default function SwarmTopology() {
  const { state } = useDashboard();

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-cream-surface border border-cream-border rounded-[4px] p-6 space-y-5 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">
            LangGraph Shared Thread Topology (<span className="text-terracotta">run_8f21ac</span>)
          </h2>
          <span className="text-[11px] font-mono text-sage bg-sage-light px-2.5 py-1 rounded-[4px] border border-sage/30 font-medium whitespace-nowrap">
            CRDT Active
          </span>
        </div>
        <div className="bg-cream-warm/60 border border-cream-border rounded-[4px] min-h-64 flex items-center justify-center p-6 text-center">
          <div className="space-y-5 font-mono text-xs">
            <div className="flex flex-wrap items-center justify-center gap-3">
              <div className={NODE}>Supervisor</div>
              <span className="text-terracotta font-bold">→</span>
              <div className={NODE}>Telemetry Analyst</div>
              <span className="text-terracotta font-bold">→</span>
              <div className={NODE}>Remediation Engineer</div>
            </div>
            <p className="text-charcoal-muted text-[11px]">Zero distributed lock conflicts. Redis shared state verified.</p>
          </div>
        </div>
      </div>

      <div className="bg-cream-surface border border-cream-border rounded-[4px] p-6 flex flex-col justify-between space-y-6 shadow-sm">
        <div className="space-y-4">
          <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">Contradiction Engine</h2>
          <div className="space-y-3 font-mono text-xs">
            {state.contradictions.map((c) => (
              <div
                key={c.id}
                className={'p-3.5 bg-cream-warm border border-cream-border rounded-[4px] space-y-1 ' + (c.isNew ? 'flash' : '')}
              >
                <div className="flex justify-between text-[11px]">
                  <span className="text-amber font-semibold">{c.id} Flag</span>
                  <span className="text-charcoal-muted">Sim: {c.sim}</span>
                </div>
                <p className="text-charcoal-muted text-[11px]">{c.text}</p>
              </div>
            ))}
            <div className="p-3.5 bg-cream-warm border border-cream-border rounded-[4px] space-y-1">
              <div className="flex justify-between text-[11px]">
                <span className="text-sage font-semibold">Loop Shield</span>
                <span className="text-charcoal-muted">Nominal</span>
              </div>
              <p className="text-charcoal-muted text-[11px]">No circular delegation loops detected in thread window.</p>
            </div>
          </div>
        </div>
        <button
          type="button"
          className="w-full bg-terracotta hover:bg-terracotta-hover text-white font-mono text-xs py-2.5 rounded-[4px] transition shadow-sm font-medium"
        >
          Force Terminate Trace
        </button>
      </div>
    </div>
  );
}
