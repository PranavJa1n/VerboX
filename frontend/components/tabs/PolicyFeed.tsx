'use client';

import { BADGES } from '@/lib/badges';
import { useDashboard } from '@/lib/dashboard-store';

export default function PolicyFeed({ onOpenDemo }: { onOpenDemo: () => void }) {
  const { state } = useDashboard();

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-cream-surface border border-cream-border p-4 rounded-[4px] shadow-sm">
        <div className="flex items-center space-x-3 text-xs font-mono">
          <span className="text-charcoal-muted font-medium">FILTER:</span>
          <select className="bg-cream-warm border border-cream-border rounded-[4px] px-3 py-1.5 text-charcoal focus:outline-none font-medium">
            <option>All Severities</option>
            <option>Critical (&gt;0.8)</option>
            <option>Warning (&gt;0.5)</option>
          </select>
          <select className="bg-cream-warm border border-cream-border rounded-[4px] px-3 py-1.5 text-charcoal focus:outline-none font-medium">
            <option>All Decisions</option>
            <option>Blocked Only</option>
            <option>Fail-Safe</option>
          </select>
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="text"
            placeholder="Search trace_id or tool..."
            className="bg-cream-warm border border-cream-border text-xs font-mono rounded-[4px] px-3.5 py-1.5 text-charcoal placeholder-charcoal-subtle focus:outline-none w-64"
          />
          <button
            type="button"
            onClick={onOpenDemo}
            className="bg-terracotta hover:bg-terracotta-hover text-white font-mono font-medium text-xs px-4 py-1.5 rounded-[4px] transition shadow-sm"
          >
            Simulate
          </button>
        </div>
      </div>

      <div className="bg-cream-surface border border-cream-border rounded-[4px] overflow-x-auto shadow-sm">
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="bg-cream-warm border-b border-cream-border text-charcoal-muted">
              {['TIMESTAMP', 'TRACE ID', 'AGENT ID', 'TOOL NAME', 'POLICY RULE', 'DECISION', 'SEVERITY'].map((h) => (
                <th key={h} className="p-3.5 font-normal">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-cream-border text-charcoal">
            {state.feed.map((r) => {
              const b = BADGES[r.decision];
              return (
                <tr key={r.id} className={'hover:bg-cream-warm/40 transition-colors ' + (r.isNew ? 'flash' : '')}>
                  <td className="p-3.5 text-charcoal-muted">{r.time}</td>
                  <td className="p-3.5 text-terracotta font-medium">{r.trace}</td>
                  <td className="p-3.5 font-medium">{r.agent}</td>
                  <td className="p-3.5">{r.tool}</td>
                  <td className="p-3.5 text-charcoal-muted">{r.rule}</td>
                  <td className="p-3.5">
                    <span className={'px-2 py-0.5 rounded-[4px] border font-semibold ' + b.cls}>{b.label}</span>
                  </td>
                  <td className={'p-3.5 font-semibold ' + b.sev}>{r.severity.toFixed(2)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
