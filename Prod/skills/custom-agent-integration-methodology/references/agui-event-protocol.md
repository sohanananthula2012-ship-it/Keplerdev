# AG-UI Event Protocol

Enter Serving streams AG-UI events over SSE. The backend intentionally accepts AG-UI `RunAgentInput` style bodies so standard clients can talk to it, but v1 Serving only uses a subset.

## Run input subset

Accepted fields:

```ts
type ServingRunInput = {
  threadId: string;
  runId?: string;
  messages?: Array<{
    id?: string;
    role: 'user' | 'assistant' | 'system' | 'tool';
    content?: unknown;
    [key: string]: unknown;
  }>;
  state?: unknown;
  context?: unknown;
  tools?: unknown[];
  forwardedProps?: {
    model_id?: string;
    [key: string]: unknown;
  };
};
```

Backend behavior:

- `threadId` is required.
- `messages` are scanned for the first `role: "user"` message.
- Empty `messages` can be used only for continuation/resume semantics.
- `state` and `context` are accepted and ignored.
- `tools` must be empty or absent.
- `forwardedProps.model_id` is rejected.

## SSE envelope

A stream may include these fields per SSE record:

```text
id: optional-event-id
event: optional-event-name
data: {"type":"..."}

```

The `data` field is the AG-UI event payload. Some clients ignore the SSE `event` name and dispatch based on the JSON payload.

## Event preservation

Persist and forward unknown event payloads. The renderer can ignore unknown types, but history replay should keep enough data to reconstruct turns later.

Recommended normalized shape:

```ts
type StoredAgUiEvent = {
  sseId?: string;
  sseEvent?: string;
  payload: unknown;
  receivedAt: string;
};
```

## Rendering categories

Do not couple UI code to every low-level event type unless you are maintaining a full AG-UI runtime. Most apps can implement category dispatch:

```ts
function classifyAgUiEvent(event: unknown):
  | 'message'
  | 'tool'
  | 'custom'
  | 'error'
  | 'cancel'
  | 'terminal'
  | 'unknown' {
  const raw = event as { type?: string; event?: { name?: string }; name?: string };
  const type = String(raw.type ?? '').toLowerCase();
  const customName = raw.event?.name ?? raw.name;

  if (customName === 'agent.turn.cancelled') return 'cancel';
  if (customName === 'agent.turn.error') return 'error';
  if (customName) return 'custom';
  if (type.includes('tool')) return 'tool';
  if (type.includes('message') || type.includes('text')) return 'message';
  if (type.includes('finish') || type.includes('complete') || type.includes('end')) return 'terminal';
  if (type.includes('error')) return 'error';
  return 'unknown';
}
```

This classification is a fallback for non-browser or migration clients. Browser chat UI should use `@enter-pro/thread-client` and prefer its built-in conversion pipeline.

## History turns

The turns API returns stored events as part of each turn summary. Enter Web converts them to AG-UI history turns using:

```ts
{
  turn_id: turn.turn_id,
  status: turn.status,
  model_id: turn.model_id,
  events: turn.events,
  degraded: turn.degraded,
  created_at: turn.created_at,
  updated_at: turn.updated_at,
  user_message: turn.user_message,
  user: turn.user,
}
```

Then it calls `toThreadTurnsFromAgUiHistory({ turns })`.

## Custom event names worth recognizing

A compact renderer should recognize:

- Startup: `agent.environment.warming`, `agent.environment.ready`, `agent.loading`, `agent.loaded`.
- Turn metadata: `agent.turn.summary`.
- User-visible failure: `agent.turn.error`.
- Cancellation: `agent.turn.cancelled`.
- Tool action resolution: `agent.tool_action.resolved`.

Builder-only preview event names can be ignored in normal project integrations:

- `agent.builder.preview.ready`
- `agent.builder.preview.failed`
