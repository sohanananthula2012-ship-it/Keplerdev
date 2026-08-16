# Create Thread Examples

Create a thread before the first run. Store the returned `thread_id` and reuse it for follow-up turns.

Endpoint:

```text
POST <ENTER_API_BASE_URL>/code/api/v1/agents/<ENTER_CUSTOM_AGENT_ID>/threads
```

Use an empty JSON body for latest published version:

```json
{}
```

Files:

- `curl.md`
- `typescript.md`
- `python.md`

Do not pass a concrete version in API-key project integrations unless the product explicitly supports version selection and the backend allows it.
