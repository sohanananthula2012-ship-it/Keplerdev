import type { ReactNode } from 'react';

export type BuilderPublicSiteLocale =
  | 'en'
  | 'zh-CN'
  | 'de-DE'
  | 'pt-BR'
  | 'es-ES'
  | 'fr-FR'
  | 'id-ID'
  | 'it-IT'
  | 'ja-JP'
  | 'ko-KR'
  | 'ru-RU'
  | 'ar-SA'
  | 'tr-TR';

export type BuilderPublicSiteLocaleInput = BuilderPublicSiteLocale | 'zh' | string;

export type BuilderPublicSiteTheme = 'light' | 'dark' | 'system';

export type BuilderPublicSiteAgentProfile = {
  name?: string;
  logo?: string;
  description?: string;
  modelLabel?: string;
  toolsCount?: number;
  skillsCount?: number;
};

export type MessageRole = 'user' | 'assistant' | 'tool' | 'system';

export type MessageContentPart = {
  type?: string;
  text?: string;
  content?: unknown;
  [key: string]: unknown;
};

export type ThreadMessageLike = {
  id?: string;
  role?: MessageRole | string;
  content?: string | MessageContentPart[] | null;
  text?: string;
  name?: string;
  toolCallId?: string;
  tool_call_id?: string;
  toolCalls?: ToolCallLike[];
  tool_calls?: ToolCallLike[];
  status?: string;
  createdAt?: string | number;
  created_at?: string | number;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
};

export type ToolCallLike = {
  id?: string;
  toolCallId?: string;
  function?: { name?: string; arguments?: unknown };
  name?: string;
  args?: unknown;
  arguments?: unknown;
  input?: unknown;
  status?: string;
  result?: unknown;
  [key: string]: unknown;
};

export type ThreadCustomEventLike = {
  id?: string;
  type?: string;
  name?: string;
  event?: string;
  data?: unknown;
  value?: unknown;
  status?: string;
  timestamp?: string | number;
  [key: string]: unknown;
};

export type ThreadTurnItemLike =
  | ThreadMessageLike
  | ThreadCustomEventLike
  | { kind?: string; message?: ThreadMessageLike; event?: ThreadCustomEventLike; custom?: ThreadCustomEventLike; [key: string]: unknown };

export type ThreadTurnLike = {
  id?: string;
  turnId?: string;
  turn_id?: string;
  status?: string;
  state?: string;
  messages?: ThreadTurnItemLike[];
  events?: ThreadTurnItemLike[];
  items?: ThreadTurnItemLike[];
  history?: ThreadTurnItemLike[];
  [key: string]: unknown;
};

export type BuilderStartupStep = {
  id: string;
  icon: 'monitor' | 'scan' | 'bot';
  label: string;
  status: 'loading' | 'done' | 'error';
};

export type BuilderToolActionView = {
  key: string;
  registryKey: string;
  label: string;
  description?: string;
  status: 'loading' | 'finished' | 'error';
  icon?: ReactNode;
};

export type BuilderQuestionOption = {
  label: string;
};

export type BuilderQuestion = {
  question: string;
  header?: string;
  options: BuilderQuestionOption[];
  multiSelect?: boolean;
};

export type BuilderQuestionAnswerEntry = {
  selected_options: string[];
  other_text: string;
};

export type BuilderQuestionAnswers = {
  answers: Record<string, BuilderQuestionAnswerEntry>;
  skipped: boolean;
};

export type BuilderQuestionCardStatus = 'waiting' | 'answered' | 'skipped' | 'cancelled';

export type BuilderPublicSiteViewMessage =
  | { uiKind: 'user-text'; key: string; content: string; createdAt?: string | number }
  | { uiKind: 'assistant-text'; key: string; content: string; createdAt?: string | number }
  | { uiKind: 'thinking'; key: string; content: string; status: 'streaming' | 'done'; durationMs?: number; turnId?: string }
  | { uiKind: 'reasoning'; key: string; content: string; status: 'streaming' | 'done'; durationMs?: number; turnId?: string }
  | { uiKind: 'tool-action-list'; key: string; messages: ThreadMessageLike[]; actions: BuilderToolActionView[]; isTurnEnded?: boolean; hasFollowingRenderableUi?: boolean; turnId?: string }
  | { uiKind: 'agent-startup'; key: string; steps: BuilderStartupStep[]; status: 'loading' | 'done' | 'error'; headerPhase: 'preparing' | 'responded'; isTurnEnded?: boolean; turnId?: string }
  | { uiKind: 'question-card'; key: string; questions: BuilderQuestion[]; toolCallId?: string; status: BuilderQuestionCardStatus; completedAnswers?: BuilderQuestionAnswers; raw?: unknown; turnId?: string; turnNumber?: number }
  | { uiKind: 'question-answer-summary'; key: string; questions?: BuilderQuestion[]; completedAnswers?: BuilderQuestionAnswers; summary?: string; toolCallId?: string; turnId?: string; turnNumber?: number }
  | { uiKind: 'turn-error'; key: string; message: string; raw?: unknown; turnId?: string }
  | { uiKind: 'out-of-credit'; key: string; message: string; turnId?: string }
  | { uiKind: 'cancel'; key: string; message: string; turnId?: string }
  | { uiKind: 'unsupported-custom-event'; key: string; eventName: string; raw: unknown; debugOnly: true; turnId?: string };

export type BuilderPublicSiteTurnView = {
  key: string;
  turnId?: string;
  status: 'idle' | 'running' | 'awaiting-user' | 'done' | 'error' | 'cancelled';
  messages: BuilderPublicSiteViewMessage[];
};

export type BuilderPublicSiteTurnRenderContext = {
  isLastItem: boolean;
  isAgentRunning: boolean;
  isTurnEnded: boolean;
  turnMessages: BuilderPublicSiteViewMessage[];
};

export type ToolDisplayRegistryEntry = {
  icon?: ReactNode;
  getLabel: (state: 'loading' | 'finished' | 'error', locale: BuilderPublicSiteLocale) => string;
};

export type ToolDisplayRegistry = Record<string, ToolDisplayRegistryEntry>;

export type BuilderPublicSiteRenderSlots = {
  renderUserMessage?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'user-text' }>) => ReactNode;
  renderAssistantText?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'assistant-text' }>) => ReactNode;
  renderThinking?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'thinking' | 'reasoning' }>) => ReactNode;
  renderToolAction?: (action: BuilderToolActionView) => ReactNode;
  renderQuestionCard?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>) => ReactNode;
  renderError?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'turn-error' | 'out-of-credit' }>) => ReactNode;
  renderUnsupportedEvent?: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'unsupported-custom-event' }>) => ReactNode;
};
