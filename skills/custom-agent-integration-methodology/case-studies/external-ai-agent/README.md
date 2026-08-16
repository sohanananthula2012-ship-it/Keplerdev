# Case Study: External AI Agent Consumer

Use this route when there is no Enter project integration system reminder, or when the consumer is Codex, Claude Code, a backend service, a workflow runner, or another AI agent.

## Inputs

Collect from the Integration Skill tab comments or secure server configuration. For local/server-side generated examples, create or update `.enter_custom_agent.env` unless the target repo already has an equivalent server-only env file:

```env
# Local server-side config. This file is ignored by git.
# Get ENTER_API_KEY from Custom Agent preview > Developer > REST API > API Key.
# Paste it here locally; do not paste it into chat.

ENTER_API_BASE_URL=<ENTER_API_BASE_URL>
ENTER_CUSTOM_AGENT_ID=<ENTER_CUSTOM_AGENT_ID>
ENTER_API_KEY=
```

Use the `ENTER_API_BASE_URL` and `ENTER_CUSTOM_AGENT_ID` values rendered in the Integration Skill tab when available, and pre-fill those two lines in the config file. Always include `ENTER_API_KEY=` as a blank line. For `ENTER_API_KEY`, ask the user to open the Custom Agent preview page, go to `Developer > REST API`, click `API Key`, and paste the value into the gitignored server-side config file.

To target a different published custom agent, ask the user to open that agent's preview/config page and double-click the custom agent logo to copy its Agent ID, then replace `<ENTER_CUSTOM_AGENT_ID>`. Draft or unpublished agents cannot be used with API-key integration.

Check `.gitignore` and add `.enter_custom_agent.env` or the chosen equivalent env file if needed. If the consumer is not trusted server-side code, add a proxy first. Do not expose the API key to a browser or user-controlled runtime.

## Minimal workflow

1. Create a thread with `POST /agents/{agent_id}/threads` and `{}`.
2. Store the `thread_id` in the AI agent's session memory, local state, or database.
3. Run with `POST /agents/{agent_id}/run` and an AG-UI user message.
4. Stream and parse SSE events.
5. Summarize/render useful output for the invoking AI agent or user.
6. Reuse the same thread for follow-ups.

## Choosing SDK vs raw SSE

| Consumer | Recommended path |
| --- | --- |
| Node app with public Enter runtime packages | `sdk-client.md` or `examples/run-agent/agui-sdk.md` |
| CLI/server script | `raw-sse-client.md` or `examples/run-agent/raw-sse.md` |
| Browser UI | Build a server proxy, then use `ThreadClient` against the proxy. |
| AI coding agent generating code for a repo | Generate proxy/runtime code and document required secrets. |

## What to return to the user

For an AI-agent consumer, the useful result is usually not the raw event dump. Return:

- Created/reused `thread_id`.
- Final assistant text if available.
- Any structured output the custom agent produced.
- Whether the stream ended cleanly, failed, or was cancelled.
- Instructions for storing secrets and thread ids.

## Files in this case study

- `ai-agent-consumer-workflow.md`: operational flow for AI agents.
- `raw-sse-client.md`: robust raw SSE client.
- `sdk-client.md`: SDK-style client using Enter runtime packages.
