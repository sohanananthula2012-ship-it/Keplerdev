import React from 'react';

export function UserMessage({ content }: { content: string }) {
  return (
    <article className="bps-user-message-row">
      <div className="bps-user-bubble">{content}</div>
    </article>
  );
}
