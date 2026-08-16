# Run Agent with SDK-Style Runtime

This pattern mirrors Enter Web: `HttpAgent` streams from `/run`, and `ThreadClient` owns UI-ready turns.

Install:

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

```ts
import { HttpAgent } from '@enter-pro/agent-client';
import { ThreadClient, ThreadManager } from '@enter-pro/thread-client';

const manager = new ThreadManager();

export async function startThreadClient(params: {
  baseUrl: string;
  apiKey: string;
  agentId: string;
  threadId: string;
}) {
  const base = params.baseUrl.replace(/\/$/, '');
  const agentRef: { current: HttpAgent | null } = { current: null };

  const agent = new HttpAgent({
    threadId: params.threadId,
    url: () => `${base}/code/api/v1/agents/${params.agentId}/run`,
    token: () => params.apiKey,
    abortUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      return turnId == null
        ? ''
        : `${base}/code/api/v1/agents/${params.agentId}/threads/${params.threadId}/turns/${turnId}/cancel`;
    },
    resumeUrl: async () => {
      const turnId = agentRef.current?.activeTurnId;
      if (turnId == null) throw new Error('No active turn to resume');
      return `${base}/code/api/v1/agents/${params.agentId}/threads/${params.threadId}/turns/${turnId}/events`;
    },
  });
  agentRef.current = agent;

  const client = new ThreadClient({
    threadId: params.threadId,
    agent,
    historyMessageLoader: {
      async load() {
        return [];
      },
      async loadSince() {
        return [];
      },
    },
    historyMessagePagination: { turnSize: 20, endTurn: 0 },
  });

  const key = `serving-${params.threadId}`;
  manager.register(key, client);
  await manager.resume(key);

  client.subscribe((event) => {
    if (event.type === 'turns') {
      console.log(client.turns);
    }
    if (event.type === 'customEvent') {
      console.log('custom event', event.customEvent.event.name);
    }
  });

  return client;
}

export async function sendUserMessage(client: ThreadClient, content: string) {
  if (client.status !== 'active') {
    throw new Error('ThreadClient is not active');
  }
  await client.sendMessage({ content, sentAt: Date.now() });
}
```

For browser-facing apps, replace `token: () => params.apiKey` with an app-session token or cookie-backed proxy. The Enter API key must stay server-side.
