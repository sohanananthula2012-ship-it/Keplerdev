import type { MessageContentPart } from './types';

export function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

export function tryParseJsonObject(value: unknown): Record<string, unknown> | undefined {
  if (isRecord(value)) return value;
  if (typeof value !== 'string') return undefined;
  try {
    const parsed = JSON.parse(value);
    return isRecord(parsed) ? parsed : undefined;
  } catch {
    return undefined;
  }
}

export function getMessageContentText(content: unknown): string {
  if (typeof content === 'string') return content;
  if (content == null) return '';
  if (Array.isArray(content)) {
    return content
      .map((part: MessageContentPart | unknown) => {
        if (typeof part === 'string') return part;
        if (!isRecord(part)) return '';
        if (typeof part.text === 'string') return part.text;
        if (typeof part.content === 'string') return part.content;
        if (isRecord(part.content) && typeof part.content.text === 'string') return part.content.text;
        return '';
      })
      .filter(Boolean)
      .join('');
  }
  if (isRecord(content)) {
    if (typeof content.text === 'string') return content.text;
    if (typeof content.content === 'string') return content.content;
  }
  return '';
}

export function stringFrom(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return undefined;
}

export function firstString(...values: unknown[]): string | undefined {
  for (const value of values) {
    const text = stringFrom(value);
    if (text) return text;
  }
  return undefined;
}

export function compactText(value: string | undefined, fallback = ''): string {
  if (!value) return fallback;
  return value.replace(/\s+/g, ' ').trim();
}
