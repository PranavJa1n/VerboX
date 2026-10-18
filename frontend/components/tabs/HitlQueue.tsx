'use client';

import { useDashboard } from '@/lib/dashboard-store';
import { useFlash } from '@/lib/use-flash';

export default function HitlQueue() {
  const { state, label } = useDashboard();
  const pendingFlash = useFlash(state.stats.pending);

  return (
    <div className="bg-cream-surface border border-cream-border rounded-[4px] p-6 space-y-6 shadow-sm">
      <div className="flex items-center justify-between border-b border-cream-border pb-4 gap-4">
        <div>
          <h2 className="text-xs font-mono uppercase tracking-wider text-charcoal font-semibold">
            Human-in-the-Loop Verdict Validation
          </h2>
          <p className="text-xs font-mono text-charcoal-muted mt-1">
            Audit Tier 2 LLM Judge verdicts to tune confidence thresholds and generate few-shot training examples.
          </p>
        </div>
        <span
          className={
            'text-xs font-mono text-amber bg-amber-light px-3 py-1 rounded-[4px] border border-amber/30 font-medium whitespace-nowrap ' +
            (pendingFlash ? 'flash' : '')
          }
        >
          {state.stats.pending} Pending Labels
        </span>
      </div>

      <div className="space-y-4">
        {state.hitl.map((h) => (
          <div
            key={h.id}
            className={'bg-cream-warm border border-cream-border rounded-[4px] p-5 space-y-4 ' + (h.isNew ? 'flash' : '')}
          >
            <div className="flex items-center justify-between font-mono text-xs gap-3">
              <span className="text-terracotta font-semibold">Verdict ID: {h.id}</span>
              <span className="text-charcoal-muted">Confidence: {h.confidence}% (Under 95% threshold)</span>
            </div>
            <p className="text-xs font-mono text-charcoal bg-cream-surface p-3.5 rounded-[4px] border border-cream-border">
              Reasoning: &quot;{h.reasoning}&quot;
            </p>
            {h.label ? (
              <div className="font-mono text-xs">
                <span className="text-sage font-medium">
                  ✓ Labeled &quot;{h.label}&quot; — stored in human_labels, queued for few-shot refinement
                </span>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-3 font-mono text-xs">
                <button
                  type="button"
                  onClick={() => label(h.id, 'agree')}
                  className="px-4 py-1.5 rounded-[4px] bg-sage-light text-sage border border-sage/30 hover:bg-sage/10 transition font-medium"
                >
                  Agree
                </button>
                <button
                  type="button"
                  onClick={() => label(h.id, 'disagree')}
                  className="px-4 py-1.5 rounded-[4px] bg-terracotta-light text-terracotta border border-terracotta/30 hover:bg-terracotta/10 transition font-medium"
                >
                  Disagree
                </button>
                <button
                  type="button"
                  onClick={() => label(h.id, 'partially correct')}
                  className="px-4 py-1.5 rounded-[4px] bg-cream-surface text-charcoal-muted border border-cream-border hover:bg-cream-warm transition"
                >
                  Partially Correct
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
