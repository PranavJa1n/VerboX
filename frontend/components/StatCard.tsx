'use client';

import type { ReactNode } from 'react';
import { useFlash } from '@/lib/use-flash';

interface Props {
  label: string;
  value: ReactNode;
  valueClass?: string;
  suffix?: ReactNode;
  footnote: ReactNode;
  /** When this value changes the card briefly highlights. */
  flashOn?: unknown;
}

export default function StatCard({ label, value, valueClass = 'text-charcoal', suffix, footnote, flashOn }: Props) {
  const flashing = useFlash(flashOn);
  return (
    <div className={'bg-cream-surface border border-cream-border rounded-[4px] p-5 space-y-2.5 shadow-sm ' + (flashing ? 'flash' : '')}>
      <p className="text-[11px] font-mono text-charcoal-muted uppercase tracking-wider">{label}</p>
      <div className="flex items-baseline space-x-2">
        <span className={'text-3xl font-mono font-semibold ' + valueClass}>{value}</span>
        {suffix}
      </div>
      <p className="text-[11px] font-mono text-charcoal-subtle">{footnote}</p>
    </div>
  );
}
