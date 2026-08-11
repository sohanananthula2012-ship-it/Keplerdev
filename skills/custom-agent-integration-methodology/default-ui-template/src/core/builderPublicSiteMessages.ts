import type {
  BuilderPublicSiteLocale,
  BuilderPublicSiteLocaleInput,
  BuilderPublicSiteTurnView,
  BuilderPublicSiteViewMessage,
  BuilderStartupStep,
  ThreadCustomEventLike,
  ThreadMessageLike,
  ThreadTurnItemLike,
  ThreadTurnLike,
} from './types';
import { localeLabels, resolveBuilderPublicSiteLocale } from './locales';
import { getMessageContentText, isRecord, stringFrom } from './messageContent';
import { getVisibleBuilderToolActions } from './toolActionDisplay';
import {
  isAskUserQuestionToolName,
  parseAskUserQuestionToolCall,
  parseBackendQuestions,
  parseToolActionResolvedEvent,
} from './questions';

const STARTUP_EVENT_NAMES = new Set([
  'agent.environment.warming',
  'agent.environment.ready',
  'agent.loading',
  'agent.loaded',
]);

const TELEMETRY_EVENT_NAMES = new Set([
  'usage.update',
  'agent.output.waiting',
  'agent.turn.summary',
  'debug',
  'telemetry',
  'RUN_STARTED',
  'RUN_FINISHED',
  'RUN_ERROR',
]);

const AG_UI_STREAM_EVENT_TYPES = new Set([
  'RUN_STARTED',
  'RUN_FINISHED',
  'RUN_ERROR',
  'TEXT_MESSAGE_START',
  'TEXT_MESSAGE_CONTENT',
  'TEXT_MESSAGE_END',
  'REASONING_START',
  'REASONING_END',
  'REASONING_MESSAGE_START',
  'REASONING_MESSAGE_CONTENT',
  'REASONING_MESSAGE_END',
  'TOOL_CALL_START',
  'TOOL_CALL_ARGS',
  'TOOL_CALL_END',
  'TOOL_CALL_RESULT',
]);

function idFor(prefix: string, value: unknown, index: number) {
  return `${prefix}-${isRecord(value) && typeof value.id === 'string' ? value.id : index}`;
}

function turnStatus(turn: ThreadTurnLike): BuilderPublicSiteTurnView['status'] {
  const raw = String(turn.status ?? turn.state ?? '').toLowerCase();
  const canonical = raw.replace(/[-\s]+/g, '_');
  if (
    canonical.includes('waiting_for_user') ||
    canonical.includes('requires_action') ||
    canonical.includes('awaiting_user') ||
    canonical.includes('awaiting_input') ||
    canonical.includes('needs_input')
  ) {
    return 'awaiting-user';
  }
  if (raw.includes('run') || raw.includes('stream') || raw.includes('pending')) return 'running';
  if (raw.includes('error') || raw.includes('fail')) return 'error';
  if (raw.includes('cancel') || raw.includes('abort')) return 'cancelled';
  if (raw.includes('done') || raw.includes('complete') || raw.includes('success')) return 'done';
  return 'done';
}

export function isActiveTurnStatus(status: BuilderPublicSiteTurnView['status']) {
  return status === 'running' || status === 'awaiting-user';
}

function hasWaitingQuestionCard(messages: BuilderPublicSiteViewMessage[]) {
  return messages.some((message) => message.uiKind === 'question-card' && message.status === 'waiting');
}

function effectiveTurnStatus(
  status: BuilderPublicSiteTurnView['status'],
  messages: BuilderPublicSiteViewMessage[],
  hasTerminalSignal: boolean,
): BuilderPublicSiteTurnView['status'] {
  if (hasWaitingQuestionCard(messages)) return 'awaiting-user';
  if (status === 'awaiting-user') return 'done';
  if (hasTerminalSignal && status === 'running') return 'done';
  return status;
}

function applyTurnStatusToMessages(
  messages: BuilderPublicSiteViewMessage[],
  status: BuilderPublicSiteTurnView['status'],
): BuilderPublicSiteViewMessage[] {
  const isActive = isActiveTurnStatus(status);
  return messages.map((message) => {
    if (message.uiKind === 'tool-action-list' || message.uiKind === 'agent-startup') {
      return { ...message, isTurnEnded: !isActive };
    }
    return message;
  });
}

