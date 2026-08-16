# Default UI Anti-patterns

Use this document to reject standalone/blank-chat fallback implementations that are protocol-correct but not Builder/Public Site-like. These are failures for the fallback template path unless the user explicitly asked for a different style or a debug/event inspector.

For established Enter projects, do not use this document to force a Public Site look. Use it as a semantic safety check: project-native UI should still preserve readable assistant answers, real thinking/reasoning, tool actions, localized labels, hidden telemetry, and stable session behavior while matching the host product.

## Generic dashboard shell

Symptoms:

- The first viewport is dominated by a large page header, status pill, toolbar, or admin-console chrome.
- The transcript feels like content inside a dashboard rather than the main product surface.
- The session list is visually heavier than the conversation.

Fallback fix:

- Keep the session sidebar lightweight.
- Make the transcript and composer the primary visual surface.
- Avoid large labels such as `THREAD`, oversized titles, or heavy top bars unless the user asked for an operational dashboard.

## Raw Markdown answer

Symptoms:

- Assistant answers show table pipes such as `| Item | Detail |`.
- Lists, links, headings, and code blocks render as plain text.
- The assistant answer container uses only `white-space: pre-wrap`.

Fallback/project-native fix:

- Use a Markdown/GFM renderer such as `react-markdown + remark-gfm`.
- Add table/list/code CSS for readable assistant answers.
- Keep `pre-wrap` only for reasoning text, not for final assistant answers.

## Missing or fake thinking

Symptoms:

- Reasoning emitted by AG-UI is ignored.
- Finished turns show no thinking section even when reasoning exists.
- The UI invents filler text such as "The agent is working through the request" after the turn completes.

Fallback/project-native fix:

- Recognize reasoning messages across SDK/AG-UI shapes.
- Show real reasoning content in a thinking group.
- While running, a loading thinking label is allowed; after completion, do not invent reasoning content.

## Inconsistent tool status

Symptoms:

- The group title says `1 action completed`, but the row says `Searching websites`.
- Tool rows display raw args, result JSON, or long result previews.
- Action count is based on raw messages rather than normalized tool calls.

Fallback/project-native fix:

- Normalize tool calls/results into action rows.
- Force completed row verbs when the group/turn is complete.
- Keep raw args and result previews in an optional debug panel only.

## Wrong default language

Symptoms:

- User prompt is Chinese, but default UI labels are English.
- Mixed-language labels appear in one transcript, such as `Agent ready` with Chinese answers.

Fallback/project-native fix:

- Infer locale from the user request or project i18n.
- Resolve the status and tool-verb labels for the built app's locale (not for the language you reply in, and not because a sample here uses some language) through the locale layer.

## Decorative assistant avatar

Symptoms:

- Every assistant answer starts with a bot/avatar icon.
- The icon makes the answer look like a generic chat widget rather than Builder/Public Site answer content.

Fallback/project-native fix:

- Render assistant answers as normal body content without a decorative assistant icon.
- Keep icons for status, thinking, and tool action rows where they communicate process state.

## Debug UI in the main transcript

Symptoms:

- `usage.update`, `agent.turn.summary`, raw event JSON, or unsupported event cards appear in the normal chat flow.

Fallback/project-native fix:

- Keep telemetry/raw events in state for debugging.
- Expose them only through an optional debug drawer/panel, off by default.

## Oversized transcript typography

Symptoms:

- Assistant answers, thinking text, or user bubbles use viewport-scaled large text such as `clamp(..., 28px)`.
- Desktop chat text feels like a marketing hero or presentation surface instead of the Public Site transcript.
- Mobile CSS increases normal transcript text to 18px or 19px by default.
- User bubbles are much wider than the Public Site cap or use large rounded-card padding.

Fallback fix:

- Use the Public Site baseline: 14px font size with 22px line-height for assistant answer, thinking text, and user bubble.
- Cap transcript and composer width at 800px.
- Cap user bubbles at 568px with 8px 12px padding and 6px radius.
- Only introduce large-display typography when the user explicitly asks for a custom visual style.

## Hand-written near-copy fallback renderer

When the chosen strategy is `standalone/blank-chat`, do not hand-write a fresh chat renderer that only approximates Builder/Public Site behavior. Copy `templates/builder-public-site-chat/` and adapt the project edges. Hand-written near-copy renderers routinely lose Markdown tables, completed tool verbs, Chinese labels, transcript visual hierarchy, or telemetry hiding.

When the chosen strategy is `project-native`, the anti-pattern is the opposite: do not copy the fallback template into an established product surface when the project already has suitable routes, components, design tokens, and interaction patterns.
