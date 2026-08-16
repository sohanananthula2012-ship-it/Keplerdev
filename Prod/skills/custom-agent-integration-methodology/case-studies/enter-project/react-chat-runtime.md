# React Chat Runtime

This pattern mirrors Enter Web's serving runtime but points to the project proxy instead of Enter directly.

Install the public SDK packages:

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

## Hook template

```tsx
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { HttpAgent } from '@enter-pro/agent-client';
import {
  ThreadClient,
  ThreadManager,
  toThreadTurnsFromAgUiHistory,
  type ThreadTurn,
} from '@enter-pro/thread-client';
import {
  toCustomAgentSemanticMessages,
  toDefaultBuilderStyleView,
} from './customAgentRenderableMessages';

type CustomAgentThread = {
  thread_id: string;
  version?: number;
  latest_history_turn_id?: number;
  running?: unknown | null;
};

export function useCustomAgentChat(params: {
  agentId: string;
  proxyBase?: string;
  appToken: () => Promise<string> | string;
  initialThreadId?: string | null;
  locale?: 'en' | 'zh';
}) {
  const proxyBase = params.proxyBase ?? `/api/custom-agent/${params.agentId}`;
  const managerRef = useRef(new ThreadManager());
  const agentsRef = useRef(new Map<string, HttpAgent>());
  const [activeThreadId, setActiveThreadId] = useState<string | null>(params.initialThreadId ?? null);
  const [turns, setTurns] = useState<readonly ThreadTurn[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [lifecycle, setLifecycle] = useState('idle');

  const authHeaders = useCallback(async () => ({
    Authorization: `Bearer ${await params.appToken()}`,
  }), [params.appToken]);

  const listTurns = useCallback(async (threadId: string, start: number, end: number) => {
    const resp = await fetch(`${proxyBase}/threads/${threadId}/turns?start_turn=${start}&end_turn=${end}`, {
      headers: await authHeaders(),
    });
    if (!resp.ok) throw new Error('Failed to load custom-agent history');
    const body = await resp.json();
    return toThreadTurnsFromAgUiHistory({
      turns: body.turns.map((turn: any) => ({
        turn_id: turn.turn_id,
        status: turn.status,
        model_id: turn.model_id,
        events: turn.events,
        degraded: turn.degraded,
        created_at: turn.created_at,
        updated_at: turn.updated_at,
        ...(turn.user_message ? { user_message: turn.user_message } : {}),
        ...(turn.user ? { user: turn.user } : {}),
      })),
    });
  }, [authHeaders, proxyBase]);

  const getOrCreateClient = useCallback(async (threadId: string) => {
    const key = `custom-agent-${threadId}`;
    const existing = managerRef.current.get(key);
    if (existing) return existing;

    const agentRef: { current: HttpAgent | null } = { current: null };
    const agent = new HttpAgent({
      threadId,
      url: () => `${proxyBase}/run`,
      token: params.appToken,
      abortUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        return turnId == null ? '' : `${proxyBase}/threads/${threadId}/turns/${turnId}/cancel`;
      },
      resumeUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        if (turnId == null) throw new Error('No running turn');
        return `${proxyBase}/threads/${threadId}/turns/${turnId}/events`;
      },
    });
    agentRef.current = agent;
    agentsRef.current.set(key, agent);

    const client = new ThreadClient({
      threadId,
      agent,
      historyMessageLoader: {
        async load(_threadId, start, end) {
          return listTurns(threadId, start, end);
        },
        async loadSince() {
          return [];
        },
      },
      historyMessagePagination: { turnSize: 20, endTurn: 0 },
    });

    client.subscribe((event) => {
      if (event.type === 'turns' || event.type === 'lifecycle' || event.type === 'agentRunning') {
        setTurns(client.turns);
        setIsRunning(client.isAgentRunning);
        setLifecycle(client.status);
      }
    });

    managerRef.current.register(key, client);
    return client;
  }, [listTurns, params.appToken, proxyBase]);

  const fetchThread = useCallback(async (threadId: string): Promise<CustomAgentThread> => {
    const resp = await fetch(`${proxyBase}/threads/${threadId}`, {
      headers: await authHeaders(),
    });
    if (!resp.ok) throw new Error('Failed to load custom-agent thread');
    return resp.json();
  }, [authHeaders, proxyBase]);

  const createThread = useCallback(async (): Promise<CustomAgentThread> => {
    const resp = await fetch(`${proxyBase}/threads`, {
      method: 'POST',
      headers: await authHeaders(),
    });
    if (!resp.ok) throw new Error('Failed to create custom-agent thread');
    return resp.json();
  }, [authHeaders, proxyBase]);

  const activateThread = useCallback(async (threadId?: string | null) => {
    const thread = threadId ? await fetchThread(threadId) : await createThread();
    const key = `custom-agent-${thread.thread_id}`;
    const client = await getOrCreateClient(thread.thread_id);
    await managerRef.current.resume(key);
    setActiveThreadId(thread.thread_id);
    setTurns(client.turns);
    setIsRunning(client.isAgentRunning);
    setLifecycle(client.status);

    const agent = agentsRef.current.get(key);
    if (thread.running != null && agent) {
      await agent.resumeTurn(thread.running as any);
    }

    return thread;
  }, [createThread, fetchThread, getOrCreateClient]);

  useEffect(() => {
    if (!params.initialThreadId) return;
    void activateThread(params.initialThreadId);
  }, [activateThread, params.initialThreadId]);

  const sendMessage = useCallback(async (content: string) => {
    const thread = activeThreadId ? { thread_id: activeThreadId } : await activateThread(null);
    const client = await getOrCreateClient(thread.thread_id);
    const key = `custom-agent-${thread.thread_id}`;
    await managerRef.current.resume(key);
    if (client.status !== 'active') throw new Error('Custom-agent thread is not active');
    await client.sendMessage({ content, sentAt: Date.now() });
  }, [activateThread, activeThreadId, getOrCreateClient]);

  const abort = useCallback(() => {
    managerRef.current.getActive()?.abort();
  }, []);

  const loadMoreHistory = useCallback(async () => {
    await managerRef.current.getActive()?.loadMoreHistoryMessages();
  }, []);

  const semanticMessages = useMemo(
    () => toCustomAgentSemanticMessages(turns.flatMap((turn) => turn.messages), {
      isRunning,
      isMessageStreaming: (messageId) => managerRef.current.getActive()?.isMessageStreaming(messageId) ?? false,
      isReasoningMessageStreaming: (messageId) => managerRef.current.getActive()?.isReasoningMessageStreaming(messageId) ?? false,
    }),
    [turns, isRunning],
  );

  const renderableMessages = useMemo(
    () => toDefaultBuilderStyleView(semanticMessages, { locale: params.locale ?? 'en' }),
    [semanticMessages, params.locale],
  );

  return useMemo(() => ({
    turns,
    semanticMessages,
    renderableMessages,
    isRunning,
    lifecycle,
    sendMessage,
    abort,
    activateThread,
    loadMoreHistory,
  }), [turns, semanticMessages, renderableMessages, isRunning, lifecycle, sendMessage, abort, activateThread, loadMoreHistory]);
}
```

