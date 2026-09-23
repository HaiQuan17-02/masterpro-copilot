const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (error) {
    console.warn('Backend not reached, health check failed:', error.message);
    return { status: 'offline', error: error.message };
  }
}

export async function sendChatMessage(message, conversationId = null) {
  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });

    if (!res.ok) {
      throw new Error(`API error ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.warn('API error, falling back to local simulation:', error.message);
    // Fallback simulation if backend is not started
    if (message.toLowerCase().includes('máy in') || message.toLowerCase().includes('in')) {
      return {
        answer: 'Để xử lý sự cố máy in không nhận lệnh hoặc không in được, bạn có thể thực hiện theo các bước sau:\n1. **Kiểm tra nguồn điện**: Đảm bảo dây nguồn cắm chặt và đèn nguồn máy in sáng xanh.\n2. **Kiểm tra kết nối cáp / mạng**: Rút và cắm lại cáp USB hoặc kiểm tra địa chỉ IP máy in trong mạng LAN nội bộ.\n3. **Kiểm tra khay giấy và mực in**: Xác nhận khay nạp còn giấy chuẩn khổ và hộp mực không bị kẹt.\n4. **Khởi động lại dịch vụ Print Spooler** trên máy tính hoặc restart máy in để xóa hàng đợi lệnh in cũ.',
        citations: [
          {
            title: 'Hướng dẫn xử lý lỗi thiết bị bán hàng & Máy in',
            document: 'HDSD_ThietBi_MasterPro_v1.2.pdf',
            page: 15,
            chunk_id: 'chunk_doc_001_p15',
            score: 0.94
          },
          {
            title: 'Cấu hình cổng COM/USB máy in hóa đơn bill',
            document: 'CauHinh_PhanCung_v2.0.pdf',
            page: 7,
            chunk_id: 'chunk_doc_003_p7',
            score: 0.88
          }
        ],
        provider: 'fallback-local',
        model: 'masterpro-copilot-mock'
      };
    }

    return {
      answer: `Hệ thống ghi nhận câu hỏi: "${message}". Đây là chế độ phản hồi dự phòng của MasterPro Copilot.`,
      citations: [
        {
          title: 'Tài liệu hướng dẫn sử dụng hệ thống MasterPro',
          document: 'HDSD_TongQuan_v1.0.pdf',
          page: 1,
          chunk_id: 'chunk_general_01',
          score: 0.85
        }
      ],
      provider: 'fallback-local',
      model: 'masterpro-copilot-mock'
    };
  }
}
