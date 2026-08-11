# Builder/Public Site Chat Template

This template is the standalone/blank-chat fallback browser UI baseline for `enter_custom_agent_integration`. It is a copy-then-decouple port of the Builder test panel / public site agent transcript behavior from the frontend repo. External browser integrations, blank/scaffold Enter projects, and user-requested standalone/default chat pages should copy this folder, wire the project proxy/auth/session adapters, and keep the core renderer plus current Public Site visual baseline intact unless the user explicitly asks for a custom UI style.

For established Enter projects, inspect the host project first and prefer project-native integration that reuses existing routes, components, design tokens, auth, persistence, and i18n. Use this template as a semantic reference or fallback, not as a mandate to replace the product experience.

## Default Integration

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2 react-markdown@^10.1.0 remark-gfm@^4.0.0 lucide-react
```

```tsx
import {
  PublicSiteLikeChatShell,
  resolvePreferredBuilderPublicSiteLocale,
  useCustomAgentChat,
} from './builder-public-site-chat';
import './builder-public-site-chat/src/styles/public-site.css';

export function CustomAgentPage({ appToken }: { appToken: string }) {
  const locale = resolvePreferredBuilderPublicSiteLocale({
    explicitLocale: window.localStorage.getItem('app-locale'),
    fallbackLocale: 'zh-CN',
  });
  const chat = useCustomAgentChat({
    agentId: 'YOUR_AGENT_ID',
    proxyBase: '/api',
    appToken,
    locale,
  });

  return (
    <PublicSiteLikeChatShell
      messages={chat.viewMessages}
      locale={locale}
      agentProfile={{
        name: 'Translation Assistant',
        logo: 'https://grazia-prod.oss-ap-southeast-1.aliyuncs.com/resources/public/Green-sleep.svg',
        description: 'Translates source text into accurate, fluent English.',
        modelLabel: 'Custom Agent',
        toolsCount: 1,
      }}
      isRunning={chat.isRunning}
      onSend={chat.sendMessage}
      onAbort={chat.abort}
    />
  );
}
```

## What May Be Customized

- `agentId`, `proxyBase`, `appToken` getter, thread/session storage, and locale.
- `agentProfile` (`name`, `logo`, `description`, `modelLabel`, `toolsCount`, `skillsCount`) and `theme` (`light`, `dark`, or `system`).
- Session list data and `onNewSession` / `onSelectSession` handlers.
- Tool display registry entries for project-specific tools.
- Renderer slots for user-specified custom UI.
- Small brand tokens after the user asks for a custom visual style.

## I18n Baseline

The template ports the frontend `yf_agentbuilder_uifix` language policy without importing private frontend i18n packages.

- Supported locale codes: `en`, `zh-CN`, `de-DE`, `pt-BR`, `es-ES`, `fr-FR`, `id-ID`, `it-IT`, `ja-JP`, `ko-KR`, `ru-RU`, `ar-SA`, and `tr-TR`.
- Compatibility aliases are normalized, so `zh` becomes `zh-CN`, `en-US` becomes `en`, and `ja-JP` stays `ja-JP`.
- `PublicSiteLikeChatShell`, `BuilderPublicSiteTranscript`, `Composer`, `useCustomAgentChat`, and the render helpers all accept the same `locale` input.
- The shell sets `lang` and `dir`; `ar-SA` renders with `dir="rtl"`.
- Host projects with their own i18n should pass the resolved app locale into the template. Do not hard-code Chinese or English labels in generated project code.
- Tool labels can be customized through `ToolDisplayRegistry`; the built-in registry localizes common tool groups and falls back safely when a locale-specific tool verb is not available.

## Default Typography And Layout Baseline

The default template follows the Public Site scale from the frontend `yf_agentbuilder_uifix` branch. Treat these values as part of the default UI contract, not as placeholder demo styling:

- Assistant answer, user bubble, and thinking text: `14px` font size with `22px` line-height.
- User bubble: `max-width: 568px`, `padding: 8px 12px`, `border-radius: 6px`, `font-weight: 500`.
- Transcript and composer: `max-width: 800px`.
- Turn/message spacing: compact 12-16px rhythm.
- Mobile default keeps the same 14px/22px text scale; it should not increase chat text to 18px or 19px.
- Page shell: `src/styles/public-site.css` renders a light zinc-like page by default, maps known Builder logo files such as `Green-sleep.svg` to a soft family gradient, uses a floating session card on desktop, and collapses session chrome on mobile.
- Dark mode: pass `theme="dark"` or import `src/styles/public-site-dark.css` only when a dark fallback is explicitly desired.

Do not replace this baseline with viewport-scaled message text such as `clamp(..., 28px)` unless the user explicitly asks for a large-display or custom visual style.

## What Must Stay Intact For Default UI

- `src/core/*` message aggregation and tool/reasoning normalization.
- `src/ui/BuilderPublicSiteTranscript.tsx` message order: user bubble, startup/status group, thinking/reasoning, tool actions, assistant answer.
- `src/ui/CollapsibleSection.tsx` header behavior: one 24px icon slot, using the primary status/action icon while closed or loading and swapping to the chevron on hover/open. Do not render a permanent `chevron + icon + title` header.
- Final assistant answers as normal Markdown content, not an internal “answer done” card.
- `src/styles/public-site.css` adaptive Public Site baseline, including the Public Site typography, width scale, logo-family background tint, floating session card, richer empty state, and compact composer chip.
- `src/core/locales.ts` locale normalization, supported locale list, label functions, and RTL direction handling.
- Hidden-by-default telemetry/raw events such as `usage.update`.

Generated projects should not rewrite this into an all-black empty shell, a heavy dashboard, a debug event feed, or a generic demo shell. If the user explicitly requests a different visual style, keep the semantic UI slots and map them into that style.

## Session Responsiveness Contract

Session navigation must feel local-first. Do not block the visual selection, transcript clearing, or cached transcript display on a network fetch.

- On New Session, immediately show a temporary selected session and clear the transcript, then replace it with the real thread id after create-thread succeeds.
- On selecting an existing session, immediately highlight it and show cached `ThreadClient.turns` or cached history if available; otherwise show an empty/loading transcript while the fetch runs.
- The shell must never show session A's transcript while session B is highlighted. If the optimistic selected session id differs from the SDK's current thread id, pass an empty/loading message list until they match.
- Keep an activation sequence or request token so stale `get thread`, `resume`, or session-list refresh responses cannot overwrite the currently selected session.
- Refresh the session list in the background after activation/send. Do not `await fetchSessions()` before updating the selected session UI.
- `ThreadClient.subscribe` handlers should ignore updates for inactive thread ids.


## Live SSE And AskUserQuestion Behavior

This template includes the post-integration fixes proven in the standalone `custom-agent-chat` project:

- Live rendering is layered: reasoning messages own streaming/done state; turn status only controls turn context such as tool/startup closure.
- Startup events are a per-turn buffer and produce one startup/status block. Duplicate startup events update that block instead of adding another `Agent ready`.
- `AskUserQuestion` is parsed from tool-call args, shown as a normal tool action plus a floating question card above the composer, and resolved through the proxy answer endpoint.
- `agent.tool_action.resolved` produces one answer summary. AskUserQuestion `TOOL_CALL_RESULT` is internal continuation input and should not create a second answer UI.
- Live terminal signals stop stale running UI immediately; server thread snapshots remain the final authority for metadata and history.
