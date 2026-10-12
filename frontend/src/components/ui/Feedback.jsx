import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Check, MessageSquare, X, Send } from 'lucide-react';
import Button from './Button';

/**
 * Feedback Controls Component
 * Allows users to provide rating (helpful / unhelpful) and detailed comments on AI responses.
 *
 * @param {string|number} messageId - Unique ID of the message
 * @param {'like'|'dislike'|null} initialFeedback - Initial feedback value
 * @param {function} onFeedbackChange - Callback (feedbackType, reasonDetails) => void
 * @param {boolean} disabled - Disable feedback buttons
 * @param {boolean} compact - Compact inline mode for message bubbles
 * @param {string} className - Additional CSS classes
 */
export default function Feedback({
  messageId,
  initialFeedback = null,
  onFeedbackChange,
  disabled = false,
  compact = true,
  className = '',
}) {
  const [feedback, setFeedback] = useState(initialFeedback);
  const [showReasonModal, setShowReasonModal] = useState(false);
  const [selectedReason, setSelectedReason] = useState('');
  const [comment, setComment] = useState('');
  const [submittedMessage, setSubmittedMessage] = useState('');

  const feedbackReasons = [
    'Thông tin không chính xác',
    'Trích dẫn không khớp nội dung',
    'Quy trình sai khác thực tế MasterPro',
    'Câu trả lời quá dài / khó hiểu',
    'Khác...',
  ];

  const handleLike = () => {
    if (disabled) return;
    const newFeedback = feedback === 'like' ? null : 'like';
    setFeedback(newFeedback);
    setSubmittedMessage(newFeedback === 'like' ? 'Đã ghi nhận hữu ích!' : '');
    onFeedbackChange?.(newFeedback, null);

    if (newFeedback === 'like') {
      setTimeout(() => setSubmittedMessage(''), 2500);
    }
  };

  const handleDislike = () => {
    if (disabled) return;
    if (feedback === 'dislike') {
      setFeedback(null);
      setSubmittedMessage('');
      onFeedbackChange?.(null, null);
    } else {
      setFeedback('dislike');
      setShowReasonModal(true);
    }
  };

  const handleSaveDislikeReason = () => {
    const details = {
      reason: selectedReason || 'Không hài lòng',
      comment: comment.trim(),
    };
    onFeedbackChange?.('dislike', details);
    setShowReasonModal(false);
    setSubmittedMessage('Cảm ơn bạn đã góp ý cải thiện!');
    setTimeout(() => setSubmittedMessage(''), 3000);
  };

  return (
    <div className={`relative inline-flex items-center gap-1.5 ${className}`}>
      {/* Thumbs Up Button */}
      <button
        type="button"
        disabled={disabled}
        onClick={handleLike}
        className={`
          inline-flex items-center gap-1 p-1 rounded-lg text-xs transition-all duration-150 cursor-pointer
          ${
            feedback === 'like'
              ? 'text-blue-400 bg-blue-500/15 border border-blue-500/30 font-medium'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}
        `}
        title="Câu trả lời hữu ích"
        aria-label="Hữu ích"
      >
        <ThumbsUp className="w-3.5 h-3.5" />
        {!compact && <span className="text-[11px]">Hữu ích</span>}
      </button>

      {/* Thumbs Down Button */}
      <button
        type="button"
        disabled={disabled}
        onClick={handleDislike}
        className={`
          inline-flex items-center gap-1 p-1 rounded-lg text-xs transition-all duration-150 cursor-pointer
          ${
            feedback === 'dislike'
              ? 'text-red-400 bg-red-500/15 border border-red-500/30 font-medium'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
          }
          ${disabled ? 'opacity-50 cursor-not-allowed pointer-events-none' : ''}
        `}
        title="Chưa chính xác hoặc cần cải thiện"
        aria-label="Cần cải thiện"
      >
        <ThumbsDown className="w-3.5 h-3.5" />
        {!compact && <span className="text-[11px]">Cần sửa</span>}
      </button>

      {/* Temporary Success Toast / Notice */}
      {submittedMessage && (
        <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-md ml-1 animate-in fade-in">
          <Check className="w-3 h-3" />
          <span>{submittedMessage}</span>
        </span>
      )}

      {/* Dislike Reason Popover Modal */}
      {showReasonModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-3 bg-slate-950/70 backdrop-blur-sm animate-in fade-in">
          <div className="w-full max-w-sm bg-slate-900 border border-slate-750 rounded-2xl p-4 shadow-2xl flex flex-col gap-3 text-left">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-red-500/15 border border-red-500/30 flex items-center justify-center text-red-400">
                  <MessageSquare className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-slate-100">Góp ý câu trả lời</h4>
                  <p className="text-[10px] text-slate-400">Giúp MasterPro Copilot hoàn thiện hơn</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowReasonModal(false)}
                className="p-1 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-md cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-1.5">
              <p className="text-[11px] font-medium text-slate-300">Vấn đề bạn gặp phải là gì?</p>
              <div className="space-y-1">
                {feedbackReasons.map((reason, idx) => (
                  <label
                    key={idx}
                    className={`
                      flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs cursor-pointer border transition-colors
                      ${
                        selectedReason === reason
                          ? 'bg-blue-600/15 border-blue-500/40 text-blue-300 font-medium'
                          : 'bg-slate-850/60 border-slate-800 text-slate-300 hover:bg-slate-800'
                      }
                    `}
                  >
                    <input
                      type="radio"
                      name={`feedback-reason-${messageId || 'default'}`}
                      value={reason}
                      checked={selectedReason === reason}
                      onChange={() => setSelectedReason(reason)}
                      className="accent-blue-500"
                    />
                    <span>{reason}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-[11px] font-medium text-slate-300">Chi tiết bổ sung (tùy chọn):</label>
              <textarea
                rows={2}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Ví dụ: Ở bản cập nhật 2026, nút Lưu đã chuyển thành phím tắt F9..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1.5 text-xs text-slate-100 placeholder-slate-500 outline-none focus:border-blue-500 resize-none"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-800">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowReasonModal(false)}
                className="text-xs h-7"
              >
                Bỏ qua
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleSaveDislikeReason}
                rightIcon={Send}
                className="text-xs h-7"
              >
                Gửi phản hồi
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
