import React from 'react';
import {
  Bot,
  Braces,
  CircleHelp,
  Code2,
  FilePenLine,
  FileSearch,
  FileText,
  Globe,
  Hammer,
  Infinity,
  PencilLine,
  Search,
  Sparkles,
  Terminal,
} from 'lucide-react';
import type { BuilderPublicSiteLocale, ToolDisplayRegistry } from './types';
import { FALLBACK_BUILDER_PUBLIC_SITE_LOCALE, resolveBuilderPublicSiteLocale } from './locales';

const iconClassName = 'bps-tool-icon-svg';

function DecoratedToolIcon({ children }: { children: React.ReactNode }) {
  return <span className="bps-tool-icon-inner">{children}</span>;
}

function makeIcon(icon: React.ReactNode) {
  return <DecoratedToolIcon>{icon}</DecoratedToolIcon>;
}

type ToolLabel = {
  loading: string;
  finished: string;
  error?: string;
};

const toolLabels: Record<string, Partial<Record<BuilderPublicSiteLocale, ToolLabel>>> = {
  default: {
    'zh-CN': { loading: '正在调用工具', finished: '已调用工具', error: '工具调用失败' },
    en: { loading: 'Using tool', finished: 'Used tool', error: 'Tool failed' },
  },
  read: {
    'zh-CN': { loading: '正在读取', finished: '已读取' },
    en: { loading: 'Reading', finished: 'Read' },
  },
  write: {
    'zh-CN': { loading: '正在写入', finished: '已写入' },
    en: { loading: 'Writing', finished: 'Wrote' },
  },
  edit: {
    'zh-CN': { loading: '正在编辑', finished: '已编辑' },
    en: { loading: 'Editing', finished: 'Edited' },
  },
  bash: {
    'zh-CN': { loading: '正在运行命令', finished: '已运行命令' },
    en: { loading: 'Running command', finished: 'Ran command' },
  },
  grep: {
    'zh-CN': { loading: '正在搜索代码', finished: '已搜索代码' },
    en: { loading: 'Searching code', finished: 'Searched code' },
  },
  websearch: {
    'zh-CN': { loading: '正在搜索网站', finished: '已搜索网站' },
    en: { loading: 'Searching websites', finished: 'Searched websites' },
  },
  webfetch: {
    'zh-CN': { loading: '正在读取网页', finished: '已读取网页' },
    en: { loading: 'Reading webpage', finished: 'Read webpage' },
  },
  skill: {
    'zh-CN': { loading: '正在激活技能', finished: '已激活技能' },
    en: { loading: 'Activating skill', finished: 'Activated skill' },
  },
  askuserquestion: {
    'zh-CN': { loading: '正在询问用户', finished: '正在询问用户' },
    en: { loading: 'Asking user', finished: 'Asking user' },
  },
};

function labelFor(key: string, state: 'loading' | 'finished' | 'error', locale: BuilderPublicSiteLocale) {
  const normalized = normalizeBuilderToolRegistryKey(key);
  const resolvedLocale = resolveBuilderPublicSiteLocale(locale);
  const labels = toolLabels[normalized] ?? toolLabels.default;
  const localized =
    labels[resolvedLocale] ??
    toolLabels.default[resolvedLocale] ??
    labels[FALLBACK_BUILDER_PUBLIC_SITE_LOCALE] ??
    toolLabels.default[FALLBACK_BUILDER_PUBLIC_SITE_LOCALE] ??
    { loading: 'Using tool', finished: 'Used tool', error: 'Tool failed' };
  return state === 'error' ? localized.error ?? localized.finished : localized[state];
}

const aliases: Record<string, string> = {
  todowrite: 'write',
  multitooluse: 'mcp',
  multi_tool_useparallel: 'mcp',
  web_search: 'websearch',
  websearchtool: 'websearch',
  web_fetch: 'webfetch',
  readfile: 'read',
  listdir: 'read',
  applypatch: 'edit',
  apply_patch: 'edit',
  askquestion: 'askuserquestion',
};

export function normalizeBuilderToolRegistryKey(toolName?: string) {
  const compact = (toolName || 'default').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
  return aliases[compact] ?? compact;
}

function makeToolEntry(key: string, icon: React.ReactNode) {
  return {
    icon,
    getLabel: (state: 'loading' | 'finished' | 'error', locale: BuilderPublicSiteLocale) => labelFor(key, state, locale),
  };
}

export const DEFAULT_TOOL_DISPLAY_REGISTRY: ToolDisplayRegistry = {
  default: makeToolEntry('default', makeIcon(<Hammer className={iconClassName} />)),
  read: makeToolEntry('read', makeIcon(<FileText className={iconClassName} />)),
  write: makeToolEntry('write', makeIcon(<FilePenLine className={iconClassName} />)),
  edit: makeToolEntry('edit', makeIcon(<PencilLine className={iconClassName} />)),
  multiedit: makeToolEntry('edit', makeIcon(<PencilLine className={iconClassName} />)),
  bash: makeToolEntry('bash', makeIcon(<Terminal className={iconClassName} />)),
  glob: makeToolEntry('grep', makeIcon(<FileSearch className={iconClassName} />)),
  grep: makeToolEntry('grep', makeIcon(<Search className={iconClassName} />)),
  webfetch: makeToolEntry('webfetch', makeIcon(<Globe className={iconClassName} />)),
  websearch: makeToolEntry('websearch', makeIcon(<Globe className={iconClassName} />)),
  skill: makeToolEntry('skill', makeIcon(<Sparkles className={iconClassName} />)),
  summarize: makeToolEntry('default', makeIcon(<Braces className={iconClassName} />)),
  askuserquestion: makeToolEntry('askuserquestion', makeIcon(<CircleHelp className={iconClassName} />)),
  mcp: makeToolEntry('default', makeIcon(<Infinity className={iconClassName} />)),
  agent: makeToolEntry('default', makeIcon(<Bot className={iconClassName} />)),
  code: makeToolEntry('default', makeIcon(<Code2 className={iconClassName} />)),
};

export function getToolDefinition(toolName?: string, registry: ToolDisplayRegistry = DEFAULT_TOOL_DISPLAY_REGISTRY) {
  const key = normalizeBuilderToolRegistryKey(toolName);
  return registry[key] ?? registry.default;
}
