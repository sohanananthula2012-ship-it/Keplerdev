# Implementation Source Map

These are the source files used to derive this skill. Read them when the contract changes.

## Backend: system reminder and project integration

Repository:

```text
/Users/mxiong/forrest/work/code/enter_backend.feature-20260609-agent_builder_merge_into_project_1
```

Files:

- `internal/features/chattask/custom_agent_integration.go`

Facts:

- Parses `<custom_agent id="" logo="">name</custom_agent>` from the user prompt.
- Validates agent id with `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`.
- Sanitizes logo to http/https URLs only.
- Finds latest published custom agent.
- Verifies agent workspace matches the project workspace.
- Upserts a `custom_agent_project_integration` record.
- Injects a `<system_reminder>` instructing the coding agent to use this skill.
- Reminder includes `id`, `name`, `logo`, `api_base_url`, and `enter_api_key_secret_name`.
- Multiple mentions are emitted as `custom_agents:`.
- Reminder tells the coding agent to preserve current project architecture/UI, inspect existing routes/components/auth/persistence/i18n/chat surfaces, and use the Builder/Public Site chat template only for blank/scaffold or explicitly standalone/default chat UI.
- Missing secret guidance says to use Workspace Settings > API keys and the secret-key tool, not normal chat.

## Backend: serving API

Files:

- `internal/http/handlers/agent/serving.go`
- `internal/http/handlers/agent/handler.go`

Facts:

- Serving JSON responses are flat JSON via `writeJSON`.
- Errors are `{ "error_code": "...", "message": "..." }`.
- `POST /agents/{agent_id}/threads` creates a thread; empty body selects latest published version.
- `POST /agents/{agent_id}/run` accepts an AG-UI `RunAgentInput` subset and streams SSE.
- `threadId` is required.
- Non-empty `tools` is rejected as `SERVING_TOOLS_NOT_SUPPORTED`.
- `forwardedProps.model_id` is rejected as `SERVING_MODEL_OVERRIDE_NOT_SUPPORTED`.
- `state`, `context`, and `runId` are accepted for envelope compatibility but ignored in v1.
- `messages` are scanned for the first user message.
- Turn history requires both `start_turn` and `end_turn` positive integers.
- Cancel and resume/read events use thread and turn ids.

## Backend: SDK examples

Files:

- `internal/features/agentbuilder/code_examples.go`

Facts:

- Official example shapes include TypeScript AG-UI SDK, Python raw SSE, Go AG-UI SDK, and cURL.
- Source examples may contain local fixed agent ids. Do not copy them into this skill; use placeholders.

## Frontend: Enter Web serving runtime

Repository:

```text
/Users/mxiong/forrest/work/code/frontend.feature-20260609-agent_builder_merge_into_project_1/apps/enter-web
```

Files:

- `src/service/codeApi.ts`
- `src/pages/workspace/:workspaceId/builder/:builderId/hooks/use-agent-builder-test.ts`
- `src/pages/workspace/:workspaceId/builder/:builderId/lib/serving-history-message-loader.ts`
- `src/pages/workspace/:workspaceId/builder/:builderId/lib/map-serving-turn-to-ag-ui-history.ts`
- `src/pages/workspace/:workspaceId/builder/:builderId/lib/agent-builder-renderable-messages.ts`
- `src/public-site/hooks/use-public-site-chat.ts`

Facts:

- `createAgentServingThread` calls `POST /agents/{agent_id}/threads`.
- `HttpAgent` is configured with `threadId`, run URL, token getter, cancel URL, and resume URL.
- `ThreadClient` owns turns, running state, lifecycle, history loading, and subscriptions.
- `ThreadManager` registers and activates one client per thread key.
- `ServingHistoryMessageLoader` loads `/turns` and converts to AG-UI history.
- `toRenderableMessages` maps thread messages/custom events to UI messages.
- Public-site chat uses the same runtime shape but a per-thread token instead of Auth0 token.

## Frontend: Builder/Public Site default UI behavior

Repository:

```text
/Users/mxiong/forrest/work/code/frontend.feature-20260609-agent_builder_merge_into_project_1
```

Current typography/layout reference:

```text
/Users/mxiong/forrest/work/code/frontend
branch: yf_agentbuilder_uifix
```

