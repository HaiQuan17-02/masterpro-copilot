import React from 'react';
import { Bot, Sparkles, Activity } from 'lucide-react';

function ChatHeader({ backendStatus = 'online' }) {
  const isHealthy = backendStatus === 'healthy' || backendStatus === 'online';

  return (
    <header className="px-5 py-4 border-b border-slate-700/60 bg-slate-900/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 p-[1px] shadow-lg shadow-blue-500/20 flex items-center justify-center">
          <div className="w-full h-full bg-slate-950/70 rounded-[11px] flex items-center justify-center">
            <Bot className="w-5 h-5 text-cyan-400 animate-pulse" />
          </div>
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
              MasterPro Copilot
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                MVP v0.1
              </span>
            </h1>
          </div>
          <p className="text-xs text-slate-400 flex items-center gap-1.5">
            Trợ lý tra cứu tri thức & tài liệu kỹ thuật
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${
          isHealthy 
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' 
            : 'bg-amber-500/10 border-amber-500/30 text-amber-400'
        }`}>
          <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`} />
          <span>{isHealthy ? 'API Sẵn sàng' : 'Chế độ Demo'}</span>
        </div>
      </div>
    </header>
  );
}

export default ChatHeader;
