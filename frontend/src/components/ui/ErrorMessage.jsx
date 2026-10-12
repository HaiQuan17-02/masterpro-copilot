import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

export default function ErrorMessage({
  message,
  title = 'Đã có lỗi xảy ra',
  onRetry,
  variant = 'banner', // 'inline' | 'banner' | 'card'
  className = '',
}) {
  if (variant === 'inline') {
    return (
      <div className={`flex items-center gap-1.5 text-xs text-red-400 ${className}`}>
        <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
        <span>{message}</span>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-1.5 underline hover:text-red-300 font-semibold cursor-pointer"
          >
            Thử lại
          </button>
        )}
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div
        className={`
          p-6 rounded-2xl bg-red-950/20 border border-red-800/40 text-center flex flex-col items-center gap-3
          ${className}
        `}
      >
        <div className="w-12 h-12 rounded-full bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div>
          <h4 className="text-base font-semibold text-red-300">{title}</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-md">{message}</p>
        </div>
        {onRetry && (
          <Button
            variant="danger"
            size="sm"
            onClick={onRetry}
            leftIcon={RefreshCw}
            className="mt-1"
          >
            Thử lại
          </Button>
        )}
      </div>
    );
  }

  // Banner variant (default)
  return (
    <div
      className={`
        p-3 sm:p-4 rounded-xl bg-red-950/30 border border-red-800/40 flex items-start justify-between gap-3 text-left
        ${className}
      `}
      role="alert"
    >
      <div className="flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
        <div>
          {title && <h5 className="text-xs font-semibold text-red-300 mb-0.5">{title}</h5>}
          <p className="text-xs text-slate-300 leading-relaxed">{message}</p>
        </div>
      </div>
      {onRetry && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onRetry}
          leftIcon={RefreshCw}
          className="text-red-300 hover:text-red-100 hover:bg-red-900/40 shrink-0 text-xs h-7"
        >
          Thử lại
        </Button>
      )}
    </div>
  );
}
