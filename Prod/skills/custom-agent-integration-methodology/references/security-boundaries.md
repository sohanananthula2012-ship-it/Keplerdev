# Security Boundaries

Custom-agent integration crosses trust boundaries. Keep them explicit in code and docs.

## Trusted vs untrusted

Trusted:

- Backend service.
- Supabase Edge Function.
- Server-side job runner.
- Local CLI or AI agent process running with secret-manager access.

Untrusted:

- Browser JavaScript.
- Mobile client bundle.
- Public static assets.
- User-editable project files that are shipped to users.
- Logs, analytics events, screenshots, and generated docs.

The Enter API key belongs only in trusted code.

## Enter project default architecture

```text
React UI -> project backend/Edge Function -> Enter Serving API
```

The UI sends app-authenticated requests to the project backend. The backend checks app authorization, reads `enter_api_key_secret_name`, and calls Enter Serving.

## Authorization checks in the proxy

A proxy should verify:

- The current user/session can access the host project or conversation.
- The requested `agent_id` is one of the agents configured for this project.
- The requested `thread_id` belongs to the current user/session/project mapping.
- The requested `turn_id` belongs to the requested thread when canceling/resuming.

Do not let the browser pass arbitrary `agent_id`, `thread_id`, or Enter base URL without validation.

## Allowed client-controlled fields

Usually safe from the browser after app authorization:

- User message content.
- Host conversation id.
- A selected local thread id known to belong to the session.
- UI-only options that do not change Enter model/tool configuration.

Do not accept from browser:

- Enter API key.
- `Authorization` header for Enter.
- Arbitrary `api_base_url`.
- Non-empty `tools` in the run payload.
- `forwardedProps.model_id`.
- Explicit draft version for API-key create-thread flows.

## Data retention

Decide whether the host app stores:

- Only `thread_id` and relies on Enter for history.
- Rendered transcript.
- Raw AG-UI events.
- Turn metadata and usage.

If storing raw events, treat them as chat content. They may include user text, assistant text, tool names, tool arguments, or custom metadata.

## Redaction checklist

Redact or omit before logging:

- `Authorization`.
- `ENTER_API_KEY` or secret values.
- User message content unless the product explicitly logs chat.
- Full SSE event payloads by default.
- Tool arguments that may contain private data.

Safe log fields:

- `agent_id`.
- `thread_id`.
- `turn_id`.
- error code.
- HTTP status.
- duration.
- retry count.

## Example placeholders only

All docs and generated examples must use placeholders. Do not paste real values from system reminders, local JSON fixtures, copied curl commands, browser requests, or logs.
