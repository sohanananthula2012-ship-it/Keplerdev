import React from 'react';
import { AlertTriangle, Bot, ListChecks, MonitorDot, ScanText, XCircle } from 'lucide-react';
import type { BuilderPublicSiteLocaleInput, BuilderPublicSiteTurnRenderContext, BuilderPublicSiteViewMessage } from '../core/types';
import { localeLabels } from '../core/locales';
import { cx } from './cx';
import { CollapsibleSection } from './CollapsibleSection';
import { ShimmeringText } from './ShimmeringText';

type StartupMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'agent-startup' }>;
type ErrorMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'turn-error' | 'out-of-credit' }>;
type CancelMessage = Extract<BuilderPublicSiteViewMessage, { uiKind: 'cancel' }>;

const STARTUP_STEP_ICONS = {
  monitor: MonitorDot,
  scan: ScanText,
  bot: Bot,
} as const;

function StartupStepRow({ step }: { step: StartupMessage['steps'][number] }) {
  const Icon = STARTUP_STEP_ICONS[step.icon] ?? Bot;
  const loading = step.status === 'loading';
  return (
    <div className={cx('bps-startup-step', loading && 'is-loading', step.status === 'error' && 'is-error')} data-status={step.status}>
      <span className="bps-startup-step-icon">
        <Icon className="bps-startup-step-svg" />
      </span>
      <span className="bps-startup-step-label">
        <ShimmeringText active={loading}>{step.label}</ShimmeringText>
      </span>
    </div>
  );
}

export function AgentStartupMessage({
  message,
  locale = 'zh-CN',
  turnContext,
}: {
  message: StartupMessage;
  locale?: BuilderPublicSiteLocaleInput;
  turnContext?: BuilderPublicSiteTurnRenderContext;
}) {
  const l = localeLabels(locale);
  const isTurnEnded = turnContext?.isTurnEnded ?? message.isTurnEnded;
  const isPreparing = message.headerPhase === 'preparing' && !isTurnEnded;
  const title = isPreparing ? l.agentRunning : l.agentReady;
  return (
    <CollapsibleSection
      className="bps-startup"
      title={<ShimmeringText active={isPreparing}>{String(title)}</ShimmeringText>}
      icon={<ListChecks className="bps-section-icon" />}
      defaultExpanded={isPreparing}
      forceExpanded={isPreparing}
      inProgress={isPreparing}
      autoCollapseWhenFinished
      disabled={isPreparing}
    >
      <div className="bps-vertical-content">
        <div className="bps-vertical-rule" />
        <div className="bps-startup-steps">
          {message.steps.map((step) => <StartupStepRow key={step.id} step={step} />)}
        </div>
      </div>
    </CollapsibleSection>
  );
}

export function ErrorMessageView({ message }: { message: ErrorMessage }) {
  return <div className="bps-error-message"><AlertTriangle className="bps-inline-icon" />{message.message}</div>;
}

export function CancelMessageView({ message }: { message: CancelMessage }) {
  return <div className="bps-cancel-message"><XCircle className="bps-inline-icon" />{message.message}</div>;
}
