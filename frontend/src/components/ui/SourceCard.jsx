import React from 'react';
import { ExternalLink, Bookmark, CheckCircle2 } from 'lucide-react';
import Badge from './Badge';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './Card';
import Button from './Button';

export default function SourceCard({
  document: doc,
  onOpenDetail,
  className = '',
}) {
  if (!doc) return null;

  return (
    <Card
      variant="interactive"
      className={`border-slate-800 text-left ${className}`}
      onClick={() => onOpenDetail?.(doc)}
    >
      <CardHeader className="pb-2.5">
        <div className="flex items-center justify-between gap-2 mb-1.5 flex-wrap">
          <div className="flex items-center gap-1.5">
            <Badge variant={doc.category} size="sm">
              {doc.category}
            </Badge>
            <span className="text-xs text-slate-400 font-medium px-2 py-0.5 rounded bg-slate-800/80 border border-slate-700/60">
              {doc.module}
            </span>
          </div>

          <div className="flex items-center gap-1 text-[11px] text-slate-400">
            <span className="font-mono text-[10px] text-slate-400">v{doc.version || doc.current_version || '1.0'}</span>
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          </div>
        </div>

        <CardTitle className="text-sm font-semibold text-slate-100 hover:text-blue-300 transition-colors line-clamp-1">
          {doc.title}
        </CardTitle>
      </CardHeader>

      <CardContent className="py-2.5">
        <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
          {doc.content}
        </p>

        {doc.note && (
          <div className="mt-2.5 pt-2 border-t border-slate-800/60 flex items-start gap-1.5 text-[11px] text-slate-400">
            <Bookmark className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
            <span className="line-clamp-1 italic">{doc.note}</span>
          </div>
        )}
      </CardContent>

      <CardFooter className="pt-2">
        <span className="text-[10px] text-slate-500 font-mono">
          {doc.document_code || (doc.id ? `DOC_${doc.id}` : 'SRC')}
        </span>
        <Button
          variant="ghost"
          size="sm"
          className="text-xs h-7 text-blue-400 hover:text-blue-300"
          rightIcon={ExternalLink}
          onClick={(e) => {
            e.stopPropagation();
            onOpenDetail?.(doc);
          }}
        >
          Xem chi tiết
        </Button>
      </CardFooter>
    </Card>
  );
}
