import React from 'react';
import { AlertCircle, Loader2 } from 'lucide-react';

export default function Input({
  label,
  error,
  helperText,
  leftIcon: LeftIcon,
  rightIcon: RightIcon,
  disabled = false,
  isLoading = false,
  className = '',
  id,
  ...props
}) {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);
  const isInputDisabled = disabled || isLoading;

  return (
    <div className="w-full flex flex-col gap-1.5 text-left">
      {label && (
        <label
          htmlFor={inputId}
          className="text-xs font-semibold text-slate-300 flex items-center justify-between"
        >
          <span>{label}</span>
        </label>
      )}

      <div className="relative flex items-center w-full">
        {LeftIcon && (
          <div className="absolute left-3 text-slate-400 pointer-events-none">
            <LeftIcon className="w-4 h-4" />
          </div>
        )}

        <input
          id={inputId}
          disabled={isInputDisabled}
          className={`
            w-full bg-slate-900/90 text-slate-100 placeholder-slate-500 text-sm rounded-xl px-3.5 py-2
            border transition-all duration-200 outline-none
            ${LeftIcon ? 'pl-9' : ''}
            ${RightIcon || error || isLoading ? 'pr-9' : ''}
            ${
              error
                ? 'border-red-500/80 focus:border-red-400 focus:ring-2 focus:ring-red-500/20'
                : 'border-slate-700/80 hover:border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
            }
            ${isInputDisabled ? 'opacity-50 cursor-not-allowed bg-slate-800/50' : ''}
            ${className}
          `}
          {...props}
        />

        {isLoading ? (
          <div className="absolute right-3 text-blue-400 pointer-events-none">
            <Loader2 className="w-4 h-4 animate-spin" />
          </div>
        ) : error ? (
          <div className="absolute right-3 text-red-400 pointer-events-none">
            <AlertCircle className="w-4 h-4" />
          </div>
        ) : (
          RightIcon && (
            <div className="absolute right-3 text-slate-400 pointer-events-none">
              <RightIcon className="w-4 h-4" />
            </div>
          )
        )}
      </div>

      {error ? (
        <p className="text-xs text-red-400 flex items-center gap-1 mt-0.5">
          <span>{error}</span>
        </p>
      ) : helperText ? (
        <p className="text-[11px] text-slate-400 mt-0.5">{helperText}</p>
      ) : null}
    </div>
  );
}
