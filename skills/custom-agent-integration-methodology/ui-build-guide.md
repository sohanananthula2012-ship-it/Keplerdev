# UI Build Guide — Path A (Project-Native)

This file is the concrete implementation companion to `SKILL.md` Path A. It gives working code for every layer of a project-native custom-agent chat surface: persistence table, secure proxy, frontend runtime hook, message conversion, and the actual chat panel component built from this project's own design-system components (`src/components/ui/*`). Adapt names/placeholders, do not skip layers.

Replace these placeholders everywhere below with the real values collected in `SKILL.md` Step 0:

- `<AGENT_ID>` — `custom_agent.id`
- `<ENTER_API_BASE_URL>` — `custom_agent.api_base_url`
- `<SECRET_NAME>` — `custom_agent.enter_api_key_secret_name` (the Supabase secret holding the Enter API key)

## File map

```
supabase/migrations/xxxx_custom_agent_threads.sql   -- thread ownership table
supabase/functions/custom-agent-proxy/index.ts      -- secure server-side proxy
src/hooks/use-custom-agent-chat.ts                  -- HttpAgent + ThreadClient runtime
src/lib/custom-agent-messages.ts                    -- turn -> semantic message conversion
src/components/custom-agent/custom-agent-chat.tsx   -- the chat panel (mount this into the host page)
src/components/custom-agent/custom-agent-message.tsx-- one semantic message -> UI row
```

Mount `<CustomAgentChat />` into whatever host surface Step 1 of `SKILL.md` chose (a page, a dashboard panel, a drawer) — do not create a new standalone route unless that host surface IS a new page.

## Step A — Persistence table

Every thread must be owned by a user/session so the proxy can enforce ownership. Load `enter_cloud` before writing migrations. Adapt via the `enter_cloud` skill's migration workflow:

```sql
create table if not exists custom_agent_threads (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id),
  anonymous_session_id text,
  agent_id text not null,
  thread_id text not null,
  version integer not null default 1,
  title text,
  latest_history_turn_id integer not null default 0,
  running_turn_id integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (agent_id, thread_id)
);

alter table custom_agent_threads enable row level security;

create policy "users manage their own custom agent threads"
  on custom_agent_threads for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);
```

If the surface is public/anonymous, use `anonymous_session_id` instead of `user_id` and scope the RLS policy accordingly — ask the user which policy fits before writing it.

Thread reuse policy: default to **one thread per user + agent** (reuse the same thread across visits). Only create a new thread when the user clicks an explicit "New chat" control. Never create a new thread on every message.

## Step B — Secure Supabase Edge Function proxy

The Enter API key never reaches the browser. The proxy reads `<SECRET_NAME>` server-side, validates the caller owns the thread, and forwards SSE untouched.