function turnItems(turn: ThreadTurnLike): ThreadTurnItemLike[] {
  const items = turn.items ?? turn.messages ?? turn.events ?? turn.history;
  return Array.isArray(items) ? items : [];
}

function unwrapMessage(item: ThreadTurnItemLike): ThreadMessageLike | undefined {
  if (!isRecord(item)) return undefined;
  if (isRecord(item.message)) return item.message as ThreadMessageLike;
  if (item.kind === 'message' && isRecord(item.value)) return item.value as ThreadMessageLike;
  if ('role' in item || 'toolCalls' in item || 'tool_calls' in item || 'content' in item) return item as ThreadMessageLike;
  return undefined;
}

function unwrapEvent(item: ThreadTurnItemLike): ThreadCustomEventLike | undefined {
  if (!isRecord(item)) return undefined;
  if (isRecord(item.event)) return item.event as ThreadCustomEventLike;
  if (isRecord(item.custom)) return item.custom as ThreadCustomEventLike;
  if (item.kind === 'custom' && isRecord(item.value)) return item.value as ThreadCustomEventLike;
  if ('name' in item || 'type' in item || 'event' in item) {
    const name = eventName(item as ThreadCustomEventLike);
    if (name && !('role' in item)) return item as ThreadCustomEventLike;
  }
  return undefined;
}

function eventName(event: ThreadCustomEventLike) {
  return stringFrom(event.name) ?? stringFrom(event.event) ?? stringFrom(event.type) ?? '';
}

function eventType(event: ThreadCustomEventLike) {
  return String(event.type ?? '').toUpperCase();
}

function eventData(event: ThreadCustomEventLike): Record<string, unknown> {
  const data = isRecord(event.data) ? event.data : isRecord(event.value) ? event.value : {};
  return data;
}

function buildStartupStepsFromEvents(events: ThreadCustomEventLike[], locale: BuilderPublicSiteLocale, responded: boolean): BuilderStartupStep[] {
  const names = new Set(events.map(eventName));
  const l = localeLabels(locale);
  const steps: BuilderStartupStep[] = [];

  if (names.has('agent.environment.warming') || names.has('agent.environment.ready')) {
    steps.push({
      id: 'startup-env',
      icon: 'monitor',
      label: names.has('agent.environment.ready') ? String(l.startupEnvPrepared) : String(l.startupEnvPreparing),
      status: names.has('agent.environment.ready') ? 'done' : 'loading',
    });
  }

  if (names.has('agent.loading') || names.has('agent.loaded')) {
    steps.push({
      id: 'startup-config',
      icon: 'scan',
      label: names.has('agent.loaded') ? String(l.startupConfigLoaded) : String(l.startupConfigLoading),
      status: names.has('agent.loaded') ? 'done' : 'loading',
    });
  }

  if (names.has('agent.loaded')) {
    steps.push({
      id: 'startup-agent',
      icon: 'bot',
      label: responded ? String(l.startupResponded) : String(l.startupResponding),
      status: responded ? 'done' : 'loading',
    });
  }

  return steps;
}

function reasoningFromMessage(message: ThreadMessageLike): string | undefined {
  const content = getMessageContentText(message.content);
  const metadata = isRecord(message.metadata) ? message.metadata : {};
  if (typeof metadata.reasoning === 'string') return metadata.reasoning;
  if (typeof metadata.thinking === 'string') return metadata.thinking;
  if (message.role === 'reasoning' || message.role === 'thinking') return content;
  if (message.role === 'assistant' && (message.type === 'reasoning' || message.type === 'thinking')) return content;
  return undefined;
}

function reasoningStatusFromMessage(message: ThreadMessageLike): 'streaming' | 'done' {
  const rawStatus = String(message.status ?? message.state ?? '').toLowerCase();
  if (rawStatus.includes('stream') || rawStatus.includes('run') || rawStatus.includes('load') || rawStatus.includes('pending')) {
    return 'streaming';
  }
  return 'done';
}

function contentIsRenderable(message: ThreadMessageLike) {
  return getMessageContentText(message.content).trim().length > 0;
}

function hasToolCalls(message: ThreadMessageLike) {
  const calls = message.toolCalls ?? message.tool_calls;
  return Array.isArray(calls) && calls.length > 0;
}

function isToolMessage(message: ThreadMessageLike) {
  return message.role === 'tool' || Boolean(message.toolCallId || message.tool_call_id);
}

