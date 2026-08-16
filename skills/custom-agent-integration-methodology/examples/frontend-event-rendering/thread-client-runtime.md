# ThreadClient Runtime

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

```ts
import { HttpAgent } from '@enter-pro/agent-client';
import { ThreadClient, ThreadManager, toThreadTurnsFromAgUiHistory } from '@enter-pro/thread-client';

export function createServingRuntime(params: {
  agentId: string;
  threadId: string;
  runUrl: string;
  token: () => Promise<string> | string;
  cancelUrl: (turnId: number) => string;
  resumeUrl: (turnId: number) => string;
  listTurns: (start: number, end: number) => Promise<{ turns: any[] }>;
}) {
  const manager = new ThreadManager();
  const agentRef: { current: HttpAgent | null } = { current: null };

  const agent = new HttpAgent({
    threadId: params.threadId,
    url: () => params.runUrl,
    token: params.token,
    abortUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      return turnId == null ? '' : params.cancelUrl(turnId);
    },
    resumeUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      if (turnId == null) throw new Error('No running turn');
      return params.resumeUrl(turnId);
    },
  });
  agentRef.current = agent;

  const client = new ThreadClient({
    threadId: params.threadId,
    agent,
    historyMessageLoader: {
      async load(_threadId, start, end) {
        const resp = await params.listTurns(start, end);
        return toThreadTurnsFromAgUiHistory({
          turns: resp.turns.map((turn) => ({
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
      },
      async loadSince() {
        return [];
      },
    },
    historyMessagePagination: { turnSize: 20, endTurn: 0 },
  });

  const key = `serving-${params.threadId}`;
  manager.register(key, client);

  return { manager, client, agent, key };
}
```

In an Enter project, `runUrl`, `cancelUrl`, `resumeUrl`, and `listTurns` should point to your project proxy endpoints, not directly to Enter with an API key.
