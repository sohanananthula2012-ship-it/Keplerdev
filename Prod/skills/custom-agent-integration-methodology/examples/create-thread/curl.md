# Create Thread with cURL

```bash
curl -sS \
  -X POST "<ENTER_API_BASE_URL>/code/api/v1/agents/<ENTER_CUSTOM_AGENT_ID>/threads" \
  -H "Authorization: Bearer <ENTER_API_KEY>" \
  -H "Content-Type: application/json" \
  --data '{}'
```

Expected business response:

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
