import React from 'react';
import { BookOpen } from 'lucide-react';

export default function Citation({
  citation,
  index,
  onClick,
  active = false,
  className = '',
}) {
  // Support string or object citation
  const title = typeof citation === 'string' ? citation : citation.title || citation.document || 'Tài liệu gốc';
  const page = typeof citation === 'object' ? citation.page : null;
  const docCode = typeof citation === 'object' ? citation.document_code : null;
  const category = typeof citation === 'object' ? citation.category : null;

  return (
    <button
      type="button"
      onClick={() => onClick?.(citation)}
      className={`
        inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[11px] font-medium
        transition-all duration-200 cursor-pointer select-none border text-left
        ${
          active
            ? 'bg-blue-600/30 text-blue-300 border-blue-400 shadow-sm shadow-blue-500/20'
            : 'bg-slate-800/80 hover:bg-slate-750 text-slate-300 hover:text-blue-300 border-slate-700/80 hover:border-blue-500/40'
        }
        ${className}
      `}
      title={`Bấm để xem trích dẫn gốc: ${title}${category ? ` (${category})` : ''}`}
    >
      <BookOpen className="w-3 h-3 text-blue-400 shrink-0" />
      <span className="font-semibold text-blue-400">[{index !== undefined ? index + 1 : 'cite'}]</span>
      {category && (
        <span className="text-[9px] px-1 py-0.2 rounded bg-slate-750 text-slate-300 font-medium">
          {category}
        </span>
      )}
      <span className="truncate max-w-[140px] sm:max-w-[200px]">{title}</span>
      {page && <span className="text-[10px] text-slate-400 shrink-0">tr.{page}</span>}
      {docCode && <span className="text-[9px] text-slate-500 shrink-0 font-mono">({docCode})</span>}
    </button>
  );
}
