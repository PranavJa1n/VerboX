'use client';

import type { TabId } from '@/lib/types';

export const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'policy', label: 'Policy Feed' },
  { id: 'swarm', label: 'Swarm Topology' },
  { id: 'benchmarks', label: 'Benchmarks' },
  { id: 'hitl', label: 'Review Queue' },
];

/** Centered pill navigation shown in the header. Active tab is a solid black pill. */
export default function TabNav({ active, onChange }: { active: TabId; onChange: (t: TabId) => void }) {
  return (
    <nav
      className="bg-cream-surface rounded-full p-1.5 flex items-center gap-1 overflow-x-auto max-w-full"
      aria-label="Dashboard sections"
    >
      {TABS.map((t) => {
        const isActive = t.id === active;
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => onChange(t.id)}
            aria-current={isActive ? 'page' : undefined}
            className={
              'rounded-full px-4 py-2 text-[13px] font-medium whitespace-nowrap transition-colors ' +
              (isActive
                ? 'bg-charcoal text-cream-surface'
                : 'text-charcoal-muted hover:text-charcoal hover:bg-cream-warm')
            }
          >
            {t.label}
          </button>
        );
      })}
    </nav>
  );
}
