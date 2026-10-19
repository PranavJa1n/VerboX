'use client';

import { useEffect, useState } from 'react';
import StatCard from '@/components/StatCard';
import { BADGES } from '@/lib/badges';
import { useDashboard } from '@/lib/dashboard-store';
import { FLEETS } from '@/lib/initial-data';

// Mock weekly policy decisions for the bar chart (replace with API data later).
const WEEK = [
  { d: 'Mon', blocked: 14, allowed: 38 },
  { d: 'Tue', blocked: 22, allowed: 45 },
  { d: 'Wed', blocked: 9, allowed: 52 },
  { d: 'Thu', blocked: 31, allowed: 40 },
  { d: 'Fri', blocked: 17, allowed: 58 },
  { d: 'Sat', blocked: 8, allowed: 24 },
  { d: 'Sun', blocked: 11, allowed: 29 },
];
const CHART_MAX = 80;
const TICKS = [80, 60, 40, 20, 0];

function useGreeting() {
  // Resolved after mount so server and client markup match.
  const [g, setG] = useState('Welcome back');
  useEffect(() => {
    const h = new Date().getHours();
    setG(h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening');
  }, []);
  return g;
}

const pill = 'rounded-full px-5 py-2.5 text-[13px] font-semibold transition-colors';

export default function Overview() {
  const { state } = useDashboard();
  const { stats } = state;
  const greeting = useGreeting();
  const recent = state.feed.slice(0, 6);

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div className="space-y-1 pt-2">
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight text-charcoal">{greeting}, Mahadev</h1>
        <p className="text-sm text-charcoal-muted">Stay on top of your agents, monitor policy decisions, and track compliance.</p>
      </div>

      {/* Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-12 gap-5">
        {/* Trust score + fleets */}
        <section className="xl:col-span-4 bg-cream-surface rounded-3xl p-6 space-y-5">
          <div className="flex items-center justify-between">
            <p className="text-xs font-medium text-charcoal-muted">Fleet Trust Score</p>
            <span className="rounded-full bg-cream-warm px-3 py-1 text-[11px] font-medium text-charcoal-muted">12 agent versions</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-5xl font-semibold tracking-tight tabular-nums text-charcoal">0.88</span>
            <span className="rounded-full bg-sage-light px-2 py-0.5 text-[11px] font-semibold text-sage">+0.04</span>
            <span className="text-[11px] text-charcoal-subtle">from last window</span>
          </div>
          <div className="flex flex-wrap gap-3">
            <button type="button" className={pill + ' bg-charcoal text-cream-surface hover:opacity-90'}>Deploy Policies</button>
            <button type="button" className={pill + ' bg-cream-warm text-charcoal hover:bg-cream-border'}>Export Report</button>
          </div>

          <div className="bg-cream-warm rounded-2xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-charcoal">Active agent fleets</p>
              <span className="flex items-center gap-1.5 text-[11px] font-medium text-sage">
                <span className="w-1.5 h-1.5 rounded-full bg-sage" />
                Live
              </span>
            </div>
            <ul className="divide-y divide-cream-border">
              {FLEETS.map((f) => (
                <li key={f.agent} className="py-2.5 flex items-center justify-between gap-3 first:pt-0 last:pb-0">
                  <div className="min-w-0">
                    <p className="text-[13px] font-semibold text-charcoal truncate">{f.agent}</p>
                    <p className="text-[11px] text-charcoal-subtle">
                      {f.version} · <span className="text-sage font-medium">{f.clean} clean</span> ·{' '}
                      <span className={f.flaggedTone === 'muted' ? '' : f.flaggedTone === 'amber' ? 'text-amber font-medium' : 'text-terracotta font-medium'}>
                        {f.flagged} flagged
                      </span>
                    </p>
                  </div>
                  <span className="text-sm font-semibold tabular-nums text-charcoal">{f.trust}</span>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* 2 x 2 stats */}
        <div className="xl:col-span-4 grid grid-cols-2 gap-5">
          <StatCard
            accent
            label="Compute / Cost Saved"
            value={'$' + Math.round(stats.saved * 0.02408)}
            footnote={`${(stats.saved / 1000).toFixed(1)}k calls avoided via Redis`}
            flashOn={stats.saved}
          />
          <StatCard
            label="Tier 1 Blocks"
            value={stats.blocks}
            footnote="YAML rules · under 2.1 ms"
            flashOn={stats.blocks}
          />
          <StatCard
            label="Auditor Flags"
            value={stats.flags}
            footnote="LLM-as-a-Judge inspections"
            flashOn={stats.flags}
          />
          <StatCard
            label="Pending Review"
            value={stats.review}
            suffix={<span className="text-xs font-medium text-amber">verdicts</span>}
            footnote="Confidence under 95%"
            flashOn={stats.review}
          />
        </div>

        {/* Bar chart */}
        <section className="lg:col-span-2 xl:col-span-4 bg-cream-surface rounded-3xl p-6 space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-charcoal">Policy Decisions</h2>
              <p className="text-[11px] text-charcoal-subtle">Blocked vs allowed tool calls this week</p>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-charcoal-muted">
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-terracotta" />Blocked</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-charcoal" />Allowed</span>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex flex-col justify-between h-[280px] text-[10px] text-charcoal-subtle tabular-nums py-0.5">
              {TICKS.map((t) => (<span key={t}>{t}</span>))}
            </div>
            <div className="relative flex-1 h-[280px]">
              <div className="absolute inset-0 flex flex-col justify-between pointer-events-none">
                {TICKS.map((t) => (<div key={t} className="border-t border-dashed border-cream-border" />))}
              </div>
              <div className="absolute inset-0 flex items-end justify-between gap-2 px-1">
                {WEEK.map((w) => (
                  <div key={w.d} className="flex-1 h-full flex flex-col justify-end items-center gap-1" title={`${w.d}: ${w.blocked} blocked, ${w.allowed} allowed`}>
                    <div className="w-full max-w-[22px] rounded-full bg-terracotta" style={{ height: `${(w.blocked / CHART_MAX) * 100}%` }} />
                    <div className="w-full max-w-[22px] rounded-full bg-charcoal" style={{ height: `${(w.allowed / CHART_MAX) * 100}%` }} />
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="flex justify-between pl-8 pr-1 text-[10px] text-charcoal-subtle">
            {WEEK.map((w) => (<span key={w.d} className="flex-1 text-center">{w.d}</span>))}
          </div>
        </section>
      </div>

      {/* Row 2 */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <section className="xl:col-span-4 bg-cream-surface rounded-3xl p-6 flex flex-col justify-between gap-6">
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-charcoal">Governance Controls</h2>
            <button type="button" className="w-full flex items-center justify-between rounded-2xl bg-cream-warm hover:bg-cream-border px-4 py-3.5 text-left text-[13px] font-medium text-charcoal transition-colors">
              <span>Purge Redis Execution Cache</span>
              <span className="text-terracotta font-semibold">flush</span>
            </button>
            <button type="button" className="w-full flex items-center justify-between rounded-2xl bg-cream-warm hover:bg-cream-border px-4 py-3.5 text-left text-[13px] font-medium text-charcoal transition-colors">
              <span>Export Audit Compliance PDF</span>
              <span className="text-charcoal-muted">report</span>
            </button>
          </div>
          <div className="flex items-center justify-between border-t border-cream-border pt-4 text-xs text-charcoal-muted">
            <span>Governance engine</span>
            <span className="font-semibold text-charcoal">LangGraph + OPA</span>
          </div>
        </section>

        <section className="xl:col-span-8 bg-cream-surface rounded-3xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-charcoal">Recent Activities</h2>
            <span className="text-[11px] text-charcoal-subtle">Latest {recent.length} decisions</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[13px]">
              <thead>
                <tr className="bg-cream-warm text-[11px] text-charcoal-muted">
                  {['Trace ID', 'Activity', 'Agent', 'Rule', 'Status', 'Time'].map((h, i, a) => (
                    <th
                      key={h}
                      className={
                        'py-2.5 px-4 font-medium whitespace-nowrap ' +
                        (h === 'Agent' ? 'hidden 2xl:table-cell ' : '') +
                        (i === 0 ? 'rounded-l-full ' : '') +
                        (i === a.length - 1 ? 'rounded-r-full' : '')
                      }
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-cream-border">
                {recent.map((r) => {
                  const b = BADGES[r.decision];
                  return (
                    <tr key={r.id} className={r.isNew ? 'flash' : ''}>
                      <td className="py-3 px-4 font-medium text-charcoal whitespace-nowrap">{r.trace}</td>
                      <td className="py-3 px-4 text-charcoal whitespace-nowrap">{r.tool}</td>
                      <td className="py-3 px-4 text-charcoal-muted whitespace-nowrap hidden 2xl:table-cell">{r.agent}</td>
                      <td className="py-3 px-4 text-charcoal-muted whitespace-nowrap">{r.rule}</td>
                      <td className="py-3 px-4 whitespace-nowrap">
                        <span className={'inline-block rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ' + b.cls}>{b.label}</span>
                      </td>
                      <td className="py-3 px-4 text-charcoal-subtle whitespace-nowrap">{r.time}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}
