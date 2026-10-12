import React, { useState } from 'react';
import { Bot, User, Copy, Check, Sparkles } from 'lucide-react';
import Citation from './Citation';
import Feedback from './Feedback';

export default function ChatBubble({
  message,
  onCitationClick,
  onFeedbackChange,
  className = '',
}) {
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Helper to render bold markdown **text** and inline code `code`
  const renderFormattedText = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, lineIdx) => {
      // Split by bold (**...**) and inline code (`...`)
      const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
      const formattedLine = parts.map((part, partIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={partIdx} className="font-semibold text-slate-100">
              {part.slice(2, -2)}
            </strong>
          );
        }
        if (part.startsWith('`') && part.endsWith('`')) {
          return (
            <code
              key={partIdx}
              className="px-1.5 py-0.5 rounded bg-slate-800 text-blue-300 font-mono text-[12px] border border-slate-700/60"
            >
              {part.slice(1, -1)}
            </code>
          );
        }
        return part;
      });

      return (
        <span key={lineIdx} className="block min-h-[20px]">
          {formattedLine}
        </span>
      );
    });
  };

  return (
    <div
      className={`
        flex gap-3 w-full my-2.5 transition-all text-left
        ${isUser ? 'justify-end' : 'justify-start'}
        ${className}
      `}
    >
      {/* Bot Avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 border border-blue-400/40 flex items-center justify-center text-white shrink-0 shadow-md shadow-blue-600/20 mt-1">
          <Bot className="w-4 h-4" />
        </div>
      )}

      {/* Bubble Container */}
      <div
        className={`
          flex flex-col max-w-[85%] sm:max-w-[78%]
          ${isUser ? 'items-end' : 'items-start'}
        `}
      >
        {/* Name and Timestamp */}
        <div className="flex items-center gap-1.5 mb-1 px-1 text-[11px] text-slate-400">
          <span>{isUser ? 'Bạn' : 'MasterPro Copilot'}</span>
          <span>•</span>
          <span>{message.timestamp || 'Vừa xong'}</span>
          {!isUser && (
            <span className="inline-flex items-center gap-0.5 text-[10px] text-blue-400 bg-blue-500/10 px-1.5 py-0.2 rounded font-medium ml-1">
              <Sparkles className="w-2.5 h-2.5" />
              AI Verified
            </span>
          )}
        </div>

        {/* Bubble Surface */}
        <div
          className={`
            p-3.5 sm:p-4 text-sm leading-relaxed rounded-2xl shadow-md
            ${
              isUser
                ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-xs shadow-blue-600/20'
                : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-xs shadow-slate-950/50'
            }
          `}
        >
          <div className="space-y-1">{renderFormattedText(message.text)}</div>

          {/* Citations section if present */}
          {message.citations && message.citations.length > 0 && (
            <div className="mt-3.5 pt-3 border-t border-slate-800/80">
              <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <span>Nguồn tham chiếu ({message.citations.length}):</span>
              </p>
              <div className="flex flex-wrap gap-1.5">
                {message.citations.map((cite, cIdx) => (
                  <Citation
                    key={cIdx}
                    index={cIdx}
                    citation={cite}
                    onClick={() => onCitationClick?.(cite)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Bot Message Action Toolbar */}
        {!isUser && (
          <div className="flex items-center gap-2 mt-1.5 px-1 text-slate-400">
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 text-[11px] hover:text-slate-200 transition-colors p-1 rounded hover:bg-slate-800 cursor-pointer"
              title="Sao chép câu trả lời"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Đã chép</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Sao chép</span>
                </>
              )}
            </button>

            <span className="text-slate-700">|</span>

            <Feedback
              messageId={message.id}
              initialFeedback={message.feedback}
              onFeedbackChange={onFeedbackChange}
              compact={true}
            />
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 shrink-0 shadow-sm mt-1">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
}
