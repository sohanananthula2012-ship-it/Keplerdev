import React, { useEffect, useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cx } from './cx';

export function CollapsibleSection({
  className,
  title,
  subtitle,
  icon,
  children,
  defaultExpanded = false,
  forceExpanded,
  inProgress,
  autoCollapseWhenFinished,
  disabled,
  expanded: controlledExpanded,
  onExpandedChange,
}: {
  className?: string;
  title: React.ReactNode;
  subtitle?: React.ReactNode;
  icon?: React.ReactNode;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  forceExpanded?: boolean;
  inProgress?: boolean;
  autoCollapseWhenFinished?: boolean;
  disabled?: boolean;
  expanded?: boolean;
  onExpandedChange?: (expanded: boolean) => void;
}) {
  const [uncontrolledExpanded, setUncontrolledExpanded] = useState(defaultExpanded || Boolean(forceExpanded));
  const [hovered, setHovered] = useState(false);
  const expanded = controlledExpanded ?? uncontrolledExpanded;

  function setExpanded(next: boolean | ((current: boolean) => boolean)) {
    const nextValue = typeof next === 'function' ? next(expanded) : next;
    if (controlledExpanded === undefined) setUncontrolledExpanded(nextValue);
    onExpandedChange?.(nextValue);
  }

  useEffect(() => {
    if (forceExpanded) {
      if (controlledExpanded === undefined) setUncontrolledExpanded(true);
      onExpandedChange?.(true);
    }
  }, [forceExpanded, controlledExpanded, onExpandedChange]);

  useEffect(() => {
    if (autoCollapseWhenFinished && !inProgress && !forceExpanded) {
      if (controlledExpanded === undefined) setUncontrolledExpanded(false);
      onExpandedChange?.(false);
    }
  }, [autoCollapseWhenFinished, forceExpanded, inProgress, controlledExpanded, onExpandedChange]);

  return (
    <section className={cx('bps-collapsible', className, expanded && 'is-expanded', inProgress && 'is-loading', disabled && 'is-disabled')}>
      <button
        type="button"
        className="bps-collapsible-header"
        onClick={() => {
          if (!disabled) setExpanded((value) => !value);
        }}
        aria-expanded={expanded}
        aria-disabled={disabled || undefined}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      >
        <span className={cx('bps-collapsible-icon', Boolean(icon) && 'has-primary-icon', (expanded || hovered) && 'show-chevron')}>
          {icon ? <span className="bps-collapsible-icon-primary">{icon}</span> : null}
          <ChevronDown className="bps-chevron" aria-hidden="true" />
        </span>
        <span className="bps-collapsible-title">{title}</span>
        {subtitle ? <span className="bps-collapsible-subtitle">{subtitle}</span> : null}
      </button>
      {expanded ? <div className="bps-collapsible-body">{children}</div> : null}
    </section>
  );
}
