# Thread and Run Flow

Use this as the default implementation sequence.

## First message

1. Check whether the host conversation already has a mapping for `agent_id`.
2. If no mapping exists, create a thread with `{}`.
3. Persist `agent_id + thread_id + version`.
4. Send `/run` with `threadId` and one user message.
5. Stream AG-UI events into UI/runtime state.
6. On completion, refresh `GET /threads/{thread_id}` and optionally `GET /turns?start_turn=N&end_turn=N`.

## Follow-up message

1. Load `thread_id` from the host mapping.
2. If local state says a run is active, resume or wait instead of starting another run.
3. Send `/run` with the same `threadId` and the new user message.
4. Stream events.
5. Refresh metadata after completion.

## Page reload

1. Load thread mapping from host persistence.
2. Call `GET /threads/{thread_id}`.
3. If `running` exists, resume with `/turns/{turn_id}/events`.
4. Load historical turns with `/turns?start_turn=&end_turn=`.
5. Rebuild UI messages from AG-UI history.

## Cancel

1. Read active turn id from runtime (`HttpAgent.activeTurnId`) or thread state.
2. POST cancel endpoint.
3. Mark local turn cancelled and stop streaming.
4. Refresh thread state/history.

## Duplicate-run guard

Before calling `/run`, make sure:

- The UI/runtime status is active and not already streaming.
- The thread state does not have a `running` turn unless you intend to resume it.
- A previous network failure was reconciled through thread state/history.

This prevents duplicate turns after network interruptions.
