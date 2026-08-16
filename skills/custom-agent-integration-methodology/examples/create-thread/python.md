# Create Thread with Python

Use this in trusted server-side Python or a local automation environment.

```python
import requests


def create_serving_thread(base_url: str, api_key: str, agent_id: str) -> dict:
    url = f"{base_url.rstrip('/')}/code/api/v1/agents/{agent_id}/threads"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={},
        timeout=30,
    )
    if not response.ok:
        try:
            detail = response.json()
        except ValueError:
            detail = {"message": response.text}
        raise RuntimeError(
            f"Create thread failed: {response.status_code} {detail.get('error_code', '')} {detail.get('message', '')}"
        )
    return response.json()
```
