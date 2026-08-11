# Upstream Mapping

This template is a portable extraction of Builder/Public Site agent transcript behavior. It does not import the frontend repo and does not carry private app dependencies.

## Frontend Source Baseline

Current typography/layout baseline is read from:

```text
/Users/mxiong/forrest/work/code/frontend
branch: yf_agentbuilder_uifix
```

- Renderable aggregation: `src/components/agent-builder/test-panel/components/agent-builder-renderable-messages.ts`
- View message contract: `src/components/agent-builder/types/agent-builder-view-message.ts`
- Test panel render switch: `src/components/agent-builder/test-panel/components/render-test-panel-message.tsx`
- Public site render switch: `src/public-site/render-public-site-message.tsx`
- Assistant markdown: `src/components/agent-builder/messages/agent-builder-assistant-message.tsx`
- Public site user bubble: `apps/enter-web/src/public-site/components/public-site-user-message/public-site-user-message.tsx`
- Public site shell/composer width: `apps/enter-web/src/public-site/components/public-site-chat-shell/public-site-chat-shell.tsx`
- Public site session card: `apps/enter-web/src/public-site/components/public-site-session-card/public-site-session-card.tsx`
- Public site logo-derived background: `apps/enter-web/src/lib/agent-builder-logo-presets.ts` and `packages/ui/src/styles/tokens/theme-extensions.css`
- Builder assistant message typography: `apps/enter-web/src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-assistant-message/agent-builder-assistant-message.tsx`
- Supported language policy: `packages/i18n/src/constants.ts` and `packages/i18n/src/language-policy.ts`
- Enter Web language switching behavior: `apps/enter-web/src/hooks/useLanguage.ts`
- Startup/status UI: `src/pages/workspace/:workspaceId/builder/:builderId/components/agent-builder-startup-message/agent-builder-startup-message.tsx`
- Thinking UI: `src/components/agent-builder/messages/agent-builder-thinking-message.tsx`
- Tool UI: `src/components/agent-builder/messages/agent-builder-tool-action-list.tsx`
- Thinking collapse behavior: `src/components/agent-builder/components/collapsibleThinkingGroup.tsx`
- Tool collapse behavior: `src/components/agent-builder/components/collapsibleActionGroup.tsx`
- Tool normalization: `src/components/agent-builder/messages/tool-call-display.ts`
- Tool registry: `src/components/agent-builder/messages/tool-registry.tsx`

## Portable Template Files

- `src/core/builderPublicSiteMessages.ts`: AG-UI/ThreadClient turn aggregation.
- `src/core/toolActionDisplay.ts`: visible tool action normalization.
- `src/core/toolRegistry.tsx`: local registry replacing frontend private icon/i18n imports.
- `src/core/locales.ts`: local supported locale metadata, normalization, labels, preferred-locale resolution, and RTL direction handling.
- `src/core/logoPresets.ts`: local logo filename to color-family mapping for portable Public Site backgrounds.
- `src/ui/BuilderPublicSiteTranscript.tsx`: render switch.
- `src/ui/AgentIdentity.tsx`: local avatar, profile name, and profile metadata helpers.
- `src/ui/SystemMessages.tsx`: startup/status group, errors, and cancel messages.
- `src/ui/ThinkingMessage.tsx`: collapsible thinking group.
- `src/ui/ToolActionList.tsx`: collapsible action group.
- `src/ui/AssistantMessage.tsx`: Markdown/GFM assistant answer.
- `src/styles/public-site.css`: default adaptive public-site-like baseline.
- `src/styles/public-site-dark.css`: opt-in dark compatibility theme.

## Refresh Workflow

When frontend behavior changes, diff the upstream files above, port only the agent transcript behavior, public-site visual baseline, logo family mapping, and language policy into the matching local file, and keep private imports out. Preserve the Public Site default scale unless the upstream product changes it: 14px/22px transcript text, 800px transcript/composer cap, and 568px user bubble cap. Preserve the light zinc-like default shell, logo-derived soft gradients, floating session card, supported locale normalization, and `ar-SA` RTL behavior. Run the acceptance checklist before updating the skill package.


## Custom-agent-chat live integration fixes

This template has absorbed the live integration fixes proven in the standalone `custom-agent-chat` prototype.

- AskUserQuestion floating card, answer body builder, answer summary, and `agent.tool_action.resolved` de-duplication.
- Layered live SSE rendering: reasoning state is message-local; terminal events stop stale running UI; waiting-for-user maps to active only while a waiting question card exists.
- Per-turn startup buffer merging to prevent duplicate `Agent ready` blocks.
- Core and browser regression scripts covering waiting questions, resolved answers, duplicate startup, terminal convergence, and completed collapsible groups.
