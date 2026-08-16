# Default Builder-style UI Contract

Use this contract for standalone/blank-chat fallback UI, or as a semantic reference for project-native Enter project integrations. It is based on the Builder test panel and public-site chat experience, but generated projects must implement it with project-local components and the public `@enter-pro/*` SDK packages. Do not import private frontend repo components into generated projects.

This is a baseline implementation contract, not loose visual inspiration, for fallback standalone/default chat pages. A fallback chat page that preserves AG-UI semantics but looks like a generic admin dashboard is not done. In established Enter projects, preserve the semantic sections while matching the host product's existing UI instead of forcing the Public Site visual shell.

If the user specifies a custom UI style, keep the same semantic sections and adapt the visuals. If the user explicitly asks for plain content only, it is acceptable to show only the final assistant answer.

## Default experience

The visible UI should feel like an agent transcript with lightweight session navigation:

```text
Lightweight session sidebar with New Session
  +
Transcript-first chat area:
  User message bubble
  Agent startup/status collapsible group
  Thinking/reasoning collapsible group
  Tool action collapsible group
  Assistant answer as Markdown-rendered body text
  Error/cancel surface when needed
  Composer
```

Session list, header controls, and config panels may exist, but they must not dominate the first viewport. Avoid heavy `THREAD` page headers, large dashboard cards, or admin-console chrome in the default UI.

The default visual shell should follow the current Public Site treatment: a light zinc-like page surface, a soft gradient derived from known Builder logo families, a floating desktop session card, an informative empty hero, and a compact composer card. Use `src/styles/public-site.css` for this baseline. `src/styles/public-site-dark.css` is opt-in only for explicit dark-theme requests or backwards-compatible imports; an all-black empty page is not an acceptable default.

## Typography and layout baseline

Default UI must use the Public Site transcript scale from the frontend `yf_agentbuilder_uifix` branch:

- Assistant answer, user bubble, and thinking text use 14px font size with 22px line-height.
- User bubble is capped at 568px with 8px 12px padding, 6px radius, and medium text weight.
- Transcript and composer are capped at 800px.
- Message rhythm is compact: turn/message gaps should stay around 12-16px.
- Mobile keeps normal transcript text at 14px/22px; do not add mobile-only 18px or 19px overrides for chat text.

Do not use viewport-scaled large text such as `font-size: clamp(..., 28px)` for the default transcript. Large-display typography is a custom visual style and requires an explicit user request.

## Required semantic sections

| Section | Default behavior |
| --- | --- |
| `agent-startup` / status | A compact collapsible group. While the startup phase is still preparing, show `Agent getting ready` and keep its startup steps expanded. Once the agent has responded or the turn ended, collapse it to `Agent ready`. Do not render this as a separate standalone line outside the collapsible group. |
| `thinking/reasoning` | A collapsible group with `Thinking...` while streaming and `Thought for N seconds` when complete. Show only real reasoning content under a vertical divider. |
| `tool-action-list` | A collapsible group with `N actions in progress` or `N actions completed`. Each action row shows icon, verb, and target. |
| `assistant-answer` | Render final assistant text as an ordinary assistant message body using Markdown/GFM. Do not add a decorative bot/avatar icon. |
| `error/cancel` | Render a concise user-facing error or cancellation state. |
| `debug/raw-events` | Optional drawer/panel only. Keep it off by default. |

## Markdown answer requirement

Assistant answers must use a Markdown renderer that supports GitHub Flavored Markdown:

- Tables
- Ordered and unordered lists
- Links
- Inline and fenced code
- Headings and emphasis

For React projects, prefer:

```bash
npm install react-markdown@^10.1.0 remark-gfm@^4.0.0
```

Do not render assistant answers with `white-space: pre-wrap` alone. A visible table like `| Item | Detail |` is a failed default UI even if the data is correct.

## Locale behavior

Default UI labels follow the locale of the app being built, which is independent of the language you reply in, unless the project already has an i18n system. The portable template must keep the frontend-style language policy local to the template and must not import private frontend i18n packages.

Required locale behavior:

