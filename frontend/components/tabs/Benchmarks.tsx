'use client';

import { BENCHMARKS } from '@/lib/initial-data';

export default function Benchmarks({ onOpenDemo }: { onOpenDemo: () => void }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {BENCHMARKS.map((b) => (
          <div key={b.label} className="bg-cream-surface border border-cream-border rounded-[4px] p-5 space-y-2.5 shadow-sm">
            <p className="text-[11px] font-mono text-charcoal-muted uppercase tracking-wider">{b.label}</p>
            <p className={'text-3xl font-mono font-semibold ' + b.tone}>{b.value}</p>
            <p className="text-[11px] font-mono text-charcoal-subtle">{b.note}</p>
          </div>
        ))}
      </div>

      <div className="bg-cream-surface border border-cream-border rounded-[4px] p-6 space-y-3 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">Adversarial Regression Suite</h2>
          <button
            type="button"
            onClick={onOpenDemo}
            className="bg-terracotta text-white font-mono text-xs px-4 py-2 rounded-[4px] font-medium hover:bg-terracotta-hover transition shadow-sm"
          >
            Run Red-Team Suite
          </button>
        </div>
        <p className="text-xs font-mono text-charcoal-muted">
          Continuous automated evaluation against LocalStack chaos injectors and benchmark policy suites.
        </p>
      </div>
    </div>
  );
}
