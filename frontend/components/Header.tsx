'use client';

import ThemeToggle from './ThemeToggle';

export default function Header({ onOpenDemo }: { onOpenDemo: () => void }) {
  return (
    <header className="border-b border-cream-border bg-cream-surface sticky top-0 z-50 px-4 sm:px-6 lg:px-10 py-3.5 flex items-center justify-between shadow-sm gap-3">
      <div className="flex items-center space-x-5">
        <div className="flex items-center space-x-3">
          <div className="w-7 h-7 bg-terracotta flex items-center justify-center font-mono font-bold text-white text-xs rounded-[4px] shadow-sm">V</div>
          <span className="font-serif font-semibold text-lg tracking-tight text-charcoal">VerboX</span>
          <span className="hidden sm:inline text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 rounded-[4px] bg-cream-warm text-charcoal-muted border border-cream-border font-medium">
            Control Plane
          </span>
        </div>
        <div className="h-4 w-px bg-cream-border hidden sm:block" />
        <div className="hidden lg:flex items-center space-x-2 text-xs font-mono text-charcoal-muted bg-cream-warm px-3 py-1 rounded-[4px] border border-cream-border">
          <span className="w-2 h-2 rounded-full bg-sage animate-pulse" />
          <span className="font-medium text-charcoal">ENV: PRODUCTION-US-EAST</span>
        </div>
      </div>

      <div className="flex items-center space-x-3 sm:space-x-4 text-xs font-mono text-charcoal-muted">
        <div className="hidden xl:flex items-center space-x-5 border-r border-cream-border pr-5">
          <span>OPA LATENCY: <strong className="text-charcoal font-semibold">1.8ms</strong></span>
          <span>ACTIVE GUARDRAILS: <strong className="text-charcoal font-semibold">148</strong></span>
        </div>

        <button
          type="button"
          onClick={onOpenDemo}
          className="flex items-center space-x-2 bg-terracotta hover:bg-terracotta-hover text-white font-mono font-medium text-xs px-3.5 py-2 rounded-[4px] transition shadow-sm"
          aria-haspopup="dialog"
        >
          <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor" aria-hidden="true"><path d="M1 0.5v9l8-4.5z" /></svg>
          <span>Live Demo</span>
        </button>

        <ThemeToggle />

        <div className="hidden sm:flex items-center space-x-2.5 bg-cream-warm px-3 py-1.5 rounded-[4px] border border-cream-border">
          <div className="w-5 h-5 rounded-[4px] bg-terracotta flex items-center justify-center text-white font-semibold text-[10px]">MG</div>
          <span className="text-charcoal font-medium">Mahadev G.</span>
        </div>
      </div>
    </header>
  );
}
