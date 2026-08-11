import React, { useMemo } from 'react';
import type { BuilderPublicSiteLocaleInput, BuilderPublicSiteViewMessage } from '../core/types';
import { buildQuestionAnswerRows, formatQuestionAnswerSummaryDisplayText } from '../core/questions';

type QuestionAnswerSummaryMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-answer-summary' }>;

export function QuestionAnswerSummary({
  message,
  locale = 'zh-CN',
}: {
  message: QuestionAnswerSummaryMessage;
  locale?: BuilderPublicSiteLocaleInput;
}) {
  const content = useMemo(() => {
    if (!message.completedAnswers && !message.summary?.trim()) return '';
    const rows = buildQuestionAnswerRows(message.questions ?? [], message.completedAnswers);
    return formatQuestionAnswerSummaryDisplayText(rows, locale, Boolean(message.completedAnswers?.skipped), message.summary);
  }, [locale, message.completedAnswers, message.questions, message.summary]);

  if (!content.trim()) return null;

  return (
    <article
      className="bps-user-message-row bps-question-answer-summary-row"
      data-testid={`bps-question-answer-summary-${message.toolCallId ?? 'unknown'}`}
    >
      <div className="bps-user-bubble bps-question-answer-summary-bubble">{content}</div>
    </article>
  );
}
