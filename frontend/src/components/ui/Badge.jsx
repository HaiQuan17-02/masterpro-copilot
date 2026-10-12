import React from 'react';

const variantClasses = {
  default: 'bg-slate-800 text-slate-300 border-slate-700/80',
  primary: 'bg-blue-600/15 text-blue-400 border-blue-500/30',
  secondary: 'bg-indigo-600/15 text-indigo-300 border-indigo-500/30',
  success: 'bg-emerald-600/15 text-emerald-400 border-emerald-500/30',
  warning: 'bg-amber-600/15 text-amber-300 border-amber-500/30',
  error: 'bg-red-600/15 text-red-400 border-red-500/30',
  info: 'bg-sky-600/15 text-sky-400 border-sky-500/30',
  outline: 'bg-transparent text-slate-300 border-slate-600',

  // MasterPro Knowledge Base Specific presets
  HDSD: 'bg-sky-500/15 text-sky-300 border-sky-400/30',
  FAQ: 'bg-indigo-500/15 text-indigo-300 border-indigo-400/30',
  RUNBOOK_L1: 'bg-amber-500/15 text-amber-300 border-amber-400/30',
  APPROVED: 'bg-emerald-500/15 text-emerald-300 border-emerald-400/30',
  DRAFT: 'bg-slate-700/30 text-slate-400 border-slate-600/40',
};

const sizeClasses = {
  sm: 'px-2 py-0.5 text-[10px] gap-1 font-semibold rounded-md',
  md: 'px-2.5 py-1 text-xs gap-1.5 font-medium rounded-lg',
  lg: 'px-3 py-1.5 text-sm gap-2 font-medium rounded-xl',
};

export default function Badge({
  variant = 'default',
  size = 'md',
  icon: Icon,
  children,
  className = '',
  ...props
}) {
  const chosenVariant = variantClasses[variant] ? variant : 'default';

  return (
    <span
      className={`
        inline-flex items-center justify-center border transition-colors select-none tracking-wide uppercase
        ${variantClasses[chosenVariant]}
        ${sizeClasses[size] || sizeClasses.md}
        ${className}
      `}
      {...props}
    >
      {Icon && <Icon className="w-3 h-3 shrink-0" />}
      {children}
    </span>
  );
}
