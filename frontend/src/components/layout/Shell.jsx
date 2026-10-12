import React, { useState } from 'react';
import {
  MessageSquare,
  Search,
  Upload,
  Cpu,
  ShieldCheck,
  Terminal,
  Activity,
  Sparkles
} from 'lucide-react';
import ChatWindow from '../chat/ChatWindow';
import SearchPoC from '../../pages/SearchPoC';
import AdminIngestion from '../../pages/AdminIngestion';
import AdminEscalation from '../../pages/AdminEscalation';
import AdminLifecycle from '../../pages/AdminLifecycle';
import AdminBenchmark from '../../pages/AdminBenchmark';
import { UserCheck, ShieldAlert, Key, GitCommit, Zap } from 'lucide-react';

export default function Shell() {
  const [activeTab, setActiveTab] = useState('chat'); // Default to Chat
  const [userRole, setUserRole] = useState('cashier'); // Default to Cashier in Week 8 RBAC

  const roleLabels = {
    cashier: { label: 'Thu ngân POS', color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30' },
    inventory: { label: 'Thủ kho ERP', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' },
    accountant: { label: 'Kế toán viên', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' },
    admin: { label: 'Quản trị viên', color: 'text-rose-400 bg-rose-500/10 border-rose-500/30' }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-slate-100 flex flex-col items-center justify-between p-3 sm:p-6 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Navbar */}
      <header className="w-full max-w-6xl flex flex-col sm:flex-row items-center justify-between py-3 px-4 mb-4 bg-slate-900/60 backdrop-blur-md border border-slate-800 rounded-2xl shadow-lg gap-3">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-extrabold text-sm shadow-md shadow-cyan-500/20">
            M
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-wide text-slate-100">
                MASTERPRO COPILOT
              </span>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                GATE 3 PASSED 🏆
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Enterprise ERP & POS AI Assistant</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center p-1 rounded-xl bg-slate-950/80 border border-slate-800 text-xs flex-wrap gap-1">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'chat'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Hội Thoại Copilot</span>
          </button>

          <button
            onClick={() => setActiveTab('search_poc')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'search_poc'
                ? 'bg-cyan-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Retrieval PoC</span>
          </button>

          <button
            onClick={() => setActiveTab('ingestion')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'ingestion'
                ? 'bg-indigo-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Upload className="w-3.5 h-3.5" />
            <span>Nạp Tri Thức</span>
          </button>

          <button
            onClick={() => setActiveTab('escalation')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'escalation'
                ? 'bg-amber-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Hỗ Trợ L2</span>
          </button>

          <button
            onClick={() => setActiveTab('lifecycle')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'lifecycle'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <GitCommit className="w-3.5 h-3.5" />
            <span>Vòng Đời Tri Thức</span>
          </button>

          <button
            onClick={() => setActiveTab('benchmark')}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${
              activeTab === 'benchmark'
                ? 'bg-rose-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Hiệu Năng Gate 3</span>
          </button>
        </nav>

        {/* Right Status & RBAC Role Switcher */}
        <div className="flex items-center gap-3 text-xs">
          {/* Role Switcher */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-slate-950 border border-slate-800">
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-[11px] text-slate-400 hidden lg:inline">Vai trò:</span>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="bg-transparent text-[11px] font-semibold text-slate-200 focus:outline-none cursor-pointer"
            >
              <option value="cashier" className="bg-slate-900 text-slate-200">Thu ngân (POS)</option>
              <option value="inventory" className="bg-slate-900 text-slate-200">Thủ kho (Kho)</option>
              <option value="accountant" className="bg-slate-900 text-slate-200">Kế toán viên</option>
              <option value="admin" className="bg-slate-900 text-slate-200">Quản trị viên (Admin)</option>
            </select>
          </div>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:flex items-center gap-1 text-cyan-400 hover:text-cyan-300 hover:underline text-[11px]"
          >
            <Terminal className="w-3 h-3" />
            <span>Docs</span>
          </a>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="w-full flex items-center justify-center flex-1">
        {activeTab === 'chat' && <ChatWindow userRole={userRole} />}
        {activeTab === 'search_poc' && <SearchPoC />}
        {activeTab === 'ingestion' && <AdminIngestion />}
        {activeTab === 'escalation' && <AdminEscalation />}
        {activeTab === 'lifecycle' && <AdminLifecycle />}
        {activeTab === 'benchmark' && <AdminBenchmark />}
      </main>

      {/* Footer */}
      <footer className="w-full max-w-6xl text-center py-3 text-[11px] text-slate-500 flex flex-col sm:flex-row items-center justify-between border-t border-slate-800/60 mt-4">
        <span>MasterPro Copilot • Tuần 7 Feedback, Escalation & Citation Drawer</span>
        <span>Tech Stack: FastAPI, Qdrant Vector Store, SSE Stream, React 19, TailwindCSS</span>
      </footer>
    </div>
  );
}
