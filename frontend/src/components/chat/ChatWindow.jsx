import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import CitationDrawer from './CitationDrawer';
import EscalationModal from './EscalationModal';
import { Send, Sparkles, Bot, Radio, ShieldAlert } from 'lucide-react';

export default function ChatWindow({ userRole = 'cashier' }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      text: 'Xin chào! Tôi là **MasterPro Copilot** - trợ lý AI hỗ trợ vận hành ERP & POS.\n\nHệ thống tích hợp **RAG Core SSE Streaming**, đánh giá phản hồi **Like/Dislike**, xem **chi tiết văn bản trích dẫn**, và phân quyền **RBAC vai trò người dùng**.',
      citations: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [useStreamMode, setUseStreamMode] = useState(true);

  // Hybrid Provider state (Week 10)
  const [currentProvider, setCurrentProvider] = useState('offline_rule_synthesizer');
  const [isFallbackMode, setIsFallbackMode] = useState(true);
  const [providerMode, setProviderMode] = useState('auto');

  // Drawer & Escalation state
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [escalationTarget, setEscalationTarget] = useState(null);
  const [isEscalationOpen, setIsEscalationOpen] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streaming]);

  const quickPrompts = [
    'Có đổi được mã kho sau khi phát sinh chứng từ?',
    'Cách cấu hình kết số và khóa sổ bán hàng?',
    'Cấu hình máy in và thiết lập thông số hệ thống',
    'Thao tác tạo phiếu bán lẻ tại quầy POS'
  ];

  const handleOpenCitation = (cite) => {
    setSelectedCitation(cite);
    setIsDrawerOpen(true);
  };

  const handleOpenEscalation = (msg) => {
    // Find the corresponding user query
    const msgIdx = messages.findIndex((m) => m.id === msg.id);
    let originalQuery = '';
    if (msgIdx > 0 && messages[msgIdx - 1]?.sender === 'user') {
      originalQuery = messages[msgIdx - 1].text;
    }
    setEscalationTarget({
      query: originalQuery || msg.query || 'Vấn đề cần hỗ trợ',
      botResponse: msg.text,
      citations: msg.citations || []
    });
    setIsEscalationOpen(true);
  };

  const handleSend = async (textToSend) => {
    const query = (textToSend || input).trim();
    if (!query || streaming) return;

    setInput('');

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setStreaming(true);

    if (useStreamMode) {
      // Real-time SSE Streaming
      const botMsgId = Date.now() + 1;
      const initialBotMsg = {
        id: botMsgId,
        sender: 'bot',
        query: query,
        text: '',
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, initialBotMsg]);

      try {
        const response = await fetch('http://localhost:8000/api/chat/stream', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-Role': userRole
          },
          body: JSON.stringify({ message: query, user_role: userRole })
        });

        if (!response.ok) {
          throw new Error(`Lỗi kết nối SSE (${response.status})`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let accumulatedText = '';
        let citations = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunkText = decoder.decode(value, { stream: true });
          const lines = chunkText.split('\n');

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith('data:')) continue;
            const dataStr = trimmed.slice(5).trim();
            if (dataStr === '[DONE]') break;

            try {
              const eventData = JSON.parse(dataStr);
              if (eventData.type === 'metadata') {
                citations = eventData.citations || [];
                if (eventData.provider) {
                  setCurrentProvider(eventData.provider);
                  setIsFallbackMode(Boolean(eventData.fallback_mode));
                }
              } else if (eventData.type === 'token') {
                accumulatedText += eventData.token;
              } else if (eventData.type === 'validation') {
                if (eventData.provider) {
                  setCurrentProvider(eventData.provider);
                  setIsFallbackMode(Boolean(eventData.is_fallback));
                }
              }

              // Live update message bubble
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId
                    ? { ...m, text: accumulatedText, citations }
                    : m
                )
              );
            } catch {
              // skip unparsed chunks
            }
          }
        }
      } catch (err) {
        // Fallback to non-streaming chat endpoint
        try {
          const fallbackRes = await fetch('http://localhost:8000/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query })
          });
          const fallbackData = await fallbackRes.json();
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botMsgId
                ? { ...m, text: fallbackData.answer, citations: fallbackData.citations || [] }
                : m
            )
          );
        } catch (e) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botMsgId
                ? { ...m, text: `⚠️ Lỗi kết nối: ${err.message}` }
                : m
            )
          );
        }
      } finally {
        setStreaming(false);
        setTimeout(() => inputRef.current?.focus(), 100);
      }
    } else {
      // Standard HTTP Post
      try {
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: query })
        });
        const data = await response.json();
        const botMsg = {
          id: Date.now() + 1,
          sender: 'bot',
          query: query,
          text: data.answer || 'Không nhận được câu trả lời.',
          citations: data.citations || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages((prev) => [...prev, botMsg]);
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            sender: 'bot',
            query: query,
            text: `⚠️ Lỗi kết nối: ${err.message}`,
            citations: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      } finally {
        setStreaming(false);
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full max-w-4xl h-[78vh] flex flex-col bg-slate-900/70 backdrop-blur-xl border border-slate-800 rounded-3xl shadow-2xl overflow-hidden relative">
      {/* Stream Mode & Hybrid Provider Toggle Bar */}
      <div className="px-5 py-2.5 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${isFallbackMode ? 'bg-amber-400' : 'bg-emerald-400'} animate-pulse`}></span>
            <span className="font-medium text-slate-200">
              {isFallbackMode ? 'Offline Fallback Engine (Local)' : 'Cloud LLM (Online)'}
            </span>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded-full font-mono bg-slate-800 text-slate-300 border border-slate-700">
            {currentProvider}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setUseStreamMode(!useStreamMode)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer ${
              useStreamMode
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                : 'bg-slate-800 text-slate-400'
            }`}
          >
            <Radio className="w-3 h-3" />
            <span>{useStreamMode ? 'SSE Stream (Bật)' : 'Chuẩn HTTP'}</span>
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-2">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onOpenCitation={handleOpenCitation}
            onOpenEscalation={handleOpenEscalation}
          />
        ))}

        {streaming && (
          <div className="flex gap-2 items-center text-xs text-slate-400 px-2 py-1">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            <span>Đang nhận dữ liệu stream từ MasterPro RAG...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts */}
      {messages.length <= 2 && (
        <div className="px-4 py-2 flex flex-wrap gap-2 border-t border-slate-800/60 bg-slate-950/40">
          <span className="text-[11px] text-slate-500 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            Gợi ý:
          </span>
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="text-[11px] px-2.5 py-1 rounded-full bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-cyan-300 border border-slate-700/60 transition-all cursor-pointer truncate max-w-[260px]"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Box Footer */}
      <div className="p-3 sm:p-4 bg-slate-950/90 border-t border-slate-800 flex flex-col gap-2">
        <div className="relative flex items-center">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Hỏi về quy trình bán hàng, máy in, tồn kho, kết số... (Nhấn Enter để gửi)"
            className="w-full resize-none bg-slate-900 border border-slate-700/80 rounded-2xl pl-4 pr-12 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all max-h-32"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || streaming}
            className="absolute right-2.5 p-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white disabled:text-slate-500 transition-all shadow-md shadow-blue-600/20 cursor-pointer disabled:cursor-not-allowed"
            title="Gửi câu hỏi"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
          <span>Shift + Enter để xuống dòng</span>
          <span>Đánh giá 👍/👎 & Chuyển ticket L2 tích hợp sẵn</span>
        </div>
      </div>

      {/* Citation Drawer Component */}
      <CitationDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        citation={selectedCitation}
      />

      {/* Escalation Modal Component */}
      <EscalationModal
        isOpen={isEscalationOpen}
        onClose={() => setIsEscalationOpen(false)}
        query={escalationTarget?.query}
        botResponse={escalationTarget?.botResponse}
        contextChunks={escalationTarget?.citations}
      />
    </div>
  );
}
