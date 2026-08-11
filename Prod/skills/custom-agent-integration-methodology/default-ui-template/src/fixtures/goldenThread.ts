import type { ThreadTurnLike } from '../core/types';

export const goldenThreadFixture: ThreadTurnLike[] = [
  {
    id: 'turn-1',
    status: 'done',
    messages: [
      { role: 'user', content: '2026年世界杯是什么时候，在哪举办？' },
      { name: 'agent.environment.ready', data: { label: '环境已就绪' }, status: 'done' },
      { role: 'assistant', type: 'reasoning', content: 'The user is asking about the 2026 FIFA World Cup. I should search for up-to-date information and answer in Chinese.' },
      {
        role: 'assistant',
        tool_calls: [{ id: 'tool-1', function: { name: 'WebSearch', arguments: JSON.stringify({ query: '2026 FIFA World Cup 时间 举办地点' }) }, status: 'done' }],
      },
      { role: 'tool', name: 'WebSearch', tool_call_id: 'tool-1', content: JSON.stringify({ description: '2026 FIFA World Cup 时间 举办地点' }) },
      {
        role: 'assistant',
        content: '以下是 2026 年世界杯的关键信息：\n\n| 项目 | 详情 |\n| --- | --- |\n| 时间 | 2026 年 6 月 11 日 - 7 月 19 日 |\n| 举办国家 | 美国、加拿大、墨西哥 |\n| 参赛队数 | 48 支球队 |',
      },
      { name: 'usage.update', data: { inputTokens: 3, outputTokens: 60 } },
    ],
  },
];