- Accept a host-provided `locale` prop in the runtime hook, shell, transcript, composer, and render helpers.
- Normalize supported inputs using the frontend policy shape: exact match, case-insensitive match, then prefix fallback.
- Support the same public locale codes as frontend `yf_agentbuilder_uifix`: `en`, `zh-CN`, `de-DE`, `pt-BR`, `es-ES`, `fr-FR`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `ru-RU`, `ar-SA`, and `tr-TR`.
- Preserve the compatibility alias `zh -> zh-CN`.
- Set `lang` on the shell, and set `dir="rtl"` for `ar-SA`.
- Let host projects pass their own resolved product locale. Do not hard-code labels for a single language in generated project glue code when a project i18n locale exists.

The template locale layer (`src/core/locales.ts`) owns the translations for every label named in this contract: `Agent ready`, `Agent getting ready`, `Thinking...`, `Thought for N seconds`, `N actions in progress`, `N actions completed`, `Searched websites`, and `Activated skill`. Read labels from that layer rather than writing literals into components.

If the user prompt is in a language other than English and no product language is specified, generate default labels by passing the matching supported locale code. If a product language is specified, that product language wins.

## Thinking UI details

Default thinking UI:

- Header uses the same single 24px icon slot as the public site: show the activity/status icon while closed or loading, and swap that icon to the chevron on hover/open. Do not render a permanent `chevron + icon + title` header.
- Loading title is `Thinking...`.
- Finished title is `Thought for N seconds`.
- Content appears below the header with a slim vertical divider.
- While running, the group can be expanded automatically. After completion, collapse by default if the transcript needs to stay compact.
- If no real reasoning content was emitted, do not invent filler text. It is acceptable to omit the finished thinking body, or show only a running indicator while the turn is active.

## Tool action UI details

Group assistant tool calls and matching tool results into a single action group.

Each visible action row should contain:

- An icon derived from the tool kind.
- A loading or completed verb consistent with the action status.
- A short target/description extracted from tool args.

Examples:

```text
Searched websites 2026 FIFA World Cup dates host cities
Activated skill enter-feishu-im-connection
Ran npm test
Read src/App.tsx
Edited package.json
```

If the group title says the action is completed, the row must use the completed verb. Do not show `Searching websites` under an `actions completed` group.

Unknown tools should still render as a generic action row, not raw JSON. Tool result previews and raw args belong in a debug drawer, not the default transcript.

## Session responsiveness details

Default browser projects with a session list must keep session navigation out of the network critical path:

- New Session immediately creates a temporary selected item and clears the transcript before the create-thread request completes.
- Selecting a session immediately updates the active row and shows cached turns/history if available.
- Never show session A's transcript while session B is highlighted. If the optimistic selected id and SDK current thread id are temporarily different, render an empty/loading transcript instead of stale messages.
- Slow `get thread`, `resume`, or session-list refresh responses must be guarded by an activation sequence/request token so they cannot overwrite a newer selected session.
- Session list metadata refreshes in the background after activation or send. It should not block the selected row, transcript switch, or composer availability.
- `ThreadClient.subscribe` updates for inactive thread ids must be ignored by the active transcript state.

## Default hidden events

These events should not appear as visible main transcript cards:

- Telemetry and usage events such as `usage.update`.
- Turn metadata such as `agent.turn.summary`.
- Raw startup metadata after it has been summarized into the `agent-startup` collapsible group.
- Raw tool payload JSON after it has been summarized into `tool-action-list`.
- Unsupported custom events, unless the app provides an explicit debug view.

Keep raw events in memory or persisted history when useful. The rule is about default user-facing presentation, not data loss.

## Source references

Use these files as behavioral references only. Do not copy private imports into generated projects:

- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/lib/agent-builder-renderable-messages.ts`
- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-detail/test-panel/views/chat-view/components/message/render-test-panel-message.tsx`
- `apps/enter-web/src/public-site/lib/render-public-site-message.tsx`
- `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-assistant-message/agent-builder-assistant-message.tsx`
- `packages/ui/src/components/chat/action/enter/collapsibleThinkingGroup.tsx`
- `packages/ui/src/components/chat/action/enter/collapsibleActionGroup.tsx`
