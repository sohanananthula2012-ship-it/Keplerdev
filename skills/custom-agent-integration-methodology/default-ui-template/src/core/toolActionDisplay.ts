import type { BuilderPublicSiteLocaleInput, BuilderToolActionView, ThreadMessageLike, ToolCallLike, ToolDisplayRegistry } from './types';
import { getToolDefinition, normalizeBuilderToolRegistryKey, DEFAULT_TOOL_DISPLAY_REGISTRY } from './toolRegistry';
import { resolveBuilderPublicSiteLocale } from './locales';
import { compactText, firstString, getMessageContentText, tryParseJsonObject } from './messageContent';
import {
  isAskUserQuestionToolName,
  parseBackendQuestions,
  questionToolDescription,
} from './questions';

const DEDUPE_REGISTRY_KEYS = new Set(['read', 'grep', 'glob']);

function toolCallsFromMessage(message: ThreadMessageLike): ToolCallLike[] {
  const toolCalls = message.toolCalls ?? message.tool_calls;
  return Array.isArray(toolCalls) ? toolCalls : [];
}

function toolCallName(toolCall: ToolCallLike): string {
  return firstString(toolCall.name, toolCall.function?.name, toolCall.type) ?? 'tool';
}

function toolCallArgs(toolCall: ToolCallLike): Record<string, unknown> | undefined {
  return (
    tryParseJsonObject(toolCall.args) ??
    tryParseJsonObject(toolCall.arguments) ??
    tryParseJsonObject(toolCall.function?.arguments) ??
    tryParseJsonObject(toolCall.input)
  );
}

function toolResultPayload(message: ThreadMessageLike): Record<string, unknown> | undefined {
  return tryParseJsonObject(message.content) ?? tryParseJsonObject(message.metadata);
}

function descriptionFromArgs(toolName: string, args: Record<string, unknown> | undefined, locale: ReturnType<typeof resolveBuilderPublicSiteLocale>) {
  if (!args) return undefined;
  const normalized = normalizeBuilderToolRegistryKey(toolName);
  if (normalized === 'websearch') return compactText(firstString(args.query, args.search, args.keyword));
  if (normalized === 'webfetch') return compactText(firstString(args.url, args.href, args.query));
  if (normalized === 'skill') return compactText(firstString(args.skill, args.skillName, args.skill_name, args.name));
  if (normalized === 'bash') return compactText(firstString(args.command, args.cmd));
  if (isAskUserQuestionToolName(toolName)) {
    const questions = parseBackendQuestions(args);
    return questionToolDescription(questions, locale) || compactText(firstString(args.question));
  }
  return compactText(firstString(args.description, args.path, args.file_path, args.pattern, args.query, args.url, args.name, args.title));
}

function descriptionFromResult(message: ThreadMessageLike) {
  const payload = toolResultPayload(message);
  return compactText(firstString(payload?.description, payload?.summary, payload?.path, payload?.query, getMessageContentText(message.content)));
}

function actionKey(message: ThreadMessageLike, toolCall?: ToolCallLike, index = 0) {
  return String(toolCall?.id ?? toolCall?.toolCallId ?? message.toolCallId ?? message.tool_call_id ?? message.id ?? `${message.name ?? 'tool'}-${index}`);
}

function isToolResultMessage(message: ThreadMessageLike) {
  return message.role === 'tool' || Boolean(message.toolCallId || message.tool_call_id);
}

function isAssistantToolCallMessage(message: ThreadMessageLike) {
  return message.role === 'assistant' && toolCallsFromMessage(message).length > 0;
}

export function getVisibleBuilderToolActions(
  messages: ThreadMessageLike[],
  options: { locale?: BuilderPublicSiteLocaleInput; registry?: ToolDisplayRegistry } = {},
): BuilderToolActionView[] {
  const locale = resolveBuilderPublicSiteLocale(options.locale);
  const registry = options.registry ?? DEFAULT_TOOL_DISPLAY_REGISTRY;
  const actionMap = new Map<string, BuilderToolActionView>();
  const ordered: BuilderToolActionView[] = [];
  const toolResults = new Map<string, ThreadMessageLike>();
  const assistantToolCallIds = new Set<string>();

  for (const message of messages) {
    if (isAssistantToolCallMessage(message)) {
      toolCallsFromMessage(message).forEach((toolCall, index) => {
        assistantToolCallIds.add(actionKey(message, toolCall, index));
      });
    }
    if (isToolResultMessage(message)) {
      toolResults.set(actionKey(message), message);
    }
  }

  function upsert(action: BuilderToolActionView) {
    const dedupeKey = DEDUPE_REGISTRY_KEYS.has(action.registryKey) && action.description
      ? `${action.registryKey}:${action.description}`
      : action.key;
    const existing = actionMap.get(dedupeKey);
    if (existing) {
      existing.status = action.status === 'finished' ? 'finished' : existing.status;
      existing.description = existing.description || action.description;
      return;
    }
    actionMap.set(dedupeKey, action);
    ordered.push(action);
  }

  for (const message of messages) {
    if (isAssistantToolCallMessage(message)) {
      toolCallsFromMessage(message).forEach((toolCall, index) => {
        const toolName = toolCallName(toolCall);
        const registryKey = normalizeBuilderToolRegistryKey(toolName);
        const definition = getToolDefinition(registryKey, registry);
        const args = toolCallArgs(toolCall);
        const key = actionKey(message, toolCall, index);
        const resultMessage = toolResults.get(key);
        const hasAskUserQuestion = isAskUserQuestionToolName(toolName) && parseBackendQuestions(args).length > 0;
        const status = toolCall.status === 'error' ? 'error' : resultMessage || toolCall.status === 'done' || toolCall.result || hasAskUserQuestion ? 'finished' : 'loading';
        upsert({
          key,
          registryKey,
          label: definition.getLabel(status, locale),
          description: descriptionFromArgs(toolName, args, locale),
          status,
          icon: definition.icon,
        });
      });
      continue;
    }

    if (isToolResultMessage(message)) {
      const toolName = firstString(message.name, message.metadata?.toolName, message.metadata?.tool_name) ?? 'tool';
      if (isAskUserQuestionToolName(toolName) || assistantToolCallIds.has(actionKey(message))) continue;
      const registryKey = normalizeBuilderToolRegistryKey(toolName);
      const definition = getToolDefinition(registryKey, registry);
      upsert({
        key: actionKey(message),
        registryKey,
        label: definition.getLabel('finished', locale),
        description: descriptionFromResult(message),
        status: 'finished',
        icon: definition.icon,
      });
    }
  }

  return ordered.map((action) => {
    const definition = getToolDefinition(action.registryKey, registry);
    const status = action.status === 'loading' ? 'loading' : action.status === 'error' ? 'error' : 'finished';
    return { ...action, label: definition.getLabel(status, locale), status };
  });
}
