import React from 'react';
import { MessageSquare, Plus } from 'lucide-react';
import type {
  BuilderPublicSiteAgentProfile,
  BuilderPublicSiteLocaleInput,
  BuilderPublicSiteRenderSlots,
  BuilderPublicSiteTheme,
  BuilderPublicSiteTurnView,
  BuilderPublicSiteViewMessage,
} from '../core/types';
import { localeLabels, localeTextDirection, resolveBuilderPublicSiteLocale } from '../core/locales';
import { getBuilderPublicSiteLogoFamily } from '../core/logoPresets';
import { BuilderPublicSiteTranscript } from './BuilderPublicSiteTranscript';
import { Composer } from './Composer';
import { QuestionCard } from './QuestionCard';
import {
  BuilderPublicSiteAgentAvatar,
  getBuilderPublicSiteAgentMetaItems,
  getBuilderPublicSiteAgentName,
} from './AgentIdentity';

type QuestionCardMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>;

export type ChatSessionSummary = {
  id: string;
  title: string;
  subtitle?: string;
  active?: boolean;
};

export function SessionSidebar({
  sessions,
  locale = 'zh-CN',
  title,
  agentProfile,
  onNewSession,
  onSelectSession,
}: {
  sessions?: ChatSessionSummary[];
  locale?: BuilderPublicSiteLocaleInput;
  title?: string;
  agentProfile?: BuilderPublicSiteAgentProfile;
  onNewSession?: () => void;
  onSelectSession?: (sessionId: string) => void;
}) {
  const l = localeLabels(locale);
  const displayName = getBuilderPublicSiteAgentName(agentProfile, title, locale);
  const metaItems = getBuilderPublicSiteAgentMetaItems(agentProfile, locale);
  return (
    <aside className="bps-session-sidebar">
      <div className="bps-session-card-header">
        <BuilderPublicSiteAgentAvatar
          agentProfile={agentProfile}
          displayName={displayName}
          className="bps-session-agent-avatar"
        />
        <div className="bps-session-agent-copy">
          <div className="bps-session-agent-name">{displayName}</div>
          {agentProfile?.description ? <div className="bps-session-agent-description">{agentProfile.description}</div> : null}
          {metaItems.length > 0 ? <div className="bps-session-agent-meta">{metaItems.join(' · ')}</div> : null}
        </div>
      </div>
      <button className="bps-new-session" type="button" onClick={onNewSession}>
        <Plus className="bps-session-action-icon" />
        <span>{String(l.newSession)}</span>
      </button>
      <div className="bps-session-list">
        {(sessions ?? []).map((session) => (
          <button key={session.id} type="button" className={`bps-session-item ${session.active ? 'is-active' : ''}`} onClick={() => onSelectSession?.(session.id)}>
            <MessageSquare className="bps-session-item-icon" />
            <span className="bps-session-text">
              <span className="bps-session-title">{session.title}</span>
              {session.subtitle ? <span className="bps-session-subtitle">{session.subtitle}</span> : null}
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}

export function PublicSiteLikeChatShell({
  messages,
  turns,
  locale = 'zh-CN',
  sessions,
  title,
  agentProfile,
  theme = 'light',
  slots,
  isRunning,
  isSubmittingQuestion,
  onSend,
  onAbort,
  onNewSession,
  onSelectSession,
  onSubmitQuestionAnswer,
}: {
  messages?: BuilderPublicSiteViewMessage[];
  turns?: BuilderPublicSiteTurnView[];
  locale?: BuilderPublicSiteLocaleInput;
  sessions?: ChatSessionSummary[];
  title?: string;
  agentProfile?: BuilderPublicSiteAgentProfile;
  theme?: BuilderPublicSiteTheme;
  slots?: BuilderPublicSiteRenderSlots;
  isRunning?: boolean;
  isSubmittingQuestion?: boolean;
  onSend: (message: string) => Promise<void> | void;
  onAbort?: () => Promise<void> | void;
  onNewSession?: () => void;
  onSelectSession?: (sessionId: string) => void;
  onSubmitQuestionAnswer?: Parameters<typeof QuestionCard>[0]['onSubmit'];
}) {
  const resolvedLocale = resolveBuilderPublicSiteLocale(locale);
  const activeQuestion = findActiveWaitingQuestion(turns, messages);
  const filteredTurns = turns ? stripQuestionCardsFromTurns(turns) : undefined;
  const filteredMessages = messages ? stripQuestionCardsFromMessages(messages) : undefined;
  const transcriptIsAgentRunning = Boolean(isRunning);
  const displayName = getBuilderPublicSiteAgentName(agentProfile, title, resolvedLocale);
  const resolvedAgentProfile = { ...agentProfile, name: displayName };
  const logoFamily = getBuilderPublicSiteLogoFamily(agentProfile?.logo);
  const hasTranscriptContent = hasRenderableMessages(filteredTurns, filteredMessages);
  return (
    <div
      className="bps-shell"
      data-variant="public-site"
      data-theme={theme}
      data-logo-family={logoFamily ?? undefined}
      lang={resolvedLocale}
      dir={localeTextDirection(resolvedLocale)}
    >
      <SessionSidebar
        sessions={sessions}
        locale={resolvedLocale}
        title={title}
        agentProfile={resolvedAgentProfile}
        onNewSession={onNewSession}
        onSelectSession={onSelectSession}
      />
      <main className="bps-main">
        {title ? <div className="bps-thread-title">{title}</div> : null}
        {hasTranscriptContent ? (
          <BuilderPublicSiteTranscript
            messages={filteredMessages}
            turns={filteredTurns}
            isAgentRunning={transcriptIsAgentRunning}
            locale={resolvedLocale}
            slots={slots}
          />
        ) : (
          <PublicSiteEmptyState
            agentProfile={resolvedAgentProfile}
            title={title}
            locale={resolvedLocale}
          />
        )}
        {activeQuestion ? (
          <div className="bps-floating-question-card" data-testid="bps-floating-question-card">
            <QuestionCard
              message={activeQuestion}
              locale={resolvedLocale}
              isSubmitting={isSubmittingQuestion}
              onSubmit={onSubmitQuestionAnswer}
            />
          </div>
        ) : null}
        <Composer
          locale={resolvedLocale}
          agentProfile={resolvedAgentProfile}
          isRunning={isRunning}
          onSend={onSend}
          onAbort={onAbort}
        />
      </main>
    </div>
  );
}

export function BuilderTestPanelLikeChatShell(props: Parameters<typeof PublicSiteLikeChatShell>[0]) {
  return <div className="bps-test-panel-wrapper"><PublicSiteLikeChatShell {...props} /></div>;
}

function isQuestionCard(message: BuilderPublicSiteViewMessage): message is QuestionCardMessage {
  return message.uiKind === 'question-card';
}

function stripQuestionCardsFromMessages(items: BuilderPublicSiteViewMessage[]) {
  return items.filter((message) => !isQuestionCard(message));
}

function stripQuestionCardsFromTurns(items: BuilderPublicSiteTurnView[]) {
  return items.map((turn) => ({
    ...turn,
    messages: stripQuestionCardsFromMessages(turn.messages),
  }));
}

function hasRenderableMessages(turns?: BuilderPublicSiteTurnView[], messages?: BuilderPublicSiteViewMessage[]) {
  if (turns) return turns.some((turn) => turn.messages.length > 0);
  return Boolean(messages?.length);
}

function PublicSiteEmptyState({
  agentProfile,
  title,
  locale,
}: {
  agentProfile?: BuilderPublicSiteAgentProfile;
  title?: string;
  locale: BuilderPublicSiteLocaleInput;
}) {
  const displayName = getBuilderPublicSiteAgentName(agentProfile, title, locale);
  const metaItems = getBuilderPublicSiteAgentMetaItems(agentProfile, locale);

  return (
    <div className="bps-empty-state" data-testid="bps-empty-state">
      <div className="bps-empty-state-inner">
        <BuilderPublicSiteAgentAvatar
          agentProfile={agentProfile}
          displayName={displayName}
          className="bps-empty-avatar"
        />
        <div className="bps-empty-title">{displayName}</div>
        {agentProfile?.description ? <div className="bps-empty-description">{agentProfile.description}</div> : null}
        {metaItems.length > 0 ? (
          <div className="bps-empty-meta">
            {metaItems.map((item) => <span className="bps-empty-meta-item" key={item}>{item}</span>)}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function findActiveWaitingQuestion(turns?: BuilderPublicSiteTurnView[], messages?: BuilderPublicSiteViewMessage[]): QuestionCardMessage | undefined {
  if (turns && turns.length > 0) {
    const lastTurn = turns[turns.length - 1];
    const waitingQuestions = lastTurn?.messages
      .filter((message): message is QuestionCardMessage => isQuestionCard(message) && message.status === 'waiting') ?? [];
    return waitingQuestions[waitingQuestions.length - 1];
  }
  const waitingQuestions = messages
    ?.filter((message): message is QuestionCardMessage => isQuestionCard(message) && message.status === 'waiting') ?? [];
  return waitingQuestions[waitingQuestions.length - 1];
}
