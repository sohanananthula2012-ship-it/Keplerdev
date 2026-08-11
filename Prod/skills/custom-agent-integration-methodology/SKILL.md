---
name: Custom Agent Integration Methodology
description: Use when the user wants to integrate a published Enter custom agent (built in Enter Builder) into THIS project, asks how to connect their custom agent, or wants an in-app assistant/support surface backed by their custom agent. Covers both states — no agent attached yet (collect agent id, api_base_url, and a server-side key) and an agent already attached via a system reminder (trust the injected fields). Contains BOTH complete UI paths baked in as real files, not just descriptions — project-native components in ui-build-guide.md and the full default/standalone Builder-style chat UI in default-ui-template/ — plus the secure proxy and persistence layer.
---

# Custom Agent Integration Methodology

This skill contains everything needed to connect a published Enter custom agent to this project: the secure backend proxy, the database table that remembers conversations, and **two complete, ready-to-use UI options**, both already written out as real files in this skill folder:

| Path | Where the code lives | Use it when |
| --- | --- | --- |
| **A — Project-native UI** | `ui-build-guide.md` (in this same skill folder) | This project already has pages/panels the agent can live inside (default choice). |
| **B — Default/standalone chat UI** | `default-ui-template/` (a full folder in this same skill, ready to copy) | The project is blank/new, or the user asks for a normal ready-made chat page. |
| **C — Backend only** | Steps A + B of `ui-build-guide.md` | The user only wants the connection working now; UI comes later. |

Nothing here needs to be re-created from scratch or fetched from elsewhere — the code is already in this skill. Follow Step 0 first, then Step 1 to pick A, B, or C, then follow that path's file.

## Step 0 — Get the 3 Things Needed Before Building Anything

Think of these like a house key, a house address, and a password — the agent cannot be reached without all three:

- `custom_agent.id` — which agent (its ID)
- `custom_agent.api_base_url` — the web address the agent lives at
- `enter_api_key_secret_name` — the name of a securely stored password that unlocks the agent

Two situations:

1. **The agent is already attached to this chat.** A `<system_reminder>` in the conversation already contains all three fields plus `custom_agent.name` and `custom_agent.logo`. Trust them as-is — do not ask the user to repeat them, and do not try to read `<custom_agent>` tags directly; Enter already checked and prepared them.
2. **Nothing is attached yet.** Ask the user (in plain, non-technical language) for the Agent ID and the web address. For the password/key: never type it into chat and never put it in the website's code — use `supabase_add_secret` so it is stored safely on the server. If secure server-side storage (Enter Cloud) is not turned on yet, explain in plain words that storing a password safely needs that turned on first, then offer `supabase_enable`. The agent must already be **published** (not a draft) for this to work.

If anything is missing, ask the user with `ask_user_question` before writing any code. Never invent or guess a password/key value.

## Step 1 — Pick Path A, B, or C

Look at the project first: does it already have pages, a dashboard, or a support/help area? Then choose:

- **Path A — Project-native (default).** A real page/panel already exists to put the agent in. Reuses this project's own buttons, colors, and layout. Go to `ui-build-guide.md`.
- **Path B — Default/standalone chat page.** The project is empty/new, or the user explicitly says "just give me a normal chat page." Go to `default-ui-template/README.md`.
- **Path C — Backend only.** The user only wants the plumbing working today, no visible chat yet. Do Steps A and B of `ui-build-guide.md` only.

Tell the user in one short sentence which path was chosen and why, before building.

## Path A — Project-Native UI (`ui-build-guide.md`)

Everything is written out step-by-step in that file, in order:

- **Step A** — the database table that remembers each conversation (with security so users only see their own).
- **Step B** — the secure server-side proxy (the "middleman" that holds the password so the browser never sees it).
- **Step C** — the connection code (`use-custom-agent-chat.ts`) that talks to the agent through the proxy.
- **Step D** — turns the agent's raw activity into simple, readable pieces (a message, a "thinking" note, a tool action, an error).
- **Step E** — the actual chat box built from this project's own buttons/cards/inputs — the real, working component to drop into a page.
- **Step F** — making labels translatable if the project supports more than one language.
- **Step G** — how to check it actually works (what to click, what to look for).

Install commands needed for Path A (also listed inside `ui-build-guide.md`):

```bash
pnpm add @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2
pnpm add react-markdown@^10.1.0 remark-gfm@^4.0.0
```

## Path B — Default/Standalone Chat UI (`default-ui-template/`)

This is a **complete, already-built chat page** bundled inside this skill — session list, message bubbles, "agent is thinking" indicator, tool-action list, error handling, translated labels, light theme, all included as real code files. Read `default-ui-template/README.md` first, it shows exactly how to wire it up.

Install commands for Path B:

```bash
pnpm add @enter-pro/agent-client@0.0.2 @enter-pro/thread-client@0.0.2 react-markdown@^10.1.0 remark-gfm@^4.0.0 lucide-react
```

Then, copy the whole `default-ui-template/src` folder into the project (for example into `src/features/custom-agent-chat/`), keep its internal structure intact, and wire only these adapter points — do not rewrite the internals:

- `agentId`, the proxy web address, how to read the logged-in user's token, and the chosen language — passed into `useCustomAgentChat` (see `default-ui-template/src/core/useCustomAgentChat.ts` and `src/runtime/useCustomAgentChat.ts`).
- `agentProfile` (name, logo, short description) passed into `PublicSiteLikeChatShell` (see `default-ui-template/src/ui/PublicSiteLikeChatShell.tsx`).
- Import `default-ui-template/src/styles/public-site.css` for the default light look; only import `public-site-dark.css` if a dark theme was explicitly requested.
- Mount the resulting page behind a real route (e.g. `/assistant` or `/support`) using this project's router (`src/router.tsx`).

Still needs Path A's Step A and Step B (persistence table + secure proxy) underneath it — Path B only replaces the UI layer, not the backend.

**Do not hand-write a simplified look-alike chat page.** Copy this bundled template and adapt only the adapter points above — see `default-ui-template/default-ui-anti-patterns.md` for exactly what "hand-written near-copy" mistakes look like and why they are rejected.

Before saying Path B is done, run through `default-ui-template/default-ui-acceptance-checklist.md` — it lists the exact look and behavior a default chat page must have (a real example conversation to try, a list of things that must NOT appear, and a screenshot check at desktop and mobile size).

Key rules baked into this template already — do not weaken them when adapting:

- 14px text with 22px line spacing for messages; chat area capped at 800px wide; message bubbles capped at 568px wide. Never oversized "hero" text.
- Light, soft-colored default look (`public-site.css`) — never an all-black page by default.
- Translated labels for 13 languages already included (`default-ui-template/src/core/locales.ts`); pass the project's current language in, do not hard-code one language.
- "Agent getting ready" while starting, "Agent ready" once done; "Thinking..." while reasoning, then the real reasoning text; tool rows say "Searched websites ..." (done) not "Searching websites..." (still going) once finished.
- Assistant replies render as real formatted text (tables, lists, links) — never as plain unformatted text with visible `|` table characters.
- Raw technical/debug data is hidden from the normal chat view.

## Non-Negotiable Rules (apply to Path A, B, and C)

- Create the conversation ("thread") once, then reuse it for every message in that conversation — never create a new one per message.
- Every request to run the agent must include that conversation's ID (`threadId`).
- Never let the browser send its own list of "tools" to the agent, and never force a specific AI model — the agent already knows which model and tools to use.
- Treat every response from the agent as a live stream of small updates (SSE), not one single finished answer — build the UI to update piece by piece.
- Keep the password/key only on the server (inside the secure proxy). It must never appear in the website's code, browser network tab, logs, screenshots, or in chat with the user.
- If more than one custom agent is used, keep each one's conversation completely separate.

## Deliverable Checklist

Before saying the integration is complete, confirm:

- The password/key is stored securely on the server only (never in frontend code, chat, or docs).
- A conversation is created once and reused (Path A Step A / `default-ui-template`'s thread handling).
- The secure proxy is in place and forwards the live stream correctly (Path A Step B).
- The chosen chat UI (Path A's component or Path B's bundled template) is wired into a real page.
- Replies show up as formatted text (tables/lists/links), not plain raw text.
- "Thinking" and "tool action" indicators show real activity, never invented text.
- Errors and a cancel/stop option are visible to the user.
- Every code example only ever uses placeholder values (`<AGENT_ID>`, `<ENTER_API_KEY>`, `<THREAD_ID>`, `<ENTER_API_BASE_URL>`, `<SECRET_NAME>`) — never a real key.

## Quality Gates

- No real password/key/token appears anywhere in the generated code, chat, or docs.
- The proxy checks that a user can only access their own conversations and only allowed agents.
- The live stream (`/run`, `/events`) is passed straight through as a stream — never converted into one flat block of text.
- Path A: reuses this project's own look and components; no unrelated template was copied in.
- Path B: the bundled `default-ui-template/` was copied and adapted, not rewritten from a blank page; its acceptance checklist passed.
- The chat is checked visually at both a normal desktop size and a phone-sized screen before calling it done.

## If Something Beyond This Skill Is Needed

This skill already contains the working code for the standard case (both UI paths, the proxy, and the persistence table). Only reach for the deeper `enter_custom_agent_integration` skill if something unusual comes up: an uncommon error code, a question-and-answer style tool card (`AskUserQuestion`), or running several agents together in one screen. Otherwise, everything needed is already here — use it directly instead of rebuilding it from memory.