function isAskUserQuestionToolResultMessage(message: ThreadMessageLike) {
  if (!isToolMessage(message)) return false;
  const metadata = isRecord(message.metadata) ? message.metadata : {};
  return isAskUserQuestionToolName(message.name)
    || isAskUserQuestionToolName(metadata.toolName)
    || isAskUserQuestionToolName(metadata.tool_name);
}

function toolCallsFromMessage(message: ThreadMessageLike) {
  const calls = message.toolCalls ?? message.tool_calls;
  return Array.isArray(calls) ? calls : [];
}

function shouldHideEvent(event: ThreadCustomEventLike) {
  return TELEMETRY_EVENT_NAMES.has(eventName(event)) || TELEMETRY_EVENT_NAMES.has(eventType(event));
}

function rawEventValue(event: ThreadCustomEventLike, ...fields: string[]) {
  for (const field of fields) {
    const value = event[field];
    if (typeof value === 'string') return value;
    if (typeof value === 'number' || typeof value === 'boolean') return String(value);
    if (value != null && typeof value === 'object') return JSON.stringify(value);
  }
  return '';
}

function normalizeAgUiEventItems(items: ThreadTurnItemLike[]): ThreadTurnItemLike[] {
  const output: ThreadTurnItemLike[] = [];
  const textMessages = new Map<string, ThreadMessageLike>();
  const reasoningMessages = new Map<string, ThreadMessageLike>();
  const toolCalls = new Map<string, { id: string; name: string; args: string; status: string }>();

  function getMessageId(event: ThreadCustomEventLike, fallback: string) {
    return rawEventValue(event, 'messageId', 'message_id', 'id') || fallback;
  }

  function getToolCallId(event: ThreadCustomEventLike, fallback: string) {
    return rawEventValue(event, 'toolCallId', 'tool_call_id', 'id') || fallback;
  }

  function appendMessageContent(map: Map<string, ThreadMessageLike>, id: string, content: string, role: string) {
    const existing = map.get(id) ?? { id, role, content: '' };
    existing.content = `${getMessageContentText(existing.content)}${content}`;
    map.set(id, existing);
  }

  function flushMessage(map: Map<string, ThreadMessageLike>, id: string, status: 'streaming' | 'done' = 'done') {
    const message = map.get(id);
    if (message && getMessageContentText(message.content).trim()) output.push({ ...message, status });
    map.delete(id);
  }

  items.forEach((item, index) => {
    const event = unwrapEvent(item);
    const type = event ? eventType(event) : '';
    if (!event || !AG_UI_STREAM_EVENT_TYPES.has(type)) {
      output.push(item);
      return;
    }

    if (type === 'TEXT_MESSAGE_START') {
      const id = getMessageId(event, `assistant-${index}`);
      textMessages.set(id, { id, role: rawEventValue(event, 'role') || 'assistant', content: '' });
      return;
    }
    if (type === 'TEXT_MESSAGE_CONTENT') {
      appendMessageContent(
        textMessages,
        getMessageId(event, `assistant-${index}`),
        rawEventValue(event, 'delta', 'content', 'text'),
        'assistant',
      );
      return;
    }
    if (type === 'TEXT_MESSAGE_END') {
      flushMessage(textMessages, getMessageId(event, `assistant-${index}`), 'done');
      return;
    }

    if (type === 'REASONING_MESSAGE_START' || type === 'REASONING_START') {
      const id = getMessageId(event, `reasoning-${index}`);
      reasoningMessages.set(id, { id, role: 'reasoning', content: '' });
      return;
    }
    if (type === 'REASONING_MESSAGE_CONTENT') {
      appendMessageContent(
        reasoningMessages,
        getMessageId(event, `reasoning-${index}`),
        rawEventValue(event, 'delta', 'content', 'text'),
        'reasoning',
      );
      return;
    }
    if (type === 'REASONING_MESSAGE_END' || type === 'REASONING_END') {
      flushMessage(reasoningMessages, getMessageId(event, `reasoning-${index}`), 'done');
      return;
    }

    if (type === 'TOOL_CALL_START') {
      const id = getToolCallId(event, `tool-${index}`);
      toolCalls.set(id, {
        id,
        name: rawEventValue(event, 'toolCallName', 'tool_call_name', 'name') || 'tool',
        args: '',
        status: 'loading',
      });
      return;
    }
    if (type === 'TOOL_CALL_ARGS') {
      const id = getToolCallId(event, `tool-${index}`);
      const existing = toolCalls.get(id) ?? { id, name: 'tool', args: '', status: 'loading' };
      existing.args += rawEventValue(event, 'delta', 'args', 'arguments', 'input');
      toolCalls.set(id, existing);
      return;
    }
    if (type === 'TOOL_CALL_END') {
      const id = getToolCallId(event, `tool-${index}`);
      const existing = toolCalls.get(id) ?? { id, name: 'tool', args: '', status: 'done' };
      existing.status = 'done';
      toolCalls.set(id, existing);
      output.push({
        id: `tool-call-${id}`,
        role: 'assistant',
        toolCalls: [{
          id,
          name: existing.name,
          args: existing.args,
          status: existing.status,
        }],
      });
      return;
    }
    if (type === 'TOOL_CALL_RESULT') {
      const id = getToolCallId(event, `tool-${index}`);
      const existing = toolCalls.get(id);
      const toolName = existing?.name ?? rawEventValue(event, 'toolCallName', 'tool_call_name', 'name') ?? 'tool';
      if (isAskUserQuestionToolName(toolName)) return;
      output.push({
        id: rawEventValue(event, 'messageId', 'message_id', 'id') || `tool-result-${id}`,
        role: 'tool',
        toolCallId: id,
        name: toolName,
        content: rawEventValue(event, 'content', 'result', 'delta', 'text'),
        metadata: {
          toolName,
        },
      });
      return;
    }

    output.push(event);
  });

  textMessages.forEach((message) => {
    if (getMessageContentText(message.content).trim()) output.push({ ...message, status: 'streaming' });
  });
  reasoningMessages.forEach((message) => {
    if (getMessageContentText(message.content).trim()) output.push({ ...message, status: 'streaming' });
  });
  toolCalls.forEach((toolCall) => {
    if (toolCall.status !== 'done') {
      output.push({
        id: `tool-call-${toolCall.id}`,
        role: 'assistant',
        toolCalls: [{
          id: toolCall.id,
          name: toolCall.name,
          args: toolCall.args,
          status: toolCall.status,
        }],
      });
    }
  });

  return output;
}

