import React from 'react';
import { Loader2 } from 'lucide-react';

const variantClasses = {
  primary: 'bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white shadow-md shadow-blue-600/20 border border-blue-500/30',
  secondary: 'bg-slate-800 hover:bg-slate-750 active:bg-slate-850 text-slate-100 border border-slate-750 shadow-sm',
  ghost: 'bg-transparent hover:bg-slate-800/60 active:bg-slate-800 text-slate-300 hover:text-slate-100',
  danger: 'bg-red-600 hover:bg-red-500 active:bg-red-700 text-white shadow-md shadow-red-600/20 border border-red-500/30',
  success: 'bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white shadow-md shadow-emerald-600/20 border border-emerald-500/30',
  outline: 'bg-transparent hover:bg-blue-600/10 active:bg-blue-600/20 text-blue-400 hover:text-blue-300 border border-blue-500/40',
};

const sizeClasses = {
  sm: 'px-2.5 py-1 text-xs rounded-lg gap-1.5 h-7',
  md: 'px-3.5 py-1.5 text-sm rounded-lg gap-2 h-9',
  lg: 'px-5 py-2.5 text-base rounded-xl gap-2.5 h-11',
  icon: 'p-2 rounded-lg aspect-square flex items-center justify-center h-9 w-9',
};

export default function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  loadingText,
  disabled = false,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  children,
  className = '',
  type = 'button',
  ...props
}) {
  const isButtonDisabled = disabled || isLoading;

  return (
    <button
      type={type}
      disabled={isButtonDisabled}
      className={`
        inline-flex items-center justify-center font-medium transition-all duration-200 cursor-pointer
        select-none focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900
        ${variantClasses[variant] || variantClasses.primary}
        ${sizeClasses[size] || sizeClasses.md}
        ${isButtonDisabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : 'hover:scale-[1.01] active:scale-[0.99]'}
        ${className}
      `}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin text-current shrink-0" />
          {loadingText ? <span>{loadingText}</span> : children}
        </>
      ) : (
        <>
          {LeftIcon && <LeftIcon className="w-4 h-4 shrink-0" />}
          {children}
          {RightIcon && <RightIcon className="w-4 h-4 shrink-0" />}
        </>
      )}
    </button>
  );
}
