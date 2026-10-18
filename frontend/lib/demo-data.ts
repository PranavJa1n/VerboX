import type { Scenario, StageId } from './types';

export const STAGES: [StageId, string][] = [
  ['agent', 'Agent'],
  ['sdk', 'SDK Interceptor'],
  ['tier1', 'Tier 1 · OPA/YAML'],
  ['cache', 'Redis · CRDT'],
  ['stream', 'Event Stream'],
  ['tier2', 'Tier 2 · Auditor'],
  ['hitl', 'Human Review'],
  ['ui', 'Control Plane'],
];

export const SCENARIOS: Scenario[] = [
  {
    title: 'Reckless Execution',
    fix: 'Tier 1 policy gate + simulated 403',
    flaw: 'The Remediation Engineer assumes every plan is safe and fires 500 replicas.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'remediation_engineer → scale_k8s_deployment(replicas=500)' },
      { stage: 'sdk', tag: 'SDK', kind: 'info', text: '@verbox.guard intercepted call · state_hash {calls:7, writes:2, goal:"fix_latency"}' },
      { stage: 'tier1', tag: 'TIER 1', kind: 'info', text: 'POST /policy-check · rule max_replicas_threshold (fail_mode: fail_safe)' },
      {
        stage: 'tier1', tag: 'TIER 1', kind: 'block',
        text: 'arguments.replicas (500) > 50 → BLOCK · evaluated in 1.8ms',
        fx: (ctx, api) => {
          api.bump('blocks', 1);
          api.addFeedRow({ trace: ctx.trace, agent: 'remediation_engineer', tool: 'scale_k8s_deployment', rule: 'max_replicas_threshold', decision: 'blocked', severity: 1.0 });
        },
      },
      { stage: 'sdk', tag: 'SDK', kind: 'warn', text: 'Returning simulated HTTP 403 → "Action blocked by verboX: replicas exceeds 50."' },
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'Agent reasons about the failure and re-plans → scale_k8s_deployment(replicas=40)' },
      { stage: 'tier1', tag: 'TIER 1', kind: 'ok', text: 'replicas (40) ≤ 50 → ALLOW' },
      { stage: 'stream', tag: 'STREAM', kind: 'info', text: 'Decision gd_{id} appended to the event stream and written to MongoDB' },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: 'Policy Feed updated · Tier 1 Blocks +1' },
    ],
  },
  {
    title: 'Delegation Death Spiral',
    fix: 'Tier 2 auditor halts circular delegation',
    flaw: 'Supervisor and Engineer ask each other the same thing forever, burning tokens.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'supervisor → remediation_engineer: "read the database logs"' },
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'remediation_engineer → supervisor: "I don\'t have read access."' },
      { stage: 'agent', tag: 'AGENT', kind: 'warn', text: 'supervisor repeats the identical request · hops 2, 3, 4 · ~18,400 tokens burned' },
      { stage: 'stream', tag: 'STREAM', kind: 'info', text: 'Spans streaming to Event Hub under thread_id {trace}' },
      { stage: 'tier2', tag: 'TIER 2', kind: 'warn', text: 'Auditor sees the same intent hash repeating across supervisor ⇄ remediation_engineer' },
      {
        stage: 'tier2', tag: 'TIER 2', kind: 'block',
        text: 'Circular delegation (4 hops) → HALT thread · flag compute_waste, severity 0.91',
        fx: (ctx, api) => {
          api.bump('flags', 1);
          api.addFeedRow({ trace: ctx.trace, agent: 'pixos_triage_supervisor', tool: 'delegate_task', rule: 'circular_delegation_guard', decision: 'halted', severity: 0.91 });
        },
      },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: 'Supervisor flagged · est. waste prevented ≈ $4.20 · Auditor Flags +1' },
    ],
  },
  {
    title: 'Split-Brain Dilemma',
    fix: 'Contradiction engine pauses the graph',
    flaw: 'Two agents give opposite root causes and the supervisor tries to act on both.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'telemetry_analyst claims: "Commit 9f3e1c caused the memory leak."' },
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'finops_agent claims: "The marketing campaign caused the traffic spike."' },
      { stage: 'tier2', tag: 'TIER 2', kind: 'info', text: 'Embedding both claims · shared entity: root_cause' },
      { stage: 'tier2', tag: 'TIER 2', kind: 'warn', text: 'cosine similarity = 0.31 (below 0.50 threshold)' },
      {
        stage: 'tier2', tag: 'TIER 2', kind: 'block',
        text: 'Contradiction c_{cid} flagged · severity 0.90 · LangGraph run paused',
        fx: (ctx, api) => {
          api.bump('flags', 1);
          api.addContradiction({
            id: 'c_' + ctx.cid,
            text: 'Telemetry Analyst ("Commit caused leak") vs FinOps Agent ("Campaign caused spike").',
            sim: '0.31',
          });
          api.addFeedRow({ trace: ctx.trace, agent: 'pixos_triage_supervisor', tool: 'apply_fix', rule: 'contradiction_engine', decision: 'paused', severity: 0.9 });
        },
      },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: 'Swarm Topology tab shows the new contradiction · supervisor cannot run both fixes' },
    ],
  },
  {
    title: 'Amnesia Effect',
    fix: 'Redis shared cache dedupes tool calls',
    flaw: 'Three agents query the same CPU metric within five seconds.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'supervisor → get_cpu_utilization(cluster="prod-eks")' },
      { stage: 'cache', tag: 'CACHE', kind: 'info', text: 'key = hash(tool + normalized args) = cpu_7be21d · MISS · claimed by supervisor' },
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'telemetry_analyst → same call (+1.2s)' },
      {
        stage: 'cache', tag: 'CACHE', kind: 'ok',
        text: 'HIT cpu_7be21d · served from Redis · 0 AWS API calls',
        fx: (ctx, api) => {
          api.bump('saved', 1);
          api.addFeedRow({ trace: ctx.trace, agent: 'telemetry_analyst', tool: 'get_cpu_utilization', rule: 'semantic_dedup_cache', decision: 'cached', severity: 0 });
        },
      },
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'finops_agent → same call (+3.4s)' },
      {
        stage: 'cache', tag: 'CACHE', kind: 'ok',
        text: 'HIT cpu_7be21d · served from Redis · 0 AWS API calls',
        fx: (ctx, api) => {
          api.bump('saved', 1);
          api.addFeedRow({ trace: ctx.trace, agent: 'finops_agent', tool: 'get_cpu_utilization', rule: 'semantic_dedup_cache', decision: 'cached', severity: 0 });
        },
      },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: '3 requests → 1 API call · 2 calls avoided · cache evicted when the session ends' },
    ],
  },
  {
    title: 'Context Overflow',
    fix: 'Ephemeral state vector instead of raw logs',
    flaw: 'Raw pod logs flood the LLM context window and trigger hallucinations.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'telemetry_analyst fetched pod logs → 48,212 tokens raw' },
      { stage: 'sdk', tag: 'SDK', kind: 'warn', text: 'Raw payload would blow the 32k context budget' },
      { stage: 'sdk', tag: 'SDK', kind: 'info', text: 'Compressing into an ephemeral state vector' },
      { stage: 'sdk', tag: 'SDK', kind: 'ok', text: '{"errors_5xx":"80%","oom_kills":3,"top_error":"ConnectionPool exhausted","pods":12} → 212 tokens' },
      {
        stage: 'tier1', tag: 'TIER 1', kind: 'ok',
        text: 'Behavioral baseline: telemetry_analyst stayed read-only, no new network destinations',
        fx: (ctx, api) => {
          api.addFeedRow({ trace: ctx.trace, agent: 'telemetry_analyst', tool: 'get_pod_logs', rule: 'state_vector_baseline', decision: 'allowed', severity: 0 });
        },
      },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: 'LLM sees the metrics that matter, not the noise · 99.6% fewer tokens' },
    ],
  },
  {
    title: 'False Confidence',
    fix: 'Low confidence triggers a human Go/No-Go',
    flaw: 'The agent is about to roll back production without any doubt.',
    steps: [
      { stage: 'agent', tag: 'AGENT', kind: 'info', text: 'remediation_engineer → rollback_github_commit(repo="checkout-api", sha="9f3e1c")' },
      { stage: 'tier2', tag: 'TIER 2', kind: 'info', text: 'Ensemble of 3 small judges voting → [safe, unsafe, safe]' },
      { stage: 'tier2', tag: 'TIER 2', kind: 'warn', text: 'Mean log-prob confidence = 74% (below 95% threshold)' },
      {
        stage: 'hitl', tag: 'HITL', kind: 'block',
        text: 'interrupt_before(remediation_node) · paging on-call for a Go/No-Go decision',
        fx: (ctx, api) => {
          api.bump('flags', 1);
          api.bump('review', 1);
          api.bump('pending', 1);
          api.addHitl({
            id: 'v_' + ctx.vid,
            reasoning: 'Irreversible production rollback proposed with sub-threshold confidence.',
            confidence: 74,
          });
          api.addFeedRow({ trace: ctx.trace, agent: 'remediation_engineer', tool: 'rollback_github_commit', rule: 'confidence_below_95', decision: 'paused', severity: 0.74 });
        },
      },
      { stage: 'hitl', tag: 'HITL', kind: 'info', text: 'Awaiting human verdict · the label will feed few-shot refinement of the judge prompt' },
      { stage: 'ui', tag: 'DASHBOARD', kind: 'ok', text: 'Verdict queued in the HITL Review Queue tab — try labeling it' },
    ],
  },
];
