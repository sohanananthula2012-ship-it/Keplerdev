import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import { build } from 'esbuild';

const tempDir = await mkdtemp(join(tmpdir(), 'custom-agent-question-core-'));
const outfile = join(tempDir, 'verify-question-core.mjs');

const entry = String.raw`
import assert from 'node:assert/strict';
import * as questions from './src/core/questions.ts';
import * as toolActions from './src/core/toolActionDisplay.ts';
import * as messages from './src/core/builderPublicSiteMessages.ts';
import * as runtimeState from './src/core/runtimeState.ts';

const idleConfirmedThreads = new Set(['thread-idle']);
assert.equal(
  runtimeState.resolveClientRunningWithServerIdleGuard({
    threadId: 'thread-idle',
    clientIsRunning: true,
    serverIdleConfirmedThreadIds: idleConfirmedThreads,
  }),
  false,
  'server-confirmed idle should block stale client running=true',
);
assert.equal(
  runtimeState.resolveClientRunningWithServerIdleGuard({
    threadId: 'thread-active',
    clientIsRunning: true,
    serverIdleConfirmedThreadIds: idleConfirmedThreads,
  }),
  true,
  'new active thread without an idle guard should accept client running=true',
);
assert.equal(
  runtimeState.resolveClientRunningWithServerIdleGuard({
    threadId: 'thread-idle',
    clientIsRunning: false,
    serverIdleConfirmedThreadIds: idleConfirmedThreads,
  }),
  false,
  'client running=false should stay false with or without an idle guard',
);
assert.equal(
  runtimeState.shouldAcceptClientSnapshotWithServerIdleGuard({
    threadId: 'thread-idle',
    serverIdleConfirmedThreadIds: idleConfirmedThreads,
  }),
  false,
  'server-confirmed idle should block stale client turns/status snapshots',
);
assert.equal(
  runtimeState.shouldAcceptClientSnapshotWithServerIdleGuard({
    threadId: 'thread-active',
    serverIdleConfirmedThreadIds: idleConfirmedThreads,
  }),
  true,
  'non-idle-guarded threads should still accept client snapshots',
);

const repeatedArgs = {
  questions: [
    {
      question: 'Pick a topic',
      options: [{ label: 'Schedule' }, { label: 'Cities' }],
      multiSelect: true,
    },
    {
      question: 'Pick a topic',
      header: 'Follow-up',
      options: [{ label: 'Teams' }, { label: 'Tickets' }],
    },
  ],
};
const parsedRepeated = questions.parseBackendQuestions(repeatedArgs);
assert.equal(parsedRepeated.length, 2, 'valid repeated questions should parse');
assert.equal(parsedRepeated[0].multiSelect, true, 'multiSelect should be preserved');

const body = questions.buildAnswerRequestBody(parsedRepeated, {
  skipped: false,
  answers: {
    'Pick a topic': { selected_options: ['Schedule', 'Cities'], other_text: 'Opening match' },
    'Pick a topic__2': { selected_options: ['Teams'], other_text: '' },
  },
});
assert.deepEqual(body, {
  response: 'answered',
  answers: [
    {
      question: 'Pick a topic',
      selected_options: ['Schedule', 'Cities'],
      note: 'Opening match',
    },
    {
      question: 'Pick a topic',
      header: 'Follow-up',
      selected_options: ['Teams'],
    },
  ],
}, 'answer body should preserve duplicate question keys and other text');

const repeatedResolved = questions.parseToolActionResolvedEvent({
  tool_call_id: 'ask-repeat',
  status: 'answered',
  response: {
    response: 'answered',
    answers: [
      { question: 'Pick a topic', selected_options: ['Schedule'] },
      { question: 'Pick a topic', header: 'Follow-up', selected_options: ['Teams'] },
    ],
  },
}, parsedRepeated);
assert.equal(
  repeatedResolved.completedAnswers.answers['Pick a topic'].selected_options[0],
  'Schedule',
  'resolved duplicate questions should keep the first answer under the first generated key',
);
assert.equal(
  repeatedResolved.completedAnswers.answers['Pick a topic__2'].selected_options[0],
  'Teams',
  'resolved duplicate questions should keep the second answer under the duplicate generated key',
);

assert.deepEqual(questions.parseAskUserQuestionArgs('{bad json'), [], 'invalid JSON should not parse');
assert.deepEqual(
  questions.parseBackendQuestions({ questions: [{ question: 'Missing options', options: [] }] }),
  [],
  'questions without options should be ignored',
);

const singleQuestionArgs = {
  questions: [
    {
      question: '您想了解世界杯的哪个方面?',
      options: [{ label: '赛程和开幕时间' }, { label: '举办城市和场馆' }],
    },
  ],
};
const actions = toolActions.getVisibleBuilderToolActions([
  {
    role: 'assistant',
    toolCalls: [
      {
        id: 'ask-1',
        name: 'AskUserQuestion',
        args: JSON.stringify(singleQuestionArgs),
        status: 'loading',
      },
    ],
  },
], { locale: 'zh-CN' });
assert.equal(actions.length, 1, 'AskUserQuestion should render as one tool action');
assert.equal(actions[0].registryKey, 'askuserquestion', 'AskUserQuestion should use CircleHelp registry key');
assert.equal(actions[0].label, '正在询问用户', 'AskUserQuestion should use asking-user label');
assert.equal(actions[0].status, 'finished', 'parseable AskUserQuestion should not shimmer forever');
assert.equal(actions[0].description, '您想了解世界杯的哪个方面?', 'tool action should show question text, not raw JSON');

const rendered = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 7,
    status: 'completed',
    events: [
      { type: 'TOOL_CALL_START', toolCallId: 'ask-1', toolCallName: 'AskUserQuestion' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'ask-1', delta: JSON.stringify(singleQuestionArgs) },
      { type: 'TOOL_CALL_END', toolCallId: 'ask-1' },
      {
        type: 'CUSTOM',
        name: 'agent.tool_action.resolved',
        value: {
          tool_call_id: 'ask-1',
          status: 'answered',
          response: {
            response: 'answered',
            answers: [
              {
                question: '您想了解世界杯的哪个方面?',
                selected_options: ['赛程和开幕时间'],
                note: '重点看开幕战',
              },
            ],
          },
        },
      },
      {
        type: 'TOOL_CALL_RESULT',
        toolCallId: 'ask-1',
        content: 'User has answered your questions: "您想了解世界杯的哪个方面?"="赛程和开幕时间". You can now continue.',
      },
    ],
  },
], { locale: 'zh-CN' });
const renderedMessages = rendered[0].messages;
const card = renderedMessages.find((message) => message.uiKind === 'question-card');
const summaries = renderedMessages.filter((message) => message.uiKind === 'question-answer-summary');
const summary = summaries[0];
const toolLists = renderedMessages.filter((message) => message.uiKind === 'tool-action-list');
assert.equal(card.status, 'answered', 'resolved event should update matching question card');
assert.equal(summaries.length, 1, 'resolved event and AskUserQuestion tool result should not render duplicate summaries');
assert.equal(toolLists.length, 1, 'AskUserQuestion tool result should not create a second tool action list');
assert.equal(toolLists[0].actions.length, 1, 'AskUserQuestion should be one visible tool action');
assert.equal(summary.completedAnswers.answers['您想了解世界杯的哪个方面?'].selected_options[0], '赛程和开幕时间', 'resolved event should carry selected options');
assert.equal(summary.completedAnswers.answers['您想了解世界杯的哪个方面?'].other_text, '重点看开幕战', 'resolved event should carry note text');
assert.equal(
  questions.formatQuestionAnswerSummary(summary.questions, summary.completedAnswers, 'zh-CN'),
  '1 个问题已回答\n1. 您想了解世界杯的哪个方面?\n   赛程和开幕时间; 重点看开幕战',
  'answer summary should match public site display text',
);
assert.ok(!questions.formatQuestionAnswerSummary(summary.questions, summary.completedAnswers, 'en').includes('Question:'), 'answer summary should not use legacy Question/Answer labels');

const waitingForUser = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 8,
    status: 'waiting_for_user',
    events: [
      { type: 'CUSTOM', name: 'agent.loaded', value: { mock: true } },
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-waiting', role: 'reasoning' },
      {
        type: 'REASONING_MESSAGE_CONTENT',
        messageId: 'reasoning-waiting',
        delta: 'I need to ask the user before continuing.',
      },
      { type: 'REASONING_MESSAGE_END', messageId: 'reasoning-waiting' },
      { type: 'TOOL_CALL_START', toolCallId: 'ask-waiting', toolCallName: 'AskUserQuestion' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'ask-waiting', delta: JSON.stringify(singleQuestionArgs) },
      { type: 'TOOL_CALL_END', toolCallId: 'ask-waiting' },
    ],
  },
], { locale: 'zh-CN' });
const waitingMessages = waitingForUser[0].messages;
const waitingThinking = waitingMessages.find((message) => message.uiKind === 'thinking');
const waitingToolList = waitingMessages.find((message) => message.uiKind === 'tool-action-list');
const waitingCard = waitingMessages.find((message) => message.uiKind === 'question-card');
assert.equal(waitingForUser[0].status, 'awaiting-user', 'waiting_for_user turn should stay active as awaiting-user');
assert.equal(messages.isActiveTurnStatus(waitingForUser[0].status), true, 'awaiting-user should be an active turn status');
assert.equal(waitingThinking.status, 'done', 'ended reasoning should stay done while waiting for user input');
assert.equal(waitingToolList.isTurnEnded, false, 'tool list should not be ended while waiting for user input');
assert.equal(waitingToolList.hasFollowingRenderableUi, false, 'floating waiting question card should not close the tool group');
assert.equal(waitingCard.status, 'waiting', 'waiting question card should be preserved for the floating card');

const startupOnly = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 18,
    status: 'running',
    events: [
      { type: 'RUN_STARTED', threadId: 'thread-startup', runId: '18' },
      { type: 'CUSTOM', name: 'agent.environment.ready', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loading', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loaded', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.output.waiting', value: { idle_ms: 1200 } },
    ],
  },
], { locale: 'en' });
const startupOnlyMessages = startupOnly[0].messages;
const preparingStartup = startupOnlyMessages.find((message) => message.uiKind === 'agent-startup');
assert.equal(startupOnly[0].status, 'running', 'startup-only active turn should stay running');
assert.equal(preparingStartup.headerPhase, 'preparing', 'startup-only active turn should show preparing header');
assert.equal(preparingStartup.status, 'loading', 'startup-only active turn should show loading startup status');
assert.deepEqual(
  preparingStartup.steps.map((step) => step.label),
  ['Agent environment prepared', 'Agent config loaded', 'Agent responding...'],
  'startup-only active turn should use public-site startup step labels',
);
assert.equal(startupOnlyMessages.some((message) => message.uiKind === 'thinking'), false, 'startup-only active turn should not synthesize Thought for 1s');
assert.equal(startupOnlyMessages.some((message) => message.uiKind === 'unsupported-custom-event'), false, 'startup telemetry should stay hidden');

const openReasoningTurn = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 19,
    status: 'running',
    events: [
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-open', role: 'reasoning' },
      { type: 'REASONING_MESSAGE_CONTENT', messageId: 'reasoning-open', delta: 'This reasoning is still streaming.' },
    ],
  },
], { locale: 'en' });
assert.equal(openReasoningTurn[0].status, 'running', 'running turn without terminal signal should stay running');
assert.equal(openReasoningTurn[0].messages.find((message) => message.uiKind === 'thinking').status, 'streaming', 'open reasoning should render as streaming');
assert.equal(
  runtimeState.hasTerminalSignalInTurns([{ turn_id: 19, events: [{ type: 'RUN_FINISHED' }] }]),
  true,
  'terminal event helper should detect RUN_FINISHED in latest client turn',
);

const b916eeLike = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 20,
    status: 'completed',
    events: [
      { type: 'RUN_STARTED', threadId: 'thread-b916ee', runId: '20' },
      { type: 'CUSTOM', name: 'agent.environment.ready', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loading', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loaded', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.output.waiting', value: { idle_ms: 1200 } },
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-b916ee', role: 'reasoning' },
      { type: 'REASONING_MESSAGE_CONTENT', messageId: 'reasoning-b916ee', delta: 'I need user preferences and then a search.' },
      { type: 'REASONING_MESSAGE_END', messageId: 'reasoning-b916ee' },
      { type: 'TOOL_CALL_START', toolCallId: 'ask-b916ee', toolCallName: 'AskUserQuestion' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'ask-b916ee', delta: JSON.stringify(singleQuestionArgs) },
      { type: 'TOOL_CALL_END', toolCallId: 'ask-b916ee' },
      {
        type: 'CUSTOM',
        name: 'agent.tool_action.resolved',
        value: {
          tool_call_id: 'ask-b916ee',
          status: 'answered',
          response: {
            response: 'answered',
            answers: [
              {
                question: '您想了解世界杯的哪个方面?',
                selected_options: ['赛程和开幕时间'],
              },
            ],
          },
        },
      },
      { type: 'TOOL_CALL_RESULT', toolCallId: 'ask-b916ee', content: 'User answered.' },
      { type: 'TOOL_CALL_START', toolCallId: 'search-b916ee', toolCallName: 'web_search' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'search-b916ee', delta: '{"query":"2026 world cup"}' },
      { type: 'TOOL_CALL_END', toolCallId: 'search-b916ee' },
      { type: 'TOOL_CALL_RESULT', toolCallId: 'search-b916ee', content: 'Search result.' },
      { type: 'TEXT_MESSAGE_START', messageId: 'assistant-b916ee', role: 'assistant' },
      { type: 'TEXT_MESSAGE_CONTENT', messageId: 'assistant-b916ee', delta: 'Final answer.' },
      { type: 'TEXT_MESSAGE_END', messageId: 'assistant-b916ee' },
      { type: 'CUSTOM', name: 'agent.turn.summary', value: { ok: true } },
      { type: 'RUN_FINISHED', threadId: 'thread-b916ee', runId: '20' },
    ],
  },
], { locale: 'en' });
const b916eeMessages = b916eeLike[0].messages;
const b916eeStartup = b916eeMessages.find((message) => message.uiKind === 'agent-startup');
const b916eeThinking = b916eeMessages.find((message) => message.uiKind === 'thinking');
const b916eeToolLists = b916eeMessages.filter((message) => message.uiKind === 'tool-action-list');
assert.equal(b916eeLike[0].status, 'done', 'completed b916ee-like turn should be done when server running is null');
assert.equal(b916eeStartup.headerPhase, 'responded', 'completed b916ee-like startup should be responded');
assert.equal(b916eeStartup.isTurnEnded, true, 'completed b916ee-like startup should be ended');
assert.equal(b916eeStartup.steps.at(-1).label, 'Agent responded', 'completed b916ee-like startup should show responded bot step');
assert.equal(b916eeThinking.status, 'done', 'completed b916ee-like thinking should be done');
assert.equal(b916eeToolLists.length, 2, 'b916ee-like turn should render AskUserQuestion and search tool groups');
assert.equal(b916eeToolLists.every((message) => message.isTurnEnded), true, 'completed b916ee-like tool groups should be ended');
assert.equal(b916eeMessages.filter((message) => message.uiKind === 'question-answer-summary').length, 1, 'b916ee-like answer summary should render once');
assert.equal(b916eeMessages.some((message) => message.uiKind === 'unsupported-custom-event'), false, 'b916ee-like telemetry and RUN_FINISHED should stay hidden');

const liveResolvedWaiting = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 21,
    status: 'waiting_for_user',
    events: [
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-live-resolved', role: 'reasoning' },
      { type: 'REASONING_MESSAGE_CONTENT', messageId: 'reasoning-live-resolved', delta: 'Ask the user and continue.' },
      { type: 'REASONING_MESSAGE_END', messageId: 'reasoning-live-resolved' },
      { type: 'TOOL_CALL_START', toolCallId: 'ask-live-resolved', toolCallName: 'AskUserQuestion' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'ask-live-resolved', delta: JSON.stringify(singleQuestionArgs) },
      { type: 'TOOL_CALL_END', toolCallId: 'ask-live-resolved' },
      {
        type: 'CUSTOM',
        name: 'agent.tool_action.resolved',
        value: {
          tool_call_id: 'ask-live-resolved',
          status: 'answered',
          response: {
            response: 'answered',
            answers: [
              {
                question: '您想了解世界杯的哪个方面?',
                selected_options: ['赛程和开幕时间'],
              },
            ],
          },
        },
      },
      { type: 'TOOL_CALL_RESULT', toolCallId: 'ask-live-resolved', content: 'User answered.' },
      { type: 'TEXT_MESSAGE_START', messageId: 'assistant-live-resolved', role: 'assistant' },
      { type: 'TEXT_MESSAGE_CONTENT', messageId: 'assistant-live-resolved', delta: 'Continuing after the answer.' },
      { type: 'TEXT_MESSAGE_END', messageId: 'assistant-live-resolved' },
    ],
  },
], { locale: 'zh-CN' });
const liveResolvedMessages = liveResolvedWaiting[0].messages;
assert.equal(liveResolvedWaiting[0].status, 'done', 'waiting_for_user should become done once the question is resolved');
assert.equal(liveResolvedMessages.find((message) => message.uiKind === 'thinking').status, 'done', 'resolved waiting turn should not keep thinking streaming');
assert.equal(liveResolvedMessages.filter((message) => message.uiKind === 'question-answer-summary').length, 1, 'live resolved waiting turn should render one answer summary');

const duplicateStartup = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 22,
    status: 'completed',
    events: [
      { type: 'CUSTOM', name: 'agent.environment.ready', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loading', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loaded', value: { mock: true } },
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-duplicate-startup', role: 'reasoning' },
      { type: 'REASONING_MESSAGE_CONTENT', messageId: 'reasoning-duplicate-startup', delta: 'First real renderable content.' },
      { type: 'REASONING_MESSAGE_END', messageId: 'reasoning-duplicate-startup' },
      { type: 'CUSTOM', name: 'agent.environment.ready', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loading', value: { mock: true } },
      { type: 'CUSTOM', name: 'agent.loaded', value: { mock: true } },
      { type: 'TEXT_MESSAGE_START', messageId: 'assistant-duplicate-startup', role: 'assistant' },
      { type: 'TEXT_MESSAGE_CONTENT', messageId: 'assistant-duplicate-startup', delta: 'Final answer.' },
      { type: 'TEXT_MESSAGE_END', messageId: 'assistant-duplicate-startup' },
      { type: 'RUN_FINISHED' },
    ],
  },
], { locale: 'en' });
const duplicateStartupMessages = duplicateStartup[0].messages;
const duplicateStartupBlocks = duplicateStartupMessages.filter((message) => message.uiKind === 'agent-startup');
assert.equal(duplicateStartupBlocks.length, 1, 'duplicate startup events in one turn should update one startup block');
assert.equal(duplicateStartupBlocks[0].headerPhase, 'responded', 'merged duplicate startup block should stay responded');

const completedButWaiting = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 88,
    status: 'completed',
    events: [
      { type: 'REASONING_MESSAGE_START', messageId: 'reasoning-completed-waiting', role: 'reasoning' },
      {
        type: 'REASONING_MESSAGE_CONTENT',
        messageId: 'reasoning-completed-waiting',
        delta: 'The transport completed after asking the user.',
      },
      { type: 'REASONING_MESSAGE_END', messageId: 'reasoning-completed-waiting' },
      { type: 'TOOL_CALL_START', toolCallId: 'ask-completed-waiting', toolCallName: 'AskUserQuestion' },
      { type: 'TOOL_CALL_ARGS', toolCallId: 'ask-completed-waiting', delta: JSON.stringify(singleQuestionArgs) },
      { type: 'TOOL_CALL_END', toolCallId: 'ask-completed-waiting' },
    ],
  },
], { locale: 'zh-CN' });
const completedWaitingMessages = completedButWaiting[0].messages;
const completedWaitingThinking = completedWaitingMessages.find((message) => message.uiKind === 'thinking');
const completedWaitingToolList = completedWaitingMessages.find((message) => message.uiKind === 'tool-action-list');
assert.equal(completedButWaiting[0].status, 'awaiting-user', 'completed-shaped turn with a waiting question should still be awaiting-user');
assert.equal(completedWaitingThinking.status, 'done', 'completed-shaped waiting turn should keep ended thinking done');
assert.equal(completedWaitingToolList.isTurnEnded, false, 'completed-shaped waiting turn should keep tool group active');

const completedWithOpenShapes = messages.toBuilderPublicSiteTurns([
  {
    turn_id: 9,
    status: 'completed',
    events: [
      { role: 'user', content: 'Run a finished turn' },
      { role: 'reasoning', content: 'Finished thinking should be collapsed.' },
      {
        role: 'assistant',
        toolCalls: [
          {
            id: 'tool-finished-turn',
            name: 'Lookup',
            args: '{"query":"world cup"}',
            status: 'loading',
          },
        ],
      },
      { role: 'assistant', content: 'Final answer.' },
    ],
  },
], { locale: 'zh-CN' });
const completedMessages = completedWithOpenShapes[0].messages;
const completedThinking = completedMessages.find((message) => message.uiKind === 'thinking');
const completedToolList = completedMessages.find((message) => message.uiKind === 'tool-action-list');
assert.equal(completedWithOpenShapes[0].status, 'done', 'completed turn should remain done');
assert.equal(completedThinking.status, 'done', 'thinking in completed turn should be done');
assert.equal(completedToolList.isTurnEnded, true, 'tool list in completed turn should be ended even with loading-shaped tool data');
assert.equal(completedToolList.hasFollowingRenderableUi, true, 'tool list followed by assistant UI should be marked as closed');

const skipped = questions.buildAnswerRequestBody(parsedRepeated, { skipped: true, answers: {} });
assert.deepEqual(skipped, { response: 'skipped' }, 'skipped body should omit answers');

console.log(JSON.stringify({ ok: true }, null, 2));
`;

try {
  await build({
    stdin: {
      contents: entry,
      resolveDir: process.cwd(),
      sourcefile: 'verify-question-core-entry.ts',
      loader: 'ts',
    },
    bundle: true,
    platform: 'node',
    format: 'esm',
    outfile,
    logLevel: 'silent',
  });
  await import(pathToFileURL(outfile).href);
} finally {
  await rm(tempDir, { recursive: true, force: true });
}
