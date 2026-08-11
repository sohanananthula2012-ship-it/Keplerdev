# Template Acceptance Checklist

Run this checklist before treating a generated project as a valid default Enter custom-agent browser UI.

- The project copied `templates/builder-public-site-chat/` instead of rebuilding a near-match renderer from scratch.
- The default shell uses `PublicSiteLikeChatShell` and `src/styles/public-site.css`; `public-site-dark.css` is used only for explicit dark-theme requests or backwards-compatible imports.
- The default page is not an all-black shell. It uses a light zinc-like surface, logo-family background tint, floating desktop session card, richer empty state, and compact composer chip.
- `src/core/*` aggregation is intact: startup/status, reasoning, tool calls/results, final assistant answer, error/cancel, and debug-only unsupported events all keep their semantic identity.
- The transcript order is user bubble -> startup/status group -> thinking/reasoning -> tool actions -> assistant answer.
- Startup/status is a collapsible group: `Agent getting ready` is expanded while preparing; `Agent ready` is collapsed after response/turn end. It is not a standalone line outside the group.
- Startup/thinking/tool headers use the public-site single-icon pattern: the closed state shows the status/action icon, hover/open shows the chevron. The default UI must not show a fixed `chevron + icon` pair.
- Default typography matches Public Site scale: assistant answer, thinking text, and user bubble use 14px font size with 22px line-height.
- Default layout matches Public Site scale: transcript and composer are capped at 800px, and user bubbles are capped at 568px with 8px 12px padding and 6px radius.
- Default desktop and mobile CSS do not use viewport-scaled oversized chat text such as `font-size: clamp(...)`, `2vw`, `28px`, or mobile-only 18px/19px overrides for transcript text.
- The assistant answer uses Markdown/GFM rendering. Tables render as tables; markdown table source is not displayed as plain text.
- I18n support is intact: `src/core/locales.ts` exports the frontend-aligned supported locale list, locale normalization, preferred-locale resolver, labels, and `localeTextDirection`.
- The default UI accepts `locale` through `useCustomAgentChat`, `PublicSiteLikeChatShell`, transcript, composer, and render helpers. Generated glue code passes the host app locale when available instead of hard-coding one language.
- `zh`, `zh-CN`, `en-US`, and at least one non-English/non-Chinese locale normalize correctly; `ar-SA` sets `dir="rtl"` on the shell.
- Tool actions use completed verbs after completion, for example `Searched websites`, not a permanent loading verb.
- `usage.update`, raw event JSON, startup metadata details, and unsupported telemetry do not appear in the main transcript.
- The project did not retheme the default into a heavy dashboard/demo shell or a heavy admin header.
- The project did not retheme the default into an all-black empty page, raw dark terminal shell, or full-screen decorative void.
- New Session is optimistic: the UI immediately selects a temporary empty session and replaces it with the real thread after create-thread succeeds.
- Existing session selection is optimistic/cached: the active row and transcript update before remote `get thread` / `fetch sessions` completes, and stale activation responses cannot overwrite the current session.
- The template contains no frontend private workspace aliases or app-internal absolute import aliases.
- No npm publish token, Enter API key, or real user token is committed or printed.
- Desktop and mobile screenshots show the transcript as the visual center, with no text overflow and visible thinking/tool/answer UI.


## AskUserQuestion And Live SSE Regression Checks

- A waiting AskUserQuestion card floats above the composer and is not rendered inline in the transcript.
- The tool area shows one AskUserQuestion action row with localized `Asking user` text and no raw JSON.
- Submitting an answer sends exactly one proxy request to `/tool-calls/{toolCallId}/answer`.
- After `agent.tool_action.resolved`, the floating card disappears, one answer summary appears, and no legacy `Question:` / `Answer:` text is visible.
- AskUserQuestion `TOOL_CALL_RESULT` does not create a duplicate answer summary or a second tool-action group.
- Duplicate startup events within one turn render one startup block only.
- After `agent.turn.summary` / `RUN_FINISHED`, the composer remains in send state, the active session is not marked running, and completed thinking/tool groups collapse.
- Refreshing after live completion produces the same transcript structure as the pre-refresh live transcript.
