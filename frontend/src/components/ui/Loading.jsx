import React from 'react';
import { Loader2 } from 'lucide-react';

export default function Loading({
  type = 'spinner', // 'spinner' | 'dots' | 'skeleton'
  size = 'md',      // 'sm' | 'md' | 'lg'
  text,
  className = '',
}) {
  const spinnerSizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  };

  if (type === 'dots') {
    return (
      <div className={`inline-flex items-center gap-1.5 py-1 px-2 ${className}`}>
        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" />
        {text && <span className="text-xs text-slate-400 ml-1.5">{text}</span>}
      </div>
    );
  }

  if (type === 'skeleton') {
    return (
      <div className={`w-full space-y-2 animate-pulse ${className}`}>
        <div className="h-4 bg-slate-800 rounded-lg w-3/4" />
        <div className="h-4 bg-slate-800/60 rounded-lg w-full" />
        <div className="h-4 bg-slate-800/40 rounded-lg w-1/2" />
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center justify-center gap-2 text-slate-400 ${className}`}>
      <Loader2 className={`animate-spin text-blue-400 ${spinnerSizes[size] || spinnerSizes.md}`} />
      {text && <span className="text-sm font-medium">{text}</span>}
    </div>
  );
}
