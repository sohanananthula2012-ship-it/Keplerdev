# API Contract

Base URL comes from the system reminder or environment, for example `<ENTER_API_BASE_URL>`. Paths below include the Enter API prefix used by the backend:

```text
/code/api/v1
```

Responses are flat JSON for JSON endpoints. Error responses are:

```json
{
  "error_code": "SOME_CODE",
  "message": "Human-readable message"
}
```

## Authentication

```text
Authorization: Bearer <ENTER_API_KEY>
```

Use API keys only from trusted server-side code.

## List published agents in a workspace

```text
GET /code/api/v1/workspaces/{workspace_public_id}/agents?page=1&page_size=20
```

Returns the latest published version for each agent in the workspace. This is useful for selection UIs, not required if the system reminder already supplied `agent_id`.

Common errors:

- `WORKSPACE_FORBIDDEN`
- `LIST_AGENTS_FAILED`

## Create thread

```text
POST /code/api/v1/agents/{agent_id}/threads
Content-Type: application/json
```

Request:

```json
{}
```

Optional Builder/debug JWT flow:

```json
{ "version": 12 }
```

Business response:

```json
{
  "thread_id": "<THREAD_ID>",
  "agent_id": "<ENTER_CUSTOM_AGENT_ID>",
  "version": 1,
  "name": "Custom agent name",
  "agent_status": "published",
  "env_ready_at": null,
  "created_at": "2026-06-10T00:00:00Z",
  "updated_at": "2026-06-10T00:00:00Z",
  "latest_history_turn_id": 0,
  "running": null
}
```

Errors:

| HTTP | Code | Meaning |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | Invalid JSON body. |
| 404 | `AGENT_NOT_FOUND` | Agent id does not exist or is not visible to caller. |
| 404 | `VERSION_NOT_FOUND` | Requested version does not exist. |
| 409 | `AGENT_VERSION_STOPPED` | Version is stopped. |
| 403 | `THREAD_CREATE_FORBIDDEN` | API key/JWT cannot create this thread. |
| 403 | `WORKSPACE_FORBIDDEN` | Caller cannot access workspace. |
| 503 | `SERVING_CREATE_THREAD_UNAVAILABLE` | Serving environment unavailable. |
| 500 | `CREATE_THREAD_FAILED` | Unexpected create failure. |

## Run agent

```text
POST /code/api/v1/agents/{agent_id}/run
Content-Type: application/json
Accept: text/event-stream
```

Request:

```json
{
  "threadId": "<THREAD_ID>",
  "messages": [
    {
      "id": "user-message-1",
      "role": "user",
      "content": "Write a concise plan."
    }
  ],
  "state": {},
  "context": [],
  "tools": [],
  "forwardedProps": {}
}
```

Response:

```text
Content-Type: text/event-stream
```

Each SSE `data:` payload is an AG-UI event JSON object.

Run body notes:

- `threadId` is mandatory.
- `runId` is ignored in v1.
- `state` and `context` are accepted but ignored in v1.
- `tools` must be absent or empty.
- `forwardedProps.model_id` is not supported.

Errors:

| HTTP | Code | Meaning |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | Invalid JSON body. |
| 400 | `SERVING_THREAD_ID_REQUIRED` | Missing `threadId`. |
| 400 | `SERVING_TOOLS_NOT_SUPPORTED` | Non-empty `tools`. |
| 400 | `SERVING_MODEL_OVERRIDE_NOT_SUPPORTED` | `forwardedProps.model_id` was set. |
| 400 | `INVALID_AGENT_MODEL_CONFIG` | Published agent model config is invalid. |
| 404 | `THREAD_NOT_FOUND` | Thread does not exist for this agent/caller. |
| 409 | `AGENT_VERSION_STOPPED` | Thread-bound version is stopped for new runs. |
| 403 | `RUN_FORBIDDEN` | Caller cannot run this version, often API key vs draft/wrong workspace. |
| 403 | `WORKSPACE_FORBIDDEN` | Caller cannot access workspace. |
| 409 | `THREAD_BUSY` | Another turn is already running on this thread. |
| 503 | `SERVING_ENV_FAILED` | Runtime environment failed. |
| 500 | `RUN_FAILED` | Unexpected run failure. |

