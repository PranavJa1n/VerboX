# VerboX Control Plane (Frontend Dashboard)

Behavioral governance and policy monitoring dashboard for autonomous AI agent fleets. It gives operators real-time visibility into tool executions, intercepts high-risk actions, tracks multi-agent swarm topologies, and manages Human-in-the-Loop (HITL) review queues.

---

## Architecture & Tech Stack

The dashboard is built with standard web technologies, avoiding heavyweight external UI or state libraries:

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | `14.2.15` | Hybrid SSR/client rendering, file routing |
| **UI Library** | React / React DOM | `18.3.1` | Component model, hooks, reducers |
| **Language** | TypeScript | `5.6.3` | Strict type safety (`strict: true`) |
| **Styling** | Tailwind CSS + PostCSS | `3.4.14` | CSS-variable-driven design system |
| **Fonts** | `next/font/google` | Next.js | `Plus Jakarta Sans` (UI), `JetBrains Mono` (Terminal) |
| **State** | React Context + `useReducer` | Native | Zero-dependency reactive global store |

```
                    ┌─────────────────────────────────────────┐
                    │      VerboX Dashboard (Next.js 14)      │
                    └────────────────────┬────────────────────┘
                                         │
        ┌──────────────┬─────────────────┼────────────────┬──────────────┐
        ▼              ▼                 ▼                ▼              ▼
   [Overview]    [Policy Feed]    [Swarm Topology]  [Benchmarks]   [Review Queue]
   KPIs & Chart  Audit Ledger     LangGraph Graph   Security Stats  HITL Triage
        ▲              ▲                 ▲                               ▲
        └──────────────┴─────────┬───────┴───────────────────────────────┘
                                 │ Dispatches live mutations
                    ┌────────────┴────────────┐
                    │    Pixos Demo Modal     │
                    │ (8-Stage Failure Matrix)│
                    └─────────────────────────┘
```

---

## Directory & File Structure

```
frontend/
├── app/
│   ├── globals.css              # Color tokens, CSS variables, keyframe animations
│   ├── layout.tsx               # Root layout, Google fonts, pre-hydration theme script
│   └── page.tsx                 # Single page entry mounting <Dashboard />
├── components/
│   ├── Dashboard.tsx            # Top-level shell, tab switcher, demo modal state
│   ├── DemoModal.tsx            # 8-stage interactive Pixos failure simulation engine
│   ├── Footer.tsx               # Control plane status footer
│   ├── Header.tsx               # Top bar (branding, TabNav, theme toggle, demo CTA)
│   ├── Sidebar.tsx              # Desktop-only vertical sticky icon rail
│   ├── StatCard.tsx             # Metric card with hero gradients & flash-on-change
│   ├── TabNav.tsx               # Rounded pill tab navigation
│   ├── ThemeToggle.tsx          # Zero-hydration-overhead dark mode switcher
│   └── tabs/
│       ├── Benchmarks.tsx       # Prompt injection resistance & regression metrics
│       ├── HitlQueue.tsx        # Human-in-the-Loop review queue for LLM verdicts
│       ├── Overview.tsx         # Fleet trust, KPI cards, weekly chart, recent activity
│       ├── PolicyFeed.tsx       # Intercepted tool call audit ledger with filtering
│       └── SwarmTopology.tsx    # LangGraph multi-agent topology & contradiction engine
├── lib/
│   ├── badges.ts                # Decision badge styling map (blocked, allowed, etc.)
│   ├── dashboard-store.tsx      # Global store, Context provider, and reducer actions
│   ├── demo-data.ts             # 8 pipeline stages and 6 failure scenarios
│   ├── initial-data.ts          # Seed data for stats, feeds, fleets, and benchmarks
│   ├── types.ts                 # Shared TypeScript interfaces and types
│   └── use-flash.ts             # Hook for transient highlight micro-animations
├── next.config.mjs              # Next.js configuration (reactStrictMode: true)
├── package.json                 # Scripts and dependencies
├── tailwind.config.ts           # Semantic colors & font mapping
└── tsconfig.json                # TypeScript aliases (@/* -> ./*)
```

---

## Design System & Theme Engine

Styling relies on a curated editorial color system defined in `app/globals.css` and bound in `tailwind.config.ts`:

