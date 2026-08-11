# Live Golden Demo

This folder documents the local-only validation path for the default chat template. It intentionally does not contain secrets.

Required local env keys, read at runtime only:

- `ENTER_API_BASE_URL`
- `ENTER_API_KEY`
- `ENTER_CUSTOM_AGENT_ID`

Do not print, commit, copy into source, or expose the key values in screenshots/logs.

Golden prompt:

```text
When is the 2026 World Cup, and where is it being held?
```

Expected screenshot traits:

- Dark public-site-like transcript is the visual center.
- User message is a right-aligned dark bubble.
- Startup/status group is compact: `Agent getting ready` while preparing, then collapsed `Agent ready` after response/turn end.
- Real reasoning appears in a collapsible thinking group.
- Web search/tool calls appear in a completed action group with completed verbs such as `Searched websites`.
- Assistant final answer is Markdown/GFM content, with tables rendered as `<table>`.
- No `usage.update`, raw event JSON, debug cards, dashboard header, or “answer done” card in the main transcript.