function numericTurnId(value: unknown): number | undefined {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) && numberValue > 0 ? numberValue : undefined;
}

function buildQuestionCardsFromToolBuffer(
  buffer: ThreadMessageLike[],
  turnId: string | undefined,
  turnNumber: number | undefined,
  index: number,
): BuilderPublicSiteViewMessage[] {
  const cards: BuilderPublicSiteViewMessage[] = [];
  for (const message of buffer) {
    for (const toolCall of toolCallsFromMessage(message)) {
      const parsed = parseAskUserQuestionToolCall(toolCall);
      if (!parsed) continue;
      cards.push({
        uiKind: 'question-card',
        key: `question-${turnId ?? 'turn'}-${parsed.toolCallId}-${index}-${cards.length}`,
        questions: parsed.questions,
        toolCallId: parsed.toolCallId,
        status: 'waiting',
        turnId,
        turnNumber,
      });
    }
  }
  return cards;
}

function cancelWaitingQuestionCards(messages: BuilderPublicSiteViewMessage[]) {
  for (let index = 0; index < messages.length; index += 1) {
    const message = messages[index];
    if (message?.uiKind === 'question-card' && message.status === 'waiting') {
      messages[index] = { ...message, status: 'cancelled' };
    }
  }
}

function applyQuestionResolution(messages: BuilderPublicSiteViewMessage[], data: Record<string, unknown>, turnId: string | undefined, turnNumber: number | undefined) {
  const toolCallId = stringFrom(data.tool_call_id) ?? stringFrom(data.toolCallId);
  if (!toolCallId) return false;
  const questionIndex = messages.findIndex((message) => message.uiKind === 'question-card' && message.toolCallId === toolCallId);
  if (questionIndex === -1) return false;
  const card = messages[questionIndex];
  if (!card || card.uiKind !== 'question-card') return false;
  const resolved = parseToolActionResolvedEvent(data, card.questions);
  if (!resolved) return false;

  const completedAnswers = resolved.completedAnswers ?? {
    answers: {},
    skipped: resolved.status === 'skipped',
  };
  messages[questionIndex] = {
    ...card,
    status: resolved.status,
    completedAnswers,
  };

  if (resolved.status === 'answered' || resolved.status === 'skipped') {
    const hasSummary = messages.some((message) => message.uiKind === 'question-answer-summary' && message.toolCallId === toolCallId);
    if (!hasSummary) {
      messages.splice(questionIndex + 1, 0, {
        uiKind: 'question-answer-summary',
        key: `question-answer-summary-${toolCallId}`,
        questions: card.questions,
        completedAnswers,
        toolCallId,
        turnId,
        turnNumber,
      });
    }
  }
  return true;
}

