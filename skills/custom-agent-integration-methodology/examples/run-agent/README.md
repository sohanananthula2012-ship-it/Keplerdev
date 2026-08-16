# Run Agent Examples

After creating a thread, run the custom agent with:

```text
POST <ENTER_API_BASE_URL>/code/api/v1/agents/<ENTER_CUSTOM_AGENT_ID>/run
```

The response is SSE with AG-UI events. Pick one approach:

- `agui-sdk.md`: default TypeScript runtime using `@enter-pro/agent-client@0.0.2` and `@enter-pro/thread-client@0.0.2`.
- `raw-sse.md`: when writing a portable CLI/server client without frontend runtime packages.

Remember:

- Always include `threadId`.
- Do not send non-empty `tools`.
- Do not send `forwardedProps.model_id`.
- Do not call `response.json()` on `/run`.
