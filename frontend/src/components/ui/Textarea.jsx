import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function Textarea({
  label,
  error,
  helperText,
  disabled = false,
  rows = 3,
  maxLength,
  showCount = false,
  value,
  onChange,
  className = '',
  id,
  ...props
}) {
  const textareaId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);
  const currentLength = typeof value === 'string' ? value.length : 0;

  return (
    <div className="w-full flex flex-col gap-1.5 text-left">
      <div className="flex items-center justify-between">
        {label && (
          <label
            htmlFor={textareaId}
            className="text-xs font-semibold text-slate-300"
          >
            {label}
          </label>
        )}
        {showCount && maxLength && (
          <span className="text-[10px] text-slate-400 font-mono">
            {currentLength}/{maxLength}
          </span>
        )}
      </div>

      <div className="relative w-full">
        <textarea
          id={textareaId}
          rows={rows}
          value={value}
          onChange={onChange}
          maxLength={maxLength}
          disabled={disabled}
          className={`
            w-full bg-slate-900/90 text-slate-100 placeholder-slate-500 text-sm rounded-xl px-3.5 py-2.5
            border transition-all duration-200 outline-none resize-y min-h-[72px]
            ${
              error
                ? 'border-red-500/80 focus:border-red-400 focus:ring-2 focus:ring-red-500/20'
                : 'border-slate-700/80 hover:border-slate-600 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed bg-slate-800/50' : ''}
            ${className}
          `}
          {...props}
        />

        {error && (
          <div className="absolute top-3 right-3 text-red-400 pointer-events-none">
            <AlertCircle className="w-4 h-4" />
          </div>
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
