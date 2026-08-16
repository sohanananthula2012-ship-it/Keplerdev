# AI Agent Consumer Workflow

This workflow is for an AI agent or automation that needs to call a custom agent as a tool-like capability.

## State to keep

```ts
type CustomAgentSession = {
  agentId: string;
  threadId: string;
  version: number;
  lastTurnId?: number;
  lastStatus?: 'idle' | 'running' | 'completed' | 'failed' | 'cancelled';
};
```

Store this in the host agent's durable state if follow-up turns should continue the same conversation.

## Invocation algorithm

1. Resolve config: base URL, API key, agent id.
2. If no session exists, create a thread.
3. Before sending a new run, call `GET /threads/{thread_id}` if the previous invocation may still be running.
4. If a turn is running, resume events or wait instead of starting another run.
5. Call `/run` with the user's prompt as one `role: "user"` message.
6. Collect AG-UI events.
7. Extract final assistant text or structured event payloads.
8. Save updated session state.

## Prompting another AI agent

If the calling agent asks this skill for code, generate code that:

- Reads local example credentials from a gitignored `.enter_custom_agent.env` file, or from server-side environment/secret manager wiring in production.
- Creates or updates `.enter_custom_agent.env` for local examples with prefilled `ENTER_API_BASE_URL`, prefilled `ENTER_CUSTOM_AGENT_ID`, and a blank `ENTER_API_KEY=` line.
- Uses placeholders in committed examples.
- Avoids browser exposure.
- Handles `THREAD_BUSY` by resume/wait/cancel.
- Uses a real SSE parser.
- Reuses threads for follow-up turns.

## Result extraction

Raw AG-UI events are often too detailed for an AI agent's final answer. Extract text conservatively:

```ts
function extractAssistantText(events: unknown[]): string {
  const chunks: string[] = [];
  for (const event of events) {
    const raw = event as any;
    const content = raw.content ?? raw.delta ?? raw.text;
    const role = raw.role ?? raw.message?.role;
    if ((role === 'assistant' || role == null) && typeof content === 'string') {
      chunks.push(content);
    }
  }
  return chunks.join('').trim();
}
```

If using `ThreadClient`, prefer extracting from converted assistant messages instead of guessing raw event fields.

## Failure behavior

- Missing config: ask for environment/secret setup, not a pasted key in chat.
- Missing API key: tell the user to get it from `Custom Agent preview > Developer > REST API > API Key` and paste it into `.enter_custom_agent.env` or the equivalent server-side config file.
- `THREAD_BUSY`: resume active turn or ask whether to cancel.
- `RUN_FORBIDDEN` or `WORKSPACE_FORBIDDEN`: explain workspace/API-key mismatch.
- Stream disconnect: check thread state, then resume events if running.
