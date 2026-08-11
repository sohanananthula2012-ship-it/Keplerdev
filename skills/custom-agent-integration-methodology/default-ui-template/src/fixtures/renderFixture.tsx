import React from 'react';
import { createRoot } from 'react-dom/client';
import { PublicSiteLikeChatShell, toBuilderPublicSiteMessages } from '../index';
import { goldenThreadFixture } from './goldenThread';
import '../styles/public-site.css';

const root = createRoot(document.getElementById('root')!);
const messages = toBuilderPublicSiteMessages(goldenThreadFixture, { locale: 'zh' });
root.render(
  <PublicSiteLikeChatShell
    messages={messages}
    locale="zh"
    agentProfile={{
      name: '中译英助手',
      logo: 'https://grazia-prod.oss-ap-southeast-1.aliyuncs.com/resources/public/Green-sleep.svg',
      description: '把中文自然翻译成准确、流畅的英文。',
      modelLabel: 'Custom Agent',
      toolsCount: 1,
    }}
    sessions={[{ id: 'fixture', title: '世界杯查询', active: true }]}
    onSend={() => undefined}
  />,
);
