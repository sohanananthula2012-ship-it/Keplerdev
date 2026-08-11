import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { HttpAgent } from '@enter-pro/agent-client';
import {
  ThreadClient,
  ThreadManager,
  toThreadTurnsFromAgUiHistory,
  type ThreadTurn,
} from '@enter-pro/thread-client';
import type { BuilderPublicSiteLocaleInput, ThreadTurnLike } from './types';
import { resolveBuilderPublicSiteLocale } from './locales';
import { toBuilderPublicSiteMessages, toBuilderPublicSiteTurns } from './builderPublicSiteMessages';
import type { BuilderQuestionAnswers, BuilderPublicSiteViewMessage } from './types';
import { buildAnswerRequestBody } from './questions';
import {
  hasTerminalSignalInTurns,
  latestNumericTurnIdFromTurns,
  resolveClientRunningWithServerIdleGuard,
  shouldAcceptClientSnapshotWithServerIdleGuard,
} from './runtimeState';

export type CustomAgentThread = {
  id?: string;
  thread_id: string;
  version?: number;
  latest_history_turn_id?: number;
  running?: unknown | null;
  turns?: unknown[];
};

export type UseCustomAgentChatOptions = {
  agentId: string;
  proxyBase?: string;
  appToken?: string | (() => string | Promise<string>);
  initialThreadId?: string | null;
  locale?: BuilderPublicSiteLocaleInput;
};

export type UseCustomAgentChatResult = {
  agentId: string;
  threadId: string | null;
  activeThreadId: string | null;
  turns: readonly ThreadTurn[];
  renderableMessages: ReturnType<typeof toBuilderPublicSiteMessages>;
  viewMessages: ReturnType<typeof toBuilderPublicSiteMessages>;
  viewTurns: ReturnType<typeof toBuilderPublicSiteTurns>;
  isRunning: boolean;
  submittingQuestionToolCallId: string | null;
  lifecycle: string;
  error?: Error;
  sendMessage: (content: string) => Promise<void>;
  answerQuestion: (message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>, answers: BuilderQuestionAnswers) => Promise<void>;
  abort: () => void;
  activateThread: (threadId?: string | null, snapshot?: CustomAgentThread) => Promise<CustomAgentThread>;
  loadMoreHistory: () => Promise<void>;
};

function joinUrl(...parts: string[]) {
  return parts.map((part, index) => index === 0 ? part.replace(/\/+$/, '') : part.replace(/^\/+|\/+$/g, '')).join('/');
}

function tokenResolver(appToken?: string | (() => string | Promise<string>)) {
  return async () => typeof appToken === 'function' ? await appToken() : appToken ?? '';
}