function buildEventMessage(event: ThreadCustomEventLike, key: string, turnId: string | undefined, locale: BuilderPublicSiteLocale): BuilderPublicSiteViewMessage | undefined {
  const name = eventName(event);
  const data = eventData(event);
  const l = localeLabels(locale);

  if (shouldHideEvent(event)) return undefined;
  if (STARTUP_EVENT_NAMES.has(name)) return undefined;

  if (name.includes('cancel') || name.includes('abort')) {
    return { uiKind: 'cancel', key, message: String(data.message ?? l.cancelled), turnId };
  }
  if (name.includes('error') || name.includes('failed')) {
    return { uiKind: 'turn-error', key, message: String(data.message ?? data.error ?? l.defaultError), raw: event, turnId };
  }
  if (name === 'out_of_credit' || name === 'out-of-credit') {
    return { uiKind: 'out-of-credit', key, message: String(data.message ?? l.outOfCredit), turnId };
  }
  if (name === 'ask-user-question' || name === 'agent.ask_user_question') {
    const questions = parseBackendQuestions(data);
    const toolCallId = stringFrom(data.tool_call_id) ?? stringFrom(data.toolCallId);
    if (questions.length > 0 && toolCallId) {
      return { uiKind: 'question-card', key, questions, raw: data, toolCallId, status: 'waiting', turnId, turnNumber: numericTurnId(turnId) };
    }
    return undefined;
  }
  if (name === 'question-answer-summary') {
    return { uiKind: 'question-answer-summary', key, summary: String(data.summary ?? data.answer ?? data.result ?? ''), turnId, turnNumber: numericTurnId(turnId) };
  }

  return { uiKind: 'unsupported-custom-event', key, eventName: name || 'custom', raw: event, debugOnly: true, turnId };
}

function annotateFollowingUi(messages: BuilderPublicSiteViewMessage[]) {
  return messages.map((message, index) => {
    if (message.uiKind !== 'tool-action-list') return message;
    const hasFollowingRenderableUi = messages.slice(index + 1).some((item) => (
      item.uiKind !== 'unsupported-custom-event' &&
      !(item.uiKind === 'question-card' && item.status === 'waiting')
    ));
    return { ...message, hasFollowingRenderableUi };
  });
}

function flushToolBuffer(
  output: BuilderPublicSiteViewMessage[],
  buffer: ThreadMessageLike[],
  turnId: string | undefined,
  turnNumber: number | undefined,
  status: BuilderPublicSiteTurnView['status'],
  locale: BuilderPublicSiteLocale,
  index: number,
) {
  if (buffer.length === 0) return;
  const actions = getVisibleBuilderToolActions(buffer, { locale });
  if (actions.length === 0) {
    buffer.length = 0;
    return;
  }
  output.push({
    uiKind: 'tool-action-list',
    key: `tools-${turnId ?? 'turn'}-${index}`,
    messages: [...buffer],
    actions,
    isTurnEnded: !isActiveTurnStatus(status),
    turnId,
  });
  output.push(...buildQuestionCardsFromToolBuffer(buffer, turnId, turnNumber, index));
  buffer.length = 0;
}

