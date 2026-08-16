# Default Builder-style CSS

For a standalone/blank-chat fallback, copy the full template and import its default stylesheet instead of recreating the visual shell from snippets:

```tsx
import './builder-public-site-chat/src/styles/public-site.css';
```

That stylesheet is the portable Public Site baseline:

- Light zinc-like page surface by default.
- Soft background tint derived from known Builder logo file names such as `Green-sleep.svg`.
- Floating session card on desktop and compact session chrome on mobile.
- Rich empty state using `agentProfile` name, logo, description, model, tools, and skills.
- Compact composer card with an agent chip.
- 14px/22px assistant, thinking, and user text.
- 800px transcript/composer cap and 568px user bubble cap.

Use `public-site-dark.css` only when the user explicitly asks for a dark fallback or when maintaining a project that already imports the legacy dark entry.

Do not paste a separate dark demo CSS block into generated projects. It tends to drift from the template, reintroduce all-black shells, and lose the Public Site typography/layout contract.