function authHeaders(token: string): Record<string, string> {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function normalizeHistoryTurns(turns: unknown[] | undefined): Promise<ThreadTurn[]> {
  if (!Array.isArray(turns) || turns.length === 0) return [];
  return toThreadTurnsFromAgUiHistory({ turns: turns as unknown as Parameters<typeof toThreadTurnsFromAgUiHistory>[0]['turns'] });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function numericTurnId(value: unknown): number | undefined {
  const numberValue = Number(value);
  return Number.isFinite(numberValue) && numberValue > 0 ? numberValue : undefined;
}

function runningFallbackTurns(thread: CustomAgentThread): ThreadTurn[] {
  if (!isRecord(thread.running)) return [];
  const turnId = Number(thread.running.turn_id ?? thread.running.turnId ?? 1);
  const userMessage = isRecord(thread.running.user_message) ? thread.running.user_message : undefined;
  const content = typeof userMessage?.content === 'string' ? userMessage.content : '';
  if (!content.trim()) return [];
  return [{
    turn_id: Number.isFinite(turnId) && turnId > 0 ? turnId : 1,
    status: 'running',
    items: [{
      id: typeof userMessage?.id === 'string' ? userMessage.id : `running-user-${turnId || 1}`,
      role: 'user',
      content,
    }],
  } as unknown as ThreadTurn];
}

function appendQuestionResolutionToTurns(
  currentTurns: readonly ThreadTurn[],
  message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>,
  response: ReturnType<typeof buildAnswerRequestBody>,
): ThreadTurn[] {
  const targetTurnId = String(message.turnNumber ?? message.turnId ?? '');
  const resolutionEvent = {
    type: 'CUSTOM',
    name: 'agent.tool_action.resolved',
    value: {
      tool_call_id: message.toolCallId,
      status: response.response === 'skipped' ? 'skipped' : 'answered',
      response,
    },
  };
  const targetIndex = currentTurns.findIndex((turn, index) => {
    const turnLike = turn as unknown as ThreadTurnLike;
    const currentTurnId = String(turnLike.turn_id ?? turnLike.turnId ?? turnLike.id ?? index + 1);
    return Boolean(targetTurnId) && currentTurnId === targetTurnId;
  });
  const resolvedTargetIndex = targetIndex >= 0 ? targetIndex : currentTurns.length - 1;
  if (resolvedTargetIndex < 0) return [];
  const targetTurn = currentTurns[resolvedTargetIndex] as unknown as ThreadTurnLike | undefined;
  const existingItems = targetTurn?.items ?? targetTurn?.messages ?? targetTurn?.events ?? targetTurn?.history;
  if (Array.isArray(existingItems) && existingItems.some((item) => {
    if (!item || typeof item !== 'object') return false;
    const record = item as Record<string, unknown>;
    const value = record.value && typeof record.value === 'object' ? record.value as Record<string, unknown> : {};
    return record.name === 'agent.tool_action.resolved'
      && String(value.tool_call_id ?? value.toolCallId ?? '') === message.toolCallId;
  })) {
    return [...currentTurns];
  }

  const nextTurns = currentTurns.map((turn, index) => {
    const turnLike = turn as unknown as ThreadTurnLike;
    if (index !== resolvedTargetIndex) return turn;
    if (Array.isArray(turnLike.items)) {
      return { ...turnLike, items: [...turnLike.items, resolutionEvent] } as unknown as ThreadTurn;
    }
    if (Array.isArray(turnLike.messages)) {
      return { ...turnLike, messages: [...turnLike.messages, resolutionEvent] } as unknown as ThreadTurn;
    }
    if (Array.isArray(turnLike.events)) {
      return { ...turnLike, events: [...turnLike.events, resolutionEvent] } as unknown as ThreadTurn;
    }
    if (Array.isArray(turnLike.history)) {
      return { ...turnLike, history: [...turnLike.history, resolutionEvent] } as unknown as ThreadTurn;
    }
    return { ...turnLike, items: [resolutionEvent] } as unknown as ThreadTurn;
  });
  return nextTurns;
}

export function useCustomAgentChat(params: UseCustomAgentChatOptions): UseCustomAgentChatResult {
  const locale = resolveBuilderPublicSiteLocale(params.locale);
  const proxyBase = params.proxyBase ?? '/api';
  const proxyUrl = useMemo(() => joinUrl(proxyBase, 'custom-agent', params.agentId), [params.agentId, proxyBase]);
  const managerRef = useRef(new ThreadManager());
  const agentsRef = useRef(new Map<string, HttpAgent>());
  const activeThreadIdRef = useRef<string | null>(params.initialThreadId ?? null);
  const activationSeqRef = useRef(0);
  const threadCacheRef = useRef(new Map<string, { thread: CustomAgentThread; turns: ThreadTurn[] }>());
  const lastActiveTurnIdRef = useRef<number | null>(null);
  const serverIdleConfirmedRef = useRef(new Set<string>());
  const [activeThreadId, setActiveThreadId] = useState<string | null>(params.initialThreadId ?? null);
  const [turns, setTurns] = useState<readonly ThreadTurn[]>([]);
  const [optimisticTurn, setOptimisticTurn] = useState<ThreadTurnLike | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [submittingQuestionToolCallId, setSubmittingQuestionToolCallId] = useState<string | null>(null);
  const [lifecycle, setLifecycle] = useState('idle');
  const [error, setError] = useState<Error | undefined>();

  const getToken = useMemo(() => tokenResolver(params.appToken), [params.appToken]);

  const clearServerIdleConfirmed = useCallback((threadId?: string | null) => {
    if (!threadId) return;
    serverIdleConfirmedRef.current.delete(threadId);
  }, []);

  const setRunningFromClient = useCallback((threadId: string, clientIsRunning: boolean, nextLifecycle?: string) => {
    if (activeThreadIdRef.current !== threadId) return false;
    const nextIsRunning = resolveClientRunningWithServerIdleGuard({
      threadId,
      clientIsRunning,
      serverIdleConfirmedThreadIds: serverIdleConfirmedRef.current,
    });
    setIsRunning(nextIsRunning);
    setLifecycle(nextIsRunning ? (nextLifecycle || 'running') : (nextLifecycle === 'error' ? 'error' : 'idle'));
    return nextIsRunning;
  }, []);

  const shouldAcceptClientSnapshot = useCallback((threadId: string) => (
    shouldAcceptClientSnapshotWithServerIdleGuard({
      threadId,
      serverIdleConfirmedThreadIds: serverIdleConfirmedRef.current,
    })
  ), []);

  const applyRunningSnapshot = useCallback((threadId: string, running: unknown | null | undefined) => {
    if (running === null) {
      serverIdleConfirmedRef.current.add(threadId);
    } else if (running !== undefined) {
      serverIdleConfirmedRef.current.delete(threadId);
    }
    const nextIsRunning = running != null;
    if (nextIsRunning && isRecord(running)) {
      const turnId = numericTurnId(running.turn_id ?? running.turnId);
      if (turnId != null) lastActiveTurnIdRef.current = turnId;
    }
    if (activeThreadIdRef.current === threadId) {
      setIsRunning(nextIsRunning);
      setLifecycle(nextIsRunning ? 'running' : 'idle');
    }
  }, []);

  const fetchJson = useCallback(async <T,>(url: string, init?: RequestInit): Promise<T> => {
    const token = await getToken();
    const resp = await fetch(url, {
      ...init,
      headers: {
        ...(init?.headers ?? {}),
        ...authHeaders(token),
      },
    });
    if (!resp.ok) {
      const detail = await resp.text().catch(() => '');
      throw new Error(`Custom-agent proxy request failed: ${resp.status}${detail ? ` ${detail}` : ''}`);
    }
    return resp.json() as Promise<T>;
  }, [getToken]);

  const listTurns = useCallback(async (threadId: string, start: number, end: number) => {
    const body = await fetchJson<{ turns: unknown[] }>(`${proxyUrl}/threads/${threadId}/turns?start_turn=${start}&end_turn=${end}`);
    return normalizeHistoryTurns(body.turns);
  }, [fetchJson, proxyUrl]);

  const getOrCreateClient = useCallback(async (threadId: string, latestHistoryTurnId = 0) => {
    const key = `custom-agent-${threadId}`;
    const existing = managerRef.current.get(key);
    if (existing) return existing;

    const agentRef: { current: HttpAgent | null } = { current: null };
    const agent = new HttpAgent({
      threadId,
      url: () => `${proxyUrl}/run`,
      token: getToken,
      abortUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        return turnId == null ? '' : `${proxyUrl}/threads/${threadId}/turns/${turnId}/cancel`;
      },
      resumeUrl: async () => {
        const turnId = agentRef.current?.activeTurnId;
        if (turnId == null) throw new Error('No running turn');
        return `${proxyUrl}/threads/${threadId}/turns/${turnId}/events`;
      },
    });
    agentRef.current = agent;
    agentsRef.current.set(key, agent);

    const client = new ThreadClient({
      threadId,
      agent,
      historyMessageLoader: {
        async load(_threadId, start, end) {
          return listTurns(threadId, start, end);
        },
        async loadSince() {
          return [];
        },
      },
      historyMessagePagination: {
        turnSize: 30,
        endTurn: Math.max(0, Number(latestHistoryTurnId || 0)),
      },
    });

    client.subscribe((event) => {
      if (activeThreadIdRef.current !== threadId) return;

      const syncLastActiveTurnIdFromAgent = () => {
        const turnId = agentRef.current?.activeTurnId;
        const numericTurnIdValue = numericTurnId(turnId);
        if (numericTurnIdValue != null) lastActiveTurnIdRef.current = numericTurnIdValue;
      };

      const markLatestTurnActive = () => {
        const turnId = latestNumericTurnIdFromTurns(client.turns as readonly unknown[]);
        if (turnId != null) lastActiveTurnIdRef.current = turnId;
      };

      const applyClientState = (opts: { forceIdle?: boolean } = {}) => {
        const cachedTurns = threadCacheRef.current.get(threadId)?.turns ?? [];
        if (shouldAcceptClientSnapshot(threadId)) {
          if (client.turns.length > 0) {
            setOptimisticTurn(null);
            setTurns(client.turns);
          } else if (cachedTurns.length === 0) {
            setTurns(client.turns);
          }
        } else {
          setOptimisticTurn(null);
        }
        const hasTerminalSignal = opts.forceIdle || hasTerminalSignalInTurns(client.turns as readonly unknown[]);
        if (hasTerminalSignal) markLatestTurnActive();
        const acceptedRunning = setRunningFromClient(
          threadId,
          hasTerminalSignal ? false : client.isAgentRunning,
          hasTerminalSignal ? 'idle' : client.status,
        );
        if (acceptedRunning) syncLastActiveTurnIdFromAgent();
      };

      if (event.type === 'turns' || event.type === 'lifecycle' || event.type === 'agentRunning') {
        const eventRunning = event.type === 'agentRunning' && typeof (event as { isRunning?: unknown }).isRunning === 'boolean'
          ? Boolean((event as { isRunning?: unknown }).isRunning)
          : undefined;
        applyClientState({ forceIdle: eventRunning === false });
      } else if (event.type === 'customEvent') {
        const customEventName = ((event as { customEvent?: { event?: { name?: string } } }).customEvent?.event?.name ?? '');
        if (customEventName === 'agent.turn.summary') {
          applyClientState({ forceIdle: true });
        }
      }
    });

    managerRef.current.register(key, client);
    return client;
  }, [getToken, listTurns, proxyUrl, setRunningFromClient, shouldAcceptClientSnapshot]);

  const fetchThread = useCallback(async (threadId: string): Promise<CustomAgentThread> => {
    return fetchJson<CustomAgentThread>(`${proxyUrl}/threads/${threadId}`);
  }, [fetchJson, proxyUrl]);

  const createThread = useCallback(async (): Promise<CustomAgentThread> => {
    return fetchJson<CustomAgentThread>(`${proxyUrl}/threads`, { method: 'POST' });
  }, [fetchJson, proxyUrl]);

  const applyThreadSnapshot = useCallback(async (thread: CustomAgentThread) => {
    const resolvedThreadId = thread.thread_id || thread.id;
    if (!resolvedThreadId) return undefined;
    const normalizedTurns = Array.isArray(thread.turns) ? await normalizeHistoryTurns(thread.turns) : [];
    const fallbackTurns = normalizedTurns.length === 0 ? runningFallbackTurns(thread) : [];
    const historyTurns = normalizedTurns.length > 0 ? normalizedTurns : fallbackTurns;
    threadCacheRef.current.set(resolvedThreadId, { thread: { ...thread, thread_id: resolvedThreadId }, turns: historyTurns });
    return {
      resolvedThreadId,
      historyTurns,
      isRunningFallback: normalizedTurns.length === 0 && fallbackTurns.length > 0,
    };
  }, []);

  const applyAuthoritativeThreadSnapshot = useCallback(async (
    thread: CustomAgentThread,
    fallbackThreadId?: string | null,
  ) => {
    const resolvedThreadId = thread.thread_id || thread.id || fallbackThreadId;
    if (!resolvedThreadId) return undefined;
    const applied = await applyThreadSnapshot({ ...thread, thread_id: resolvedThreadId });
    if (!applied) return undefined;
    if (activeThreadIdRef.current === resolvedThreadId) {
      setOptimisticTurn(null);
      setTurns(applied.historyTurns);
      applyRunningSnapshot(resolvedThreadId, thread.running);
    }
    return applied;
  }, [applyRunningSnapshot, applyThreadSnapshot]);

  const activateThread = useCallback(async (threadId?: string | null, snapshot?: CustomAgentThread) => {
    const sequence = ++activationSeqRef.current;
    setError(undefined);
    setOptimisticTurn(null);

    if (!threadId) {
      activeThreadIdRef.current = null;
      lastActiveTurnIdRef.current = null;
      setActiveThreadId(null);
      setTurns([]);
      setIsRunning(false);
      setLifecycle('idle');
    } else {
      activeThreadIdRef.current = threadId;
      setActiveThreadId(threadId);
      const key = `custom-agent-${threadId}`;
      const cached = threadCacheRef.current.get(threadId);
      const existingClient = managerRef.current.get(key);
      if (snapshot) {
        const applied = await applyAuthoritativeThreadSnapshot(snapshot, threadId);
        if (sequence !== activationSeqRef.current) return { ...snapshot, thread_id: snapshot.thread_id || snapshot.id || threadId };
        if (applied && applied.resolvedThreadId === threadId) setTurns(applied.historyTurns);
      } else if (existingClient?.turns.length) {
        if (shouldAcceptClientSnapshot(threadId)) {
          setTurns(existingClient.turns);
        } else if (cached) {
          setTurns(cached.turns);
        }
        setRunningFromClient(threadId, existingClient.isAgentRunning, existingClient.status);
      } else if (cached) {
        setTurns(cached.turns);
        applyRunningSnapshot(threadId, cached.thread.running);
      } else {
        setTurns([]);
        setIsRunning(false);
        setLifecycle('loading');
      }
    }

    const thread = threadId ? await fetchThread(threadId) : await createThread();
    const resolvedThreadId = thread.thread_id || thread.id;
    if (!resolvedThreadId) throw new Error('Custom-agent proxy did not return a thread id.');
    if (sequence !== activationSeqRef.current) return { ...thread, thread_id: resolvedThreadId };

    activeThreadIdRef.current = resolvedThreadId;
    setActiveThreadId(resolvedThreadId);
    const applied = await applyAuthoritativeThreadSnapshot({ ...snapshot, ...thread, thread_id: resolvedThreadId }, resolvedThreadId);
    const historyTurns = applied?.historyTurns ?? [];

    const key = `custom-agent-${resolvedThreadId}`;
    const latestHistoryTurnId = Number(thread.latest_history_turn_id || 0);
    const client = await getOrCreateClient(resolvedThreadId, latestHistoryTurnId);
    if (sequence !== activationSeqRef.current) return { ...thread, thread_id: resolvedThreadId };
    await managerRef.current.resume(key);
    if (sequence !== activationSeqRef.current) return { ...thread, thread_id: resolvedThreadId };
    setActiveThreadId(resolvedThreadId);
    setTurns(
      shouldAcceptClientSnapshot(resolvedThreadId) && client.turns.length > 0
        ? client.turns
        : historyTurns,
    );
    setRunningFromClient(resolvedThreadId, client.isAgentRunning, client.status);

    const agent = agentsRef.current.get(key);
    if (thread.running != null && agent && sequence === activationSeqRef.current) {
      clearServerIdleConfirmed(resolvedThreadId);
      await agent.resumeTurn(thread.running as unknown as Parameters<HttpAgent['resumeTurn']>[0]);
    }

    return { ...thread, thread_id: resolvedThreadId };
  }, [applyAuthoritativeThreadSnapshot, applyRunningSnapshot, clearServerIdleConfirmed, createThread, fetchThread, getOrCreateClient, setRunningFromClient, shouldAcceptClientSnapshot]);

  useEffect(() => {
    if (!params.initialThreadId) return;
    void activateThread(params.initialThreadId).catch((cause) => setError(cause instanceof Error ? cause : new Error(String(cause))));
  }, [activateThread, params.initialThreadId]);

  useEffect(() => {
    if (isRunning || !activeThreadId) return;
    const turnId = lastActiveTurnIdRef.current;
    if (turnId == null) return;
    let cancelled = false;

    void (async () => {
      try {
        const thread = await fetchThread(activeThreadId);
        if (cancelled || activeThreadIdRef.current !== activeThreadId) return;
        await applyAuthoritativeThreadSnapshot({ ...thread, thread_id: thread.thread_id || thread.id || activeThreadId }, activeThreadId);
      } catch {
        // Final metadata refresh is best-effort; the live ThreadClient state is already idle.
      } finally {
        if (!cancelled && lastActiveTurnIdRef.current === turnId) {
          lastActiveTurnIdRef.current = null;
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [activeThreadId, applyAuthoritativeThreadSnapshot, fetchThread, isRunning]);

  const sendMessage = useCallback(async (content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;
    setError(undefined);
    const thread = activeThreadId ? { thread_id: activeThreadId } : await activateThread(null);
    const optimisticId = `optimistic-${Date.now()}`;
    clearServerIdleConfirmed(thread.thread_id);
    setIsRunning(true);
    setLifecycle('running');
    setOptimisticTurn({
      id: optimisticId,
      status: 'running',
      items: [{
        id: `${optimisticId}-user`,
        role: 'user',
        content: trimmed,
      }],
    });
    try {
      const client = await getOrCreateClient(thread.thread_id);
      const key = `custom-agent-${thread.thread_id}`;
      await managerRef.current.resume(key);
      await client.sendMessage({ content: trimmed });
      setOptimisticTurn(null);
      if (shouldAcceptClientSnapshot(thread.thread_id)) setTurns(client.turns);
      const snapshot = await fetchThread(thread.thread_id);
      await applyAuthoritativeThreadSnapshot({ ...snapshot, thread_id: snapshot.thread_id || snapshot.id || thread.thread_id }, thread.thread_id);
    } catch (cause) {
      setOptimisticTurn(null);
      setIsRunning(false);
      setLifecycle('error');
      const nextError = cause instanceof Error ? cause : new Error(String(cause));
      setError(nextError);
      throw nextError;
    }
  }, [activateThread, activeThreadId, applyAuthoritativeThreadSnapshot, clearServerIdleConfirmed, fetchThread, getOrCreateClient, shouldAcceptClientSnapshot]);

  const answerQuestion = useCallback(async (
    message: Extract<BuilderPublicSiteViewMessage, { uiKind: 'question-card' }>,
    answers: BuilderQuestionAnswers,
  ) => {
    if (!activeThreadId) throw new Error('No active thread is selected.');
    if (!message.toolCallId) throw new Error('Question card is missing a tool call id.');
    const turnNumber = message.turnNumber ?? Number(message.turnId);
    if (!Number.isFinite(turnNumber) || turnNumber <= 0) throw new Error('Question card is missing a serving turn id.');
    setSubmittingQuestionToolCallId(message.toolCallId);
    setLifecycle('answering-question');
    setError(undefined);
    try {
      const token = await getToken();
      const answerBody = buildAnswerRequestBody(message.questions, answers);
      const resp = await fetch(`${proxyUrl}/threads/${encodeURIComponent(activeThreadId)}/turns/${turnNumber}/tool-calls/${encodeURIComponent(message.toolCallId)}/answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders(token),
        },
        body: JSON.stringify(answerBody),
      });
      if (!resp.ok && resp.status !== 409) {
        const detail = await resp.text().catch(() => '');
        throw new Error(`Custom-agent proxy request failed: ${resp.status}${detail ? ` ${detail}` : ''}`);
      }
      const hadConflict = resp.status === 409;
      if (hadConflict) {
        setTurns((current) => appendQuestionResolutionToTurns(current, message, answerBody));
      }
      const thread = await fetchThread(activeThreadId);
      const applied = await applyAuthoritativeThreadSnapshot({ ...thread, thread_id: thread.thread_id || thread.id || activeThreadId }, activeThreadId);
      if (activeThreadIdRef.current === activeThreadId && applied) {
        if (hadConflict && !applied.isRunningFallback && applied.historyTurns.length > 0) {
          setTurns(appendQuestionResolutionToTurns(applied.historyTurns, message, answerBody));
        } else if (!hadConflict && (!applied.isRunningFallback || turns.length === 0)) {
          setTurns(applied.historyTurns);
        }
        if (thread.running) {
          const key = `custom-agent-${activeThreadId}`;
          const latestHistoryTurnId = Number(thread.latest_history_turn_id || 0);
          const client = await getOrCreateClient(activeThreadId, latestHistoryTurnId);
          await managerRef.current.resume(key).catch(() => undefined);
          const agent = agentsRef.current.get(key);
          clearServerIdleConfirmed(activeThreadId);
          await agent?.resumeTurn(thread.running as unknown as Parameters<HttpAgent['resumeTurn']>[0]).catch(() => undefined);
          const snapshotAfterResume = await fetchThread(activeThreadId).catch(() => undefined);
          const appliedAfterResume = snapshotAfterResume
            ? await applyAuthoritativeThreadSnapshot({ ...snapshotAfterResume, thread_id: snapshotAfterResume.thread_id || snapshotAfterResume.id || activeThreadId }, activeThreadId)
            : undefined;
          if (activeThreadIdRef.current === activeThreadId) {
            const nextTurns = appliedAfterResume?.historyTurns.length
              ? appliedAfterResume.historyTurns
              : shouldAcceptClientSnapshot(activeThreadId)
                ? client.turns
                : [];
            if (nextTurns.length > 0) {
              setTurns(hadConflict ? appendQuestionResolutionToTurns(nextTurns, message, answerBody) : nextTurns);
            }
            if (!snapshotAfterResume) setRunningFromClient(activeThreadId, client.isAgentRunning, client.status);
          }
        }
      }
    } catch (cause) {
      const nextError = cause instanceof Error ? cause : new Error(String(cause));
      setLifecycle('idle');
      setError(nextError);
      throw nextError;
    } finally {
      setSubmittingQuestionToolCallId(null);
    }
  }, [activeThreadId, applyAuthoritativeThreadSnapshot, clearServerIdleConfirmed, fetchThread, getOrCreateClient, getToken, proxyUrl, setRunningFromClient, shouldAcceptClientSnapshot, turns.length]);

  const abort = useCallback(() => {
    setOptimisticTurn(null);
    managerRef.current.getActive()?.abort();
  }, []);

  const loadMoreHistory = useCallback(async () => {
    await managerRef.current.getActive()?.loadMoreHistoryMessages();
  }, []);

  const projectedTurns = useMemo(() => {
    const baseTurns = turns.map((turn) => ({ ...(turn as unknown as ThreadTurnLike) }));
    return optimisticTurn && isRunning ? [...baseTurns, optimisticTurn] : baseTurns;
  }, [isRunning, optimisticTurn, turns]);

  const viewTurns = useMemo(() => toBuilderPublicSiteTurns(projectedTurns, { locale }), [locale, projectedTurns]);
  const viewMessages = useMemo(() => toBuilderPublicSiteMessages(projectedTurns, { locale }), [locale, projectedTurns]);

  return useMemo(() => ({
    agentId: params.agentId,
    threadId: activeThreadId,
    activeThreadId,
    turns,
    renderableMessages: viewMessages,
    viewMessages,
    viewTurns,
    isRunning,
    submittingQuestionToolCallId,
    lifecycle,
    error,
    sendMessage,
    answerQuestion,
    abort,
    activateThread,
    loadMoreHistory,
  }), [params.agentId, activeThreadId, turns, viewMessages, viewTurns, isRunning, submittingQuestionToolCallId, lifecycle, error, sendMessage, answerQuestion, abort, activateThread, loadMoreHistory]);
}
