# Default UI Anti-Patterns

The following outputs are not acceptable as the default Enter custom-agent browser UI, even if they preserve some AG-UI semantics.

- A heavy dashboard or generic demo app that makes sidebars, headers, or status panels the visual center.
- An all-black empty shell where most of the first viewport is a dark void.
- A raw event/debug card feed as the main chat transcript.
- An outer `Agent run` card containing `startup done`, `thinking done`, `answer done`, and `usage.update` blocks.
- Final assistant answers wrapped inside an internal answer/status card instead of rendered as normal assistant Markdown content.
- Raw markdown table source rendered with `white-space: pre-wrap` instead of a GFM table renderer.
- Tool rows that keep loading verbs after completion, for example `Searching websites` after the tool result has arrived.
- Default UI tokens changed from the adaptive Public Site baseline to a pale back-office theme, raw dark terminal shell, or unrelated brand palette without an explicit user style request.
- Rewritten renderer logic that drops thinking, reasoning, tool actions, error, cancel, or question-card semantics.

If a user explicitly asks for a custom visual style, these anti-patterns still apply to semantics: do not leak debug telemetry or collapse all AG-UI into final text unless the user explicitly asks for plain-content-only output.
