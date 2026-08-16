# Errors and Recovery

Handle custom-agent integrations as a stateful stream, not as a stateless request. Recovery usually means checking thread state, resuming a turn, or asking for a missing secret.

## Create-thread errors

| Code | Recovery |
| --- | --- |
| `AGENT_NOT_FOUND` | Verify `agent_id` from reminder/config. Do not invent another id. |
| `VERSION_NOT_FOUND` | For API-key integrations, remove explicit version and use latest published. |
| `AGENT_VERSION_STOPPED` | Ask user to publish/re-publish or choose another published version. |
| `THREAD_CREATE_FORBIDDEN` | Check API key workspace and whether caller is trying to create draft-version threads. |
| `WORKSPACE_FORBIDDEN` | Use an API key or JWT from the workspace that owns the custom agent. |
| `SERVING_CREATE_THREAD_UNAVAILABLE` | Retry with backoff; if persistent, surface service unavailable. |
| `CREATE_THREAD_FAILED` | Log sanitized request ids/status, show generic failure. |

## Run errors

| Code | Recovery |
| --- | --- |
| `SERVING_THREAD_ID_REQUIRED` | Create a thread first and include `threadId`. |
| `SERVING_TOOLS_NOT_SUPPORTED` | Remove client-supplied `tools`; tools are server-declared. |
| `SERVING_MODEL_OVERRIDE_NOT_SUPPORTED` | Remove `forwardedProps.model_id`; model comes from the thread-bound version. |
| `THREAD_NOT_FOUND` | Clear stale local mapping and create a new thread after user confirmation or product policy. |
| `THREAD_BUSY` | Do not start a second run. Resume or wait for the active turn; offer cancel if supported. |
| `RUN_FORBIDDEN` | Check published version and workspace ownership for the API key. |
| `AGENT_VERSION_STOPPED` | Stop sending new runs; let user choose/publish another version. |
| `SERVING_ENV_FAILED` | Surface retry/recreate-thread path if product allows; environment may be non-recoverable. |
| `INVALID_AGENT_MODEL_CONFIG` | Builder owner must fix/publish agent model config. |
| `RUN_FAILED` | Mark turn failed, preserve events, allow retry on same or new thread per product policy. |

## History/resume/cancel errors

| Code | Recovery |
| --- | --- |
| `INVALID_TURN_RANGE` | Send both `start_turn` and `end_turn` as positive integers. |
| `TURN_NOT_FOUND` | Refresh thread state; active turn id may be stale. |
| `TURN_ALREADY_TERMINAL` | Treat cancel as no-op success from a UX perspective and refresh history. |
| `TURN_NOT_CANCELLABLE` | Disable cancel UI and continue listening or refresh state. |
| `RESOLVE_FAILED` | Fall back to `GET /threads/{thread_id}` and history API. |

## Streaming failures

If `/run` network streaming fails before a terminal event:

1. Call `GET /threads/{thread_id}`.
2. If `running` is present, resume with `/turns/{turn_id}/events`.
3. If no running turn exists, load recent history and render the final stored state.
4. If neither path yields a result, mark the local turn as uncertain and let the user retry.

## Secret failures

If an Enter project integration cannot read `enter_api_key_secret_name`:

- Do not ask for the key in chat.
- Tell the user to create/copy an Enter API key in Workspace Settings > API keys.
- Use the secret-key tool or project secret UI to store it under the exact secret name from the reminder.
- Retry the proxy call after the secret exists.

## Retry guidance

Safe retries:

- Create thread after transient 503, if the host can tolerate another thread.
- Resume events after network interruption.
- Read thread/turn state.

Risky retries:

- Retrying `/run` after a partial stream. First check thread state to avoid duplicate turns.
- Creating a new thread automatically after `THREAD_NOT_FOUND` if it would hide lost history.

## User-facing wording

Prefer actionable messages:

- "This thread is already running. I can wait, reconnect, or cancel the current run."
- "The API key cannot access this custom agent's workspace. Create an Enter API key in the same workspace as the agent."
- "The custom agent version is stopped. Publish a version before running it through API-key integration."

Avoid exposing raw stack traces, credentials, or full request payloads.