### Semantic Color Tokens
| Token | Light (RGB) | Dark (RGB) | UI Role |
| :--- | :--- | :--- | :--- |
| `cream` | `236 236 236` | `12 12 12` | Canvas background, surface cards, inputs |
| `charcoal` | `17 17 17` | `245 245 245` | Typography, active tabs, dark accents |
| `terracotta` | `242 87 41` | `255 106 61` | Primary accent, hero gradients, blocked actions |
| `sage` | `22 148 84` | `74 201 134` | Allowed status, clean trust ratings, cache hits |
| `amber` | `217 119 6` | `245 175 66` | Warnings, paused graphs, low-confidence reviews |

### Zero-Flash Dark Mode
An inline script in `app/layout.tsx` reads `localStorage` and system preferences before first paint, appending `.dark` to `<html>` to eliminate FOUC. The `ThemeToggle` component toggles this class directly while swapping SVG icons purely in CSS (`.icon-sun` / `.icon-moon`), preventing React hydration mismatches.

### Micro-Animations
- **Live Highlight Flash (`.flash`)**: Controlled via `useFlash()`. Triggers a 1.6s fade on mutated stats or newly injected feed rows.
- **Terminal Line Stream (`.term .line`)**: Renders incoming logs with `@keyframes rise`.
- **Reduced Motion**: Automatically respected through `@media (prefers-reduced-motion: reduce)`.

---

## Core Views & Components

### 1. Overview (`components/tabs/Overview.tsx`)
- **Fleet Trust Score**: Overall trust index (`0.88`, `+0.04`) and active fleet breakdown (`support_agent_v2`, `pixos_triage_supervisor`, `remediation_engineer`).
- **2x2 KPI Stat Cards**:
  - *Compute / Cost Saved*: Calculated dynamically from cached calls (`saved * $0.02408`).
  - *Tier 1 Blocks*: Count of instant deterministic rule rejections.
  - *Auditor Flags*: LLM-as-a-Judge inspection warnings.
  - *Pending Review*: Verdicts queued below 95% confidence.
- **Policy Decisions Bar Chart**: Weekly blocked vs. allowed comparison across Mon–Sun.
- **Recent Activities Ledger**: Quick-look table showing the 6 most recent tool decisions.

### 2. Policy Feed (`components/tabs/PolicyFeed.tsx`)
- Granular audit ledger showing `TIMESTAMP`, `TRACE ID`, `AGENT ID`, `TOOL NAME`, `POLICY RULE`, `DECISION`, and `SEVERITY`.
- Severity filtering (Critical `>0.8`, Warning `>0.5`), decision filtering, and trace search.

### 3. Swarm Topology (`components/tabs/SwarmTopology.tsx`)
- **LangGraph Thread Graph**: Visualizes active multi-agent execution flows (`Supervisor` → `Telemetry Analyst` → `Remediation Engineer`) with CRDT synchronization status.
- **Contradiction Engine**: Flags conflicting claims across agents with semantic cosine similarity scores.
- **Emergency Action**: "Force Terminate Trace" button for immediate manual thread intervention.

### 4. Review Queue (`components/tabs/HitlQueue.tsx`)
- Triage interface for Tier 2 LLM Judge verdicts whose confidence falls below 95%.
- Operators review the reasoning and click **Agree**, **Disagree**, or **Partially Correct**.
- Labeled decisions update pending counts and queue data for few-shot prompt refinement.

### 5. Benchmarks (`components/tabs/Benchmarks.tsx`)
- Performance cards tracking Prompt Injection Resistance (`99.4%`), Reckless Remediation Guard (`100%`), Infinite Loop Prevention (`96.8%`), and Prompt Drift.
- Includes a trigger to run automated adversarial red-team test suites.

---

## State Management (`lib/dashboard-store.tsx`)

A single React Context and `useReducer` store manages dashboard state with automatic immutability:

```typescript
interface State {
  stats: { blocks: number; saved: number; flags: number; review: number; pending: number };
  feed: FeedRow[];                 // Recent tool decisions (capped at 14 items)
  contradictions: Contradiction[]; // Active cross-agent conflicts
  hitl: HitlCard[];                // Pending / labeled human review cards
}
```

### Action Dispatchers
- `bump(key, n)`: Increments metric counters (`blocks`, `saved`, `flags`, `review`, `pending`).
- `addFeedRow(row)`: Prepends a new audit record with a generated ID and timestamp.
- `addContradiction(item)`: Prepends a cross-agent conflict alert.
- `addHitl(item)`: Pushes a low-confidence verdict into the HITL queue.
- `label(id, verdict)`: Marks a verdict as resolved and decrements pending counts.
- `resetStats()`: Resets all KPI metrics back to baseline values.

