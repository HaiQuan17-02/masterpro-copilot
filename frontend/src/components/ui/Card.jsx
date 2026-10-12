import React from 'react';

const cardVariants = {
  default: 'bg-slate-900/90 border border-slate-800 text-slate-100 shadow-md',
  raised: 'bg-slate-850 border border-slate-700/80 text-slate-100 shadow-xl',
  interactive: 'bg-slate-900/80 hover:bg-slate-850 border border-slate-800 hover:border-blue-500/50 text-slate-100 shadow-md hover:shadow-blue-500/10 transition-all duration-200 cursor-pointer hover:-translate-y-0.5',
  outline: 'bg-transparent border border-slate-700/80 text-slate-200',
};

export function Card({
  variant = 'default',
  className = '',
  children,
  ...props
}) {
  return (
    <div
      className={`rounded-2xl backdrop-blur-md overflow-hidden ${cardVariants[variant] || cardVariants.default} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ className = '', children, ...props }) {
  return (
    <div className={`p-4 sm:p-5 border-b border-slate-800/80 flex flex-col gap-1 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className = '', children, ...props }) {
  return (
    <h3 className={`text-base sm:text-lg font-semibold text-slate-100 tracking-tight ${className}`} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className = '', children, ...props }) {
  return (
    <p className={`text-xs sm:text-sm text-slate-400 ${className}`} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className = '', children, ...props }) {
  return (
    <div className={`p-4 sm:p-5 text-sm text-slate-300 leading-relaxed ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className = '', children, ...props }) {
  return (
    <div className={`p-4 sm:p-5 pt-0 border-t border-slate-800/50 mt-auto flex items-center justify-between ${className}`} {...props}>
      {children}
    </div>
  );
}

export default Card;
