# Supabase Edge Function Proxy

Use this pattern when the project backend is Supabase Edge Functions. The Edge Function reads the Enter API key from server-side secrets, validates project/session ownership, and forwards requests to Enter Serving.

The proxy must preserve AG-UI SSE. Do not convert `/run` or `/events` into text-only deltas.

## Environment

Server-side secret names:

```text
ENTER_API_BASE_URL=<ENTER_API_BASE_URL>
<SECRET_NAME>=<ENTER_API_KEY>
```

`<SECRET_NAME>` must match `enter_api_key_secret_name` from the system reminder. Do not place either value in browser-visible env vars.

## Endpoint contract

Expose these app-local routes:

```text
POST /api/custom-agent/{agentId}/threads
GET  /api/custom-agent/{agentId}/threads/{threadId}
GET  /api/custom-agent/{agentId}/threads/{threadId}/turns?start_turn=&end_turn=
POST /api/custom-agent/{agentId}/run
GET  /api/custom-agent/{agentId}/threads/{threadId}/turns/{turnId}/events
POST /api/custom-agent/{agentId}/threads/{threadId}/turns/{turnId}/tool-calls/{toolCallId}/answer
POST /api/custom-agent/{agentId}/threads/{threadId}/turns/{turnId}/cancel
```

If Supabase Function routing cannot use `/api/...`, keep the same suffix after `custom-agent/{agentId}`.

## Proxy template

```ts
// supabase/functions/custom-agent/index.ts
import { serve } from 'https://deno.land/std/http/server.ts';

const ENTER_API_BASE_URL = Deno.env.get('ENTER_API_BASE_URL') ?? '<ENTER_API_BASE_URL>';
const ENTER_API_KEY = Deno.env.get('<SECRET_NAME>');
const ALLOWED_AGENT_IDS = new Set(['<ENTER_CUSTOM_AGENT_ID>']);

type AppSession = {
  projectId: string;
  userId?: string;
  anonymousSessionId?: string;
};

function jsonResponse(body: unknown, status = 200, extraHeaders: HeadersInit = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...extraHeaders,
    },
  });
}

function requireSecret() {
  if (!ENTER_API_KEY) {
    throw jsonResponse(
      { error_code: 'ENTER_API_KEY_MISSING', message: 'Enter API key secret is missing.' },
      500,
    );
  }
  return ENTER_API_KEY;
}

function enterHeaders(extra?: HeadersInit): HeadersInit {
  return {
    ...extra,
    Authorization: `Bearer ${requireSecret()}`,
  };
}

function enterUrl(pathname: string, search = '') {
  return `${ENTER_API_BASE_URL.replace(/\/$/, '')}/code/api/v1${pathname}${search}`;
}

async function authenticateProjectRequest(req: Request): Promise<AppSession> {
  // Replace this with the project's real app auth/session validation.
  const appAuth = req.headers.get('Authorization');
  if (!appAuth) {
    throw jsonResponse({ error_code: 'UNAUTHORIZED', message: 'Missing app session.' }, 401);
  }
  return {
    projectId: '<PROJECT_ID>',
    userId: '<USER_ID_FROM_APP_AUTH>',
  };
}

async function recordThreadMapping(_session: AppSession, _agentId: string, _thread: unknown) {
  // Insert or update:
  // project_id, user_id/anonymous_session_id, agent_id, thread_id, version,
  // title, latest_history_turn_id, running_turn_id, created_at, updated_at.
}

async function assertThreadOwner(_session: AppSession, _agentId: string, _threadId: string) {
  // Look up the mapping and throw 404/403 if this thread does not belong to this app session.
}

async function updateThreadStateFromEnter(_session: AppSession, _agentId: string, _threadId: string, _thread: unknown) {
  // Persist latest_history_turn_id and running_turn_id if the project needs reload/reconnect support.
}

function parseRoute(url: URL) {
  const parts = url.pathname.split('/').filter(Boolean);
  const agentIndex = parts.indexOf('custom-agent') + 1;
  const agentId = parts[agentIndex];
  const suffix = agentIndex > 0 ? parts.slice(agentIndex + 1) : [];
  return { agentId, suffix };
}

function requireAllowedAgent(agentId: string | undefined) {
  if (!agentId) {
    throw jsonResponse({ error_code: 'BAD_REQUEST', message: 'Missing agent id.' }, 400);
  }
  if (!ALLOWED_AGENT_IDS.has(agentId)) {
    throw jsonResponse({ error_code: 'AGENT_NOT_ALLOWED', message: 'Agent is not configured for this project.' }, 403);
  }
  return agentId;
}

function sseResponse(upstream: Response) {
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      'Content-Type': upstream.headers.get('Content-Type') ?? 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
    },
  });
}

function jsonUpstreamResponse(upstream: Response) {
  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      'Content-Type': upstream.headers.get('Content-Type') ?? 'application/json',
    },
  });
}

async function createThread(session: AppSession, agentId: string) {
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads`), {
    method: 'POST',
    headers: enterHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({}),
  });
  const body = await upstream.json();
  if (upstream.ok) await recordThreadMapping(session, agentId, body);
  return jsonResponse(body, upstream.status);
}

