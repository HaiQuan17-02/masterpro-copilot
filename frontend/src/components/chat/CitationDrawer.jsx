import React from 'react';
import { X, FileText, Bookmark, ExternalLink, Hash, Layers } from 'lucide-react';

export default function CitationDrawer({ isOpen, onClose, citation }) {
  if (!isOpen || !citation) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="relative w-full max-w-lg bg-slate-900 border-l border-slate-800 h-full shadow-2xl flex flex-col p-6 animate-in slide-in-from-right duration-300">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-slate-100 text-base">Chi Tiết Nguồn Trích Dẫn</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto py-5 space-y-4 pr-1">
          {/* Metadata Cards */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block mb-1">Mã tài liệu:</span>
              <span className="text-xs font-mono font-medium text-cyan-300 break-all">
                {citation.document_id || citation.document || 'N/A'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
              <span className="text-[11px] text-slate-400 block mb-1">Độ tương đồng (Score):</span>
              <span className="text-xs font-mono font-semibold text-emerald-400">
                {citation.score ? `${Math.round(citation.score * 100)}%` : 'Grounded'}
              </span>
            </div>
          </div>

          {/* Heading Path */}
          <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80">
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-1">
              <Layers className="w-3.5 h-3.5 text-indigo-400" />
              <span>Cấu trúc phân cấp mục (Heading Path):</span>
            </div>
            <p className="text-sm font-medium text-slate-200">
              {citation.heading_path || citation.title || 'Không xác định'}
            </p>
          </div>

          {/* Document Title / Page */}
          <div className="flex items-center gap-3 text-xs text-slate-300 bg-slate-800/40 p-2.5 rounded-lg">
            <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
            <span className="font-medium text-slate-200">{citation.title || citation.document}</span>
            {citation.page && (
              <span className="ml-auto px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-[11px]">
                Trang {citation.page}
              </span>
            )}
          </div>

          {/* Full Content */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-slate-300">Trích đoạn gốc từ Vector Store:</span>
              <span className="text-[11px] font-mono text-slate-400">
                {citation.content ? `${citation.content.length} ký tự` : ''}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap select-text selection:bg-cyan-500/30">
              {citation.content || citation.preview || 'Không có bản xem trước toàn văn cho phân đoạn này.'}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors cursor-pointer"
          >
            Đóng bảng
          </button>
        </div>
      </div>
    </div>
  );
}
