# Frontend Rendering

Enter Web's Builder test panel and public site use the same runtime shape for custom-agent serving. Project integrations should mirror that pattern with the public SDK packages.

## Canonical runtime stack

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

```text
HttpAgent (@enter-pro/agent-client)
  talks to project proxy /run, /cancel, and /events
ThreadClient (@enter-pro/thread-client)
  owns turns, history loading, streaming flags, subscriptions, abort, and resume
ThreadManager (@enter-pro/thread-client)
  switches active thread sessions and disposes old runtimes
Renderer
  maps ThreadTurn messages to product-specific UI messages
```

This is richer than a raw SSE client because it owns active turn state, history pagination, `isMessageStreaming`, `isReasoningMessageStreaming`, abort, and resume hooks.

Raw SSE parsing is not the default for browser chat UI. Keep raw SSE for CLIs, trusted backend services, or temporary migration paths that still preserve AG-UI events losslessly.

## Runtime skeleton

```ts
import { HttpAgent, type HttpAgentConfig } from '@enter-pro/agent-client';
import { ThreadClient, ThreadManager } from '@enter-pro/thread-client';

const manager = new ThreadManager();
const sessions = new Map<string, { agent: HttpAgent }>();

async function getOrCreateClient(params: {
  agentId: string;
  threadId: string;
  getToken: () => Promise<string> | string;
  runUrl: string;
  cancelUrl: (turnId: number) => string;
  resumeUrl: (turnId: number) => string;
  historyLoader: ConstructorParameters<typeof ThreadClient>[0]['historyMessageLoader'];
}) {
  const key = `serving-${params.threadId}`;
  const existing = manager.get(key);
  if (existing && sessions.has(key)) return existing;

  const agentRef: { current: HttpAgent | null } = { current: null };
  const config: HttpAgentConfig = {
    threadId: params.threadId,
    url: () => params.runUrl,
    token: params.getToken,
    abortUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      return turnId == null ? '' : params.cancelUrl(turnId);
    },
    resumeUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      if (turnId == null) throw new Error('resumeUrl: no running turn');
      return params.resumeUrl(turnId);
    },
  };

  const agent = new HttpAgent(config);
  agentRef.current = agent;
  sessions.set(key, { agent });

  const client = new ThreadClient({
    threadId: params.threadId,
    agent,
    historyMessageLoader: params.historyLoader,
    historyMessagePagination: { turnSize: 20, endTurn: 0 },
  });

  manager.register(key, client);
  return client;
}
```

In an Enter project, `getToken` should return an app/session token for the project proxy, not the raw Enter API key. The proxy attaches the Enter API key server-side.

## Activating a thread

```ts
async function activateThread(thread: { thread_id: string; running?: unknown | null }) {
  const key = `serving-${thread.thread_id}`;
  const client = await getOrCreateClient(/* params */);
  await manager.resume(key);

  const session = sessions.get(key);
  if (thread.running != null && session) {
    await session.agent.resumeTurn(thread.running);
  }

  return manager.getActive() ?? client;
}
```

If `thread.running` is non-null, resume it. Do not send a new message just because the UI reloaded.

## Sending a message

```ts
async function sendMessage(content: string) {
  const client = manager.getActive();
  if (!client || client.status !== 'active') {
    throw new Error('ThreadClient is not active; cannot send message');
  }
  await client.sendMessage({ content, sentAt: Date.now() });
}
```

The `HttpAgent` builds the AG-UI run request with the configured `threadId` and streams events back into the `ThreadClient`.

## Rendering turns

Render from `ThreadClient.turns`, not directly from raw network fragments. Do not generate a browser UI that only handles phase-only or text-delta-only events.

Every browser UI should preserve the semantic rendering contract:

```text
User bubble
Agent startup/status collapsible group
Thinking/reasoning collapsible group
Tool action collapsible group
Assistant answer as normal assistant text
```

For established Enter projects, map those sections into the host project's existing components, routes, design tokens, auth, persistence, and i18n. "No UI style specified" means inspect and preserve the project-native experience, not copy the portable template by default.

For external browser chat, blank/scaffold projects, or user-requested standalone/default chat pages, implement the Builder/Public Site-like fallback contract in `case-studies/enter-project/default-builder-style-ui-contract.md`. The fallback UI should be transcript-first. Session navigation can exist, but a heavy dashboard header or admin-console layout is not the fallback. The UI should not show a raw event/debug card stack, should not show `usage.update` telemetry JSON, should not wrap final assistant text inside an internal "answer done" card, and should not place a decorative bot/avatar icon before every assistant answer.

The fallback visual scale should match the Public Site baseline: assistant answer, thinking text, and user bubble use 14px font size with 22px line-height; transcript and composer are capped at 800px; user bubble is capped at 568px with 8px 12px padding and 6px radius. Do not use viewport-scaled large transcript text such as `clamp(..., 28px)` unless the user explicitly requests a custom large-display style.

