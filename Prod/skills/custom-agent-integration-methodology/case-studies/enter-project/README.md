# Case Study: Integrate a Custom Agent into an Enter Project

Use this route when a system reminder says the user attached a custom agent mention and asks to integrate it into the current project.

## Inputs from the reminder

Read these fields exactly:

```text
custom_agent:
- id: <ENTER_CUSTOM_AGENT_ID>
- name: <CUSTOM_AGENT_NAME>
- logo: <CUSTOM_AGENT_LOGO>
- api_base_url: <ENTER_API_BASE_URL>
- enter_api_key_secret_name: <SECRET_NAME>
```

If there are multiple custom agents, repeat the plan per agent and store separate thread mappings.

## Canonical project architecture

```text
Project UI
  uses @enter-pro/agent-client + @enter-pro/thread-client
  calls project proxy with the app/session token
Project proxy
  validates app auth, agent allowlist, and thread ownership
  reads <SECRET_NAME> from server-side secrets
  calls Enter Serving APIs
  forwards AG-UI SSE without flattening it
Enter Serving
  owns custom-agent threads, turns, events, history, resume, and cancel
```

Install the public runtime packages in the generated project:

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

Do not add registry publish credentials to the project. Downloading these packages is public; publish credentials are not part of project integration.

## Implementation sequence

1. Inspect the current project before choosing files or UI. Record the app framework, route structure, existing pages/workflows, design system, auth/session model, API/proxy layer, persistence layer, i18n source, and any chat/assistant/agent surfaces.
2. Choose exactly one strategy:
   - `project-native`: an existing product surface can host the agent. Reuse project routes, components, design tokens, auth, persistence, i18n, layout density, and interaction patterns.
   - `standalone/blank-chat`: the project is blank/scaffold-like, no suitable host surface exists, or the user explicitly asked for a standalone/default chat UI. Copy `templates/builder-public-site-chat/` and adapt only project edges.
   - `proxy-only`: the task only needs secure backend/API integration, or the UI will be built later. Add proxy, thread persistence, and adapter documentation without a full chat page.
3. Add a server-side proxy for create-thread, get-thread, list-turns, run, resume events, answer tool calls, and cancel.
4. Store project/user/session to `agent_id + thread_id` mapping in the project's persistence layer.
5. Add frontend runtime with `HttpAgent`, `ThreadClient`, and `ThreadManager` from the `@enter-pro/*` packages when a browser UI is involved.
6. Render from `ThreadClient.turns`, converting turns to a product-specific renderable message model.
7. For `project-native`, map semantic message sections into the host UI: agent status, thinking/reasoning, tool actions, assistant answer, question cards, errors, cancellation, and unsupported debug-only events. Do not copy the portable template just because the user did not name a UI style.
8. For `standalone/blank-chat`, copy `templates/builder-public-site-chat/` into the target project and adapt proxy URL, auth token getter, session storage, locale, visual tokens, and optional renderer slots. Keep the Public Site typography baseline: 14px/22px transcript text, 800px transcript/composer cap, and 568px user bubble cap.
9. Keep session navigation local-first: new-session and select-session update UI immediately, then refresh thread/session data in the background with stale-response guards.
10. Verify assistant answers render Markdown/GFM, tool actions use state-consistent verbs, UI labels follow the project/user language, and the API key never appears in frontend code, browser-visible env, localStorage, logs, generated docs, or chat output.
11. If a local dev server is available, screenshot-check the affected project-native surface or run the fallback template checks for `standalone/blank-chat`.

Do not generate browser UI that consumes a simplified phase-only or text-delta-only event protocol. If a project temporarily cannot install the SDK, its fallback must still preserve raw AG-UI events in a lossless turn state.
Do not generate a raw event/debug card UI unless the user explicitly asked for a debug/event inspector. Telemetry and raw event JSON belong in an optional debug view, not in the default chat transcript.

## Project inspection checklist

Before writing UI code, inspect enough of the target project to answer these questions:

| Area | What to inspect | Decision it informs |
| --- | --- | --- |
| Routes and navigation | Router config, pages, app shell, sidebar/header patterns | Where the custom agent belongs, or whether a new route is justified. |
| Existing agent/chat surfaces | Chat pages, support widgets, assistant panels, message components, command palettes | Whether to embed into an existing conversation/workflow surface. |
| Design system | Component library, tokens, Tailwind/theme config, icon set, spacing/type scale | How status/thinking/tool/answer UI should look in `project-native`. |
| Auth and API layer | Session/token getter, fetch client, edge functions, backend routes | How the browser calls the project proxy without seeing the Enter API key. |
| Persistence | DB schema, local storage policy, existing conversation/session tables | Where to store `agent_id + thread_id + version` mappings. |
| I18n | Locale provider, message catalog, language detection | How labels such as status/thinking/tool verbs are localized. |
| Runtime constraints | Package manager, React/Vue/etc., server/client boundaries, streaming support | Whether `@enter-pro/*` can be used directly or needs a thin adapter. |

If inspection finds a natural host surface, use `project-native`. If it finds no product surface and the user asked to "add chat" or "make a page", use `standalone/blank-chat`. If the current request is infrastructure-only, use `proxy-only`.

## Proxy endpoints to expose inside the project

Suggested app-local endpoints:

```text
POST /api/custom-agent/{agentId}/threads
GET  /api/custom-agent/{agentId}/threads/{threadId}
GET  /api/custom-agent/{agentId}/threads/{threadId}/turns?start_turn=&end_turn=
POST /api/custom-agent/{agentId}/run
GET  /api/custom-agent/{agentId}/threads/{threadId}/turns/{turnId}/events
POST /api/custom-agent/{agentId}/threads/{threadId}/turns/{turnId}/cancel
```

