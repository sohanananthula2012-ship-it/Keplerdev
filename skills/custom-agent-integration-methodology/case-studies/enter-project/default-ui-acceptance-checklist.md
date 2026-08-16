# Standalone / Blank Chat Fallback Acceptance Checklist

Use this checklist when the chosen strategy is `standalone/blank-chat`, or when the user explicitly requested the Builder/Public Site default chat UI. For `project-native`, use the semantic checks here without forcing the fallback visual shell.

Run this checklist before presenting an Enter project browser chat integration as complete when the user did not specify a custom UI style.

## Static checks

- Browser UI installs `@enter-pro/agent-client@0.0.2` and `@enter-pro/thread-client@0.0.2`.
- Assistant answers use a Markdown/GFM renderer, such as `react-markdown + remark-gfm`.
- The default transcript renderer does not include raw event/debug cards, telemetry JSON, `startup done` cards, or `answer done` cards.
- The default assistant answer component does not render a decorative bot/avatar icon before every answer.
- Tool action rows use normalized action views, not raw tool-call JSON.
- UI strings are localizable and default to the locale of the app being built, which is independent of the language you reply in. The template must preserve `src/core/locales.ts` with supported locales, normalization, preferred-locale resolution, labels, and RTL direction handling.
- Generated project glue passes the host app locale into `useCustomAgentChat` and `PublicSiteLikeChatShell` when a product i18n locale exists. It should not hard-code `zh-CN` or `en` unless the project has no locale source and the prompt language requires that default.
- Locale normalization handles `zh -> zh-CN`, `en-US -> en`, case-insensitive matches, prefix fallbacks, and `ar-SA` shell `dir="rtl"`.
- Default transcript CSS uses the Public Site scale: 14px/22px assistant, user, and thinking text; 800px transcript/composer cap; 568px user bubble cap.
- Default shell CSS uses the current Public Site visual baseline: `public-site.css`, light zinc-like surface, logo-family gradient, floating desktop session card, richer empty state, and compact composer chip. `public-site-dark.css` is opt-in only.
- Default desktop/mobile CSS does not use oversized viewport-scaled chat text such as `font-size: clamp(...)`, `2vw`, `28px`, or mobile-only 18px/19px transcript text.
- Default desktop/mobile CSS does not hard-code an all-black page background as the default shell.

## Golden scenario

Use a prompt like:

```text
When does the 2026 World Cup start, and where is it being held?
```

Expected visible transcript:

- User bubble on the right.
- Collapsed `Agent ready` startup/status group after the agent responds, and expanded `Agent getting ready` while startup is still preparing.
- Startup/thinking/tool group headers follow the public-site single-icon interaction: closed state shows the status/action icon, hover/open shows the chevron; do not render a fixed `chevron + icon` pair.
- `Thought for N seconds` group when reasoning exists, with real reasoning content under a vertical divider.
- `1 action completed` group when one search/tool action happened.
- Tool row such as `Searched websites 2026 FIFA World Cup dates host cities`.
- Assistant answer rendered as Markdown: tables, lists, links, headings, and code blocks should be formatted, not shown as raw markdown source.
- Public Site-like text scale: normal answer, thinking text, and user bubble look like compact chat transcript text, not large dashboard or hero text.
- Locale labels follow the selected locale consistently. Labels from one locale must not be mixed into another.

Not acceptable by default:

- Heavy dashboard page header such as `THREAD` dominating the viewport.
- All-black empty shell where the first viewport is mostly a dark void.
- Raw markdown table pipes in the assistant answer.
- `Searching websites` under a completed action group.
- Decorative assistant bot/avatar icon before the answer.
- Telemetry or raw event cards in the transcript.

## Browser screenshot check

When the project has a local dev server:

1. Start the dev server.
2. Capture a desktop screenshot around 1280x900.
3. Capture a mobile/narrow screenshot around 390x844.
4. Inspect that the transcript or empty hero is the visual center, text does not overflow, the composer is reachable, and sidebar/header elements do not dominate.
5. Confirm normal transcript text is around the Public Site scale: 14px/22px for assistant, thinking, and user bubble text; transcript/composer no wider than 800px; user bubble no wider than 568px.
6. Confirm the page is not visually all-black by default; known Builder logos such as `Green-sleep.svg` produce a soft family tint rather than a black void.
7. Confirm thinking/tool groups are visible or collapsible as appropriate, and assistant Markdown is readable.

If a screenshot fails these checks, fix the generated UI before claiming the integration is complete.

## Template reuse gate

- Standalone/blank-chat fallback UI copied or faithfully adapted `templates/builder-public-site-chat/` instead of hand-writing a new approximate renderer.
- Project-specific changes are isolated to proxy/auth/session adapters, locale, visual tokens, and renderer slots.
- No private frontend repo import paths remain in generated code.

## Session performance gate

- Clicking New Session immediately selects an empty temporary session and does not wait for the create-thread request before updating the UI.
- Clicking session A then session B rapidly leaves session B selected; late responses from session A must be ignored.
- The highlighted session and transcript cannot disagree. During optimistic activation, show an empty/loading transcript instead of stale messages from the previous session.
- Existing sessions show cached turns or cached history immediately when available. If there is no cache, show an empty/loading transcript while fetching rather than blocking the click.
- Refresh session list metadata in the background after activation/send. Do not make `fetchSessions()` part of the critical path for row selection or transcript switching.