The fallback visual shell should use the current Public Site default stylesheet, `templates/builder-public-site-chat/src/styles/public-site.css`: light zinc-like page surface by default, logo-family gradient from the custom-agent logo, floating desktop session card, richer empty state, and compact composer chip. `public-site-dark.css` is an explicit dark-theme compatibility entry, not the default.

The browser UI i18n layer should follow the host product when available. The fallback template keeps supported locale metadata and normalization locally, passes the host app locale into `useCustomAgentChat` and `PublicSiteLikeChatShell`, and preserves `lang` / `dir` on the shell. If the host has no i18n source, choose a default from the user/project language; Chinese prompts should pass `zh-CN` or compatible `zh`.

Assistant answers must render Markdown/GFM. Use a renderer such as `react-markdown + remark-gfm`; do not render final assistant Markdown with `white-space: pre-wrap` alone. When adding those dependencies, pin the major version such as `react-markdown@^10.1.0 remark-gfm@^4.0.0`, and wrap `ReactMarkdown` in a styled parent element instead of passing `className` to `ReactMarkdown`.

If the user specified a UI style, or the host project has an established visual system, adapt the visual components but keep the same semantic coverage unless the user explicitly asked for plain content only.

The semantic renderer should map turns into these UI kinds:

- `user-text`
- `assistant-answer`
- `agent-startup` / startup-status group
- `thinking`
- `reasoning`
- `tool-action-list`
- `question-card`
- `question-answer-summary`
- `turn-error`
- `out-of-credit`
- `cancel`
- `unsupported-custom-event` or debug-only event

Keep the renderer adapter-based so projects can replace user bubbles, assistant text, thinking rows, tool action rows, question cards, error surfaces, labels, icons, and i18n strings.

Use `examples/frontend-event-rendering/event-to-message-rendering.md` for the two-layer model:

- `CustomAgentSemanticMessage`: style-agnostic semantic messages for custom UI.
- `DefaultBuilderStyleView`: default visible transcript model when the user did not specify a style.

Use `examples/frontend-event-rendering/default-builder-style-react.md`, `examples/frontend-event-rendering/default-builder-style-css.md`, and `examples/frontend-event-rendering/tool-action-normalization.md` for the default implementation.

Before finishing a default UI, review `case-studies/enter-project/default-ui-anti-patterns.md` and run the static/screenshot checks in `case-studies/enter-project/default-ui-acceptance-checklist.md` when a local dev server is available.

## History loader pattern

A history loader calls the project proxy turns API and converts serving turns to AG-UI history:

```ts
import { toThreadTurnsFromAgUiHistory } from '@enter-pro/thread-client';

async function loadHistory(agentId: string, threadId: string, start: number, end: number) {
  const resp = await api.listAgentServingTurns(agentId, threadId, {
    start_turn: start,
    end_turn: end,
  });

  const agUiTurns = resp.turns.map((turn) => ({
    turn_id: turn.turn_id,
    status: turn.status,
    model_id: turn.model_id,
    events: turn.events,
    degraded: turn.degraded,
    created_at: turn.created_at,
    updated_at: turn.updated_at,
    ...(turn.user_message ? { user_message: turn.user_message } : {}),
    ...(turn.user ? { user: turn.user } : {}),
  }));

  return toThreadTurnsFromAgUiHistory({ turns: agUiTurns });
}
```

## Public-site variation

The public-site chat runtime uses the same `HttpAgent + ThreadClient` shape. The important difference is authentication:

- Public thread creation returns a per-thread token.
- `HttpAgent.token` returns that thread token.
- History loading may be empty or limited depending on public-site product constraints.

Do not copy the public-site token model into project integrations unless the backend supports it. For normal Enter project integration, proxy with project/user auth and keep the Enter API key server-side.


## AskUserQuestion rendering and answers

The default template supports the serving `AskUserQuestion` tool as a first-class UI flow:

- Parse question cards from `AskUserQuestion` / `ask_user_question` tool-call args first. Legacy custom events such as `ask-user-question` are fallback only.
- A waiting question card floats above the composer and is filtered out of the transcript. The transcript still shows the normal tool action row, e.g. `Asking user`.
- A parseable `AskUserQuestion` action is not a perpetual loading shimmer. It is considered awaiting user input, and the tool group stays open only while that waiting card exists.
- Submit answers through the project proxy to `/threads/{threadId}/turns/{turnId}/tool-calls/{toolCallId}/answer` with `{ response: "answered" | "skipped", answers?: [...] }`.
- `agent.tool_action.resolved` is the single source for completed answer UI. Insert one `question-answer-summary` per `toolCallId`; ignore `TOOL_CALL_RESULT` for AskUserQuestion display so answers do not duplicate.
- After answer resolution, remove the floating card, collapse completed thinking/tool groups, keep the composer in send state unless a real new run is active, and let assistant continuation render as normal assistant Markdown.