async function getThread(session: AppSession, agentId: string, threadId: string) {
  await assertThreadOwner(session, agentId, threadId);
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${threadId}`), {
    headers: enterHeaders(),
  });
  const body = await upstream.json();
  if (upstream.ok) await updateThreadStateFromEnter(session, agentId, threadId, body);
  return jsonResponse(body, upstream.status);
}

async function listTurns(session: AppSession, agentId: string, threadId: string, search: string) {
  await assertThreadOwner(session, agentId, threadId);
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${threadId}/turns`, search), {
    headers: enterHeaders(),
  });
  return jsonUpstreamResponse(upstream);
}

async function runAgent(session: AppSession, agentId: string, req: Request) {
  const body = await req.json();
  if (!body?.threadId || typeof body.threadId !== 'string') {
    return jsonResponse({ error_code: 'BAD_REQUEST', message: 'threadId is required.' }, 400);
  }
  await assertThreadOwner(session, agentId, body.threadId);

  const upstream = await fetch(enterUrl(`/agents/${agentId}/run`), {
    method: 'POST',
    headers: enterHeaders({ 'Content-Type': 'application/json', Accept: 'text/event-stream' }),
    body: JSON.stringify({
      threadId: body.threadId,
      runId: body.runId,
      messages: body.messages,
      state: body.state,
      context: body.context,
      tools: [],
      forwardedProps: {},
    }),
  });
  return sseResponse(upstream);
}

async function resumeEvents(session: AppSession, agentId: string, threadId: string, turnId: string) {
  await assertThreadOwner(session, agentId, threadId);
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${threadId}/turns/${turnId}/events`), {
    headers: enterHeaders({ Accept: 'text/event-stream' }),
  });
  return sseResponse(upstream);
}

async function answerToolCall(session: AppSession, agentId: string, threadId: string, turnId: string, toolCallId: string, req: Request) {
  await assertThreadOwner(session, agentId, threadId);
  const body = await req.json();
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${threadId}/turns/${turnId}/tool-calls/${toolCallId}/answer`), {
    method: 'POST',
    headers: enterHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body),
  });
  return jsonUpstreamResponse(upstream);
}

async function cancelTurn(session: AppSession, agentId: string, threadId: string, turnId: string) {
  await assertThreadOwner(session, agentId, threadId);
  const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${threadId}/turns/${turnId}/cancel`), {
    method: 'POST',
    headers: enterHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({}),
  });
  return jsonUpstreamResponse(upstream);
}

serve(async (req) => {
  try {
    const session = await authenticateProjectRequest(req);
    const url = new URL(req.url);
    const { agentId: rawAgentId, suffix } = parseRoute(url);
    const agentId = requireAllowedAgent(rawAgentId);

    if (req.method === 'POST' && suffix.length === 1 && suffix[0] === 'threads') {
      return await createThread(session, agentId);
    }

    if (req.method === 'GET' && suffix.length === 2 && suffix[0] === 'threads') {
      return await getThread(session, agentId, suffix[1]);
    }

    if (req.method === 'GET' && suffix.length === 3 && suffix[0] === 'threads' && suffix[2] === 'turns') {
      return await listTurns(session, agentId, suffix[1], url.search);
    }

    if (req.method === 'POST' && suffix.length === 1 && suffix[0] === 'run') {
      return await runAgent(session, agentId, req);
    }

    if (
      req.method === 'GET' &&
      suffix.length === 5 &&
      suffix[0] === 'threads' &&
      suffix[2] === 'turns' &&
      suffix[4] === 'events'
    ) {
      return await resumeEvents(session, agentId, suffix[1], suffix[3]);
    }

    if (
      req.method === 'POST' &&
      suffix.length === 7 &&
      suffix[0] === 'threads' &&
      suffix[2] === 'turns' &&
      suffix[4] === 'tool-calls' &&
      suffix[6] === 'answer'
    ) {
      return await answerToolCall(session, agentId, suffix[1], suffix[3], suffix[5], req);
    }

    if (
      req.method === 'POST' &&
      suffix.length === 5 &&
      suffix[0] === 'threads' &&
      suffix[2] === 'turns' &&
      suffix[4] === 'cancel'
    ) {
      return await cancelTurn(session, agentId, suffix[1], suffix[3]);
    }

    return jsonResponse({ error_code: 'NOT_FOUND', message: 'Unsupported custom-agent proxy route.' }, 404);
  } catch (error) {
    if (error instanceof Response) return error;
    return jsonResponse({ error_code: 'PROXY_FAILED', message: 'Custom-agent proxy failed.' }, 500);
  }
});
```

## Production hardening checklist

- Replace the auth placeholder with real app auth and anonymous-session handling.
- Implement thread mapping persistence and ownership checks before exposing history, run, resume, answer tool-calls, or cancel.
- Scope CORS to the project origin if the function is cross-origin.
- Sanitize logs: no auth headers, API keys, message bodies, or tool payloads.
- Keep `tools: []` and `forwardedProps: {}` in proxied `/run` requests.
- Return upstream JSON errors unchanged when safe; never include the Enter API key in error details.