Renderable aggregation:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/lib/agent-builder-renderable-messages.ts`

Render switches:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/render-test-panel-message.tsx`
- `apps/enter-web/src/public-site/lib/render-public-site-message.tsx`

Thinking UI:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/agent-builder-thinking-message.tsx`
- `packages/ui/src/components/chat/action/enter/collapsibleThinkingGroup.tsx`
- `packages/ui/src/components/chat/action/enter/thinkingGroupHeader.tsx`

Tool UI:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/agent-builder-tool-action-list/agent-builder-tool-action-list.tsx`
- `packages/ui/src/components/chat/action/enter/collapsibleActionGroup.tsx`

Tool normalization:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/agent-builder-tool-action-list/tool-call-display.ts`
- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/agent-builder-tool-action-list/tool-registry.tsx`

Typography and layout sources from `yf_agentbuilder_uifix`:

- `apps/enter-web/src/public-site/components/public-site-user-message/public-site-user-message.tsx`
- `apps/enter-web/src/public-site/components/public-site-chat-shell/public-site-chat-shell.tsx`
- `apps/enter-web/src/public-site/components/public-site-message-list/public-site-message-list.tsx`
- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-assistant-message/agent-builder-assistant-message.tsx`
- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/test-panel-turn-wrapper.tsx`

I18n sources from `yf_agentbuilder_uifix`:

- `packages/i18n/src/constants.ts`
- `packages/i18n/src/language-policy.ts`
- `apps/enter-web/src/hooks/useLanguage.ts`

Facts:

- Builder and public-site render final assistant text as ordinary assistant content, not as an internal answer/debug card.
- Assistant answers are rendered through a Markdown/streaming Markdown component; GFM tables should be formatted, not shown as raw markdown.
- Public-site/test-panel renderers are message switches over renderable view messages, not raw event cards.
- Startup custom events are summarized into the compact `agent-startup` collapsible group: a getting-ready label while preparing, then collapsed to a ready label after response/turn end.
- Reasoning is preserved and rendered as a collapsible thinking group with a header and vertical divider.
- Tool calls/results are grouped into an action list with icons, state-consistent verbs, and concise targets.
- Startup/thinking/tool group headers use a single 24px icon slot. Closed/completed state shows the status/action icon; hover or expanded state swaps to the chevron. The default UI should not render a permanent chevron next to a permanent icon.
- Telemetry such as `usage.update` and raw event payloads are not part of the normal chat transcript.
- Session/navigation chrome is secondary to the transcript in the default user-facing experience.
- Current public-site page styling is light by default, with logo-family background tints, a floating session card, centered transcript/composer, and a compact composer surface. The portable fallback template should not default to an all-black empty shell.
- Session switching is local-first in generated projects: update active selection immediately, display cached turns/history before remote fetch completes, show empty/loading instead of stale messages when optimistic selection and current SDK thread differ, refresh session metadata in the background, and ignore stale activation/resume responses for inactive thread ids.
- Public Site typography uses compact chat text, not large display text: user bubble and assistant answer text are 14px with 22px line-height; user bubble max width is 568px with 8px 12px padding and 6px radius; public-site composer and message area are capped at 800px.
- The portable standalone/blank-chat fallback template must not reintroduce viewport-scaled transcript text such as `clamp(..., 28px)` or mobile-only 18px/19px chat text unless the user explicitly asks for a custom large-display style.
- Frontend supported locales are `en`, `zh-CN`, `de-DE`, `pt-BR`, `es-ES`, `fr-FR`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `ru-RU`, `ar-SA`, and `tr-TR`. The portable template keeps a local copy of the normalization policy and does not import private frontend i18n packages.
- Locale matching follows exact match, case-insensitive match, then prefix fallback. `zh` maps to `zh-CN`; `en-US` maps to `en`; `ar-SA` sets RTL direction on the shell.


## Portable template: Builder/Public Site chat

Skill asset:

```text
templates/builder-public-site-chat/
```

Facts:

