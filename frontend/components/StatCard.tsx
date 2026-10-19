'use client';

import type { ReactNode } from 'react';
import { useFlash } from '@/lib/use-flash';

interface Props {
  label: string;
  value: ReactNode;
  suffix?: ReactNode;
  footnote: ReactNode;
  /** Orange gradient hero style. */
  accent?: boolean;
  /** When this value changes the card briefly highlights. */
  flashOn?: unknown;
}

export default function StatCard({ label, value, suffix, footnote, accent = false, flashOn }: Props) {
  const flashing = useFlash(flashOn);
  return (
    <div
      className={
        'rounded-3xl p-5 flex flex-col justify-between gap-6 min-h-[150px] ' +
        (accent
          ? 'accent-card text-white shadow-lg shadow-terracotta/25 '
          : 'bg-cream-surface text-charcoal ') +
        (flashing ? 'flash' : '')
      }
    >
      <div className="flex items-start justify-between gap-2">
        <p className={'text-xs font-medium ' + (accent ? 'text-white/85' : 'text-charcoal-muted')}>{label}</p>
        <span
          className={
            'w-7 h-7 shrink-0 rounded-full flex items-center justify-center text-xs ' +
            (accent ? 'bg-white/20 text-white' : 'bg-cream-warm text-charcoal-muted')
          }
          aria-hidden="true"
        >
          ↗
        </span>
      </div>
      <div className="space-y-1">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-semibold tracking-tight tabular-nums">{value}</span>
          {suffix}
        </div>
        <p className={'text-[11px] ' + (accent ? 'text-white/80' : 'text-charcoal-subtle')}>{footnote}</p>
      </div>
    </div>
  );
}
