import React, { useState } from 'react';
import { X, Send, AlertTriangle, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function EscalationModal({ isOpen, onClose, query, botResponse, contextChunks }) {
  if (!isOpen) return null;

  const [priority, setPriority] = useState('medium');
  const [userRole, setUserRole] = useState('cashier');
  const [userNote, setUserNote] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedTicket, setSubmittedTicket] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:8000/api/escalation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query || 'Yêu cầu hỗ trợ từ hội thoại',
          bot_response: botResponse || '',
          user_note: userNote,
          priority: priority,
          user_role: userRole,
          retrieved_chunks: contextChunks || []
        })
      });

      if (!res.ok) {
        throw new Error(`Gửi ticket thất bại (${res.status})`);
      }

      const data = await res.json();
      setSubmittedTicket(data);
    } catch (err) {
      setError(err.message || 'Lỗi kết nối máy chủ');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetAndClose = () => {
    setSubmittedTicket(null);
    setUserNote('');
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-100 text-base">Chuyển Tiếp Hỗ Trợ Chuyên Viên (L2)</h3>
              <p className="text-xs text-slate-400">Tạo ticket chuyển đến IT/Helpdesk MasterPro khi Copilot chưa giải quyết được</p>
            </div>
          </div>
          <button
            onClick={handleResetAndClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {submittedTicket ? (
          <div className="py-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/20">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-base font-semibold text-white">Đã Tạo Ticket Hỗ Trợ Thành Công</h4>
              <p className="text-xs text-slate-400 mt-1">
                Mã Ticket: <span className="font-mono text-cyan-400 font-bold">{submittedTicket.ticket_id}</span>
              </p>
              <p className="text-xs text-slate-400 mt-2">
                Đội ngũ kỹ thuật MasterPro L2 đã nhận được toàn bộ ngữ cảnh và sẽ phản hồi sớm nhất.
              </p>
            </div>
            <button
              onClick={handleResetAndClose}
              className="px-5 py-2 text-xs font-semibold rounded-xl bg-cyan-600 text-white hover:bg-cyan-500 cursor-pointer"
            >
              Hoàn tất
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Query Summary */}
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
              <span className="text-slate-400 block mb-1">Vấn đề cần hỗ trợ:</span>
              <p className="text-slate-200 font-medium line-clamp-2">{query || 'Chưa có câu hỏi cụ thể'}</p>
            </div>

            {/* Role & Priority */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1.5 font-medium">Vai trò người gửi</label>
                <select
                  value={userRole}
                  onChange={(e) => setUserRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="cashier">Thu ngân (POS)</option>
                  <option value="inventory">Thủ kho (Kho vận)</option>
                  <option value="accountant">Kế toán viên</option>
                  <option value="admin">Quản trị cửa hàng</option>
                </select>
              </div>

              <div>
                <label className="text-xs text-slate-400 block mb-1.5 font-medium">Mức độ ưu tiên</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="low">Thấp (Tư vấn nghiệp vụ)</option>
                  <option value="medium">Trung bình (Thắc mắc quy trình)</option>
                  <option value="high">Cao (Lỗi phần mềm / Lệch số)</option>
                  <option value="urgent">Khẩn cấp (Ngừng thanh toán/POS)</option>
                </select>
              </div>
            </div>

            {/* User Note */}
            <div>
              <label className="text-xs text-slate-400 block mb-1.5 font-medium">
                Mô tả chi tiết tình huống thực tế tại cửa hàng:
              </label>
              <textarea
                rows={3}
                required
                value={userNote}
                onChange={(e) => setUserNote(e.target.value)}
                placeholder="Ví dụ: Đã thử làm theo hướng dẫn in lại hóa đơn nhưng máy POS báo lỗi COM port disconnected..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 resize-none"
              />
            </div>

            {/* Actions */}
            <div className="pt-2 flex justify-end gap-2.5">
              <button
                type="button"
                onClick={handleResetAndClose}
                className="px-4 py-2 text-xs font-medium rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 cursor-pointer"
              >
                Hủy
              </button>
              <button
                type="submit"
                disabled={isSubmitting || !userNote.trim()}
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded-xl bg-amber-600 text-white hover:bg-amber-500 disabled:opacity-50 cursor-pointer shadow-lg shadow-amber-600/20"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{isSubmitting ? 'Đang gửi...' : 'Gửi phiếu L2'}</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
