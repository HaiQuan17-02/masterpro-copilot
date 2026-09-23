import React from 'react';
import { User, Bot } from 'lucide-react';
import Citation from './Citation';

function ChatMessage({ message }) {
  const isUser = message.sender === 'user';

  // Render markdown-like bold text and lines
  const renderFormattedText = (text) => {
    return text.split('\n').map((line, idx) => {
      // Bold handling
      const parts = line.split(/(\*\*.*?\*\*)/g);
      return (
        <span key={idx} className="block min-h-[1.25rem]">
          {parts.map((part, pIdx) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={pIdx} className="font-semibold text-white">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          })}
        </span>
      );
    });
  };

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-md ${
          isUser
            ? 'bg-gradient-to-tr from-cyan-500 to-blue-600 text-white'
            : 'bg-gradient-to-tr from-indigo-600 to-violet-600 text-white border border-indigo-400/30'
        }`}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      {/* Bubble Content */}
      <div
        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 text-sm leading-relaxed shadow-lg ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-none shadow-blue-500/10'
            : 'bg-slate-800/90 text-slate-200 border border-slate-700/70 rounded-tl-none shadow-black/20'
        }`}
      >
        <div className="space-y-1">{renderFormattedText(message.text)}</div>

        {/* Citations block for bot */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <Citation citations={message.citations} />
        )}

        {/* Timestamp */}
        {message.timestamp && (
          <div
            className={`mt-2 text-[10px] text-right ${
              isUser ? 'text-blue-200' : 'text-slate-400'
            }`}
          >
            {message.timestamp}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