---

## Pixos Failure Simulation Engine

The `DemoModal` (`components/DemoModal.tsx`) provides an interactive simulation demonstrating how VerboX detects and mitigates failures in the **Pixos** SRE agent swarm.

### 8-Stage Request Pipeline
1. **Agent**: Emits autonomous tool call.
2. **SDK Interceptor**: `@verbox.guard` intercepts execution before reaching target APIs.
3. **Tier 1 (OPA/YAML)**: Evaluates sub-2ms deterministic boundary rules.
4. **Redis CRDT Cache**: Checks semantic argument hashes to prevent redundant calls.
5. **Event Stream**: Logs telemetry spans to Kafka/MongoDB.
6. **Tier 2 (Auditor)**: LLM judge reviews reasoning and context asynchronously.
7. **Human Review (HITL)**: Holds execution if judge confidence is under 95%.
8. **Control Plane UI**: Pushes live events to the dashboard.

### Simulated Failure Scenarios (`lib/demo-data.ts`)
| # | Scenario | Failure Mode | VerboX Interception | Dashboard Impact |
| :-: | :--- | :--- | :--- | :--- |
| **01** | **Reckless Execution** | Agent scales K8s to 500 replicas | Tier 1 rule (`replicas > 50`) blocks call in 1.8ms | `blocks` +1, Feed row added |
| **02** | **Delegation Spiral** | Supervisor & Engineer loop tasks | Tier 2 halts circular delegation after 4 hops | `flags` +1, Feed row added |
| **03** | **Split-Brain Dilemma** | 2 agents assert conflicting causes | Cosine similarity (0.31 < 0.50) pauses graph | `flags` +1, Contradiction added |
| **04** | **Amnesia Effect** | 3 agents query same CPU metric | Redis normalizes key; serves hits without API calls | `saved` +2, Cached rows added |
| **05** | **Context Overflow** | 48k raw log tokens exceed budget | SDK compresses logs into 212-token state vector | Feed row added |
| **06** | **False Confidence** | Rollback initiated with 74% confidence | HITL interrupt pauses run below 95% threshold | `pending` +1, Review queued |

---

## Core Data Types & Badges (`lib/types.ts` & `lib/badges.ts`)

```typescript
export type TabId = 'overview' | 'policy' | 'swarm' | 'benchmarks' | 'hitl';
export type Decision = 'blocked' | 'failsafe' | 'halted' | 'paused' | 'cached' | 'allowed';

export interface FeedRow {
  id: string;
  time: string;
  trace: string;
  agent: string;
  tool: string;
  rule: string;
  decision: Decision;
  severity: number;
  isNew?: boolean;
}

export interface HitlCard {
  id: string;
  reasoning: string;
  confidence: number;
  label?: string;
  isNew?: boolean;
}

export interface Stats {
  blocks: number;
  saved: number;
  flags: number;
  review: number;
  pending: number;
}
```

### Policy Decision Badges (`lib/badges.ts`)
- `blocked`: Red terracotta badge (`bg-terracotta-light text-terracotta`)
- `failsafe` / `halted` / `paused`: Amber badge (`bg-amber-light text-amber`)
- `cached` / `allowed`: Green sage badge (`bg-sage-light text-sage`)

---

## Getting Started & Scripts

### Prerequisites
- Node.js 18.17+ or 20.x
- npm, pnpm, or yarn

### Commands
Run all commands from the `frontend/` directory:

```bash
# 1. Install dependencies
npm install

# 2. Run local development server (http://localhost:3000)
npm run dev

# 3. Validate TypeScript types (zero-emit check)
npm run typecheck

# 4. Create optimized production build
npm run build

# 5. Start production server
npm run start
```

---

## Backend Integration Points

The dashboard is structured for plug-and-play integration with the **verboX-Backend** FastAPI service:

1. **Live Decision Stream**: Connect `addFeedRow()` to a Server-Sent Events (SSE) or WebSocket endpoint (`GET /api/v1/stream/decisions`).
2. **HITL Feedback**: Route the `label(id, verdict)` handler to `POST /api/v1/hitl/verdicts/{id}` to persist human decisions for judge model fine-tuning.
3. **Graph Synchronization**: Replace mock nodes in `SwarmTopology.tsx` with dynamic graph payloads from `GET /api/v1/traces/{trace_id}/graph`.
4. **Cache Management**: Bind the "Purge Redis Execution Cache" button in `Overview.tsx` to `POST /api/v1/cache/flush`.
