import React from 'react';
import { LucideIcon, Lock } from 'lucide-react';

export interface ActionButtonProps {
  variant?: 'primary' | 'ghost' | 'icon';
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

  // Base layout: exactly 30px visual height, >= 44px tap target via pseudo-element, accessible focus ring, no-wrap
  const baseClasses =
    'relative inline-flex items-center justify-center font-sans text-[13px] font-semibold whitespace-nowrap rounded-md transition-colors select-none shrink-0 ' +
    "after:content-[''] after:absolute after:top-1/2 after:left-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-[max(100%,44px)] after:h-[max(100%,44px)] after:min-w-[44px] after:min-h-[44px] " +
    'focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500 focus-visible:ring-offset-2 dark:focus-visible:ring-offset-slate-900';

  if (disabled) {
    const disabledClasses =
      variant === 'icon'
        ? `${baseClasses} w-[30px] h-[30px] p-0 bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-700/60 cursor-not-allowed opacity-80 ${className}`
        : `${baseClasses} h-[30px] px-3 gap-1.5 bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-700/60 cursor-not-allowed opacity-80 ${className}`;

    return (
      <button
        type="button"
        disabled
        aria-label={fullActionName}
        title={effectiveTitle}
        className={disabledClasses}
      >
        <Lock className="w-3.5 h-3.5 shrink-0 text-slate-400 dark:text-slate-500" />
        {variant !== 'icon' && <span>{label || 'Blocked'}</span>}
      </button>
    );
  }

  let variantClasses = '';
  if (variant === 'primary') {
    variantClasses =
      'h-[30px] px-3 gap-1.5 bg-violet-600 hover:bg-violet-700 active:bg-violet-800 text-white shadow-none active:scale-[0.98]';
  } else if (variant === 'ghost') {
    variantClasses =
      'h-[30px] px-2.5 gap-1.5 bg-transparent border-0 text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 hover:bg-violet-50 dark:hover:bg-violet-950/40 active:bg-violet-100 dark:active:bg-violet-950/60 active:scale-[0.98]';
  } else if (variant === 'icon') {
    variantClasses =
      'w-[30px] h-[30px] p-0 bg-transparent border-0 text-violet-600 dark:text-violet-400 hover:text-violet-700 dark:hover:text-violet-300 hover:bg-violet-50 dark:hover:bg-violet-950/40 active:bg-violet-100 dark:active:bg-violet-950/60 rounded-md active:scale-[0.98]';
  }

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={fullActionName}
      title={effectiveTitle}
      className={`${baseClasses} ${variantClasses} ${className}`}
    >
      {Icon && <Icon className="w-4 h-4 shrink-0 stroke-[2]" />}
      {variant !== 'icon' && label && <span>{label}</span>}
    </button>
  );
};
