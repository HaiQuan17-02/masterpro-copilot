import React, { useState } from 'react';
import { Send, Sparkles, Loader2 } from 'lucide-react';

function ChatInput({ onSendMessage, disabled = false, onSuggestionClick }) {
  const [input, setInput] = useState('');

  const suggestions = [
    'Làm sao xử lý lỗi máy in?',
    'Cấu hình cổng USB máy in hóa đơn bill',
    'Quy trình mở ca và đóng ca bán hàng'
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="p-4 border-t border-slate-700/60 bg-slate-900/90 backdrop-blur-md">
      {/* Suggestions chips */}
      <div className="flex items-center gap-1.5 mb-3 overflow-x-auto pb-1 scrollbar-none text-xs">
        <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
        <span className="text-slate-400 shrink-0 mr-1">Gợi ý:</span>
        {suggestions.map((text, i) => (
          <button
            key={i}
            type="button"
            onClick={() => onSuggestionClick(text)}
            className="px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/80 transition-all shrink-0 hover:scale-[1.02] active:scale-95"
          >
            {text}
          </button>
        ))}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Nhập câu hỏi hỗ trợ vận hành hoặc kỹ thuật MasterPro..."
          disabled={disabled}
          className="w-full pl-4 pr-12 py-3 bg-slate-800/90 border border-slate-700 text-slate-100 placeholder-slate-400 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 text-sm shadow-inner transition-all disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="absolute right-2 p-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white disabled:opacity-40 disabled:hover:from-blue-600 disabled:hover:to-indigo-600 transition-all duration-200 shadow-md shadow-blue-500/20 active:scale-95 flex items-center justify-center"
        >
          {disabled ? (
            <Loader2 className="w-4 h-4 animate-spin text-white" />
          ) : (
            <Send className="w-4 h-4 text-white" />
          )}
        </button>
      </form>
    </div>
  );
}

export default ChatInput;
