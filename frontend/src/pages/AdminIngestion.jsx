import React, { useState, useEffect } from 'react';
import {
  Upload,
  FileText,
  Database,
  CheckCircle2,
  AlertCircle,
  Clock,
  Layers,
  Sparkles,
  RefreshCw
} from 'lucide-react';

export default function AdminIngestion() {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'file'
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('HDSD');
  const [moduleName, setModuleName] = useState('Kho hàng');
  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);
  const [successResult, setSuccessResult] = useState(null);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({ total_vectors: 0, collection_name: 'masterpro_kb' });

  const fetchStats = () => {
    fetch('http://localhost:8000/api/ingestion/stats')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setStats(data);
      })
      .catch(() => {});
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleIngestText = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;

    setLoading(true);
    setError(null);
    setSuccessResult(null);

    try {
      const payload = {
        title: title.trim(),
        content: content.trim(),
        category,
        module: moduleName,
        chunk_size: 500,
        chunk_overlap: 80
      };

      const res = await fetch('http://localhost:8000/api/ingestion/text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Lỗi API (${res.status})`);
      }

      const data = await res.json();
      setSuccessResult(data);
      setTitle('');
      setContent('');
      fetchStats();
    } catch (err) {
      setError(err.message || 'Không thể kết nối đến Ingestion API');
    } finally {
      setLoading(false);
    }
  };

  const handleIngestFile = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    setSuccessResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);
      formData.append('module', moduleName);
      if (title.trim()) formData.append('title', title.trim());

      const res = await fetch('http://localhost:8000/api/ingestion/file', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Lỗi API (${res.status})`);
      }

      const data = await res.json();
      setSuccessResult(data);
      setFile(null);
      setTitle('');
      fetchStats();
    } catch (err) {
      setError(err.message || 'Không thể upload file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl flex flex-col gap-6 py-2">
      {/* Header Banner */}
      <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Upload className="w-4 h-4" />
            </span>
            <h2 className="text-lg font-bold text-slate-100">
              Ingestion Pipeline Portal (Tuần 5)
            </h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Quy trình nạp tài liệu: Làm sạch Unicode NFC ➔ HeadingAwareChunker ➔ Qdrant Vector Store
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Qdrant Vectors: <strong className="text-cyan-300">{stats.total_vectors}</strong></span>
            <button onClick={fetchStats} title="Làm mới" className="text-slate-500 hover:text-slate-300 ml-1">
              <RefreshCw className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Switcher: Nhập Text vs Upload File */}
      <div className="flex p-1 rounded-xl bg-slate-950/70 border border-slate-800 w-fit text-xs">
        <button
          onClick={() => setActiveTab('text')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all cursor-pointer ${
            activeTab === 'text'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Soạn Thảo / Dán Văn Bản</span>
        </button>

        <button
          onClick={() => setActiveTab('file')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all cursor-pointer ${
            activeTab === 'file'
              ? 'bg-indigo-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Tải Lên File (.md, .txt)</span>
        </button>
      </div>

      {/* Success Banner */}
      {successResult && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 text-emerald-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>
              <strong>Thành công:</strong> Đã phân đoạn và lưu{' '}
              <strong>{successResult.chunks_count} chunks</strong> vào Qdrant trong {successResult.elapsed_time_s}s!
            </span>
          </div>
          <span className="font-mono text-[11px] text-emerald-400/80">{successResult.job_id}</span>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Form Area */}
      <div className="p-6 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl shadow-xl">
        {activeTab === 'text' ? (
          <form onSubmit={handleIngestText} className="flex flex-col gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Nhóm (Category)</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="HDSD">HDSD (Hướng dẫn sử dụng)</option>
                  <option value="RUNBOOK_L1">RUNBOOK_L1 (Quy trình vận hành)</option>
                  <option value="FAQ">FAQ (Câu hỏi thường gặp)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Phân hệ (Module)</label>
                <input
                  type="text"
                  value={moduleName}
                  onChange={(e) => setModuleName(e.target.value)}
                  placeholder="Kho hàng, Bán hàng, Hardware..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Tiêu đề tài liệu</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Nhập tiêu đề tài liệu..."
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Nội dung Markdown</label>
              <textarea
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Nhập nội dung tài liệu Markdown (hỗ trợ ## tiêu đề, danh sách - bước 1, bảng | ... |)..."
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 font-mono placeholder-slate-600 focus:outline-none focus:border-indigo-500 leading-relaxed"
              />
            </div>

            <button
              type="submit"
              disabled={loading || !title.trim() || !content.trim()}
              className="w-fit self-end px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              <Upload className="w-4 h-4" />
              <span>{loading ? 'Đang phân đoạn & Embed...' : 'Thực hiện Ingest vào Qdrant'}</span>
            </button>
          </form>
        ) : (
          <form onSubmit={handleIngestFile} className="flex flex-col gap-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Nhóm (Category)</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                >
                  <option value="HDSD">HDSD</option>
                  <option value="RUNBOOK_L1">RUNBOOK_L1</option>
                  <option value="FAQ">FAQ</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Phân hệ (Module)</label>
                <input
                  type="text"
                  value={moduleName}
                  onChange={(e) => setModuleName(e.target.value)}
                  placeholder="Kho hàng, Bán hàng..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Drag & Drop File Zone */}
            <div className="p-8 border-2 border-dashed border-slate-700/80 rounded-2xl bg-slate-950/50 flex flex-col items-center justify-center gap-2 text-center">
              <Upload className="w-8 h-8 text-indigo-400 mb-1" />
              <p className="text-xs text-slate-200 font-medium">
                {file ? file.name : 'Chọn hoặc kéo thả file Markdown (.md, .txt) vào đây'}
              </p>
              <p className="text-[11px] text-slate-500">Kích thước tối đa 10MB</p>
              <input
                type="file"
                accept=".md,.txt,.markdown"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="mt-2 px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-200 font-medium cursor-pointer transition-colors"
              >
                Duyệt file trên máy
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !file}
              className="w-fit self-end px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-medium text-xs rounded-xl shadow-lg shadow-indigo-600/20 flex items-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed"
            >
              <Upload className="w-4 h-4" />
              <span>{loading ? 'Đang tải lên & nạp...' : 'Tải lên & Ingest vào Qdrant'}</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
