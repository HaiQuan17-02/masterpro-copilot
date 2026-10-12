import React, { useState, useEffect } from 'react';
import {
  FileText,
  CheckCircle,
  Clock,
  Archive,
  RefreshCw,
  Plus,
  GitCommit,
  AlertTriangle,
  History,
  Send,
  Layers,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';

export default function AdminLifecycle() {
  const [documents, setDocuments] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState('');

  // Modal create/supersede state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newCategory, setNewCategory] = useState('HDSD');
  const [newModule, setNewModule] = useState('Bán hàng');
  const [newVersion, setNewVersion] = useState('v2.0');
  const [supersedesDocId, setSupersedesDocId] = useState('');

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const url = statusFilter
        ? `http://localhost:8000/api/lifecycle/documents?status=${statusFilter}`
        : 'http://localhost:8000/api/lifecycle/documents';
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (err) {
      console.error('Failed to load lifecycle docs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, [statusFilter]);

  const handleApprove = async (docId) => {
    try {
      const res = await fetch(`http://localhost:8000/api/lifecycle/documents/${docId}/approve?approver=LeadAdmin`, {
        method: 'POST'
      });
      const data = await res.json();
      if (res.ok) {
        setActionMsg(data.message || 'Đã phê duyệt và lập chỉ mục');
        setTimeout(() => setActionMsg(''), 4000);
        fetchDocs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmitForReview = async (docId) => {
    try {
      const res = await fetch(`http://localhost:8000/api/lifecycle/documents/${docId}/submit`, {
        method: 'POST'
      });
      if (res.ok) {
        setActionMsg('Đã chuyển tài liệu sang bước Thẩm định');
        setTimeout(() => setActionMsg(''), 3000);
        fetchDocs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleArchive = async (docId) => {
    try {
      const res = await fetch(`http://localhost:8000/api/lifecycle/documents/${docId}/archive`, {
        method: 'POST'
      });
      if (res.ok) {
        setActionMsg('Đã lưu trữ tài liệu và gỡ khỏi Qdrant');
        setTimeout(() => setActionMsg(''), 3000);
        fetchDocs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleReindexAll = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/lifecycle/reindex', {
        method: 'POST'
      });
      const data = await res.json();
      if (res.ok) {
        setActionMsg(data.message);
        setTimeout(() => setActionMsg(''), 5000);
        fetchDocs();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/lifecycle/documents?direct_submit=true', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          content: newContent,
          category: newCategory,
          module: newModule,
          version_id: newVersion,
          supersedes_doc_id: supersedesDocId || null
        })
      });

      if (res.ok) {
        setShowCreateModal(false);
        setNewTitle('');
        setNewContent('');
        setSupersedesDocId('');
        setActionMsg('Đã tạo tài liệu mới và gửi vào hàng đợi Thẩm định!');
        setTimeout(() => setActionMsg(''), 4000);
        fetchDocs();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Approved (Active Qdrant)</span>
          </span>
        );
      case 'under_review':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
            <Clock className="w-3.5 h-3.5" />
            <span>Under Review</span>
          </span>
        );
      case 'superseded':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-500/15 text-rose-300 border border-rose-500/30 line-through">
            <History className="w-3.5 h-3.5" />
            <span>Superseded (Lỗi thời)</span>
          </span>
        );
      case 'archived':
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <Archive className="w-3.5 h-3.5" />
            <span>Archived</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
            Draft
          </span>
        );
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Action banner */}
      {actionMsg && (
        <div className="p-3.5 rounded-2xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-200 text-xs font-medium flex items-center justify-between animate-in fade-in duration-200">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>{actionMsg}</span>
          </div>
          <button onClick={() => setActionMsg('')} className="text-slate-400 hover:text-white cursor-pointer">✕</button>
        </div>
      )}

      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-5 rounded-2xl">
        <div>
          <div className="flex items-center gap-2.5">
            <GitCommit className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white">Vòng Đời Tri Thức & Quản Lý Phiên Bản (Tuần 9)</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Quy trình Thẩm định (Review) → Duyệt (Approve & Index) → Đánh dấu lỗi thời (Superseded) cho tài liệu ERP
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/20 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Soạn Thảo Phiên Bản Mới</span>
          </button>

          <button
            onClick={handleReindexAll}
            disabled={loading}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 cursor-pointer"
            title="Đồng bộ lại toàn bộ tài liệu Approved vào Qdrant"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Reindex Toàn Bộ</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        {[
          { key: '', label: `Tất cả (${documents.length})` },
          { key: 'approved', label: 'Approved (Active)' },
          { key: 'under_review', label: 'Đang thẩm định' },
          { key: 'superseded', label: 'Lỗi thời (Superseded)' },
          { key: 'archived', label: 'Đã lưu trữ' },
          { key: 'draft', label: 'Bản nháp' }
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setStatusFilter(tab.key)}
            className={`px-3 py-1.5 rounded-xl font-medium transition-all cursor-pointer whitespace-nowrap ${
              statusFilter === tab.key
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Document Table / Cards */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
        {documents.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-xs">
            Không tìm thấy tài liệu nào trong danh mục này.
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className={`p-4 rounded-xl border transition-all ${
                  doc.status === 'superseded'
                    ? 'bg-slate-950/40 border-slate-800/50 opacity-70'
                    : 'bg-slate-950/80 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/60 pb-3">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-mono text-xs font-bold text-cyan-400">{doc.document_id}</span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-300">
                      {doc.version_id}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] bg-slate-800/80 text-slate-400">
                      {doc.module} • {doc.category}
                    </span>
                    {getStatusBadge(doc.status)}
                  </div>

                  <span className="text-[11px] text-slate-500 font-mono">
                    Cập nhật: {new Date(doc.updated_at).toLocaleDateString('vi-VN')}
                  </span>
                </div>

                <div className="py-2.5 space-y-1.5">
                  <h4 className="text-sm font-semibold text-slate-100">{doc.title}</h4>
                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {doc.content}
                  </p>
                </div>

                {/* Superseded Links */}
                {doc.superseded_by && (
                  <div className="text-[11px] text-rose-300 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20 mb-2 flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                    <span>Đã bị thay thế bởi phiên bản mới: <strong className="font-mono">{doc.superseded_by}</strong></span>
                  </div>
                )}
                {doc.supersedes_doc_id && (
                  <div className="text-[11px] text-cyan-300 bg-cyan-500/10 p-2 rounded-lg border border-cyan-500/20 mb-2 flex items-center gap-1.5">
                    <Layers className="w-3.5 h-3.5 shrink-0" />
                    <span>Phiên bản này thay thế cho tài liệu cũ: <strong className="font-mono">{doc.supersedes_doc_id}</strong></span>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
                  <span className="text-slate-500 text-[11px]">
                    {doc.chunks_count > 0 ? `${doc.chunks_count} chunks trong Qdrant` : 'Chưa lập chỉ mục'}
                  </span>

                  <div className="flex items-center gap-2">
                    {doc.status === 'draft' && (
                      <button
                        onClick={() => handleSubmitForReview(doc.document_id)}
                        className="px-3 py-1 rounded-lg font-medium bg-amber-600/20 text-amber-300 hover:bg-amber-600/30 border border-amber-500/30 cursor-pointer"
                      >
                        Nộp Thẩm Định
                      </button>
                    )}

                    {(doc.status === 'under_review' || doc.status === 'draft') && (
                      <button
                        onClick={() => handleApprove(doc.document_id)}
                        className="px-3 py-1 rounded-lg font-medium bg-emerald-600 text-white hover:bg-emerald-500 shadow-md shadow-emerald-600/20 cursor-pointer"
                      >
                        Duyệt & Nạp Qdrant
                      </button>
                    )}

                    {doc.status === 'approved' && (
                      <button
                        onClick={() => handleArchive(doc.document_id)}
                        className="px-3 py-1 rounded-lg font-medium bg-slate-800 text-slate-400 hover:text-rose-300 hover:bg-slate-700 cursor-pointer"
                      >
                        Lưu trữ (Archive)
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal Soạn Thảo / Thay Thế Phiên Bản */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6">
            <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
              <Plus className="w-5 h-5 text-indigo-400" />
              <span>Soạn Thảo & Đổi Mới Tài Liệu Tri Thức</span>
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Nộp tài liệu mới hoặc tạo bản nâng cấp thay thế tài liệu đã lỗi thời
            </p>

            <form onSubmit={handleCreateDocument} className="space-y-3.5 text-xs">
              <div>
                <label className="text-slate-300 block mb-1 font-medium">Tiêu đề tài liệu:</label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="Ví dụ: Quy định chính sách chiết khấu đại lý v2..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-3 gap-2.5">
                <div>
                  <label className="text-slate-300 block mb-1 font-medium">Phiên bản:</label>
                  <input
                    type="text"
                    required
                    value={newVersion}
                    onChange={(e) => setNewVersion(e.target.value)}
                    placeholder="v2.0"
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-slate-300 block mb-1 font-medium">Phân hệ:</label>
                  <select
                    value={newModule}
                    onChange={(e) => setNewModule(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="Bán hàng">Bán hàng</option>
                    <option value="Kho hàng">Kho hàng</option>
                    <option value="Sổ quỹ">Sổ quỹ</option>
                    <option value="Hệ thống">Hệ thống</option>
                  </select>
                </div>
                <div>
                  <label className="text-slate-300 block mb-1 font-medium">Danh mục:</label>
                  <select
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                  >
                    <option value="HDSD">HDSD</option>
                    <option value="RUNBOOK_L1">RUNBOOK_L1</option>
                    <option value="FAQ">FAQ</option>
                  </select>
                </div>
              </div>

              {/* Thay thế tài liệu cũ */}
              <div>
                <label className="text-slate-300 block mb-1 font-medium">
                  Thay thế tài liệu cũ (Supersedes Doc ID - Nếu có):
                </label>
                <select
                  value={supersedesDocId}
                  onChange={(e) => setSupersedesDocId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="">-- Không thay thế (Tài liệu độc lập mới) --</option>
                  {documents
                    .filter((d) => d.status === 'approved')
                    .map((d) => (
                      <option key={d.document_id} value={d.document_id}>
                        {d.document_id} - {d.title} ({d.version_id})
                      </option>
                    ))}
                </select>
                <span className="text-[10px] text-slate-500 block mt-1">
                  Khi tài liệu mới được duyệt, tài liệu được chọn sẽ tự động chuyển sang trạng thái <strong>Superseded</strong> và gỡ khỏi Qdrant.
                </span>
              </div>

              {/* Markdown Content */}
              <div>
                <label className="text-slate-300 block mb-1 font-medium">Nội dung chi tiết (Markdown):</label>
                <textarea
                  rows={6}
                  required
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  placeholder="# Tiêu đề chính&#10;&#10;## Mục 1: Quy trình thực hiện&#10;- Bước 1: ..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-200 font-mono text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:bg-slate-700 cursor-pointer"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 text-white hover:bg-indigo-500 cursor-pointer font-semibold shadow-lg shadow-indigo-600/20"
                >
                  Nộp Thẩm Định
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
