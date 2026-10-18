'use client';

import type { TabId } from '@/lib/types';

const TABS: { id: TabId; label: string }[] = [
  { id: 'overview', label: '01. Overview' },
  { id: 'policy', label: '02. Policy Feed' },
  { id: 'swarm', label: '03. Swarm Topology' },
  { id: 'benchmarks', label: '04. Benchmarks & Drift' },
  { id: 'hitl', label: '05. HITL Review Queue' },
];

export default function TabNav({ active, onChange }: { active: TabId; onChange: (t: TabId) => void }) {
  return (
    <nav className="bg-cream-surface border-b border-cream-border px-6 lg:px-10 flex space-x-8 overflow-x-auto" aria-label="Dashboard sections">
      {TABS.map((t) => {
        const isActive = t.id === active;
        return (
          <button
            key={t.id}
            type="button"
            onClick={() => onChange(t.id)}
            aria-current={isActive ? 'page' : undefined}
            className={
              'py-3.5 text-xs font-mono uppercase tracking-wider border-b-2 transition-colors flex items-center space-x-2 whitespace-nowrap ' +
              (isActive
                ? 'border-terracotta text-terracotta font-semibold'
                : 'border-transparent text-charcoal-muted hover:text-charcoal')
            }
          >
            <span>{t.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
