# Frontend Event Rendering Examples

These snippets show how to wire a frontend runtime and convert thread messages into UI messages. They are intentionally small; full architecture is in `case-studies/enter-project/`.

Files:

- `thread-client-runtime.md`: `HttpAgent + ThreadClient + ThreadManager` runtime skeleton using `@enter-pro/*`.
- `event-to-message-rendering.md`: two-layer conversion from `ThreadClient.turns` into semantic messages and the fallback Builder-style view model.
- `tool-action-normalization.md`: turns assistant tool calls/results into localized, state-consistent action rows.
- `default-builder-style-react.md`: fallback baseline React transcript components for the Builder/Public Site-like UI, including Markdown/GFM answer rendering.
- `default-builder-style-css.md`: CSS for the fallback transcript layout.

Use the public runtime packages for browser chat UI:

```bash
npm install @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
```

For browser chat UI, install a Markdown/GFM renderer unless the host project already has one:

```bash
npm install react-markdown@^10.1.0 remark-gfm@^4.0.0
```

For established Enter projects, keep the semantic conversion layer and render it through project-native components. Use the Builder-style React/CSS templates only for external, blank/scaffold, or explicitly standalone/default chat UI.

Raw SSE parsing is appropriate for CLIs and backend services, but normal project browser UI should render from `ThreadClient.turns`. The main chat transcript should not be a raw event inspector unless the user explicitly asked for debug UI.
