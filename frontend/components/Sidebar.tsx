'use client';

import type { ReactNode } from 'react';
import type { TabId } from '@/lib/types';
import { TABS } from './TabNav';

const svg = (children: ReactNode) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {children}
  </svg>
);

const ICONS: Record<TabId, ReactNode> = {
  overview: svg(<><rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" /><rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" /></>),
  policy: svg(<path d="M12 3l8 3v6c0 4.5-3.2 8.3-8 9-4.8-.7-8-4.5-8-9V6z" />),
  swarm: svg(<><circle cx="6" cy="12" r="2.5" /><circle cx="18" cy="6" r="2.5" /><circle cx="18" cy="18" r="2.5" /><path d="M8.2 10.8l7.6-3.6M8.2 13.2l7.6 3.6" /></>),
  benchmarks: svg(<path d="M5 20V10M12 20V4M19 20v-7" />),
  hitl: svg(<><circle cx="9" cy="8" r="3.5" /><path d="M2.5 20c.6-3.6 3.2-5.5 6.5-5.5S14.9 16.4 15.5 20" /><path d="M16 11l2 2 4-4" /></>),
};

/** Slim rounded icon rail (desktop only), mirrors the header navigation. */
export default function Sidebar({ active, onChange }: { active: TabId; onChange: (t: TabId) => void }) {
  return (
    <aside className="hidden lg:flex flex-col items-center gap-2 bg-cream-surface rounded-full p-2 w-14 self-start sticky top-24" aria-label="Quick navigation">
      {TABS.map((t) => {
        const isActive = t.id === active;
        return (
          <button
            key={t.id}
            type="button"
            title={t.label}
            aria-label={t.label}
            aria-current={isActive ? 'page' : undefined}
            onClick={() => onChange(t.id)}
            className={
              'w-10 h-10 rounded-full flex items-center justify-center transition-colors ' +
              (isActive ? 'bg-charcoal text-cream-surface' : 'text-charcoal-muted hover:bg-cream-warm hover:text-charcoal')
            }
          >
            {ICONS[t.id]}
          </button>
        );
      })}
    </aside>
  );
}
