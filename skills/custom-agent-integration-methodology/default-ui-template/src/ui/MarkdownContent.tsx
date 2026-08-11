import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { cx } from './cx';

export function MarkdownContent({ content, className }: { content: string; className?: string }) {
  return (
    <div className={cx('bps-markdown', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ children, ...props }) => <a {...props} target="_blank" rel="noreferrer">{children}</a>,
          table: ({ children, ...props }) => <div className="bps-table-wrap"><table {...props}>{children}</table></div>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
