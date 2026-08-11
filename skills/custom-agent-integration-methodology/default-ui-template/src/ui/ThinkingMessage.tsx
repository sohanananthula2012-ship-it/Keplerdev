import React, { useEffect, useState } from 'react';
import { Activity } from 'lucide-react';
import type { BuilderPublicSiteLocaleInput, BuilderPublicSiteViewMessage } from '../core/types';
import { localeLabels, secondsFromDuration } from '../core/locales';
import { CollapsibleSection } from './CollapsibleSection';
import { ShimmeringText } from './ShimmeringText';

type ThinkingMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'thinking' | 'reasoning' }>;

export function ThinkingMessage({ message, locale = 'zh-CN' }: { message: ThinkingMessage; locale?: BuilderPublicSiteLocaleInput }) {
  const l = localeLabels(locale);
  const inProgress = message.status === 'streaming';
  const [expanded, setExpanded] = useState(false);
  const title = inProgress ? l.thinkingStreaming : l.thinkingDone(secondsFromDuration(message.durationMs));

  useEffect(() => {
    if (!inProgress) setExpanded(false);
  }, [inProgress]);

  if (!message.content.trim() && !inProgress) return null;
  return (
    <CollapsibleSection
      className="bps-thinking"
      title={<ShimmeringText active={inProgress}>{String(title)}</ShimmeringText>}
      icon={<Activity className="bps-section-icon" />}
      expanded={inProgress ? true : expanded}
      onExpandedChange={setExpanded}
      inProgress={inProgress}
      disabled={inProgress || !message.content.trim()}
    >
      <div className="bps-vertical-content">
        <div className="bps-vertical-rule" />
        <div className="bps-thinking-text">{message.content}</div>
      </div>
    </CollapsibleSection>
  );
}
