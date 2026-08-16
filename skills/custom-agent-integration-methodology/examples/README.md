# Examples

This directory contains small reusable snippets. Use `case-studies/` for full scenario architecture.

## Pick the example you need

| Need | File |
| --- | --- |
| Create a serving thread | `create-thread/` |
| Run a custom agent with the public SDK runtime | `run-agent/agui-sdk.md` |
| Run a custom agent with raw SSE for CLI/server code | `run-agent/raw-sse.md` |
| Understand thread/run sequencing | `thread-and-run-flow/README.md` |
| Render AG-UI events in a frontend | `frontend-event-rendering/` |

All examples use placeholders only:

- `<ENTER_API_BASE_URL>`
- `<ENTER_API_KEY>`
- `<ENTER_CUSTOM_AGENT_ID>`
- `<THREAD_ID>`

Fill `ENTER_API_BASE_URL` and `ENTER_CUSTOM_AGENT_ID` from Integration Skill tab comments when available. For local server-side examples, create or update a gitignored `.enter_custom_agent.env` file with those two values prefilled and a blank `ENTER_API_KEY=` line for the user to fill from `Custom Agent preview > Developer > REST API > API Key`. Never commit real values.

If adapting examples into an Enter project, move direct Enter calls behind a server-side proxy before exposing the UI. Browser chat UI should use `@enter-pro/agent-client@0.0.2` and `@enter-pro/thread-client@0.0.2`, not a text-only SSE adapter.
