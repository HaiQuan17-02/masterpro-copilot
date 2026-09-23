import React from 'react';
import Chat from './pages/Chat';
import { Layers, ShieldCheck, Terminal, Cpu } from 'lucide-react';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-slate-100 flex flex-col items-center justify-between p-3 sm:p-6 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Brand Banner */}
      <nav className="w-full max-w-4xl flex items-center justify-between py-2 px-1 mb-2">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-md shadow-blue-500/30">
            M
          </div>
          <span className="font-semibold text-sm tracking-wide text-slate-200">
            MASTERPRO ECOSYSTEM
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <span className="hidden sm:flex items-center gap-1.5 hover:text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            AI RAG Core
          </span>
          <span className="hidden sm:flex items-center gap-1.5 hover:text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Enterprise Guard
          </span>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 hover:underline"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>FastAPI Docs</span>
          </a>
        </div>
      </nav>

      {/* Main Chat Interface */}
      <main className="w-full flex items-center justify-center flex-1">
        <Chat />
      </main>

      {/* Footer */}
      <footer className="w-full max-w-4xl text-center py-3 text-[11px] text-slate-500">
        MasterPro Copilot MVP • Built with React, Vite, TailwindCSS & FastAPI
      </footer>
    </div>
  );
}
