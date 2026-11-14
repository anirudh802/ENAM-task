import React from 'react';
import { LucideIcon, Lock } from 'lucide-react';

export interface ActionButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'icon';
  icon?: LucideIcon | React.ComponentType<{ className?: string }>;
  label?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
  disabledReason?: string;
  className?: string;
  title?: string;
  'aria-label'?: string;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  variant = 'primary',
  icon: Icon,
  label,
  onClick,
  disabled = false,
  disabledReason,
  className = '',
  title,
  'aria-label': ariaLabel,
}) => {
  const fullActionName = ariaLabel || label || title || (disabled ? disabledReason : undefined) || 'Action';
  const effectiveTitle = disabled ? (disabledReason || title || label) : (title || (variant === 'icon' ? label : undefined));

  // Base layout: refined 26px visual height, >= 44px tap target via pseudo-element, accessible focus ring, no-wrap
  const baseClasses =
    'relative inline-flex items-center justify-center font-sans text-[11.5px] font-semibold whitespace-nowrap rounded-md transition-all select-none shrink-0 ' +
    "after:content-[''] after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-[max(100%,44px)] after:h-[max(100%,44px)] after:min-w-[44px] after:min-h-[44px] " +
    'focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-900 active:scale-[0.98]';

  if (disabled) {
    const disabledClasses =
      variant === 'icon'
        ? `${baseClasses} w-[26px] h-[26px] p-0 bg-slate-100 dark:bg-slate-800/60 text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-700/60 cursor-not-allowed opacity-75 ${className}`
        : `${baseClasses} h-[26px] px-2.5 gap-1.5 bg-slate-100 dark:bg-slate-800/60 text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-700/60 cursor-not-allowed opacity-75 ${className}`;

    return (
      <button
        type="button"
        disabled
        aria-label={fullActionName}
        title={effectiveTitle}
        className={disabledClasses}
      >
        <Lock className="w-3 h-3 shrink-0 text-slate-400 dark:text-slate-500" />
        {variant !== 'icon' && <span>{label || 'Blocked'}</span>}
      </button>
    );
  }

  let variantClasses = '';
  if (variant === 'primary') {
    // Sleek institutional tinted action button (matches FINN design tokens)
    variantClasses =
      'h-[26px] px-2.5 gap-1.5 ' +
      'bg-violet-50 hover:bg-violet-100 text-violet-700 border border-violet-200/90 shadow-xs ' +
      'dark:bg-violet-950/70 dark:hover:bg-violet-900/80 dark:text-violet-200 dark:border-violet-700/60';
  } else if (variant === 'secondary') {
    // Sleek institutional slate button
    variantClasses =
      'h-[26px] px-2.5 gap-1.5 ' +
      'bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200/90 shadow-xs ' +
      'dark:bg-slate-800/90 dark:hover:bg-slate-700 dark:text-slate-200 dark:border-slate-700/80';
  } else if (variant === 'ghost') {
    variantClasses =
      'h-[26px] px-2 gap-1 bg-transparent border-0 ' +
      'text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 ' +
      'hover:bg-violet-50 dark:hover:bg-violet-950/40 active:bg-violet-100 dark:active:bg-violet-950/60';
  } else if (variant === 'icon') {
    variantClasses =
      'w-[26px] h-[26px] p-0 bg-transparent border border-transparent ' +
      'text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 ' +
      'hover:bg-violet-50 dark:hover:bg-violet-950/40 hover:border-violet-200 dark:hover:border-violet-800/40 rounded-md';
  }

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={fullActionName}
      title={effectiveTitle}
      className={`${baseClasses} ${variantClasses} ${className}`}
    >
      {Icon && <Icon className="w-3.5 h-3.5 shrink-0 stroke-[2]" />}
      {variant !== 'icon' && label && <span>{label}</span>}
    </button>
  );
};