## Get thread state

```text
GET /code/api/v1/agents/{agent_id}/threads/{thread_id}
```

Use this to refresh `running`, `latest_history_turn_id`, name, status, and timestamps after activation or run completion.

Errors:

- `THREAD_NOT_FOUND`
- `WORKSPACE_FORBIDDEN`
- `GET_THREAD_FAILED`

## List agent threads

```text
GET /code/api/v1/agents/{agent_id}/threads?page=1&page_size=20
```

Lists thread metadata across all versions of one agent.

Errors:

- `AGENT_NOT_FOUND`
- `WORKSPACE_FORBIDDEN`
- `LIST_AGENT_THREADS_FAILED`

## List version threads

```text
GET /code/api/v1/agents/{agent_id}/versions/{version}/threads?page=1&page_size=20
```

Used by Builder test UI to pick or create a default session for a version.

Errors:

- `VERSION_NOT_FOUND`
- `WORKSPACE_FORBIDDEN`
- `LIST_VERSION_THREADS_FAILED`

## List turns

```text
GET /code/api/v1/agents/{agent_id}/threads/{thread_id}/turns?start_turn=1&end_turn=20
```

Both query params are required positive integers.

Response:

```json
{
  "thread_id": "<THREAD_ID>",
  "turns": [
    {
      "turn_id": 1,
      "status": "completed",
      "model_id": "model-name-or-id",
      "events": [],
      "degraded": false,
      "created_at": "2026-06-10T00:00:00Z",
      "updated_at": "2026-06-10T00:00:00Z",
      "user_message": {
        "id": "user-message-1",
        "role": "user",
        "content": "Hello"
      }
    }
  ]
}
```

Errors:

- `INVALID_TURN_RANGE`
- `THREAD_NOT_FOUND`
- `WORKSPACE_FORBIDDEN`
- `LIST_TURNS_FAILED`

## Answer tool call

Used when a serving tool such as `AskUserQuestion` pauses the turn for user input.

```text
POST /code/api/v1/agents/{agent_id}/threads/{thread_id}/turns/{turn_id}/tool-calls/{tool_call_id}/answer
Content-Type: application/json
```

Request:

```json
{
  "response": "answered",
  "answers": [
    {
      "question": "Which result do you prefer?",
      "header": "Optional section label",
      "selected_options": ["A"],
      "note": "Optional free text"
    }
  ]
}
```

For skip-all:

```json
{ "response": "skipped" }
```

Errors:

- `THREAD_NOT_FOUND`
- `TURN_NOT_FOUND`
- `TOOL_CALL_NOT_FOUND`
- `TOOL_CALL_ALREADY_RESOLVED`
- `WORKSPACE_FORBIDDEN`
- `ANSWER_TOOL_CALL_FAILED`

A browser UI may treat HTTP 409 as already handled/expired and refresh the thread instead of showing a fatal error.

## Cancel turn

```text
POST /code/api/v1/agents/{agent_id}/threads/{thread_id}/turns/{turn_id}/cancel
```

Response:

```json
{
  "agent_id": "<ENTER_CUSTOM_AGENT_ID>",
  "thread_id": "<THREAD_ID>",
  "turn_id": 1,
  "status": "cancelled"
}
```

Errors:

- `THREAD_NOT_FOUND`
- `TURN_NOT_FOUND`
- `WORKSPACE_FORBIDDEN`
- `TURN_ALREADY_TERMINAL`
- `TURN_NOT_CANCELLABLE`
- `CANCEL_FAILED`

## Resume/read turn events

```text
GET /code/api/v1/agents/{agent_id}/threads/{thread_id}/turns/{turn_id}/events
Accept: text/event-stream
```

Use for active turn resume/reconnect. For completed historical turns, use the JSON turns endpoint.

Errors:

- `THREAD_NOT_FOUND`
- `TURN_NOT_FOUND`
- `RESOLVE_FAILED`