Every endpoint validates app/session ownership before calling Enter Serving with the server-side key.

## Required customization adapters

Generated code should isolate host-project choices behind small adapters:

| Adapter | Purpose |
| --- | --- |
| Auth adapter | Reads the app/session token and resolves the current user or anonymous session. |
| Secret getter | Reads `<SECRET_NAME>` and `ENTER_API_BASE_URL` server-side. |
| Agent allowlist | Accepts only reminder-configured custom-agent ids. |
| Thread storage | Maps project/user/session/conversation to `agent_id + thread_id + version`. |
| Proxy base URL | Lets the frontend target `/api/custom-agent/{agentId}` or a Supabase Function URL. |
| Message renderer slots | Lets the project-native surface replace user bubble, assistant text, thinking, tool action, question, and error UI. |
| Tool display registry | Maps tool names/action metadata to product-specific labels and icons. |
| i18n strings | Passes the host app locale into project-native renderers or the fallback template and optionally overrides labels/tool registry entries. |
| Markdown renderer | Renders assistant answers with GFM tables/lists/links/code instead of raw markdown text. |

## Thread ownership

A project should not let any user fetch any thread id. Store a mapping such as:

```text
project_id
user_id or anonymous_session_id
agent_id
thread_id
version
title
latest_history_turn_id
running_turn_id
created_at
updated_at
```

On every proxy request, verify the requested `agent_id + thread_id` belongs to the current user/session/project.

## Frontend runtime

Use the public SDK packages:

```ts
import { HttpAgent } from '@enter-pro/agent-client';
import {
  ThreadClient,
  ThreadManager,
  toThreadTurnsFromAgUiHistory,
} from '@enter-pro/thread-client';
```

The runtime hook should expose:

```ts
useCustomAgentChat({
  agentId,
  proxyBase,
  appToken,
  initialThreadId,
});
```

Return at least `turns`, `renderableMessages`, `isRunning`, `lifecycle`, `sendMessage`, `abort`, `activateThread`, and `loadMoreHistory`.

When integrating into an established project, project-native rendering is the default even when no explicit UI style is specified. Reuse existing message, panel, drawer, card, timeline, or workflow components where they fit, and add only the missing semantic sections needed for AG-UI state.

When the chosen strategy is `standalone/blank-chat`, copy and adapt `templates/builder-public-site-chat/` instead of re-generating the renderer from snippets. The fallback shell should remain transcript-first: a lightweight session list/new-session control is fine, but avoid a heavy dashboard header. If a custom UI style is specified, use the same renderable message semantics but adapt the visual components.

The fallback template includes a local i18n layer aligned with frontend `yf_agentbuilder_uifix`: supported locale metadata, alias normalization, preferred-locale resolution, localized labels, and `ar-SA` RTL direction. Generated project glue should pass the project i18n locale to both project-native renderers and, when used, `useCustomAgentChat` / `PublicSiteLikeChatShell`; do not replace labels with hard-coded Chinese or English strings when the project has i18n.

Session switching must not wait for remote thread/session metadata before updating the visible selection. Use cached `ThreadClient.turns` or cached history when possible, show an empty/loading transcript when not cached, and guard async activation with a monotonically increasing sequence so stale responses cannot override the latest selected session.

## Missing secret behavior

If `<SECRET_NAME>` is missing:

- Tell the user to open Workspace Settings > API keys.
- Tell them to create/copy an Enter API key.
- Request it through the secret-key tool under the exact `<SECRET_NAME>`.
- Do not ask for the API key in chat.

## Files in this case study

- `../../templates/builder-public-site-chat/`: portable Builder/Public Site-like React chat fallback for external, blank, scaffold, or explicitly standalone/default chat projects.
- `supabase-edge-function-proxy.md`: complete Supabase Edge Function proxy template.
- `default-builder-style-ui-contract.md`: default browser chat UI contract.
- `default-ui-anti-patterns.md`: default UI failure modes.
- `default-ui-acceptance-checklist.md`: static and screenshot acceptance checks.
- `react-chat-runtime.md`: React runtime pattern using the public SDK packages.
- `thread-persistence.md`: thread mapping and ownership model.


## Standalone / Blank Chat Fallback

For external browser chat, blank/scaffold projects, or user-requested standalone/default chat pages, the fallback implementation baseline is `templates/builder-public-site-chat/`, not a newly generated approximation. Copy the template into the project, then connect only the adapters:

- Project proxy base URL.
- App/session auth token getter.
- Thread/session persistence.
- Agent ID and allowlist configuration.
- Optional project-specific tool display registry entries.
- Optional renderer slots for user-requested custom UI.

The fallback copied UI must remain a Public Site-like adaptive transcript. The default style is `src/styles/public-site.css`: a light zinc-like page surface, soft logo-family background tint, floating desktop session card, informative empty hero, and compact composer card. The shell should keep the transcript as the main visual surface; session list and new-session controls are supporting UI. Do not convert the fallback into an all-black empty shell, heavy dashboard/demo layout, raw AG-UI event viewer, or oversized display transcript.

The copied template already handles startup/status, reasoning, tool calls/results, Markdown answers, cancel/error, question cards, hidden telemetry, i18n, and the compact Public Site typography/layout scale. Fallback projects should not rewrite `src/core/*`, replace the default message order, hard-code labels, or upscale message typography unless the user explicitly requests a different UI style.

The copied template also encodes two interaction details that should not be rewritten away: collapsible startup/thinking/tool headers use the public-site single-icon slot, and session navigation is optimistic/cached so New Session and rapid A -> B session clicks feel immediate.

For `project-native`, use the same semantic model and runtime behavior but let the host product's component system decide the visual treatment. A settings page may render the agent as a side panel; a workflow app may render it as an inline assistant; an existing chat app may add status/thinking/tool sections to its own message stream.
