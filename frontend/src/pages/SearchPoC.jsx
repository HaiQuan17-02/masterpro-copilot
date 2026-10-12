import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  SlidersHorizontal,
  FileText,
  Bookmark,
  Sparkles,
  Layers,
  ChevronRight,
  Database,
  Clock,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';

export default function SearchPoC({ onSelectDocForChat }) {
  const [query, setQuery] = useState('cách cấu hình máy in hóa đơn');
  const [category, setCategory] = useState('');
  const [moduleFilter, setModuleFilter] = useState('');
  const [limit, setLimit] = useState(3);
  const [scoreThreshold, setScoreThreshold] = useState(0.3);
  
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [latency, setLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ categories: [], modules: [] });

  // Fetch available filters on mount
  useEffect(() => {
    fetch('http://localhost:8000/api/search/filters')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data) setFilters(data);
      })
      .catch(() => {
        // Fallback default filters
        setFilters({
          categories: ['HDSD', 'RUNBOOK_L1', 'FAQ'],
          modules: ['Hệ thống', 'Kho hàng', 'Sổ quỹ', 'Cửa hàng', 'Tài khoản', 'Sản phẩm', 'Khách hàng', 'Mua hàng', 'Bán hàng']
        });
      });
  }, []);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const payload = {
        query: query.trim(),
        limit: Number(limit),
        score_threshold: Number(scoreThreshold),
        category: category || null,
        module: moduleFilter || null
      };

      const response = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`Lỗi API: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setTotal(data.total || 0);
      setLatency(data.latency_ms);
    } catch (err) {
      setError(err.message || 'Không thể kết nối đến API Search backend.');
    } finally {
      setLoading(false);
    }
  };

  // Run initial search
  useEffect(() => {
    handleSearch();
  }, []);

  const getScoreBadge = (score) => {
    if (score >= 0.65) {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          Rất cao ({score})
        </span>
      );
    }
    if (score >= 0.45) {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30 flex items-center gap-1">
          <Sparkles className="w-3 h-3 text-blue-400" />
          Khá ({score})
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
        <AlertCircle className="w-3 h-3 text-amber-400" />
        Vừa ({score})
      </span>
    );
  };

  return (
    <div className="w-full max-w-5xl flex flex-col gap-5 py-2">
      {/* Search Header Banner */}
      <div className="bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Database className="w-4 h-4" />
              </span>
              <h2 className="text-lg font-bold text-slate-100">
                Retrieval PoC — Qdrant Vector Semantic Search
              </h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Kiểm thử truy xuất ngữ nghĩa trên 50 tài liệu phân đoạn bằng <code className="text-cyan-300">HeadingAwareChunker</code>
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
              <Layers className="w-3.5 h-3.5 text-blue-400" />
              <span>Qdrant: <strong className="text-slate-100">50 Docs</strong></span>
            </div>
            {latency !== null && (
              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 text-slate-300">
                <Clock className="w-3.5 h-3.5 text-emerald-400" />
                <span>Độ trễ: <strong className="text-emerald-300">{latency} ms</strong></span>
              </div>
            )}
          </div>
        </div>

        {/* Search Input Bar */}
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-2.5">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Nhập câu hỏi nghiệp vụ (vd: cách kết số, thêm kho hàng, kẹt dao in bill)..."
              className="w-full bg-slate-950/70 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-5 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white font-medium text-sm rounded-xl shadow-lg shadow-cyan-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
          >
            <Search className="w-4 h-4" />
            <span>{loading ? 'Đang tìm...' : 'Tìm kiếm'}</span>
          </button>
        </form>

        {/* Filters and Sliders Control */}
        <div className="flex flex-wrap items-center gap-3 mt-4 pt-4 border-t border-slate-800 text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Nhóm:</span>
          </div>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Tất cả Category</option>
            {filters.categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>

          <div className="flex items-center gap-1.5 text-slate-400 ml-2">
            <span>Phân hệ:</span>
          </div>
          <select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">Tất cả Module</option>
            {filters.modules.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>

          <div className="flex items-center gap-1.5 text-slate-400 ml-auto">
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Top-K:</span>
            <select
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 focus:outline-none"
            >
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/60 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Search Results List */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span>Tìm thấy <strong className="text-slate-200">{total}</strong> chunks phù hợp trong Qdrant</span>
          <span>Ngưỡng tương đồng cosine: &gt;= {scoreThreshold}</span>
        </div>

        {results.length === 0 && !loading && !error && (
          <div className="p-8 text-center bg-slate-900/40 border border-slate-800/80 rounded-2xl text-slate-500 text-sm">
            Không tìm thấy chunk nào khớp với tiêu chí tìm kiếm. Hãy thử từ khóa khác hoặc hạ ngưỡng tương đồng.
          </div>
        )}

        {results.map((hit, idx) => (
          <div
            key={idx}
            className="bg-slate-900/60 border border-slate-800 hover:border-slate-700/80 rounded-2xl p-4.5 transition-all shadow-md hover:shadow-lg flex flex-col gap-2.5"
          >
            {/* Header: Score + Breadcrumbs */}
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-1.5 text-xs text-cyan-400 font-medium">
                <Bookmark className="w-3.5 h-3.5" />
                <span>{hit.heading_path || hit.title}</span>
              </div>
              <div className="flex items-center gap-2">
                {getScoreBadge(hit.score)}
                <span className="text-[11px] text-slate-400 px-2 py-0.5 rounded bg-slate-800">
                  #{hit.chunk_index || 1}
                </span>
              </div>
            </div>

            {/* Document Title & Module Badges */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-200 font-semibold">{hit.title}</span>
              <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/50">
                {hit.category} / {hit.module}
              </span>
              {hit.page && (
                <span className="text-[11px] px-2 py-0.5 rounded bg-blue-950/60 text-blue-300 border border-blue-800/40">
                  Trang {hit.page}
                </span>
              )}
            </div>

            {/* Chunk Body Content */}
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">
              {hit.content}
            </div>

            {/* Source Info & Quick Actions */}
            <div className="flex items-center justify-between pt-1 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <FileText className="w-3 h-3 text-slate-400" />
                Nguồn: {hit.source || 'Tài liệu MasterPro'}
              </span>
              {onSelectDocForChat && (
                <button
                  onClick={() => onSelectDocForChat(hit.content)}
                  className="text-cyan-400 hover:text-cyan-300 font-medium flex items-center gap-1 hover:underline cursor-pointer"
                >
                  <span>Hỏi Copilot về đoạn này</span>
                  <ChevronRight className="w-3 h-3" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