```ts
// supabase/functions/custom-agent-proxy/index.ts
import { serve } from 'https://deno.land/std/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const ENTER_API_BASE_URL = Deno.env.get('ENTER_API_BASE_URL') ?? '<ENTER_API_BASE_URL>';
const ENTER_API_KEY = Deno.env.get('<SECRET_NAME>');
const ALLOWED_AGENT_IDS = new Set(['<AGENT_ID>']);

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

function enterUrl(path: string, search = '') {
  return `${ENTER_API_BASE_URL.replace(/\/$/, '')}/code/api/v1${path}${search}`;
}

function enterHeaders(extra: HeadersInit = {}) {
  if (!ENTER_API_KEY) throw json({ error_code: 'ENTER_API_KEY_MISSING' }, 500);
  return { ...extra, Authorization: `Bearer ${ENTER_API_KEY}` };
}

function sse(upstream: Response) {
  return new Response(upstream.body, {
    status: upstream.status,
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' },
  });
}

serve(async (req) => {
  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } },
    );
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return json({ error_code: 'UNAUTHORIZED' }, 401);

    const url = new URL(req.url);
    const parts = url.pathname.split('/').filter(Boolean);
    const idx = parts.indexOf('custom-agent-proxy');
    const agentId = parts[idx + 1];
    const suffix = parts.slice(idx + 2);
    if (!ALLOWED_AGENT_IDS.has(agentId)) return json({ error_code: 'AGENT_NOT_ALLOWED' }, 403);

    async function assertOwnedThread(threadId: string) {
      const { data } = await supabase
        .from('custom_agent_threads')
        .select('id')
        .eq('user_id', user.id)
        .eq('agent_id', agentId)
        .eq('thread_id', threadId)
        .maybeSingle();
      if (!data) throw json({ error_code: 'THREAD_NOT_FOUND' }, 404);
    }

    // POST /custom-agent-proxy/{agentId}/threads
    if (req.method === 'POST' && suffix.length === 1 && suffix[0] === 'threads') {
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads`), {
        method: 'POST',
        headers: enterHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({}),
      });
      const body = await upstream.json();
      if (upstream.ok) {
        await supabase.from('custom_agent_threads').insert({
          user_id: user.id, agent_id: agentId, thread_id: body.thread_id, version: body.version ?? 1,
        });
      }
      return json(body, upstream.status);
    }

    // GET /custom-agent-proxy/{agentId}/threads/{threadId}
    if (req.method === 'GET' && suffix.length === 2 && suffix[0] === 'threads') {
      await assertOwnedThread(suffix[1]);
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${suffix[1]}`), { headers: enterHeaders() });
      return json(await upstream.json(), upstream.status);
    }

    // GET /custom-agent-proxy/{agentId}/threads/{threadId}/turns
    if (req.method === 'GET' && suffix.length === 3 && suffix[0] === 'threads' && suffix[2] === 'turns') {
      await assertOwnedThread(suffix[1]);
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${suffix[1]}/turns`, url.search), { headers: enterHeaders() });
      return new Response(upstream.body, { status: upstream.status, headers: { 'Content-Type': 'application/json' } });
    }

    // POST /custom-agent-proxy/{agentId}/run
    if (req.method === 'POST' && suffix.length === 1 && suffix[0] === 'run') {
      const body = await req.json();
      if (!body?.threadId) return json({ error_code: 'BAD_REQUEST' }, 400);
      await assertOwnedThread(body.threadId);
      const upstream = await fetch(enterUrl(`/agents/${agentId}/run`), {
        method: 'POST',
        headers: enterHeaders({ 'Content-Type': 'application/json', Accept: 'text/event-stream' }),
        body: JSON.stringify({
          threadId: body.threadId, runId: body.runId, messages: body.messages,
          state: body.state, context: body.context, tools: [], forwardedProps: {},
        }),
      });
      return sse(upstream);
    }

    // GET /custom-agent-proxy/{agentId}/threads/{threadId}/turns/{turnId}/events  (resume)
    if (req.method === 'GET' && suffix.length === 5 && suffix[0] === 'threads' && suffix[2] === 'turns' && suffix[4] === 'events') {
      await assertOwnedThread(suffix[1]);
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${suffix[1]}/turns/${suffix[3]}/events`), {
        headers: enterHeaders({ Accept: 'text/event-stream' }),
      });
      return sse(upstream);
    }

    // POST /custom-agent-proxy/{agentId}/threads/{threadId}/turns/{turnId}/cancel
    if (req.method === 'POST' && suffix.length === 5 && suffix[0] === 'threads' && suffix[2] === 'turns' && suffix[4] === 'cancel') {
      await assertOwnedThread(suffix[1]);
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${suffix[1]}/turns/${suffix[3]}/cancel`), {
        method: 'POST', headers: enterHeaders({ 'Content-Type': 'application/json' }), body: '{}',
      });
      return json(await upstream.json(), upstream.status);
    }

    // POST /custom-agent-proxy/{agentId}/threads/{threadId}/turns/{turnId}/tool-calls/{toolCallId}/answer
    if (req.method === 'POST' && suffix.length === 7 && suffix[0] === 'threads' && suffix[2] === 'turns' && suffix[4] === 'tool-calls' && suffix[6] === 'answer') {
      await assertOwnedThread(suffix[1]);
      const body = await req.json();
      const upstream = await fetch(enterUrl(`/agents/${agentId}/threads/${suffix[1]}/turns/${suffix[3]}/tool-calls/${suffix[5]}/answer`), {
        method: 'POST', headers: enterHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(body),
      });
      return json(await upstream.json(), upstream.status);
    }

    return json({ error_code: 'NOT_FOUND' }, 404);
  } catch (error) {
    if (error instanceof Response) return error;
    return json({ error_code: 'PROXY_FAILED' }, 500);
  }
});
```

Store `<SECRET_NAME>` via `supabase_add_secret`; never hard-code the real key. Keep `tools: []` and `forwardedProps: {}` in the run body always.

## Step C — Frontend runtime hook

```bash
pnpm add @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

