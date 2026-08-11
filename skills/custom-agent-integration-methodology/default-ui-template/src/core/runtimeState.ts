export function resolveClientRunningWithServerIdleGuard({
  threadId,
  clientIsRunning,
  serverIdleConfirmedThreadIds,
}: {
  threadId: string;
  clientIsRunning: boolean;
  serverIdleConfirmedThreadIds: ReadonlySet<string>;
}) {
  return clientIsRunning && serverIdleConfirmedThreadIds.has(threadId) ? false : clientIsRunning;
}

export function shouldAcceptClientSnapshotWithServerIdleGuard({
  threadId,
  serverIdleConfirmedThreadIds,
}: {
  threadId: string;
  serverIdleConfirmedThreadIds: ReadonlySet<string>;
}) {
  return !serverIdleConfirmedThreadIds.has(threadId);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === 'object' && !Array.isArray(value));
}

function turnItems(turn: unknown): unknown[] {
  if (!isRecord(turn)) return [];
  const items = turn.items ?? turn.messages ?? turn.events ?? turn.history;
  return Array.isArray(items) ? items : [];
}

function itemEvent(item: unknown): Record<string, unknown> | undefined {
  if (!isRecord(item)) return undefined;
  if (isRecord(item.event)) return item.event;
  if (isRecord(item.custom)) return item.custom;
  if (item.kind === 'custom' && isRecord(item.value)) return item.value;
  if ('name' in item || 'type' in item || 'event' in item) return item;
  return undefined;
}

function eventName(event: Record<string, unknown>) {
  const raw = event.name ?? event.event ?? event.type;
  return typeof raw === 'string' ? raw : '';
}

export function hasTerminalSignalInTurns(turns: readonly unknown[]) {
  const latestTurn = turns[turns.length - 1];
  if (!latestTurn) return false;
  return turnItems(latestTurn).some((item) => {
    const event = itemEvent(item);
    if (!event) return false;
    const name = eventName(event);
    const type = String(event.type ?? '').toUpperCase();
    return name === 'agent.turn.summary' || type === 'RUN_FINISHED' || type === 'RUN_ERROR';
  });
}

export function latestNumericTurnIdFromTurns(turns: readonly unknown[]) {
  const latestTurn = turns[turns.length - 1];
  if (!isRecord(latestTurn)) return undefined;
  const raw = latestTurn.turn_id ?? latestTurn.turnId ?? latestTurn.id;
  const numberValue = Number(raw);
  return Number.isFinite(numberValue) && numberValue > 0 ? numberValue : undefined;
}
