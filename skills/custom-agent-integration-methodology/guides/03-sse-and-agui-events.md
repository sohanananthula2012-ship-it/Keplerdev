# SSE and AG-UI Events

`POST /run` returns `text/event-stream`, not a single JSON object. The stream data is AG-UI events encoded as SSE records. A correct integration processes events incrementally and updates UI/state as they arrive.

## SSE record shape

A typical SSE record is one or more lines, followed by a blank line:

```text
event: message
data: {"type":"...","...":"..."}

```

Consumers should support:

- `data:` lines split across chunks.
- Multiple SSE records in one network chunk.
- One SSE record split across multiple network chunks.
- Comment lines that start with `:`.
- Optional `event:` and `id:` lines.
- JSON event payloads in `data:`.

Do not parse by line alone without buffering. Always buffer until the blank line that terminates one SSE record.

## AG-UI event handling model

The exact event union is owned by AG-UI and `@enter-pro/thread-client`. Treat unknown event types as forward-compatible and preserve them when persisting history.

At minimum, your runtime should distinguish these categories:

| Category | What to do |
| --- | --- |
| Text/message events | Append or update assistant/user messages in the active turn. |
| Tool call and tool result events | Show tool progress or group them into a tool activity block. |
| Custom events | Route by `event.name`. Some are UI status, metadata, cancellation, or errors. |
| Error events | End the active turn with an error state and show a recoverable message when possible. |
| Cancellation events | Mark the turn cancelled and stop streaming indicators. |
| Terminal/completion events | Stop the active streaming state and refresh metadata if needed. |

## Enter custom events used by existing frontend

Enter Web currently recognizes these custom events around custom-agent serving and Builder runtimes:

| Event name | Existing frontend behavior |
| --- | --- |
| `agent.environment.warming` | Add startup step: environment preparing. |
| `agent.environment.ready` | Mark environment prepared. |
| `agent.loading` | Add startup step: config loading. |
| `agent.loaded` | Mark config loaded and agent responding. |
| `agent.turn.summary` | Finalize startup state and merge turn metadata such as model/usage when available. |
| `agent.turn.error` through `AGENT_TURN_ERROR_EVENT` | Render `turn-error`; render out-of-credit UI when code/message indicates `INSUFFICIENT_CREDITS`. |
| `agent.turn.cancelled` through `AGENT_TURN_CANCELLED_EVENT` | Render cancellation and cancel waiting question cards. |
| `agent.tool_action.resolved` | Update ask-user-question cards and insert answer summary when answered/skipped. |
| `agent.builder.preview.ready` | Builder/debug surface only: render version card. |
| `agent.builder.preview.failed` | Builder/debug surface only: render failed version card. |

For a project integration, preserve unknown custom events even if you do not render them. They may matter for later history replay or new UI capabilities.

## Streaming state

Maintain per-thread active state:

```ts
type ActiveRunState = {
  threadId: string;
  turnId?: number;
  status: 'idle' | 'streaming' | 'cancelled' | 'error' | 'complete';
  events: unknown[];
};
```

Update rules:

- Set status to `streaming` when `/run` starts or when resuming a running turn.
- Capture the first reliable turn id from SDK/runtime metadata if available. Raw SSE clients may only know it after a specific event or a later `GET /threads/{thread_id}` call.
- Append parsed AG-UI events in order.
- On terminal/error/cancel, stop streaming and refresh thread/turn metadata if the UI displays status, credits, model id, or history.

## Raw SSE parser requirements

A raw parser should:

1. Read the response body as bytes.
2. Decode as UTF-8 with streaming `TextDecoder` or equivalent.
3. Accumulate text into a buffer.
4. Split complete records on `\n\n` after normalizing CRLF.
5. For each record, join all `data:` lines with newline.
6. Ignore empty data and keep-alive comments.
7. JSON-parse data and dispatch the event.
8. Leave incomplete trailing text in the buffer for the next chunk.

See `examples/run-agent/raw-sse.md` and `case-studies/external-ai-agent/raw-sse-client.md`.

## Resume stream

To resume an active turn:

```text
GET /code/api/v1/agents/{agent_id}/threads/{thread_id}/turns/{turn_id}/events
Accept: text/event-stream
```

Use this when a page reloads, the frontend reconnects, or the host process loses the original `/run` connection while the turn is still running. Historical turns should use the `/turns?start_turn=&end_turn=` JSON API instead.

## Persisting events

If the host stores its own transcript, persist raw AG-UI events or a lossless normalized version. Avoid storing only rendered text, because later UI features may need tool calls, custom events, metadata, cancellation, or errors.

A useful local record:

```json
{
  "threadId": "<THREAD_ID>",
  "turnId": 1,
  "events": [],
  "status": "completed",
  "updatedAt": "2026-06-10T00:00:00Z"
}
```

## Do not do this

- Do not wait for `response.json()` on `/run`.
- Do not treat every SSE event as displayable text.
- Do not drop custom events by default.
- Do not render assistant messages with empty content and no tool calls.
- Do not assume terminal events are the only way to learn final metadata; refresh turn/thread state after live completion when metadata matters.


## Live rendering convergence rules

Browser integrations should keep the live SSE model layered, matching Builder/Public Site behavior:

- Do not use global `isRunning` or raw turn status to batch-overwrite every rendered message. Reasoning/thinking streaming state comes from the reasoning message itself: open reasoning is streaming; ended reasoning is done.
- `waiting_for_user`, `requires_action`, `awaiting_user`, `awaiting_input`, and `needs_input` mean the turn is active only while a waiting question card exists. Once `agent.tool_action.resolved` arrives, the turn should fall back to done unless a new run is actually active.
- Treat `agent.turn.summary`, `RUN_FINISHED`, `RUN_ERROR`, and explicit `agentRunning=false` as live terminal signals. Stop composer/run indicators immediately and refresh the thread snapshot for authoritative metadata.
- Startup events are buffered per turn. Repeated `agent.environment.ready` / `agent.loading` / `agent.loaded` events in the same turn update one startup block; they must not create multiple `Agent ready` blocks.
- `agent.output.waiting` and `usage.update` remain telemetry. They may affect internal timing/debug panels, but do not render in the main transcript.
