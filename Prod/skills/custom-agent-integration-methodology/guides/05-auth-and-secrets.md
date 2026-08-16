# Auth and Secrets

The Enter API key is a server-side credential. The biggest integration mistake is letting a browser, generated frontend bundle, or public repository see it.

## Enter project route

When the system reminder includes `enter_api_key_secret_name`, use that exact secret name. The backend builds names like `ENTER_API_KEY_<PROJECT_PREFIX>` and tells the coding agent what to request.

If the secret is missing:

1. Tell the user to retry the custom-agent import flow, or re-trigger Enter Cloud enable / cloud-secret refresh so the backend can populate `enter_api_key_secret_name` automatically.
2. If a manual secret is still required, tell the user to open the Custom Agent preview page, go to `Developer > REST API`, click `API Key`, and copy the key.
3. Request the value through the project secret-key tool or the platform's secret-entry mechanism.
4. Do not ask the user to paste the key in normal chat.

The generated project code should read the key only in server-side code, such as a Supabase Edge Function or backend route.

## External AI-agent route

For trusted server-side consumers, create or update a local server-side config file such as `.enter_custom_agent.env`. Prefer this concrete file pattern for generated local examples so the user has an obvious place to paste the API key without exposing it in chat.

```env
# Local server-side config. This file is ignored by git.
# Get ENTER_API_KEY from Custom Agent preview > Developer > REST API > API Key.
# Paste it here locally; do not paste it into chat.

ENTER_API_BASE_URL=<ENTER_API_BASE_URL>
ENTER_CUSTOM_AGENT_ID=<ENTER_CUSTOM_AGENT_ID>
ENTER_API_KEY=
```

Prefer values from the Integration Skill tab comments when available: `ENTER_API_BASE_URL` and `ENTER_CUSTOM_AGENT_ID` are rendered there by Enter, so generated config files should pre-fill those two values. Always include `ENTER_API_KEY=` as an empty line for the user to fill locally. For `ENTER_API_KEY`, ask the user to open the Custom Agent preview page, go to `Developer > REST API`, click `API Key`, and paste the key into the server-side config file. Check `.gitignore` and add `.enter_custom_agent.env` or the chosen equivalent env file if needed. To use another published custom agent, open that agent's preview/config page and double-click the custom agent logo to copy its Agent ID, then replace `ENTER_CUSTOM_AGENT_ID`.

For local examples, show placeholders only. Never include a real key or a fixed local custom-agent id copied from source examples.

## Proxy rule

If any untrusted client is involved, insert a proxy:

```text
Browser -> App backend or Edge Function -> Enter Serving API
```

The proxy should:

- Authenticate the browser with the app's own auth.
- Authorize access to the host project/session/thread.
- Read the Enter API key from server-side secrets.
- Attach `Authorization: Bearer <ENTER_API_KEY>` only when calling Enter.
- Forward streaming responses without buffering the entire run.
- Redact authorization headers and message content from logs unless explicitly needed and safe.

## What the API key can do

API-key serving is limited by workspace and published-agent rules:

- Create threads for published agent versions in the key's workspace.
- Run published agent versions in the key's workspace.
- Read allowed thread/turn state for that workspace.
- It cannot run draft versions through the normal API-key flow.
- It cannot run agents from another workspace.

## Frontend token distinction

In Enter Web Builder test panel, `HttpAgent.token` returns an Auth0 access token because the UI is talking to Enter's own authenticated backend.

In an Enter project integration, the browser should not receive the Enter API key. `HttpAgent.token` should return either:

- The user's app session token for your proxy, or
- An empty string if the proxy authenticates by cookie and same-origin policy.

The proxy then attaches the Enter API key to Enter Serving.

## Logging and storage rules

Never log or store:

- Enter API keys.
- `Authorization` headers.
- API keys in normal chat, browser bundles, localStorage, URL query strings, screenshots, generated docs, or committed code.
- Full SSE payloads if they may include user-private content, unless the product has explicit retention rules.
- Project secret values.

Safe to store:

- `agent_id`
- `thread_id`
- `version`
- turn status and timestamps
- sanitized error codes
- rendered transcript if the product already stores chat content and users expect persistence

## Generated docs and code examples

Use these placeholders only:

- `<ENTER_API_BASE_URL>`
- `<ENTER_API_KEY>`
- `<ENTER_CUSTOM_AGENT_ID>`
- `<THREAD_ID>`
- `<APP_SESSION_TOKEN>`

Do not copy concrete values from local fixtures, code examples, tests, logs, browser devtools, or system reminders into committed examples.
