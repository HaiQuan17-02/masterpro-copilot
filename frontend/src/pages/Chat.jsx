import React, { useState, useEffect, useRef } from 'react';
import ChatHeader from '../components/ChatHeader';
import ChatMessage from '../components/ChatMessage';
import ChatInput from '../components/ChatInput';
import { checkBackendHealth, sendChatMessage } from '../services/api';
import { Bot, RefreshCw, MessageSquare } from 'lucide-react';

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 'init-1',
      sender: 'bot',
      text: 'Xin chào! Tôi là **MasterPro Copilot**.\nTôi có thể hỗ trợ bạn tra cứu quy trình vận hành POS, khắc phục lỗi thiết bị ngoại vi và các tài liệu hướng dẫn nghiệp vụ.',
      citations: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
    {
      id: 'init-2',
      sender: 'user',
      text: 'Làm sao xử lý lỗi máy in?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
    {
      id: 'init-3',
      sender: 'bot',
      text: 'Bạn có thể kiểm tra và xử lý sự cố máy in theo các bước sau:\n1. **Kiểm tra nguồn điện**: Đảm bảo dây nguồn cắm chắc và đèn LED hiển thị màu xanh.\n2. **Kiểm tra kết nối**: Rút và cắm lại cáp USB máy in hoặc kiểm tra cáp mạng LAN.\n3. **Kiểm tra khay giấy**: Đảm bảo giấy in hóa đơn khổ K80/K57 đặt đúng chiều và không bị kẹt.\n4. **Khởi động lại Print Spooler** trên Windows hoặc tắt bật lại nút nguồn máy in.',
      citations: [
        {
          title: 'Hướng dẫn xử lý lỗi thiết bị bán hàng & Máy in',
          document: 'HDSD_ThietBi_MasterPro_v1.2.pdf',
          page: 15,
          chunk_id: 'chunk_doc_001_p15',
          score: 0.94,
        },
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);

  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    const verifyHealth = async () => {
      const res = await checkBackendHealth();
      if (res.status === 'healthy') {
        setBackendStatus('healthy');
      } else {
        setBackendStatus('offline');
      }
    };
    verifyHealth();
    const interval = setInterval(verifyHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const userMsg = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const response = await sendChatMessage(text);
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: response.answer,
        citations: response.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: 'bot',
        text: 'Xin lỗi, đã xảy ra lỗi trong quá trình xử lý yêu cầu. Vui lòng thử lại sau.',
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: `reset-${Date.now()}`,
        sender: 'bot',
        text: 'Phiên hội thoại đã được làm mới. Bạn cần hỗ trợ gì về MasterPro?',
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  return (
    <div className="w-full max-w-4xl h-[92vh] sm:h-[86vh] flex flex-col rounded-2xl overflow-hidden border border-slate-700/80 bg-slate-900/90 shadow-2xl backdrop-blur-xl">
      {/* Top Header */}
      <ChatHeader backendStatus={backendStatus} />

      {/* Toolbar / Actions */}
      <div className="px-5 py-2 bg-slate-950/40 border-b border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-3.5 h-3.5 text-blue-400" />
          <span>Hội thoại hỗ trợ kỹ thuật trực tuyến</span>
        </div>
        <button
          onClick={handleResetChat}
          className="flex items-center gap-1 hover:text-slate-200 transition-colors"
          title="Xóa làm mới phiên chat"
        >
          <RefreshCw className="w-3 h-3" />
          <span>Làm mới</span>
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-2">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {loading && (
          <div className="flex items-center gap-3 my-3 text-slate-400 text-sm animate-pulse">
            <div className="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-400/40 flex items-center justify-center text-indigo-300">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3 rounded-2xl bg-slate-800/60 border border-slate-700/50 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span>Đang tra cứu tài liệu & sinh câu trả lời...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        onSuggestionClick={(q) => handleSendMessage(q)}
        disabled={loading}
      />
    </div>
  );
}
