# Create Thread with TypeScript

Use this in trusted server-side TypeScript. Browser code should call your own proxy instead.

```ts
type ServingThread = {
  thread_id: string;
  agent_id: string;
  version: number;
  name: string;
  agent_status: string;
  env_ready_at: string | null;
  created_at: string;
  updated_at: string;
  latest_history_turn_id: number;
  running: unknown | null;
};

async function createServingThread(params: {
  baseUrl: string;
  apiKey: string;
  agentId: string;
}): Promise<ServingThread> {
  const res = await fetch(
    `${params.baseUrl.replace(/\/$/, '')}/code/api/v1/agents/${encodeURIComponent(params.agentId)}/threads`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${params.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    },
  );

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(`Create thread failed: ${res.status} ${error.error_code ?? ''}`.trim());
  }

  return await res.json() as ServingThread;
}
```
