# Thread Persistence

Thread persistence connects the host app's conversation/session to Enter's serving thread.

## Minimal table

```sql
create table if not exists custom_agent_threads (
  id uuid primary key default gen_random_uuid(),
  project_id text not null,
  user_id text,
  anonymous_session_id text,
  agent_id text not null,
  thread_id text not null,
  version integer not null,
  title text,
  latest_history_turn_id integer not null default 0,
  running_turn_id integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, agent_id, thread_id)
);
```

For anonymous/public experiences, use `anonymous_session_id`. For authenticated project apps, use `user_id`.

## Create or reuse policy

Choose one:

| Policy | Behavior |
| --- | --- |
| One thread per user and agent | Good default for assistant widgets. Reuse the same thread for that user. |
| One thread per host conversation and agent | Best when the host already has conversation objects. |
| New thread per explicit chat | Best for session menus and "new chat" buttons. |

Do not create a new thread on every message.

## Ownership checks

Before proxying get/run/cancel/resume:

1. Resolve current project and user/session.
2. Look up `agent_id + thread_id` in the mapping table.
3. Confirm it belongs to the current user/session/project.
4. Only then call Enter Serving.

## Active turn tracking

When using `HttpAgent`, the runtime exposes `activeTurnId`. Store it after live turn start if you need server-side cancellation or reconnect across reloads.

After a turn completes:

1. Refresh `GET /threads/{thread_id}`.
2. Refresh `GET /turns?start_turn=<turnId>&end_turn=<turnId>` if you render metadata.
3. Clear `running_turn_id` locally.
4. Update `latest_history_turn_id`.

## Reconnect

On page reload:

1. Load persisted mapping.
2. Get thread state from Enter.
3. If `running` exists, call resume events endpoint or `agent.resumeTurn(thread.running)`.
4. Load history range ending at `latest_history_turn_id`.

## Multiple custom agents

Use one row per `agent_id + thread_id`. If the system reminder contains multiple agents, keep the mappings independent.
