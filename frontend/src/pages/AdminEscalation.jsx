import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ThumbsUp,
  ThumbsDown,
  TrendingUp,
  RefreshCw,
  Clock,
  CheckCircle,
  AlertCircle,
  Filter,
  User,
  MessageSquare
} from 'lucide-react';

export default function AdminEscalation() {
  const [stats, setStats] = useState(null);
  const [tickets, setTickets] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Fetch Stats
      const statsRes = await fetch('http://localhost:8000/api/feedback/stats');
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }

      // 2. Fetch Tickets
      const url = statusFilter
        ? `http://localhost:8000/api/escalation/tickets?status=${statusFilter}`
        : 'http://localhost:8000/api/escalation/tickets';
      const ticketsRes = await fetch(url);
      if (ticketsRes.ok) {
        const ticketsData = await ticketsRes.json();
        setTickets(ticketsData);
      }
    } catch (err) {
      console.error('Failed to load tickets/stats', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const handleUpdateStatus = async (ticketId, nextStatus) => {
    try {
      const res = await fetch(`http://localhost:8000/api/escalation/tickets/${ticketId}?status=${nextStatus}`, {
        method: 'PATCH'
      });
      if (res.ok) {
        fetchData();
      }
    } catch (err) {
      console.error('Failed to update ticket status', err);
    }
  };

  const priorityBadge = (priority) => {
    switch (priority) {
      case 'urgent':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">Khẩn cấp</span>;
      case 'high':
        return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">Cao</span>;
      case 'medium':
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/20 text-blue-300 border border-blue-500/30">Trung bình</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-700 text-slate-300">Thấp</span>;
    }
  };

  const statusBadge = (status) => {
    switch (status) {
      case 'resolved':
        return <span className="flex items-center gap-1 text-[11px] text-emerald-400 font-medium"><CheckCircle className="w-3.5 h-3.5" /> Đã xử lý</span>;
      case 'in_progress':
        return <span className="flex items-center gap-1 text-[11px] text-cyan-400 font-medium"><Clock className="w-3.5 h-3.5 animate-spin" /> Đang điều tra</span>;
      default:
        return <span className="flex items-center gap-1 text-[11px] text-amber-400 font-medium"><AlertCircle className="w-3.5 h-3.5" /> Chờ xử lý</span>;
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-white">Trung Tâm Hỗ Trợ Kỹ Thuật L2 & Phản Hồi (Tuần 7)</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Theo dõi độ hài lòng câu trả lời Copilot và điều phối xử lý ticket từ nhân viên cửa hàng
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-3 py-2 text-xs font-medium rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 transition-colors cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Làm mới dữ liệu</span>
        </button>
      </div>

      {/* Analytics KPI Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Độ Hữu Ích</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-white font-mono">{stats.helpful_rate_percent}%</div>
            <div className="text-[11px] text-slate-400 mt-1">
              {stats.likes} Hài lòng / {stats.total} Đánh giá
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Lượt Thích (Like)</span>
              <ThumbsUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">{stats.likes}</div>
            <div className="text-[11px] text-slate-400 mt-1">Câu trả lời chính xác</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Lượt Chưa Hài Lòng</span>
              <ThumbsDown className="w-4 h-4 text-rose-400" />
            </div>
            <div className="text-2xl font-bold text-rose-400 font-mono">{stats.dislikes}</div>
            <div className="text-[11px] text-slate-400 mt-1">Cần tối ưu prompt / KB</div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-2xl">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Ticket L2 Mở</span>
              <ShieldAlert className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-amber-400 font-mono">
              {tickets.filter((t) => t.status === 'pending').length}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Yêu cầu can thiệp kỹ thuật</div>
          </div>
        </div>
      )}

      {/* Ticket List Header & Filters */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-cyan-400" />
            <h3 className="font-semibold text-slate-200 text-sm">Danh Sách Phiếu Hỗ Trợ Chuyển Cấp ({tickets.length})</h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Lọc theo trạng thái:</span>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="">Tất cả trạng thái</option>
              <option value="pending">Chờ xử lý (Pending)</option>
              <option value="in_progress">Đang điều tra (In Progress)</option>
              <option value="resolved">Đã xử lý (Resolved)</option>
            </select>
          </div>
        </div>

        {/* Tickets Cards */}
        {tickets.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            Hiện không có phiếu hỗ trợ L2 nào trong danh mục này.
          </div>
        ) : (
          <div className="space-y-3">
            {tickets.map((t) => (
              <div
                key={t.ticket_id}
                className="p-4 rounded-xl bg-slate-950/80 border border-slate-800 hover:border-slate-700 transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/60 pb-2.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400">{t.ticket_id}</span>
                    {priorityBadge(t.priority)}
                    <span className="text-[11px] text-slate-400 font-medium px-2 py-0.5 rounded bg-slate-800">
                      Vai trò: {t.user_role}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    {statusBadge(t.status)}
                    <span className="text-[11px] text-slate-500 font-mono">
                      {new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block mb-1 font-medium">Vấn đề của người dùng:</span>
                    <p className="text-slate-200 font-medium">{t.query}</p>
                    {t.user_note && (
                      <div className="mt-2 pt-2 border-t border-slate-800/80 text-amber-300 text-[11px]">
                        <strong>Ghi chú bổ sung:</strong> {t.user_note}
                      </div>
                    )}
                  </div>

                  <div className="p-3 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block mb-1 font-medium">Phản hồi của Copilot:</span>
                    <p className="text-slate-300 line-clamp-3 leading-relaxed">{t.bot_response}</p>
                  </div>
                </div>

                {/* Status Action Buttons */}
                <div className="flex items-center justify-end gap-2 pt-1">
                  {t.status === 'pending' && (
                    <button
                      onClick={() => handleUpdateStatus(t.ticket_id, 'in_progress')}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-cyan-600/20 text-cyan-300 hover:bg-cyan-600/30 border border-cyan-500/30 cursor-pointer"
                    >
                      Tiếp nhận xử lý
                    </button>
                  )}
                  {t.status === 'in_progress' && (
                    <button
                      onClick={() => handleUpdateStatus(t.ticket_id, 'resolved')}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/30 border border-emerald-500/30 cursor-pointer"
                    >
                      Đánh dấu Đã xử lý
                    </button>
                  )}
                  {t.status === 'resolved' && (
                    <button
                      onClick={() => handleUpdateStatus(t.ticket_id, 'in_progress')}
                      className="px-3 py-1 rounded-lg text-xs font-medium bg-slate-800 text-slate-400 hover:text-slate-200 cursor-pointer"
                    >
                      Mở lại ticket
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
