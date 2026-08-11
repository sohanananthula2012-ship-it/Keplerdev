import React from 'react';
import type {
  BuilderPublicSiteLocaleInput,
  BuilderPublicSiteRenderSlots,
  BuilderPublicSiteTurnRenderContext,
  BuilderPublicSiteTurnView,
  BuilderPublicSiteViewMessage,
} from '../core/types';
import { AssistantMessage } from './AssistantMessage';
import { UserMessage } from './UserMessage';
import { ThinkingMessage } from './ThinkingMessage';
import { ToolActionList } from './ToolActionList';
import { AgentStartupMessage, CancelMessageView, ErrorMessageView } from './SystemMessages';
import { QuestionAnswerSummary } from './QuestionAnswerSummary';

export function BuilderPublicSiteMessageRenderer({
  message,
  locale = 'zh-CN',
  slots,
  turnContext,
}: {
  message: BuilderPublicSiteViewMessage;
  locale?: BuilderPublicSiteLocaleInput;
  slots?: BuilderPublicSiteRenderSlots;
  turnContext?: BuilderPublicSiteTurnRenderContext;
}) {
  switch (message.uiKind) {
    case 'user-text':
      return <>{slots?.renderUserMessage?.(message) ?? <UserMessage content={message.content} />}</>;
    case 'assistant-text':
      return <>{slots?.renderAssistantText?.(message) ?? <AssistantMessage content={message.content} />}</>;
    case 'thinking':
    case 'reasoning':
      return <>{slots?.renderThinking?.(message) ?? <ThinkingMessage message={message} locale={locale} />}</>;
    case 'tool-action-list':
      return <ToolActionList message={message} locale={locale} turnContext={turnContext} renderToolAction={slots?.renderToolAction} />;
    case 'agent-startup':
      return <AgentStartupMessage message={message} locale={locale} turnContext={turnContext} />;
    case 'question-card':
      return <>{slots?.renderQuestionCard?.(message) ?? null}</>;
    case 'question-answer-summary':
      return <QuestionAnswerSummary message={message} locale={locale} />;
    case 'turn-error':
    case 'out-of-credit':
      return <>{slots?.renderError?.(message) ?? <ErrorMessageView message={message} />}</>;
    case 'cancel':
      return <CancelMessageView message={message} />;
    case 'unsupported-custom-event':
      return <>{slots?.renderUnsupportedEvent?.(message) ?? null}</>;
    default:
      return null;
  }
}

function buildTurnContext(
  turn: BuilderPublicSiteTurnView,
  index: number,
  turnCount: number,
  isAgentRunning?: boolean,
): BuilderPublicSiteTurnRenderContext {
  const isLastItem = index === turnCount - 1;
  const isActiveTurn = turn.status === 'running' || turn.status === 'awaiting-user';
  const isRunningTurn = isLastItem && Boolean(isAgentRunning || isActiveTurn);
  const isEndedTurn = !isLastItem || !isRunningTurn;
  return {
    isLastItem,
    isAgentRunning: isRunningTurn,
    isTurnEnded: isEndedTurn,
    turnMessages: turn.messages,
  };
}

export function BuilderPublicSiteTranscript({
  messages,
  turns,
  isAgentRunning,
  locale = 'zh-CN',
  slots,
  className,
}: {
  messages?: BuilderPublicSiteViewMessage[];
  turns?: BuilderPublicSiteTurnView[];
  isAgentRunning?: boolean;
  locale?: BuilderPublicSiteLocaleInput;
  slots?: BuilderPublicSiteRenderSlots;
  className?: string;
}) {
  const renderedTurns = turns ?? [{
    key: 'flat-turn',
    status: 'done' as const,
    messages: messages ?? [],
  }];

  return (
    <div className={`bps-transcript ${className ?? ''}`}>
      {renderedTurns.map((turn, turnIndex) => {
        const turnContext = buildTurnContext(turn, turnIndex, renderedTurns.length, isAgentRunning);
        return (
          <div className="bps-turn" key={turn.key}>
            {turn.messages.map((message) => (
              <BuilderPublicSiteMessageRenderer
                key={message.key}
                message={message}
                locale={locale}
                slots={slots}
                turnContext={turnContext}
              />
            ))}
          </div>
        );
      })}
    </div>
  );
}
