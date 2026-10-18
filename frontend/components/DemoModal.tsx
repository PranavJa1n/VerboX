'use client';

import { useEffect, useRef, useState } from 'react';
import { SCENARIOS, STAGES } from '@/lib/demo-data';
import { useDashboard } from '@/lib/dashboard-store';
import type { LogKind, ScenarioCtx, StageId } from '@/lib/types';

interface LogLine {
  id: number;
  ts: string;
  tag: string;
  kind: LogKind;
  text: string;
}

const hex = (n: number) =>
  Array.from({ length: n }, () => '0123456789abcdef'[Math.floor(Math.random() * 16)]).join('');
const sleep = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

export default function DemoModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const api = useDashboard();

  const [lines, setLines] = useState<LogLine[]>([]);
  const [stage, setStage] = useState<{ active: StageId | null; done: StageId[] }>({ active: null, done: [] });
  const [current, setCurrent] = useState<number | null>(null);
  const [status, setStatus] = useState('Idle');
  const [running, setRunning] = useState(false);
  const [speed, setSpeed] = useState(1);

  const runId = useRef(0);
  const t0 = useRef(0);
  const lineId = useRef(0);
  const speedRef = useRef(1);
  const termRef = useRef<HTMLDivElement>(null);
  const runAllRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    speedRef.current = speed;
  }, [speed]);

  // Auto-scroll the terminal
  useEffect(() => {
    const el = termRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [lines]);

  // Scroll lock, focus and Escape handling while open
  useEffect(() => {
    if (!open) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    runAllRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = prevOverflow;
      document.removeEventListener('keydown', onKey);
    };
  }, [open, onClose]);

  // Cancel any in-flight run when the modal closes or unmounts
  useEffect(() => {
    if (!open) {
      runId.current++;
      setRunning(false);
    }
  }, [open]);
  useEffect(() => () => void runId.current++, []);

  const log = (tag: string, kind: LogKind, text: string) => {
    const ts = ((Date.now() - t0.current) / 1000).toFixed(1).padStart(4, '0');
    setLines((prev) => [...prev, { id: lineId.current++, ts, tag, kind, text }]);
  };

  const moveStage = (name: StageId | null) =>
    setStage((s) => {
      const done = new Set(s.done);
      if (s.active) done.add(s.active);
      if (name) done.delete(name);
      return { active: name, done: [...done] };
    });

  async function runScenarios(indices: number[]) {
    if (running) return;
    const my = ++runId.current;
    const wait = (ms: number) => sleep(ms / speedRef.current);

    setRunning(true);
    setLines([]);
    t0.current = Date.now();
    setStatus('Running…');
    log('SYSTEM', 'sys', 'VerboX demo started · mock agents, no real API calls');

    for (const i of indices) {
      if (my !== runId.current) return;
      const sc = SCENARIOS[i];
      const ctx: ScenarioCtx = { trace: 'run_' + hex(6), cid: '00' + (8 + i), vid: '000' + (43 + i) };

      setStage({ active: null, done: [] });
      setCurrent(i);
      log('SYSTEM', 'sys', `── Scenario 0${i + 1}: ${sc.title} · trace ${ctx.trace} ──`);
      await wait(500);

      for (const step of sc.steps) {
        if (my !== runId.current) return;
        moveStage(step.stage);
        const text = step.text
          .replace('{trace}', ctx.trace)
          .replace('{id}', hex(5))
          .replace('{cid}', ctx.cid);
        log(step.tag, step.kind, text);
        step.fx?.(ctx, api);
        await wait(950);
      }
      moveStage(null);
      await wait(450);
    }

    if (my !== runId.current) return;
    log('SYSTEM', 'sys', 'Done. Check the Policy Feed, Swarm Topology and HITL tabs to see what was recorded.');
    setStatus('Finished · dashboard updated');
    setRunning(false);
  }

  function stop() {
    runId.current++;
    setRunning(false);
    moveStage(null);
    log('SYSTEM', 'warn', 'Stopped by user');
    setStatus('Stopped');
  }

  function resetStats() {
    api.resetStats();
    setStatus('Dashboard numbers reset (demo rows stay in the feeds until reload)');
  }

  if (!open) return null;

  const sc = current !== null ? SCENARIOS[current] : null;

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm p-3 sm:p-6 overflow-y-auto"
      role="dialog"
      aria-modal="true"
      aria-labelledby="demo-title"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="max-w-6xl mx-auto bg-cream-surface border border-cream-border rounded-[4px] shadow-2xl">
        <div className="flex items-center justify-between gap-4 px-5 py-4 border-b border-cream-border">
          <div>
            <h2 id="demo-title" className="font-serif text-xl italic text-charcoal">
              VerboX in action — Pixos failure matrix
            </h2>
            <p className="text-[11px] font-mono text-charcoal-muted mt-0.5">
              A simulated walkthrough. Nothing here touches a real agent, API or cloud account.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 shrink-0 flex items-center justify-center rounded-[4px] border border-cream-border bg-cream-warm hover:bg-cream-border/60 text-charcoal"
            aria-label="Close demo"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" aria-hidden="true">
              <path d="M5 5l14 14M19 5L5 19" />
            </svg>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr]">
          {/* Scenario list */}
          <div className="p-5 border-b lg:border-b-0 lg:border-r border-cream-border space-y-2.5">
            <p className="text-[11px] font-mono text-charcoal-muted uppercase tracking-wider">Scenarios</p>
            <button
              ref={runAllRef}
              type="button"
              disabled={running}
              onClick={() => runScenarios(SCENARIOS.map((_, i) => i))}
              className={
                'w-full bg-terracotta hover:bg-terracotta-hover text-white font-mono text-xs font-medium py-2.5 rounded-[4px] transition shadow-sm ' +
                (running ? 'opacity-50' : '')
              }
            >
              ▶ Run all {SCENARIOS.length} scenarios
            </button>
            <div className="space-y-2">
              {SCENARIOS.map((s, i) => (
                <button
                  key={s.title}
                  type="button"
                  disabled={running}
                  onClick={() => runScenarios([i])}
                  className={
                    'w-full text-left px-3 py-2.5 rounded-[4px] bg-cream-warm hover:bg-cream-border/50 border border-cream-border transition font-mono text-xs ' +
                    (running ? 'opacity-50' : '')
                  }
                >
                  <span className="text-terracotta font-semibold">0{i + 1}</span>{' '}
                  <span className="text-charcoal font-medium">{s.title}</span>
                  <span className="block text-[11px] text-charcoal-muted mt-0.5">{s.fix}</span>
                </button>
              ))}
            </div>
            <div className="pt-3 border-t border-cream-border flex items-center justify-between gap-2 font-mono text-xs text-charcoal-muted">
              <label className="flex items-center gap-2">
                Speed
                <select
                  value={speed}
                  onChange={(e) => setSpeed(parseFloat(e.target.value) || 1)}
                  className="bg-cream-warm border border-cream-border rounded-[4px] px-2 py-1 text-charcoal focus:outline-none"
                >
                  <option value={1}>1×</option>
                  <option value={2}>2×</option>
                  <option value={0.5}>0.5×</option>
                </select>
              </label>
              <button
                type="button"
                onClick={stop}
                disabled={!running}
                className="px-3 py-1 rounded-[4px] border border-cream-border bg-cream-warm hover:bg-cream-border/60 text-charcoal disabled:opacity-40"
              >
                Stop
              </button>
            </div>
          </div>

          {/* Pipeline + terminal */}
          <div className="p-5 space-y-4 min-w-0">
            <div>
              <p className="text-[11px] font-mono text-charcoal-muted uppercase tracking-wider mb-2">Request pipeline</p>
              <div className="flex flex-wrap gap-2 font-mono text-[11px]">
                {STAGES.map(([id, label]) => {
                  const state = stage.active === id ? 'active' : stage.done.includes(id) ? 'done' : '';
                  return (
                    <span key={id} className={`stage px-2.5 py-1 rounded-[4px] ${state}`}>
                      {label}
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="bg-cream-warm border border-cream-border rounded-[4px] p-4 space-y-1.5 text-xs font-mono">
              {sc ? (
                <>
                  <p className="text-terracotta font-semibold">0{(current ?? 0) + 1} · {sc.title}</p>
                  <p className="text-charcoal-muted">
                    <span className="text-charcoal font-medium">Pixos flaw:</span> {sc.flaw}
                  </p>
                  <p className="text-charcoal-muted">
                    <span className="text-charcoal font-medium">VerboX fix:</span> {sc.fix}
                  </p>
                </>
              ) : (
                <p className="text-charcoal-muted">
                  Pick a scenario or run them all. Each one replays a Pixos failure and shows the VerboX layer that
                  catches it, while the dashboard behind this window updates live.
                </p>
              )}
            </div>

            <div
              ref={termRef}
              className="term rounded-[4px] p-4 font-mono text-[12px] leading-relaxed h-72 overflow-y-auto"
              aria-live="polite"
            >
              {lines.map((l) => (
                <div key={l.id} className={`line k-${l.kind}`}>
                  <span className="ts">[{l.ts}s] </span>
                  <span className="tag">{l.tag}</span>
                  <span className="msg"> {l.text}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-charcoal-muted">
              <span>{status}</span>
              <button type="button" onClick={resetStats} className="underline underline-offset-2 hover:text-charcoal">
                Reset dashboard numbers
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
