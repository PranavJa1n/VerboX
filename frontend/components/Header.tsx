'use client';

import type { TabId } from '@/lib/types';
import TabNav from './TabNav';
import ThemeToggle from './ThemeToggle';

const circleBtn =
  'w-10 h-10 rounded-full bg-cream-surface text-charcoal-muted hover:text-charcoal flex items-center justify-center transition-colors';

interface Props {
  active: TabId;
  onTabChange: (t: TabId) => void;
  onOpenDemo: () => void;
}

export default function Header({ active, onTabChange, onOpenDemo }: Props) {
  return (
    <header className="sticky top-0 z-50 px-4 sm:px-6 lg:px-8 pt-4 pb-3 bg-cream/85 backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3 lg:flex-nowrap">
        {/* Brand */}
        <div className="bg-cream-surface rounded-full pl-1.5 pr-4 py-1.5 flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-full bg-terracotta flex items-center justify-center font-bold text-white text-sm">V</div>
          <span className="font-semibold text-[15px] tracking-tight text-charcoal">VerboX</span>
        </div>

        {/* Center navigation (full row on small screens) */}
        <div className="order-last w-full flex justify-center lg:order-none lg:w-auto min-w-0">
          <TabNav active={active} onChange={onTabChange} />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          <button type="button" className={circleBtn + ' hidden sm:flex'} aria-label="Search">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-3.5-3.5" />
            </svg>
          </button>
          <button type="button" className={circleBtn + ' relative hidden sm:flex'} aria-label="Notifications">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M6 9a6 6 0 1 1 12 0c0 6 2.5 7.5 2.5 7.5h-17S6 15 6 9z" />
              <path d="M10 20a2 2 0 0 0 4 0" />
            </svg>
            <span className="absolute top-2.5 right-2.5 w-2 h-2 rounded-full bg-terracotta" />
          </button>

          <button
            type="button"
            onClick={onOpenDemo}
            className="h-10 px-4 rounded-full bg-terracotta hover:bg-terracotta-hover text-white text-[13px] font-semibold flex items-center gap-2 transition-colors"
            aria-haspopup="dialog"
          >
            <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor" aria-hidden="true"><path d="M1 0.5v9l8-4.5z" /></svg>
            <span>Live Demo</span>
          </button>

          {/* ThemeToggle picks up its look from the global pill rules */}
          <ThemeToggle />

          <div className="hidden md:flex items-center gap-2.5 bg-cream-surface rounded-full pl-1.5 pr-4 py-1.5">
            <div className="w-8 h-8 rounded-full bg-charcoal text-cream-surface flex items-center justify-center text-[11px] font-semibold">MG</div>
            <div className="leading-tight">
              <p className="text-[13px] font-semibold text-charcoal">Mahadev G.</p>
              <p className="text-[11px] text-charcoal-subtle">Admin</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