## Rendering

Convert `turns` with the renderer in `examples/frontend-event-rendering/event-to-message-rendering.md`.

- For established Enter projects, render `semanticMessages` into the host project's existing UI while keeping agent status, thinking/reasoning, tool actions, assistant answer, questions, errors, and cancellation visible.
- For external, blank/scaffold, or explicitly standalone/default chat UI, render `renderableMessages` with `examples/frontend-event-rendering/default-builder-style-react.md` and `examples/frontend-event-rendering/default-builder-style-css.md`.
- If the user specified a custom UI style, render `semanticMessages` into that style while keeping agent status, thinking/reasoning, tool actions, assistant answer, errors, and cancellation visible.
- If the user explicitly asked for plain content only, it is acceptable to omit thinking/tool UI and render only final assistant answers plus errors.

Default assistant answers must use a Markdown/GFM renderer such as `react-markdown + remark-gfm`. When adding those dependencies, pin the major version such as `react-markdown@^10.1.0 remark-gfm@^4.0.0`. Do not render final assistant Markdown with raw `pre-wrap` text, and do not pass styling through `ReactMarkdown className`; use a styled wrapper element.

Do not render raw AG-UI events, `usage.update` telemetry, `startup done` cards, `answer done` cards, decorative assistant bot icons, or heavy dashboard headers in the main chat transcript by default.

## Key details

- `params.appToken` authenticates the browser to the project proxy. It is not the Enter API key.
- `HttpAgent.resumeTurn(thread.running)` is how reload/reconnect resumes an active turn.
- `ThreadClient.sendMessage` is the only send path for browser chat UI.
- `ThreadClient.abort` should be wired to a visible cancel control when long-running turns are possible.