```ts
// src/hooks/use-custom-agent-chat.ts
import { useCallback, useMemo, useRef, useState } from 'react';
import { HttpAgent } from '@enter-pro/agent-client';
import { ThreadClient, ThreadManager, toThreadTurnsFromAgUiHistory, type ThreadTurn } from '@enter-pro/thread-client';
import { supabase } from '@/integrations/supabase/client';
import { toCustomAgentSemanticMessages, type CustomAgentSemanticMessage } from '@/lib/custom-agent-messages';

const AGENT_ID = '<AGENT_ID>';
const PROXY_BASE = `https://<PROJECT_REF>.supabase.co/functions/v1/custom-agent-proxy/${AGENT_ID}`;

async function appToken() {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token ?? '';
}

export function useCustomAgentChat() {
  const managerRef = useRef(new ThreadManager());
  const agentRef = useRef<HttpAgent | null>(null);
  const [threadId, setThreadId] = useState<string | null>(null);
  const [turns, setTurns] = useState<readonly ThreadTurn[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const authHeaders = useCallback(async () => ({ Authorization: `Bearer ${await appToken()}` }), []);

  const getOrCreateClient = useCallback(async (id: string) => {
    const key = `custom-agent-${id}`;
    const existing = managerRef.current.get(key);
    if (existing) return existing;

    const agent = new HttpAgent({
      threadId: id,
      url: () => `${PROXY_BASE}/run`,
      token: appToken,
      abortUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        return turnId == null ? '' : `${PROXY_BASE}/threads/${id}/turns/${turnId}/cancel`;
      },
      resumeUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        if (turnId == null) throw new Error('No running turn');
        return `${PROXY_BASE}/threads/${id}/turns/${turnId}/events`;
      },
    });
    agentRef.current = agent;

    const client = new ThreadClient({
      threadId: id,
      agent,
      historyMessageLoader: {
        async load(_id, start, end) {
          const resp = await fetch(`${PROXY_BASE}/threads/${id}/turns?start_turn=${start}&end_turn=${end}`, { headers: await authHeaders() });
          const body = await resp.json();
          return toThreadTurnsFromAgUiHistory({ turns: body.turns });
        },
        async loadSince() { return []; },
      },
      historyMessagePagination: { turnSize: 20, endTurn: 0 },
    });

    client.subscribe(() => {
      setTurns(client.turns);
      setIsRunning(client.isAgentRunning);
    });

    managerRef.current.register(key, client);
    return client;
  }, [authHeaders]);

  const activateThread = useCallback(async () => {
    const resp = await fetch(`${PROXY_BASE}/threads`, { method: 'POST', headers: await authHeaders() });
    const thread = await resp.json();
    const client = await getOrCreateClient(thread.thread_id);
    await managerRef.current.resume(`custom-agent-${thread.thread_id}`);
    setThreadId(thread.thread_id);
    if (thread.running != null) await agentRef.current?.resumeTurn(thread.running);
    return thread.thread_id as string;
  }, [authHeaders, getOrCreateClient]);

  const sendMessage = useCallback(async (content: string) => {
    const id = threadId ?? await activateThread();
    const client = await getOrCreateClient(id);
    if (client.status !== 'active') throw new Error('Thread is not active');
    await client.sendMessage({ content, sentAt: Date.now() });
  }, [activateThread, getOrCreateClient, threadId]);

  const cancel = useCallback(() => managerRef.current.getActive()?.abort(), []);

  const semanticMessages: CustomAgentSemanticMessage[] = useMemo(
    () => toCustomAgentSemanticMessages(turns.flatMap((t) => t.messages), { isRunning }),
    [turns, isRunning],
  );

  return { semanticMessages, isRunning, sendMessage, cancel, activateThread };
}
```

Adjust `PROXY_BASE` to the project's real Supabase Functions URL and `@/integrations/supabase/client` to the project's actual Supabase client path (see `enter_cloud` skill for the canonical client location).

## Step D — Turn-to-message conversion

```ts
// src/lib/custom-agent-messages.ts
import { isThreadAgUiMessage, isThreadCustomMessage, type ThreadMessage } from '@enter-pro/thread-client';

