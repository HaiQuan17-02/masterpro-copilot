import React from 'react';
import { FileText, Bookmark, ExternalLink } from 'lucide-react';

function Citation({ citations = [] }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-slate-700/50">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 mb-2">
        <Bookmark className="w-3.5 h-3.5 text-cyan-400" />
        <span>Nguồn tham chiếu từ tài liệu MasterPro:</span>
      </div>
      
      <div className="flex flex-col gap-2">
        {citations.map((cite, idx) => (
          <div
            key={cite.chunk_id || idx}
            className="group flex items-start justify-between gap-3 p-2.5 rounded-lg bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-cyan-500/40 transition-all duration-200"
          >
            <div className="flex items-start gap-2.5 min-w-0">
              <div className="p-1.5 rounded bg-cyan-500/10 text-cyan-400 shrink-0 mt-0.5">
                <FileText className="w-3.5 h-3.5" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-medium text-slate-200 truncate group-hover:text-cyan-300 transition-colors">
                  {cite.title || cite.document}
                </p>
                <div className="flex items-center gap-2 mt-0.5 text-[11px] text-slate-400">
                  <span className="text-slate-300 font-mono">{cite.document}</span>
                  {cite.page && (
                    <>
                      <span>•</span>
                      <span className="text-amber-400/90 font-medium">Trang {cite.page}</span>
                    </>
                  )}
                  {cite.score && (
                    <>
                      <span>•</span>
                      <span className="text-emerald-400/90 font-mono">Độ khớp: {Math.round(cite.score * 100)}%</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            
            <button
              title="Xem trích đoạn tài liệu"
              className="p-1 rounded text-slate-500 hover:text-cyan-400 hover:bg-cyan-500/10 transition-colors shrink-0"
              onClick={() => alert(`Xem chi tiết tài liệu: ${cite.document} (Trang ${cite.page})`)}
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Citation;
