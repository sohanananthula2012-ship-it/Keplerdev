# Raw SSE Client for External AI Agents

This is a complete trusted-runtime TypeScript client. It creates a thread when needed, runs a prompt, parses SSE, and returns collected events.

```ts
type CustomAgentConfig = {
  baseUrl: string;
  apiKey: string;
  agentId: string;
};

type CustomAgentSession = {
  threadId: string;
  version: number;
};

type SseRecord = { id?: string; event?: string; data: string };

function endpoint(config: CustomAgentConfig, path: string) {
  return `${config.baseUrl.replace(/\/$/, '')}/code/api/v1${path}`;
}

async function enterFetch(config: CustomAgentConfig, path: string, init: RequestInit = {}) {
  return fetch(endpoint(config, path), {
    ...init,
    headers: {
      ...init.headers,
      Authorization: `Bearer ${config.apiKey}`,
    },
  });
}

export async function createSession(config: CustomAgentConfig): Promise<CustomAgentSession> {
  const res = await enterFetch(config, `/agents/${config.agentId}/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  if (!res.ok) throw new Error(`Create thread failed: ${res.status} ${await res.text()}`);
  const body = await res.json();
  return { threadId: body.thread_id, version: body.version };
}

function parseRecord(raw: string): SseRecord | null {
  const record: SseRecord = { data: '' };
  const data: string[] = [];
  for (const line of raw.split('\n')) {
    if (!line || line.startsWith(':')) continue;
    const index = line.indexOf(':');
    const field = index === -1 ? line : line.slice(0, index);
    const value = index === -1 ? '' : line.slice(index + 1).replace(/^ /, '');
    if (field === 'id') record.id = value;
    if (field === 'event') record.event = value;
    if (field === 'data') data.push(value);
  }
  if (!data.length) return null;
  record.data = data.join('\n');
  return record;
}

async function collectSse(response: Response): Promise<unknown[]> {
  if (!response.body) throw new Error('SSE response has no body');
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const events: unknown[] = [];
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');
    let boundary = buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const raw = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const record = parseRecord(raw);
      if (record && record.data !== '[DONE]') events.push(JSON.parse(record.data));
      boundary = buffer.indexOf('\n\n');
    }
  }

  const tail = buffer.trim();
  if (tail) {
    const record = parseRecord(tail);
    if (record && record.data !== '[DONE]') events.push(JSON.parse(record.data));
  }
  return events;
}

export async function runCustomAgent(params: {
  config: CustomAgentConfig;
  session?: CustomAgentSession;
  prompt: string;
}): Promise<{ session: CustomAgentSession; events: unknown[] }> {
  const session = params.session ?? await createSession(params.config);

  const res = await enterFetch(params.config, `/agents/${params.config.agentId}/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      threadId: session.threadId,
      messages: [{ id: `user-${Date.now()}`, role: 'user', content: params.prompt }],
      tools: [],
      forwardedProps: {},
    }),
  });

  if (!res.ok) throw new Error(`Run failed: ${res.status} ${await res.text()}`);
  return { session, events: await collectSse(res) };
}
```

For long-running agents, add thread-state checks and resume handling from `guides/02-thread-and-run-lifecycle.md` before retrying failed runs.