export function toBuilderPublicSiteTurns(
  turns: ThreadTurnLike[] | undefined,
  options: { locale?: BuilderPublicSiteLocaleInput; includeDebugEvents?: boolean } = {},
): BuilderPublicSiteTurnView[] {
  const locale = resolveBuilderPublicSiteLocale(options.locale);
  return (turns ?? []).map((turn, turnIndex) => {
    const status = turnStatus(turn);
    const turnId = String(turn.turnId ?? turn.turn_id ?? turn.id ?? turnIndex);
    const turnNumber = numericTurnId(turn.turnId ?? turn.turn_id);
    const output: BuilderPublicSiteViewMessage[] = [];
    const pendingStartupEvents: ThreadCustomEventLike[] = [];
    const startupEventsForTurn: ThreadCustomEventLike[] = [];
    const toolBuffer: ThreadMessageLike[] = [];
    let startupMessageIndex = -1;
    let hasTerminalSignal = false;

    const finalizeStartupBuffer = (responded: boolean, index: number) => {
      if (pendingStartupEvents.length === 0) return;
      startupEventsForTurn.push(...pendingStartupEvents);
      pendingStartupEvents.length = 0;
      const existing = startupMessageIndex >= 0 ? output[startupMessageIndex] : undefined;
      const nextResponded = responded || (existing?.uiKind === 'agent-startup' && existing.headerPhase === 'responded');
      const steps = buildStartupStepsFromEvents(startupEventsForTurn, locale, nextResponded);
      if (steps.length === 0) return;
      const startupMessage: BuilderPublicSiteViewMessage = {
        uiKind: 'agent-startup',
        key: existing?.uiKind === 'agent-startup' ? existing.key : `startup-${turnId}-${index}`,
        steps,
        status: nextResponded ? 'done' : 'loading',
        headerPhase: nextResponded ? 'responded' : 'preparing',
        isTurnEnded: false,
        turnId,
      };
      if (startupMessageIndex >= 0) {
        output[startupMessageIndex] = startupMessage;
      } else {
        output.push(startupMessage);
        startupMessageIndex = output.length - 1;
      }
    };

    normalizeAgUiEventItems(turnItems(turn)).forEach((item, index) => {
      const message = unwrapMessage(item);
      if (message) {
        const reasoning = reasoningFromMessage(message);
        if (reasoning) {
          finalizeStartupBuffer(true, index);
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          output.push({ uiKind: 'thinking', key: idFor('thinking', message, index), content: reasoning, status: reasoningStatusFromMessage(message), turnId });
          return;
        }

        if (message.role === 'user' && contentIsRenderable(message)) {
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          output.push({ uiKind: 'user-text', key: idFor('user', message, index), content: getMessageContentText(message.content), createdAt: message.createdAt ?? message.created_at });
          return;
        }

        if (isAskUserQuestionToolResultMessage(message)) {
          finalizeStartupBuffer(true, index);
          return;
        }

        if (hasToolCalls(message) || isToolMessage(message)) {
          finalizeStartupBuffer(true, index);
          toolBuffer.push(message);
          return;
        }

        if (message.role === 'assistant' && contentIsRenderable(message)) {
          finalizeStartupBuffer(true, index);
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          output.push({ uiKind: 'assistant-text', key: idFor('assistant', message, index), content: getMessageContentText(message.content), createdAt: message.createdAt ?? message.created_at });
          return;
        }
      }

      const event = unwrapEvent(item);
      if (event) {
        const name = eventName(event);
        if (STARTUP_EVENT_NAMES.has(name)) {
          pendingStartupEvents.push(event);
          return;
        }
        if (name === 'agent.turn.summary' || eventType(event) === 'RUN_FINISHED') {
          hasTerminalSignal = true;
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          finalizeStartupBuffer(true, index);
          return;
        }
        if (name === 'agent.tool_action.resolved') {
          finalizeStartupBuffer(true, index);
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          if (applyQuestionResolution(output, eventData(event), turnId, turnNumber)) return;
        }
        if (name.includes('cancel') || name.includes('abort')) {
          finalizeStartupBuffer(true, index);
          cancelWaitingQuestionCards(output);
        }
        const eventMessage = buildEventMessage(event, idFor('event', event, index), turnId, locale);
        if (eventMessage && (eventMessage.uiKind !== 'unsupported-custom-event' || options.includeDebugEvents)) {
          finalizeStartupBuffer(true, index);
          flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, index);
          output.push(eventMessage);
        }
      }
    });

    finalizeStartupBuffer(false, 9998);
    flushToolBuffer(output, toolBuffer, turnId, turnNumber, status, locale, 9999);

    const effectiveStatus = effectiveTurnStatus(status, output, hasTerminalSignal);

    return {
      key: `turn-${turnId}`,
      turnId,
      status: effectiveStatus,
      messages: annotateFollowingUi(applyTurnStatusToMessages(output, effectiveStatus)),
    };
  });
}

export function toBuilderPublicSiteMessages(
  turns: ThreadTurnLike[] | undefined,
  options: { locale?: BuilderPublicSiteLocaleInput; includeDebugEvents?: boolean } = {},
): BuilderPublicSiteViewMessage[] {
  return toBuilderPublicSiteTurns(turns, options).flatMap((turn) => turn.messages);
}
