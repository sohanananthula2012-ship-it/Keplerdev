import React from 'react';
import { cx } from './cx';

export function ShimmeringText({ children, active, className }: { children: React.ReactNode; active?: boolean; className?: string }) {
  return <span className={cx('bps-shimmer-text', active && 'is-active', className)}>{children}</span>;
}