export type CustomAgentSemanticMessage =
  | { id: string; uiKind: 'user-text'; content: string }
  | { id: string; uiKind: 'assistant-answer'; content: string; streaming?: boolean }
  | { id: string; uiKind: 'agent-status'; phase: 'preparing' | 'responded' }
  | { id: string; uiKind: 'thinking'; content: string; streaming?: boolean }
  | { id: string; uiKind: 'tool-action-list'; labels: string[]; isLoading: boolean }
  | { id: string; uiKind: 'turn-error'; detail: string }
  | { id: string; uiKind: 'cancel' };

const startupNames = new Set(['agent.environment.warming', 'agent.environment.ready', 'agent.loading', 'agent.loaded']);

export function toCustomAgentSemanticMessages(
  items: readonly ThreadMessage[],
  options: { isRunning?: boolean } = {},
): CustomAgentSemanticMessage[] {
  const out: CustomAgentSemanticMessage[] = [];
  let sawStartup = false;
  let tools: string[] = [];
  const flushTools = (isLoading = false) => {
    if (!tools.length) return;
    out.push({ id: `tools:${out.length}`, uiKind: 'tool-action-list', labels: tools, isLoading });
    tools = [];
  };

  for (const item of items) {
    if (isThreadCustomMessage(item)) {
      const name = item.event.name;
      if (startupNames.has(name)) { sawStartup = true; continue; }
      if (name === 'agent.turn.cancelled') { flushTools(); out.push({ id: item.id, uiKind: 'cancel' }); continue; }
      if (name === 'agent.turn.error') {
        flushTools();
        const value = item.event.value as Record<string, unknown> | undefined;
        out.push({ id: item.id, uiKind: 'turn-error', detail: String(value?.message ?? 'The agent run failed.') });
        continue;
      }
      continue; // hide other custom/telemetry events from the main transcript
    }
    if (!isThreadAgUiMessage(item)) continue;

    const msg = item.message as Record<string, unknown>;
    const role = msg.role as string | undefined;
    const calls = (msg.toolCalls ?? msg.tool_calls) as Array<Record<string, unknown>> | undefined;

    if (role === 'user') { flushTools(); out.push({ id: item.id, uiKind: 'user-text', content: String(msg.content ?? '') }); continue; }
    if (calls?.length) { tools.push(...calls.map((c) => String((c.function as Record<string, unknown> | undefined)?.name ?? c.name ?? 'Tool call'))); continue; }
    if (role === 'assistant') {
      const content = String(msg.content ?? '').trim();
      if (!content) continue;
      flushTools();
      out.push({ id: item.id, uiKind: 'assistant-answer', content, streaming: options.isRunning });
    }
  }

  flushTools(options.isRunning === true);
  if (sawStartup) out.unshift({ id: 'status', uiKind: 'agent-status', phase: options.isRunning ? 'preparing' : 'responded' });
  return out;
}
```

This is intentionally simplified (no `AskUserQuestion` card, no per-tool icon registry). Add those only if the target agent actually uses them — check with the user or inspect a live run first, or look at `default-ui-template/src/core/questions.ts` and `default-ui-template/src/core/toolActionDisplay.ts` for a fuller reference implementation already bundled in this skill.

## Step E — Chat panel component (project design system)

Uses only this project's existing `src/components/ui/*` primitives and semantic Tailwind tokens — no raw colors.

```bash
pnpm add react-markdown@^10.1.0 remark-gfm@^4.0.0
```

```tsx
// src/components/custom-agent/custom-agent-message.tsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import type { CustomAgentSemanticMessage } from '@/lib/custom-agent-messages';

export function CustomAgentMessage({ message }: { message: CustomAgentSemanticMessage }) {
  switch (message.uiKind) {
    case 'user-text':
      return (
        <div className="ml-auto max-w-[80%] rounded-lg bg-primary px-3 py-2 text-primary-foreground">
          {message.content}
        </div>
      );
    case 'assistant-answer':
      return (
        <div className="prose prose-sm max-w-none text-foreground dark:prose-invert">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>
      );
    case 'agent-status':
      return (
        <Badge variant="secondary">{message.phase === 'preparing' ? 'Agent getting ready' : 'Agent ready'}</Badge>
      );
    case 'thinking':
      return (
        <p className={cn('text-sm italic text-muted-foreground', message.streaming && 'animate-pulse')}>
          {message.content || 'Thinking…'}
        </p>
      );
    case 'tool-action-list':
      return (
        <div className="space-y-1 text-sm text-muted-foreground">
          {message.labels.map((label, i) => (
            <div key={i}>{message.isLoading ? `Running: ${label}` : `Completed: ${label}`}</div>
          ))}
        </div>
      );
    case 'turn-error':
      return <Alert variant="destructive"><AlertDescription>{message.detail}</AlertDescription></Alert>;
    case 'cancel':
      return <p className="text-sm text-muted-foreground">Cancelled</p>;
  }
}
```

```tsx
// src/components/custom-agent/custom-agent-chat.tsx
import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useCustomAgentChat } from '@/hooks/use-custom-agent-chat';
import { CustomAgentMessage } from './custom-agent-message';

export function CustomAgentChat() {
  const { semanticMessages, isRunning, sendMessage, cancel } = useCustomAgentChat();
  const [draft, setDraft] = useState('');

  const handleSend = async () => {
    if (!draft.trim() || isRunning) return;
    const content = draft;
    setDraft('');
    await sendMessage(content);
  };

  return (
    <Card className="flex h-full flex-col">
      <CardHeader>
        <CardTitle>Assistant</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col gap-4 overflow-hidden">
        <ScrollArea className="flex-1 pr-4">
          <div className="flex flex-col gap-3">
            {semanticMessages.map((m) => <CustomAgentMessage key={m.id} message={m} />)}
          </div>
        </ScrollArea>
        <div className="flex gap-2">
          <Textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void handleSend(); } }}
            placeholder="Type a message…"
            className="min-h-[44px] resize-none"
          />
          {isRunning ? (
            <Button variant="outline" onClick={cancel}>Cancel</Button>
          ) : (
            <Button onClick={handleSend}>Send</Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

Mount `<CustomAgentChat />` inside the host page/panel chosen in `SKILL.md` Step 1 — do not create a new top-level route unless that host surface is itself a new page the user asked for.

## Step F — Labels and i18n

If the project has i18n enabled (`src/i18n/config.ts` + `public/locales/*.json` present), replace literal strings above (`"Agent getting ready"`, `"Send"`, `"Cancel"`, `"Type a message…"`, etc.) with `useTranslation()` keys added to every locale file under `public/locales/`. Do not hard-code labels for a single language when the project supports more than one.

## Step G — Verify

- Screenshot the host page/panel at desktop and mobile widths after wiring `<CustomAgentChat />` in.
- Send a real message and confirm: status badge shows while preparing, tool rows show running verbs while active and completed verbs after, assistant answer renders Markdown (not raw text), and Cancel stops a long-running turn.
- Confirm the Enter API key never appears in browser network requests — only calls to the project's own Supabase Function URL should be visible in the browser's network tab.
