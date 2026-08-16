# SDK Client for External AI Agents

Use this when the consumer can install and run Enter's TypeScript runtime packages.

Install:

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

```ts
import { HttpAgent } from '@enter-pro/agent-client';
import { ThreadClient, ThreadManager } from '@enter-pro/thread-client';

export class CustomAgentSdkClient {
  private readonly manager = new ThreadManager();
  private readonly sessions = new Map<string, { agent: HttpAgent; client: ThreadClient }>();

  constructor(private readonly config: {
    baseUrl: string;
    apiKey: string;
    agentId: string;
  }) {}

  private base() {
    return this.config.baseUrl.replace(/\/$/, '');
  }

  async createThread(): Promise<{ threadId: string; version: number }> {
    const res = await fetch(`${this.base()}/code/api/v1/agents/${this.config.agentId}/threads`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error(`Create thread failed: ${res.status} ${await res.text()}`);
    const body = await res.json();
    return { threadId: body.thread_id, version: body.version };
  }

  async getClient(threadId: string): Promise<ThreadClient> {
    const key = `external-${threadId}`;
    const existing = this.sessions.get(key);
    if (existing) return existing.client;

    const agentRef: { current: HttpAgent | null } = { current: null };
    const agent = new HttpAgent({
      threadId,
      url: () => `${this.base()}/code/api/v1/agents/${this.config.agentId}/run`,
      token: () => this.config.apiKey,
      abortUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        return turnId == null
          ? ''
          : `${this.base()}/code/api/v1/agents/${this.config.agentId}/threads/${threadId}/turns/${turnId}/cancel`;
      },
      resumeUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        if (turnId == null) throw new Error('No active turn to resume');
        return `${this.base()}/code/api/v1/agents/${this.config.agentId}/threads/${threadId}/turns/${turnId}/events`;
      },
    });
    agentRef.current = agent;

    const client = new ThreadClient({
      threadId,
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

    this.manager.register(key, client);
    await this.manager.resume(key);
    this.sessions.set(key, { agent, client });
    return client;
  }

  async send(threadId: string, content: string): Promise<ThreadClient> {
    const client = await this.getClient(threadId);
    if (client.status !== 'active') throw new Error('ThreadClient is not active');
    await client.sendMessage({ content, sentAt: Date.now() });
    return client;
  }
}
```

This direct SDK client is safe only in trusted runtime code. For browser UI, put a proxy between `HttpAgent` and Enter Serving.
