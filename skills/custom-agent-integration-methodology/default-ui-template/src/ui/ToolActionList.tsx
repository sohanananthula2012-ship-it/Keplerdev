import React, { useEffect, useState } from 'react';
import { Hammer, ListChecks } from 'lucide-react';
import type {
  BuilderPublicSiteLocaleInput,
  BuilderPublicSiteRenderSlots,
  BuilderPublicSiteTurnRenderContext,
  BuilderPublicSiteViewMessage,
  BuilderToolActionView,
} from '../core/types';
import { localeLabels } from '../core/locales';
import { CollapsibleSection } from './CollapsibleSection';
import { ShimmeringText } from './ShimmeringText';

type ToolListMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'tool-action-list' }>;

function ToolActionRow({ action, renderToolAction }: { action: BuilderToolActionView; renderToolAction?: BuilderPublicSiteRenderSlots['renderToolAction'] }) {
  if (renderToolAction) return <>{renderToolAction(action)}</>;
  return (
    <div className="bps-tool-row">
      <span className="bps-tool-icon">{action.icon ?? <Hammer className="bps-tool-icon-svg" />}</span>
      <span className="bps-tool-label"><ShimmeringText active={action.status === 'loading'}>{action.label}</ShimmeringText></span>
      {action.description ? <span className="bps-tool-description" title={action.description}>{action.description}</span> : null}
    </div>
  );
}

export function ToolActionList({
  message,
  locale = 'zh-CN',
  turnContext,
  renderToolAction,
}: {
  message: ToolListMessage;
  locale?: BuilderPublicSiteLocaleInput;
  turnContext?: BuilderPublicSiteTurnRenderContext;
  renderToolAction?: BuilderPublicSiteRenderSlots['renderToolAction'];
}) {
  if (message.actions.length === 0) return null;
  const l = localeLabels(locale);
  const isTurnEnded = turnContext?.isTurnEnded ?? message.isTurnEnded;
  const isLastItem = turnContext?.isLastItem ?? true;
  const isAgentRunning = turnContext?.isAgentRunning ?? !isTurnEnded;
  const loadingCount = message.actions.filter((action) => action.status === 'loading').length;
  const isToolPhaseOpen = isLastItem && isAgentRunning && !message.hasFollowingRenderableUi;
  const isToolGroupClosed = isTurnEnded || message.hasFollowingRenderableUi;
  const inProgress = !isToolGroupClosed && (loadingCount > 0 || isToolPhaseOpen);
  const hasError = message.actions.some((action) => action.status === 'error');
  const [expanded, setExpanded] = useState(inProgress);

  useEffect(() => {
    setExpanded(inProgress);
  }, [inProgress]);

  const title = hasError
    ? l.actionsError(message.actions.length)
    : inProgress
      ? l.actionsStreaming(message.actions.length)
      : l.actionsDone(message.actions.length);
  return (
    <CollapsibleSection
      className="bps-tool-list"
      title={<ShimmeringText active={inProgress}>{String(title)}</ShimmeringText>}
      icon={<ListChecks className="bps-section-icon" />}
      expanded={expanded}
      onExpandedChange={setExpanded}
      inProgress={inProgress}
    >
      <div className="bps-vertical-content">
        <div className="bps-vertical-rule" />
        <div className="bps-tool-items">
          {message.actions.map((action) => <ToolActionRow key={action.key} action={action} renderToolAction={renderToolAction} />)}
        </div>
      </div>
    </CollapsibleSection>
  );
}
