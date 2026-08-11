/* eslint-disable react-refresh/only-export-components */
import React from 'react';
import { resolveBuilderPublicSiteLocale } from '../core/locales';
import { getBuilderPublicSiteAvatarObjectFit } from '../core/logoPresets';
import type { BuilderPublicSiteAgentProfile, BuilderPublicSiteLocaleInput } from '../core/types';

export function getBuilderPublicSiteAgentName(
  agentProfile: BuilderPublicSiteAgentProfile | undefined,
  title: string | undefined,
  locale: BuilderPublicSiteLocaleInput,
) {
  const name = agentProfile?.name?.trim() || title?.trim();
  if (name) return name;
  return resolveBuilderPublicSiteLocale(locale) === 'zh-CN' ? '智能体' : 'Agent';
}

export function getBuilderPublicSiteAgentMetaItems(
  agentProfile: BuilderPublicSiteAgentProfile | undefined,
  locale: BuilderPublicSiteLocaleInput,
) {
  if (!agentProfile) return [];
  const isChinese = resolveBuilderPublicSiteLocale(locale) === 'zh-CN';
  const items: string[] = [];
  const toolsCount = agentProfile.toolsCount;
  const skillsCount = agentProfile.skillsCount;

  if (agentProfile.modelLabel?.trim()) {
    items.push(agentProfile.modelLabel.trim());
  }
  if (typeof toolsCount === 'number' && Number.isFinite(toolsCount) && toolsCount > 0) {
    items.push(isChinese ? `${toolsCount} 个工具` : `${toolsCount} tools`);
  }
  if (typeof skillsCount === 'number' && Number.isFinite(skillsCount) && skillsCount > 0) {
    items.push(isChinese ? `${skillsCount} 个技能` : `${skillsCount} skills`);
  }

  return items;
}

export function BuilderPublicSiteAgentAvatar({
  agentProfile,
  displayName,
  className,
}: {
  agentProfile?: BuilderPublicSiteAgentProfile;
  displayName: string;
  className: string;
}) {
  const logo = agentProfile?.logo?.trim();
  const initial = displayName.trim().slice(0, 1).toUpperCase() || 'A';

  return (
    <span className={className} aria-hidden={logo ? undefined : true}>
      {logo ? (
        <img
          src={logo}
          alt={displayName}
          style={{ objectFit: getBuilderPublicSiteAvatarObjectFit(logo) }}
        />
      ) : initial}
    </span>
  );
}
