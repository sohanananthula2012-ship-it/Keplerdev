import type {
  BuilderPublicSiteLocaleInput,
  BuilderQuestion,
  BuilderQuestionAnswerEntry,
  BuilderQuestionAnswers,
  BuilderQuestionCardStatus,
  ToolCallLike,
} from './types';
import { resolveBuilderPublicSiteLocale } from './locales';
import { compactText, firstString, isRecord, tryParseJsonObject } from './messageContent';

export type ParsedResolvedQuestionEvent = {
  toolCallId: string;
  status: BuilderQuestionCardStatus;
  completedAnswers?: BuilderQuestionAnswers;
};

const ASK_USER_QUESTION_NAMES = new Set([
  'askuserquestion',
  'askquestion',
]);

function normalizedToolName(value: unknown) {
  return String(value ?? '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
}

function stringField(value: unknown, key: string): string | undefined {
  if (!isRecord(value)) return undefined;
  return firstString(value[key]);
}

export function isAskUserQuestionToolName(value: unknown) {
  return ASK_USER_QUESTION_NAMES.has(normalizedToolName(value));
}

export function toolCallId(toolCall: ToolCallLike): string | undefined {
  return firstString(toolCall.id, toolCall.toolCallId, toolCall.tool_call_id);
}

export function toolCallName(toolCall: ToolCallLike): string {
  return firstString(toolCall.name, toolCall.function?.name, toolCall.type) ?? 'tool';
}

export function toolCallArgsObject(toolCall: ToolCallLike): Record<string, unknown> | undefined {
  return (
    tryParseJsonObject(toolCall.args) ??
    tryParseJsonObject(toolCall.arguments) ??
    tryParseJsonObject(toolCall.function?.arguments) ??
    tryParseJsonObject(toolCall.input)
  );
}

export function parseBackendQuestions(value: unknown): BuilderQuestion[] {
  if (!isRecord(value)) return [];
  const rawQuestions = value.questions;
  if (!Array.isArray(rawQuestions)) return [];

  return rawQuestions
    .map((item): BuilderQuestion | null => {
      if (!isRecord(item)) return null;
      const question = stringField(item, 'question');
      if (!question) return null;
      const header = stringField(item, 'header');
      const options = Array.isArray(item.options)
        ? item.options
          .map((option): { label: string } | null => {
            if (!isRecord(option)) return null;
            const label = stringField(option, 'label');
            return label ? { label } : null;
          })
          .filter((option): option is { label: string } => option !== null)
          .slice(0, 25)
        : [];
      if (options.length === 0) return null;
      return {
        question,
        ...(header ? { header } : {}),
        options,
        multiSelect: Boolean(item.multiSelect),
      };
    })
    .filter((question): question is BuilderQuestion => question !== null)
    .slice(0, 4);
}

export function parseAskUserQuestionArgs(rawArgs: unknown): BuilderQuestion[] {
  return parseBackendQuestions(tryParseJsonObject(rawArgs));
}

export function parseAskUserQuestionToolCall(toolCall: ToolCallLike) {
  if (!isAskUserQuestionToolName(toolCallName(toolCall))) return undefined;
  const id = toolCallId(toolCall);
  if (!id) return undefined;
  const questions = parseBackendQuestions(toolCallArgsObject(toolCall));
  if (questions.length === 0) return undefined;
  return { toolCallId: id, questions };
}

export function createQuestionAnswerKeys(questions: BuilderQuestion[]): string[] {
  const counter = new Map<string, number>();
  return questions.map((question) => {
    const key = question.question.trim();
    const current = counter.get(key) ?? 0;
    counter.set(key, current + 1);
    return current === 0 ? key : `${key}__${current + 1}`;
  });
}

export function buildAnswerRequestBody(questions: BuilderQuestion[], payload: BuilderQuestionAnswers) {
  if (payload.skipped) return { response: 'skipped' as const };

  const answerKeys = createQuestionAnswerKeys(questions);
  const answers = questions.flatMap((question, index) => {
    const entry = payload.answers[answerKeys[index]];
    if (!entry) return [];
    const selectedOptions = entry.selected_options.filter(Boolean);
    const note = entry.other_text.trim();
    if (selectedOptions.length === 0 && note === '') return [];
    return [{
      question: question.question,
      ...(question.header ? { header: question.header } : {}),
      ...(selectedOptions.length > 0 ? { selected_options: selectedOptions } : {}),
      ...(note ? { note } : {}),
    }];
  });

  return {
    response: 'answered' as const,
    ...(answers.length > 0 ? { answers } : {}),
  };
}

function normalizeResolvedStatus(rawStatus: unknown): BuilderQuestionCardStatus {
  switch (firstString(rawStatus)) {
    case 'answered':
      return 'answered';
    case 'skipped':
      return 'skipped';
    case 'cancelled':
    case 'expired':
      return 'cancelled';
    default:
      return 'cancelled';
  }
}

export function parseToolActionResolvedEvent(value: unknown, questions: BuilderQuestion[]): ParsedResolvedQuestionEvent | undefined {
  if (!isRecord(value)) return undefined;
  const resolvedToolCallId = firstString(value.tool_call_id, value.toolCallId, value.tool_call_id);
  if (!resolvedToolCallId) return undefined;
  const status = normalizeResolvedStatus(value.status);
  const responseRaw = isRecord(value.response) ? value.response : undefined;

  if (!responseRaw) {
    return { toolCallId: resolvedToolCallId, status };
  }

  const responseType = stringField(responseRaw, 'response');
  if (responseType === 'skipped' || status === 'skipped') {
    return {
      toolCallId: resolvedToolCallId,
      status: 'skipped',
      completedAnswers: { answers: {}, skipped: true },
    };
  }

  const answerKeys = createQuestionAnswerKeys(questions);
  const usedQuestionIndexes = new Set<number>();
  const answers: Record<string, BuilderQuestionAnswerEntry> = {};
  const rawAnswers = responseRaw.answers;
  if (Array.isArray(rawAnswers)) {
    rawAnswers.forEach((item) => {
      if (!isRecord(item)) return;
      const questionText = stringField(item, 'question');
      if (!questionText) return;
      const normalizedQuestion = questionText.trim();
      const questionIndex = questions.findIndex((question, index) => (
        !usedQuestionIndexes.has(index)
        && (question.question.trim() === normalizedQuestion || answerKeys[index] === normalizedQuestion)
      ));
      const key = questionIndex >= 0 ? answerKeys[questionIndex]! : normalizedQuestion;
      if (questionIndex >= 0) usedQuestionIndexes.add(questionIndex);
      const selectedOptions = Array.isArray(item.selected_options)
        ? item.selected_options.filter((option): option is string => typeof option === 'string' && option.trim() !== '')
        : [];
      const note = stringField(item, 'note') ?? '';
      if (selectedOptions.length === 0 && note === '') return;
      answers[key] = { selected_options: selectedOptions, other_text: note };
    });
  }

  return {
    toolCallId: resolvedToolCallId,
    status: status === 'cancelled' ? 'cancelled' : 'answered',
    completedAnswers: { answers, skipped: false },
  };
}

export function normalizeAnswerText(entry: BuilderQuestionAnswerEntry | undefined): string {
  if (!entry) return '';
  const selectedOptions = entry.selected_options.filter(Boolean);
  const otherText = entry.other_text.trim();
  if (otherText && selectedOptions.length > 0) return `${selectedOptions.join(', ')}; ${otherText}`;
  if (otherText) return otherText;
  return selectedOptions.join(', ');
}

export function buildQuestionAnswerRows(questions: BuilderQuestion[], completedAnswers: BuilderQuestionAnswers | undefined) {
  if (!completedAnswers) return [];
  const answerKeys = createQuestionAnswerKeys(questions);
  return questions
    .map((question, index) => ({
      question: question.question,
      answer: normalizeAnswerText(completedAnswers.answers[answerKeys[index]]),
    }))
    .filter((row) => row.answer);
}

export function formatQuestionAnswerSummary(
  questions: BuilderQuestion[] | undefined,
  completedAnswers: BuilderQuestionAnswers | undefined,
  localeInput: BuilderPublicSiteLocaleInput,
  fallbackSummary?: string,
) {
  return formatQuestionAnswerSummaryDisplayText(
    buildQuestionAnswerRows(questions ?? [], completedAnswers),
    localeInput,
    Boolean(completedAnswers?.skipped),
    fallbackSummary,
  );
}

export function formatQuestionAnswerSummaryDisplayText(
  rows: Array<{ question: string; answer: string }>,
  localeInput: BuilderPublicSiteLocaleInput,
  skipped = false,
  fallbackSummary?: string,
) {
  const locale = resolveBuilderPublicSiteLocale(localeInput);
  if (fallbackSummary?.trim()) return fallbackSummary.trim();
  if (skipped || rows.length === 0) return locale === 'zh-CN' ? '跳过全部问题' : 'Skip All Questions';
  const header = locale === 'zh-CN'
    ? `${rows.length} 个问题已回答`
    : `${rows.length} ${rows.length === 1 ? 'Question' : 'Questions'} Answered`;
  const lines = rows.map((row, index) => `${index + 1}. ${row.question}\n   ${row.answer}`);
  return `${header}\n${lines.join('\n')}`;
}

export function questionCountLabel(count: number, localeInput: BuilderPublicSiteLocaleInput) {
  const locale = resolveBuilderPublicSiteLocale(localeInput);
  if (locale === 'zh-CN') return `${count} 个问题`;
  return `${count} ${count === 1 ? 'question' : 'questions'}`;
}

export function questionToolDescription(questions: BuilderQuestion[], localeInput: BuilderPublicSiteLocaleInput) {
  if (questions.length === 0) return '';
  if (questions.length === 1) return compactText(questions[0]!.question);
  return questionCountLabel(questions.length, localeInput);
}
