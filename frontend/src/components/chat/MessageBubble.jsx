import React, { useState } from 'react';
import {
  User,
  Bot,
  Copy,
  Check,
  Bookmark,
  FileText,
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  ShieldAlert,
  ExternalLink,
  HelpCircle
} from 'lucide-react';

export default function MessageBubble({ message, onOpenCitation, onOpenEscalation }) {
  const isUser = message.sender === 'user';
  const [copied, setCopied] = useState(false);
  const [showCitations, setShowCitations] = useState(true);

  // Feedback state
  const [rating, setRating] = useState(message.userFeedback || null); // 'like' | 'dislike' | null
  const [showDislikeMenu, setShowDislikeMenu] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const sendFeedback = async (vote, reason = null) => {
    setRating(vote);
    setShowDislikeMenu(false);
    try {
      await fetch('http://localhost:8000/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: message.id || `msg_${Date.now()}`,
          rating: vote,
          reason: reason,
          query: message.query || null,
          cited_doc_ids: (message.citations || []).map((c) => c.document_id || c.document).filter(Boolean)
        })
      });
      setFeedbackSent(true);
      setTimeout(() => setFeedbackSent(false), 2500);
    } catch (e) {
      console.error('Failed to submit feedback', e);
    }
  };

  // Basic formatted markdown rendering (bold, lists, headings)
  const renderFormattedText = (text) => {
    if (!text) return null;
    const lines = text.split('\n');

    return lines.map((line, idx) => {
      // Heading 3 / 2
      if (line.startsWith('### ')) {
        return <h4 key={idx} className="text-sm font-bold text-cyan-300 mt-2 mb-1">{line.slice(4)}</h4>;
      }
      if (line.startsWith('## ')) {
        return <h3 key={idx} className="text-sm font-bold text-slate-100 mt-2 mb-1">{line.slice(3)}</h3>;
      }
      // List item
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={idx} className="ml-4 list-disc text-slate-200">
            {formatInline(line.slice(2))}
          </li>
        );
      }
      // Numbered step
      if (/^\d+\.\s/.test(line)) {
        return (
          <li key={idx} className="ml-4 list-decimal text-slate-200">
            {formatInline(line.replace(/^\d+\.\s/, ''))}
          </li>
        );
      }

      return (
        <p key={idx} className="min-h-[1rem]">
          {formatInline(line)}
        </p>
      );
    });
  };

  const formatInline = (str) => {
    const parts = str.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, pIdx) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={pIdx} className="font-semibold text-white">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={pIdx} className="px-1 py-0.5 rounded bg-slate-950 font-mono text-cyan-300 text-xs">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <div className={`flex gap-3 my-4 group ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
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

      {/* Bubble Box */}
      <div
        className={`relative max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 text-sm leading-relaxed shadow-lg transition-all ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-none shadow-blue-500/10'
            : 'bg-slate-900/90 text-slate-200 border border-slate-800 rounded-tl-none shadow-black/20'
        }`}
      >
        {/* Copy Button */}
        {!isUser && (
          <button
            onClick={handleCopy}
            className="absolute top-2.5 right-2.5 p-1 rounded-md text-slate-500 hover:text-slate-200 hover:bg-slate-800 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
            title="Sao chép nội dung"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        )}

        {/* Text Content */}
        <div className="space-y-1.5">{renderFormattedText(message.text)}</div>

        {/* Citations Block */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="mt-3.5 pt-3 border-t border-slate-800">
            <button
              onClick={() => setShowCitations(!showCitations)}
              className="flex items-center justify-between w-full text-xs font-semibold text-slate-400 hover:text-cyan-400 transition-colors cursor-pointer mb-2"
            >
              <span className="flex items-center gap-1.5">
                <Bookmark className="w-3.5 h-3.5 text-cyan-400" />
                <span>Nguồn tham chiếu Qdrant ({message.citations.length}):</span>
              </span>
              {showCitations ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showCitations && (
              <div className="flex flex-col gap-2 mt-2">
                {message.citations.map((cite, cIdx) => (
                  <div
                    key={cIdx}
                    onClick={() => onOpenCitation && onOpenCitation(cite)}
                    className="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800/80 hover:border-cyan-500/50 hover:bg-slate-950 transition-all text-xs cursor-pointer group/cite"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <FileText className="w-3.5 h-3.5 text-cyan-400 shrink-0 group-hover/cite:text-cyan-300" />
                        <span className="font-semibold text-slate-200 group-hover/cite:text-white truncate">
                          {cite.heading_path || cite.title}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        {cite.score && (
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                            {Math.round(cite.score * 100)}%
                          </span>
                        )}
                        <ExternalLink className="w-3 h-3 text-slate-500 group-hover/cite:text-cyan-400" />
                      </div>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-[11px] text-slate-400">
                      <span>{cite.document}</span>
                      {cite.page && (
                        <>
                          <span>•</span>
                          <span className="text-amber-400">Trang {cite.page}</span>
                        </>
                      )}
                      <span className="ml-auto text-[10px] text-cyan-400 opacity-0 group-hover/cite:opacity-100 transition-opacity">
                        Nhấn để xem trích đoạn &rarr;
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Footer Actions: Like, Dislike, Escalation */}
        {!isUser && (
          <div className="mt-3 pt-2.5 border-t border-slate-800/80 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2 relative">
              {/* Like Button */}
              <button
                onClick={() => sendFeedback('like')}
                className={`p-1 rounded-md transition-colors cursor-pointer flex items-center gap-1 ${
                  rating === 'like'
                    ? 'text-emerald-400 bg-emerald-500/10'
                    : 'text-slate-500 hover:text-emerald-400 hover:bg-slate-800'
                }`}
                title="Hữu ích"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>

              {/* Dislike Button & Dropdown */}
              <button
                onClick={() => {
                  if (rating === 'dislike') {
                    setRating(null);
                  } else {
                    setShowDislikeMenu(!showDislikeMenu);
                  }
                }}
                className={`p-1 rounded-md transition-colors cursor-pointer flex items-center gap-1 ${
                  rating === 'dislike'
                    ? 'text-rose-400 bg-rose-500/10'
                    : 'text-slate-500 hover:text-rose-400 hover:bg-slate-800'
                }`}
                title="Chưa đúng hoặc chưa đầy đủ"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>

              {/* Popover chọn lý do dislike */}
              {showDislikeMenu && (
                <div className="absolute left-0 bottom-8 z-30 w-52 p-2 rounded-xl bg-slate-950 border border-slate-800 shadow-xl space-y-1 animate-in fade-in zoom-in-95 duration-150">
                  <span className="text-[10px] font-semibold text-slate-400 px-2 block">Lý do chưa hữu ích:</span>
                  {[
                    { label: 'Sai bước thực hiện', key: 'incorrect_step' },
                    { label: 'Thiếu thông tin / chưa rõ', key: 'missing_info' },
                    { label: 'Không khớp câu hỏi', key: 'irrelevant' },
                    { label: 'Tài liệu hướng dẫn cũ', key: 'outdated' }
                  ].map((item) => (
                    <button
                      key={item.key}
                      onClick={() => sendFeedback('dislike', item.key)}
                      className="w-full text-left px-2 py-1.5 rounded-lg text-xs text-slate-300 hover:bg-slate-800 hover:text-rose-300 transition-colors cursor-pointer"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}

              {feedbackSent && (
                <span className="text-[11px] text-emerald-400 font-medium animate-pulse">
                  Đã ghi nhận phản hồi!
                </span>
              )}
            </div>

            {/* Escalation Button */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => onOpenEscalation && onOpenEscalation(message)}
                className="flex items-center gap-1 text-[11px] text-amber-400/90 hover:text-amber-300 bg-amber-500/10 hover:bg-amber-500/20 px-2 py-1 rounded-md border border-amber-500/20 transition-all cursor-pointer"
                title="Chưa hài lòng? Chuyển câu hỏi cho IT/Chuyên viên L2"
              >
                <ShieldAlert className="w-3 h-3" />
                <span>Chuyển L2</span>
              </button>

              {/* Timestamp */}
              {message.timestamp && (
                <span className="text-[10px] text-slate-500 font-mono">
                  {message.timestamp}
                </span>
              )}
            </div>
          </div>
        )}

        {/* User Timestamp */}
        {isUser && message.timestamp && (
          <div className="mt-1 text-[10px] text-right text-blue-200">
            {message.timestamp}
          </div>
        )}
      </div>
    </div>
  );
}
