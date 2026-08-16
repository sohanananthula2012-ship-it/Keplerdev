# Run Agent with Raw SSE

Use this for portable CLI/server clients, or as a temporary migration fallback when the public SDK packages cannot be installed. Browser chat UI should use `@enter-pro/agent-client` and `@enter-pro/thread-client` through a project proxy.

## TypeScript

```ts
type SseRecord = {
  id?: string;
  event?: string;
  data: string;
};

function parseSseRecord(raw: string): SseRecord | null {
  const record: SseRecord = { data: '' };
  const dataLines: string[] = [];

  for (const line of raw.split('\n')) {
    if (!line || line.startsWith(':')) continue;
    const sep = line.indexOf(':');
    const field = sep === -1 ? line : line.slice(0, sep);
    const value = sep === -1 ? '' : line.slice(sep + 1).replace(/^ /, '');
    if (field === 'id') record.id = value;
    if (field === 'event') record.event = value;
    if (field === 'data') dataLines.push(value);
  }

  if (dataLines.length === 0) return null;
  record.data = dataLines.join('\n');
  return record;
}

export async function runAgentRawSse(params: {
  baseUrl: string;
  apiKey: string;
  agentId: string;
  threadId: string;
  content: string;
  onEvent: (event: unknown, sse: SseRecord) => void;
}) {
  const base = params.baseUrl.replace(/\/$/, '');
  const response = await fetch(`${base}/code/api/v1/agents/${params.agentId}/run`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${params.apiKey}`,
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({
      threadId: params.threadId,
      messages: [
        {
          id: `user-${Date.now()}`,
          role: 'user',
          content: params.content,
        },
      ],
      tools: [],
      forwardedProps: {},
    }),
  });

  if (!response.ok || !response.body) {
    const detail = await response.text().catch(() => '');
    throw new Error(`Run failed: ${response.status} ${detail}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');

    let boundary = buffer.indexOf('\n\n');
    while (boundary !== -1) {
      const rawRecord = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const sse = parseSseRecord(rawRecord);
      if (sse && sse.data !== '[DONE]') {
        params.onEvent(JSON.parse(sse.data), sse);
      }
      boundary = buffer.indexOf('\n\n');
    }
  }

  const tail = buffer.trim();
  if (tail) {
    const sse = parseSseRecord(tail);
    if (sse && sse.data !== '[DONE]') {
      params.onEvent(JSON.parse(sse.data), sse);
    }
  }
}
```

## Python

```python
import json
import requests


def iter_sse_records(response):
    buffer = ""
    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if not chunk:
            continue
        buffer += chunk.replace("\r\n", "\n")
        while "\n\n" in buffer:
            raw, buffer = buffer.split("\n\n", 1)
            yield raw
    if buffer.strip():
        yield buffer


def parse_sse_record(raw):
    event_id = None
    event_name = None
    data_lines = []
    for line in raw.split("\n"):
        if not line or line.startswith(":"):
            continue
        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "id":
            event_id = value
        elif field == "event":
            event_name = value
        elif field == "data":
            data_lines.append(value)
    if not data_lines:
        return None
    return {"id": event_id, "event": event_name, "data": "\n".join(data_lines)}


def run_agent_raw_sse(base_url, api_key, agent_id, thread_id, content, on_event):
    url = f"{base_url.rstrip('/')}/code/api/v1/agents/{agent_id}/run"
    with requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        json={
            "threadId": thread_id,
            "messages": [{"id": "user-message", "role": "user", "content": content}],
            "tools": [],
            "forwardedProps": {},
        },
        stream=True,
        timeout=300,
    ) as response:
        if not response.ok:
            raise RuntimeError(f"Run failed: {response.status_code} {response.text}")
        for raw in iter_sse_records(response):
            record = parse_sse_record(raw)
            if not record or record["data"] == "[DONE]":
                continue
            on_event(json.loads(record["data"]), record)
```
