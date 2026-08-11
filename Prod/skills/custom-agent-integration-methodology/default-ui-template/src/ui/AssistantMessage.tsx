import React from 'react';
import { MarkdownContent } from './MarkdownContent';

export function AssistantMessage({ content }: { content: string }) {
  if (!content.trim()) return null;
  return (
    <article className="bps-assistant-message">
      <MarkdownContent content={content} />
    </article>
  );
}