- This template is the fallback implementation path for external browser chat, blank/scaffold Enter projects, or user-requested standalone/default custom-agent chat.
- Established Enter projects should first use project-native integration. Copy/adapt this template only when the chosen strategy is standalone/blank-chat, or use it as a semantic reference while rendering through project-local components.
- The template intentionally removes private frontend imports and replaces them with local components, local CSS, local locale strings, and public dependencies.
- The template exposes `useCustomAgentChat`, `CustomAgentChatShell`, `CustomAgentTranscript`, `toEnterRenderableMessages`, `DefaultBuilderStyleMessageRenderer`, and renderer slots.
- The template runtime caches per-thread history, guards activation with a request sequence, ignores inactive-thread subscriptions, and supports optimistic New Session/select-session shells.
- The template i18n layer exposes supported locale metadata, `resolveBuilderPublicSiteLocale`, `resolvePreferredBuilderPublicSiteLocale`, `localeLabels`, and `localeTextDirection` so host projects can pass their own product locale without private frontend dependencies.
- Refresh this template when the upstream Builder/Public Site renderable aggregation, thinking group, tool action list, or assistant Markdown behavior changes.

## When to update this skill

Update the skill when any of these change:

- Serving endpoint paths or auth rules.
- Run body accepted/rejected fields.
- Error codes.
- AG-UI event names used by frontend renderers.
- Thread history response shape.
- Project integration reminder fields.
- Secret acquisition flow.


## Builder/Public Site Portable Template Mapping

The source skill package ships `templates/builder-public-site-chat/` as the standalone/blank-chat fallback baseline. This template is a copy-then-decouple port of frontend behavior, not an import of frontend private code.

| Frontend source | Portable template target | Purpose |
| --- | --- | --- |
| `src/components/agent-builder/test-panel/components/agent-builder-renderable-messages.ts` | `templates/builder-public-site-chat/src/core/builderPublicSiteMessages.ts` | AG-UI/ThreadClient turns to view messages |
| `src/components/agent-builder/types/agent-builder-view-message.ts` | `templates/builder-public-site-chat/src/core/types.ts` | Portable view-message contract |
| `src/components/agent-builder/test-panel/components/render-test-panel-message.tsx` | `templates/builder-public-site-chat/src/ui/BuilderPublicSiteTranscript.tsx` | Render switch |
| `src/public-site/render-public-site-message.tsx` | `templates/builder-public-site-chat/src/ui/BuilderPublicSiteTranscript.tsx` and `PublicSiteLikeChatShell.tsx` | Public-site-like default transcript |
| `src/components/agent-builder/messages/agent-builder-thinking-message.tsx` | `templates/builder-public-site-chat/src/ui/ThinkingMessage.tsx` | Thinking/reasoning group |
| `src/components/agent-builder/components/collapsibleThinkingGroup.tsx` | `templates/builder-public-site-chat/src/ui/CollapsibleSection.tsx` | Collapsible behavior |
| `src/components/agent-builder/messages/agent-builder-tool-action-list.tsx` | `templates/builder-public-site-chat/src/ui/ToolActionList.tsx` | Tool action group |
| `src/components/agent-builder/components/collapsibleActionGroup.tsx` | `templates/builder-public-site-chat/src/ui/CollapsibleSection.tsx` | Tool collapse behavior |
| `src/components/agent-builder/messages/tool-call-display.ts` | `templates/builder-public-site-chat/src/core/toolActionDisplay.ts` | Tool action normalization |
| `src/components/agent-builder/messages/tool-registry.tsx` | `templates/builder-public-site-chat/src/core/toolRegistry.tsx` | Local portable tool registry |
| `src/components/agent-builder/messages/agent-builder-assistant-message.tsx` | `templates/builder-public-site-chat/src/ui/AssistantMessage.tsx` and `MarkdownContent.tsx` | Markdown/GFM final answer |
| `apps/enter-web/src/lib/agent-builder-logo-presets.ts` | `templates/builder-public-site-chat/src/core/logoPresets.ts` | Logo URL/file-name to background family mapping |
| `apps/enter-web/src/public-site/components/public-site-session-card/public-site-session-card.tsx` | `templates/builder-public-site-chat/src/ui/PublicSiteLikeChatShell.tsx` and `AgentIdentity.tsx` | Floating session card, agent profile, and avatar treatment |
| `packages/ui/src/styles/tokens/theme-extensions.css` | `templates/builder-public-site-chat/src/styles/public-site.css` | Portable public-site visual baseline and logo-family gradients |

Refresh rule: diff upstream frontend files, port behavior into the matching template file, keep private frontend imports out, and rerun `default-ui-acceptance-checklist.md`.
