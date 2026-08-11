import React, { useState } from 'react';
import { ArrowUp, Square } from 'lucide-react';
import { localeLabels } from '../core/locales';
import type { BuilderPublicSiteAgentProfile, BuilderPublicSiteLocaleInput } from '../core/types';
import { BuilderPublicSiteAgentAvatar, getBuilderPublicSiteAgentName } from './AgentIdentity';

export function Composer({
  locale = 'zh-CN',
  agentProfile,
  disabled,
  isRunning,
  onSend,
  onAbort,
}: {
  locale?: BuilderPublicSiteLocaleInput;
  agentProfile?: BuilderPublicSiteAgentProfile;
  disabled?: boolean;
  isRunning?: boolean;
  onSend: (message: string) => Promise<void> | void;
  onAbort?: () => Promise<void> | void;
}) {
  const [value, setValue] = useState('');
  const l = localeLabels(locale);
  const displayName = getBuilderPublicSiteAgentName(agentProfile, undefined, locale);

  async function submit() {
    const text = value.trim();
    if (!text || disabled || isRunning) return;
    setValue('');
    await onSend(text);
  }

  return (
    <form className="bps-composer" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
      <div className="bps-composer-agent-chip">
        <BuilderPublicSiteAgentAvatar
          agentProfile={agentProfile}
          displayName={displayName}
          className="bps-composer-agent-avatar"
        />
        <span className="bps-composer-agent-name">{displayName}</span>
      </div>
      <div className="bps-composer-row">
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder={String(l.placeholder)}
          disabled={disabled}
          rows={1}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault();
              void submit();
            }
          }}
        />
        {isRunning ? (
          <button type="button" className="bps-composer-button" onClick={() => void onAbort?.()} aria-label={String(l.stop)}><Square /></button>
        ) : (
          <button type="submit" className="bps-composer-button" disabled={disabled || !value.trim()} aria-label={String(l.send)}><ArrowUp /></button>
        )}
      </div>
    </form>
  );
}
