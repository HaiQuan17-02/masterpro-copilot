import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import Button from './Button';

export default function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder = 'Đặt câu hỏi về nghiệp vụ, lỗi phần cứng, phân quyền...',
  suggestions = [
    'Cách xử lý lỗi máy in hóa đơn bill?',
    'Quy định khóa sổ kế toán cuối kỳ?',
    'Import sản phẩm Excel cột nào bắt buộc?',
    'Quy trình xuất trả hàng cho nhà cung cấp?'
  ],
  onSuggestionClick,
  className = '',
}) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage?.(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={`w-full flex flex-col gap-2.5 p-3 sm:p-4 bg-slate-950/60 border-t border-slate-800 ${className}`}>
      {/* Suggestions / Quick chips */}
      {suggestions && suggestions.length > 0 && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar text-xs">
          <span className="text-[11px] text-slate-500 flex items-center gap-1 shrink-0 font-medium mr-1">
            <Sparkles className="w-3 h-3 text-blue-400" />
            Gợi ý:
          </span>
          {suggestions.map((sug, idx) => (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => {
                if (onSuggestionClick) {
                  onSuggestionClick(sug);
                } else {
                  setInput(sug);
                  textareaRef.current?.focus();
                }
              }}
              className="px-2.5 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-blue-300 border border-slate-800 hover:border-blue-500/40 shrink-0 transition-colors cursor-pointer text-left"
            >
              {sug}
            </button>
          ))}
        </div>
      )}

      {/* Input bar */}
      <form onSubmit={handleSubmit} className="relative flex items-end gap-2 bg-slate-900 border border-slate-750 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 rounded-2xl p-2 transition-all shadow-inner">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          disabled={disabled}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 resize-none outline-none max-h-36 py-1.5 px-2 leading-relaxed"
        />

        <div className="flex items-center gap-1.5 shrink-0 pb-0.5">
          <Button
            type="submit"
            size="sm"
            disabled={!input.trim() || disabled}
            className="rounded-xl px-3 h-8 shadow-none"
            rightIcon={Send}
          >
            <span className="hidden sm:inline">Gửi</span>
          </Button>
        </div>
      </form>

      {/* Helper footer */}
      <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
        <span>Nhấn <kbd className="px-1 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono text-[10px]">Enter</kbd> để gửi, <kbd className="px-1 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono text-[10px]">Shift + Enter</kbd> để xuống dòng</span>
        <span className="flex items-center gap-1 text-slate-400 font-medium">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          MasterPro RAG L1
        </span>
      </div>
    </div>
  );
}
