# Default Builder-style React Components

Use this template when the user did not specify a custom UI style. It is the default baseline implementation for the Builder/Public Site-like transcript, not a loose inspiration snippet.

Install Markdown dependencies for assistant answers:

```bash
npm install react-markdown@^10.1.0 remark-gfm@^4.0.0
```

Generated projects may adapt colors and spacing, but should keep the same message structure, Markdown behavior, and debug separation. Do not import private Enter Web components.

```tsx
import { useState, type ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { DefaultBuilderStyleView } from './customAgentRenderableMessages';
import type { CustomAgentActionView, Locale } from './toolActionNormalization';

type Strings = {
  errorTitle: string;
  questionTitle: string;
  questionAnswer: string;
};

// Add one entry per locale you support; see `src/core/locales.ts` for the supported set.
const STRINGS: Partial<Record<Locale, Strings>> & { en: Strings } = {
  en: {
    errorTitle: 'Something went wrong',
    questionTitle: 'Question',
    questionAnswer: 'Answered',
  },
};

export function DefaultBuilderStyleChat(props: {
  messages: readonly DefaultBuilderStyleView[];
  locale?: Locale;
}) {
  const locale = props.locale ?? 'en';
  const strings = STRINGS[locale] ?? STRINGS.en;

  return (
    <div className="ca-chat" data-custom-agent-chat>
      {props.messages.map((message) => {
        switch (message.kind) {
          case 'user-bubble':
            return <UserBubble key={message.id} content={message.content} />;
          case 'startup-status-group':
            return <StartupStatusGroup key={message.id} headerPhase={message.headerPhase} label={message.label} defaultOpen={message.defaultOpen} />;
          case 'thinking-group':
            return <ThinkingGroup key={message.id} title={message.title} content={message.content} isLoading={message.isLoading} defaultOpen={message.defaultOpen} />;
          case 'action-group':
            return <ActionGroup key={message.id} title={message.title} actions={message.actions} isLoading={message.isLoading} defaultOpen={message.defaultOpen} />;
          case 'assistant-message':
            return <AssistantMessage key={message.id} content={message.content} streaming={message.streaming} />;
          case 'question-card':
            return <QuestionCard key={message.id} question={message.question} title={strings.questionTitle} />;
          case 'question-answer-summary':
            return <QuestionAnswerSummary key={message.id} answer={message.answer} skipped={message.skipped} label={strings.questionAnswer} />;
          case 'error-message':
            return <ErrorMessage key={message.id} detail={message.detail} errorType={message.errorType} title={strings.errorTitle} />;
          case 'cancel-message':
            return <CancelMessage key={message.id} label={message.label} />;
        }
      })}
    </div>
  );
}

export function CustomAgentTranscriptShell(props: {
  sessions: readonly { id: string; title: string; active?: boolean }[];
  onNewSession: () => void;
  onSelectSession: (id: string) => void;
  children: ReactNode;
  composer: ReactNode;
}) {
  return (
    <main className="ca-shell">
      <aside className="ca-sidebar" aria-label="Sessions">
        <div className="ca-sidebar-header">
          <div className="ca-sidebar-title">Sessions</div>
          <button className="ca-icon-button" type="button" onClick={props.onNewSession} aria-label="New session">+</button>
        </div>
        <div className="ca-session-list">
          {props.sessions.map((session) => (
            <button
              key={session.id}
              className="ca-session-item"
              data-active={session.active}
              type="button"
              onClick={() => props.onSelectSession(session.id)}
            >
              {session.title}
            </button>
          ))}
        </div>
      </aside>
      <section className="ca-thread">
        <div className="ca-transcript">{props.children}</div>
        <div className="ca-composer">{props.composer}</div>
      </section>
    </main>
  );
}

function UserBubble(props: { content: string }) {
  return (
    <div className="ca-message ca-message-user">
      <div className="ca-user-bubble">{props.content}</div>
    </div>
  );
}

function StartupStatusGroup(props: { headerPhase: 'preparing' | 'responded'; label: string; defaultOpen: boolean }) {
  const [open, setOpen] = useState(props.defaultOpen);
  return (
    <section className="ca-startup-status" data-phase={props.headerPhase}>
      <button className="ca-group-header" type="button" onClick={() => props.headerPhase === 'responded' && setOpen((value) => !value)} aria-expanded={open}>
        <span className="ca-startup-icon" aria-hidden="true" />
        <span>{props.label}</span>
      </button>
      {open ? (
        <div className="ca-group-body">
          <div className="ca-vertical-line" aria-hidden="true" />
          <div className="ca-thinking-text">{props.headerPhase === 'preparing' ? 'Preparing agent...' : 'Agent is ready.'}</div>
        </div>
      ) : null}
    </section>
  );
}

function ThinkingGroup(props: { title: string; content: string; isLoading: boolean; defaultOpen: boolean }) {
  const [open, setOpen] = useState(props.defaultOpen);
  if (!props.isLoading && !props.content.trim()) return null;

  return (
    <section className="ca-group ca-thinking" data-loading={props.isLoading}>
      <button className="ca-group-header" type="button" onClick={() => setOpen((value) => !value)}>
        <span className="ca-group-icon ca-thinking-icon" data-open={open} data-loading={props.isLoading} aria-hidden="true" />
        <span>{props.title}</span>
      </button>
      {open && props.content.trim() ? (
        <div className="ca-group-body">
          <div className="ca-vertical-line" aria-hidden="true" />
          <div className="ca-thinking-text">{props.content}</div>
        </div>
      ) : null}
    </section>
  );
}

function ActionGroup(props: { title: string; actions: readonly CustomAgentActionView[]; isLoading: boolean; defaultOpen: boolean }) {
  const [open, setOpen] = useState(props.defaultOpen);
  if (props.actions.length === 0) return null;

  return (
    <section className="ca-group ca-actions" data-loading={props.isLoading}>
      <button className="ca-group-header" type="button" onClick={() => setOpen((value) => !value)}>
        <span className="ca-group-icon ca-actions-icon" data-open={open} data-loading={props.isLoading} aria-hidden="true" />
        <span>{props.title}</span>
      </button>
      {open ? (
        <div className="ca-group-body">
          <div className="ca-vertical-line" aria-hidden="true" />
          <div className="ca-action-list">
            {props.actions.map((action) => <ActionRow key={action.id} action={action} />)}
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ActionRow(props: { action: CustomAgentActionView }) {
  return (
    <div className="ca-action-row" data-status={props.action.status}>
      <span className={`ca-tool-icon ca-tool-icon-${props.action.icon}`} aria-hidden="true" />
      <span className="ca-action-verb">{props.action.localizedVerb}</span>
      <span className="ca-action-target">{props.action.target}</span>
    </div>
  );
}

function AssistantMessage(props: { content: string; streaming?: boolean }) {
  return (
    <div className="ca-message ca-message-assistant" data-streaming={props.streaming}>
      <div className="ca-markdown">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {props.content}
        </ReactMarkdown>
      </div>
    </div>
  );
}

function QuestionCard(props: { question: string; title: string }) {
  return (
    <div className="ca-question-card">
      <div className="ca-question-title">{props.title}</div>
      <div>{props.question}</div>
    </div>
  );
}

function QuestionAnswerSummary(props: { answer?: string; skipped?: boolean; label: string }) {
  if (props.skipped) return null;
  return (
    <div className="ca-question-summary">
      <span className="ca-question-title">{props.label}</span>
      {props.answer ? <span>{props.answer}</span> : null}
    </div>
  );
}

function ErrorMessage(props: { detail: string; errorType?: string; title: string }) {
  return (
    <div className="ca-error-message" role="alert">
      <div className="ca-error-title">{props.title}</div>
      <div>{props.detail}</div>
      {props.errorType ? <div className="ca-error-code">{props.errorType}</div> : null}
    </div>
  );
}

function CancelMessage(props: { label: string }) {
  return <div className="ca-cancel-message">{props.label}</div>;
}
```

The main transcript intentionally has no outer turn card, no `startup done` card, no `answer done` card, no assistant bot/avatar icon, no raw Markdown answer, and no telemetry JSON block. Put raw events behind a developer-only debug drawer when needed.
