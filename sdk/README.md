# SDK Decorators Documentation
---

This document outlines the architecture and execution flow for the two core SDK decorators: @guard and @trace. These decorators intercept tool calls to enforce security/policy evaluations and capture observability telemetry, respectively.

---

## 1. `@guard` Decorator

The `@guard` decorator acts as a policy enforcement point. It intercepts agent tool calls *before* execution, communicates with the backend evaluation engine, and decides whether the tool should run, be bypassed with a cache, or be blocked entirely.

### Execution Flow

1. **Interception:** The agent calls the decorated tool function. The decorator catches the invocation before the underlying function executes.
2. **Payload Construction:** It extracts the `tool_name` (derived from the function name) and the input arguments (`kwargs`).
3. **Backend Evaluation:** It sends a request to the backend’s `/evaluate` endpoint.
4. **Decision Handling:** The backend replies with one of three directives:
* **`block`**: The decorator raises an error, preventing the real tool from executing.
* **`cache_hit`**: The decorator returns the cached result directly, bypassing the real tool execution.
* **`allow`**: The decorator proceeds to run the real tool normally and returns its result to the agent.



### Sequence Diagram

```text
Agent -> @guard Decorator: Calls tool function
@guard Decorator -> Backend (/evaluate): Sends tool_name & arguments
Backend --> @guard Decorator: Returns directive (block / cache_hit / allow)
alt block
    @guard Decorator -> Agent: Raises error (Execution halted)
else cache_hit
    @guard Decorator -> Agent: Returns cached result
else allow
    @guard Decorator -> Real Tool: Executes function
    Real Tool --> @guard Decorator: Returns result
    @guard Decorator -> Agent: Returns result
end

```

---

## 2. `@trace` Decorator

The `@trace` decorator handles observability by timing tool execution, capturing inputs and outputs, and transmitting span data to the backend for logging and asynchronous evaluation.

### Execution Flow

1. **Interception:** The agent calls the decorated tool function.
2. **Start Timing:** The decorator records the start timestamp.
3. **Tool Execution:** The real tool function executes normally.
4. **End Timing:** The decorator records the end timestamp.
5. **Span Construction:** It builds a span payload containing:
* Tool name
* Arguments (`kwargs`)
* Execution result
* `trace_id`
* Start and end timestamps


6. **Telemetry Transmission:** It sends the completed span to the backend’s `/traces` endpoint.
* *Backend Behavior:* The backend saves the span and asynchronously triggers the Tier 2 judge in the background.


7. **Result Delivery:** It returns the tool's original result transparently to the agent (identical to an undecorated function).

### Sequence Diagram

```text
Agent -> @trace Decorator: Calls tool function
@trace Decorator -> @trace Decorator: Note start time (timestamp)
@trace Decorator -> Real Tool: Executes function
Real Tool --> @trace Decorator: Returns result & notes end time
@trace Decorator -> Backend (/traces): Sends span (name, args, result, trace_id, timestamps)
Note over Backend: Saves span & triggers Tier 2 judge (background)
@trace Decorator -> Agent: Returns tool result

```

---

## Summary Table

| Decorator | When it runs | Backend Endpoint | Primary Purpose | Execution Impact on Tool |
| --- | --- | --- | --- | --- |
| **`@guard`** | **Before** execution | `/evaluate` | Policy enforcement, security, and caching | May block execution or return cached results |
| **`@trace`** | **Around** execution | `/traces` | Observability, telemetry, and background auditing | Transparent (runs the tool normally and returns output) |

---