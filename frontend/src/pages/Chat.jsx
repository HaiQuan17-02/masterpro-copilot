import React, { useState, useRef, useEffect } from 'react';
import {
  Bot,
  RefreshCw,
  Search,
  BookOpen,
  Filter,
  CheckCircle2,
  AlertTriangle,
  FolderOpen
} from 'lucide-react';

import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import Modal from '../components/ui/Modal';
import Loading from '../components/ui/Loading';
import ErrorMessage from '../components/ui/ErrorMessage';
import ChatBubble from '../components/ui/ChatBubble';
import ChatInput from '../components/ui/ChatInput';
import SourceCard from '../components/ui/SourceCard';

// Comprehensive realistic Mock Knowledge Base data based on MasterPro dataset
const MOCK_KNOWLEDGE_DOCS = [
  {
    id: 1,
    document_code: 'DOC_HDSD_001',
    category: 'HDSD',
    module: 'Đăng nhập',
    title: 'Đăng nhập vào hệ thống MasterPro',
    content: 'Khởi động phần mềm MasterPro, nhập Tên đăng nhập, Mật khẩu, lựa chọn đúng Chi nhánh làm việc từ danh sách thả xuống rồi nhấn Đăng nhập.',
    note: 'Bắt buộc chọn đúng chi nhánh được cấp quyền[cite: 4].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 2,
    document_code: 'DOC_HDSD_002',
    category: 'HDSD',
    module: 'Hệ thống',
    title: 'Cấu hình kết số và khóa sổ trong MasterPro',
    content: 'Vào Hệ thống -> Cấu hình tham số -> Khóa sổ kế toán. Nhập ngày khóa sổ mới rồi bấm Lưu (F2). Sau khi khóa sổ, các chứng từ trước ngày này sẽ không được sửa hay xóa.',
    note: 'Chỉ tài khoản quyền Admin hoặc Kế toán trưởng mới có quyền đổi ngày khóa sổ[cite: 6].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 29,
    document_code: 'DOC_HDSD_029',
    category: 'HDSD',
    module: 'Bán hàng',
    title: 'Tạo phiếu bán lẻ tại quầy POS',
    content: 'Vào Bán hàng -> Thêm đơn bán lẻ (hoặc bấm icon máy tính) -> Chọn nhân viên bán, kho bán -> Quét mã vạch sản phẩm, nhập số lượng, giảm giá -> Bấm Lưu và in (F4).',
    note: 'Giao diện chuyên dùng cho thu ngân bán lẻ[cite: 29, 30].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 35,
    document_code: 'DOC_HDSD_035',
    category: 'HDSD',
    module: 'Kho hàng',
    title: 'Lập phiếu nhập kho từ nhà cung cấp',
    content: 'Vào Quản lý kho -> Nhập kho -> Bấm Thêm mới (F2) -> Chọn Nhà cung cấp, Kho nhập -> Nhập danh sách mặt hàng, số lượng và đơn giá -> Bấm Hoàn thành và Duyệt phiếu.',
    note: 'Phiếu nhập kho sau khi duyệt sẽ tự động tăng số lượng tồn kho thực tế[cite: 18].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 51,
    document_code: 'DOC_FAQ_001',
    category: 'FAQ',
    module: 'Hệ thống',
    title: 'Tôi có thể đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc không?',
    content: 'Không. Khi đăng nhập bạn bắt buộc phải chọn cố định 1 chi nhánh làm việc trong phiên đăng nhập để phần mềm quản lý sổ sách chính xác.',
    note: 'Phải đăng xuất ra để chuyển sang chi nhánh khác[cite: 4].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 52,
    document_code: 'DOC_FAQ_002',
    category: 'FAQ',
    module: 'Bán hàng',
    title: 'Đơn đặt hàng có làm tăng giảm tồn kho thực tế ngay không?',
    content: 'Không. Đơn đặt hàng (SO) chỉ ghi nhận nhu cầu của khách hàng và cập nhật số lượng Đặt giữ chỗ (Hold). Tồn kho thực tế chỉ giảm khi đã xuất hóa đơn bán hàng hoặc lập Phiếu xuất kho.',
    note: 'Quy trình kiểm soát tồn kho tiêu chuẩn MasterPro ERP[cite: 31].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 60,
    document_code: 'DOC_FAQ_010',
    category: 'FAQ',
    module: 'Kế toán',
    title: 'Tại sao không xóa hay chỉnh sửa được hóa đơn đã khóa sổ?',
    content: 'Khi kỳ kế toán đã được thực hiện kết số và khóa sổ, toàn bộ giao dịch trước ngày khóa sổ bị đóng băng để đảm bảo tính toàn vẹn báo cáo tài chính thuế. Nếu cần điều chỉnh, phải lập phiếu điều chỉnh tăng/giảm ở kỳ hiện tại.',
    note: 'Liên hệ Kế toán trưởng nếu cần mở sổ tạm thời[cite: 6].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 81,
    document_code: 'DOC_RB1_001',
    category: 'RUNBOOK_L1',
    module: 'Đăng nhập',
    title: 'Sự cố không đăng nhập được phần mềm hoặc sai chi nhánh',
    content: '1. Kiểm tra lại kết nối mạng LAN/Internet đến máy chủ. 2. Nhập chính xác Username/Password (chú ý phím CapsLock). 3. Nhấp vào mục Thông tin kết nối để kiểm tra IP máy chủ. 4. Chọn đúng Chi nhánh được cấp quyền. 5. Bấm Đăng nhập.',
    note: 'Nếu vẫn lỗi liên hệ Hotline kỹ thuật 1900.2929.51[cite: 1, 4].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 83,
    document_code: 'DOC_RB1_003',
    category: 'RUNBOOK_L1',
    module: 'Kho hàng',
    title: 'Xử lý lỗi kẹt lệnh in hóa đơn và máy in không nhận tín hiệu',
    content: '1. Kiểm tra dây nguồn 24V và đèn LED xanh trên máy in. 2. Rút cắm lại cáp USB/mạng LAN. 3. Mở services.msc trên Windows, tìm dịch vụ Print Spooler -> Bấm Restart. 4. Khởi động lại phần mềm MasterPro.',
    note: 'Khởi động lại Print Spooler là bước chuẩn hóa L1[cite: 5, 15].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  },
  {
    id: 88,
    document_code: 'DOC_RB1_008',
    category: 'RUNBOOK_L1',
    module: 'Kho hàng',
    title: 'Xử lý lỗi lệch số liệu tồn kho và cảnh báo âm kho khi xuất bán',
    content: '1. Kiểm tra lại thẻ kho của sản phẩm xem có phiếu nhập hàng chưa duyệt không. 2. Vào Báo cáo kho -> Chạy lại tính toán tồn tức thời. 3. Nếu cấu hình phần mềm cấm xuất âm, yêu cầu thủ kho duyệt phiếu nhập trước khi thu ngân xuất hóa đơn.',
    note: 'Quy trình đối soát tồn kho L1[cite: 22].',
    version: '1.0',
    source: 'Tài liệu vận hành MasterPro',
    status: 'APPROVED',
  }
];

const SUGGESTIONS_BY_CATEGORY = {
  ALL: [
    'Làm sao để xử lý sự cố không đăng nhập được hoặc chọn nhầm chi nhánh?',
    'Cách xử lý lỗi máy in hóa đơn bill kẹt lệnh in?',
    'Tạo phiếu bán lẻ tại quầy POS thế nào?',
    'Quy định kết số và khóa sổ kế toán cuối kỳ?'
  ],
  HDSD: [
    'Tạo phiếu bán lẻ tại quầy POS thế nào?',
    'Quy định kết số và khóa sổ kế toán cuối kỳ?',
    'Lập phiếu nhập kho từ nhà cung cấp?',
    'Đăng nhập vào hệ thống MasterPro?'
  ],
  FAQ: [
    'Đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc được không?',
    'Đơn đặt hàng có làm tăng giảm tồn kho thực tế ngay không?',
    'Tại sao không xóa hay chỉnh sửa được hóa đơn đã khóa sổ?'
  ],
  RUNBOOK_L1: [
    'Làm sao để xử lý sự cố không đăng nhập được hoặc chọn nhầm chi nhánh?',
    'Cách xử lý lỗi máy in hóa đơn bill kẹt lệnh in?',
    'Xử lý lỗi lệch số liệu tồn kho và cảnh báo âm kho khi xuất bán?'
  ]
};

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      id: 'msg-welcome',
      sender: 'bot',
      text: 'Xin chào! Tôi là **MasterPro Copilot** — Trợ lý AI hỗ trợ vận hành và xử lý sự cố hệ thống MasterPro.\n\nTôi có thể giúp bạn tra cứu nhanh:\n- **Hướng dẫn sử dụng (HDSD)**: Nghiệp vụ Kho, Bán hàng, Khuyến mãi, Thu ngân.\n- **Câu hỏi thường gặp (FAQ)**: Logic khóa sổ, hạch toán cấn trừ, đơn hàng giữ chỗ.\n- **Quy trình vận hành L1 (Runbook L1)**: Khắc phục lỗi đăng nhập, máy in hóa đơn bill, sai lệch tồn kho.\n\n*Bạn có thể bấm vào nguồn trích dẫn `[cite]` bên dưới câu trả lời để xem tài liệu gốc hoặc đánh giá độ hữu ích.*',
      citations: [],
      timestamp: '10:00',
      feedback: null
    },
    {
      id: 'msg-user-1',
      sender: 'user',
      text: 'Làm sao để xử lý sự cố không đăng nhập được vào phần mềm hoặc chọn nhầm chi nhánh?',
      timestamp: '10:01'
    },
    {
      id: 'msg-bot-1',
      sender: 'bot',
      text: 'Đối với sự cố không đăng nhập được hoặc chọn sai chi nhánh, bạn xử lý theo **Quy trình chuẩn L1** sau:\n\n1. **Kiểm tra kết nối mạng**: Đảm bảo máy POS/Client thông mạng LAN hoặc Internet đến máy chủ MasterPro.\n2. **Xác nhận thông tin**: Gõ chính xác Tên đăng nhập và Mật khẩu (lưu ý phím `CapsLock`).\n3. **Kiểm tra IP máy chủ**: Nhấp vào nút `Thông tin kết nối` trên giao diện đăng nhập để đối chiếu địa chỉ IP máy chủ.\n4. **Chọn đúng Chi nhánh**: Chọn đúng chi nhánh mà tài khoản của bạn được gán quyền làm việc.\n5. **Nhấn Đăng nhập**.\n\n*Lưu ý*: Một tài khoản không thể đăng nhập cùng lúc ở nhiều chi nhánh khác nhau.',
      citations: [
        {
          title: 'Sự cố không đăng nhập được phần mềm hoặc sai chi nhánh',
          document_code: 'DOC_RB1_001',
          category: 'RUNBOOK_L1',
          page: 4,
          note: 'Nếu vẫn lỗi liên hệ Hotline kỹ thuật 1900.2929.51[cite: 1, 4].'
        },
        {
          title: 'Tôi có thể đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc không?',
          document_code: 'DOC_FAQ_001',
          category: 'FAQ',
          page: 4,
          note: 'Phải đăng xuất ra để chuyển sang chi nhánh khác[cite: 4].'
        }
      ],
      timestamp: '10:01',
      feedback: 'like'
    }
  ]);

  const [loading, setLoading] = useState(false);
  const [selectedCitationDoc, setSelectedCitationDoc] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isKbBrowserOpen, setIsKbBrowserOpen] = useState(false);
  const [showErrorBanner, setShowErrorBanner] = useState(false);
  const [activeCategoryFilter, setActiveCategoryFilter] = useState('ALL');
  const [kbSearchQuery, setKbSearchQuery] = useState('');

  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Handle Feedback updates from ChatBubble / Feedback control
  const handleFeedbackChange = (messageId, feedbackType, details) => {
    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.id === messageId) {
          return {
            ...msg,
            feedback: feedbackType,
            feedbackDetails: details
          };
        }
        return msg;
      })
    );
  };

  // Handle Send Message
  const handleSendMessage = (text) => {
    const userMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    // Simulate AI Retrieval and Response after 1.1s
    setTimeout(() => {
      const lowerText = text.toLowerCase();
      let botResponseText = '';
      let citations = [];

      if (lowerText.includes('in') || lowerText.includes('máy in')) {
        botResponseText = `Quy trình chuẩn L1 khắc phục lỗi máy in hóa đơn bill kẹt lệnh in:\n\n1. **Kiểm tra nguồn điện**: Đảm bảo adapter 24V cắm chặt và đèn LED xanh trên máy in sáng bình thường.\n2. **Kiểm tra cáp kết nối**: Rút ra và cắm lại đầu cáp USB hoặc cáp mạng LAN.\n3. **Khởi động lại Print Spooler**: Nhấn phím \`Windows + R\`, gõ \`services.msc\`, tìm dịch vụ \`Print Spooler\` rồi bấm **Restart**.\n4. **Khởi động lại phần mềm**: Tắt và mở lại ứng dụng MasterPro bán hàng.`;
        citations = [
          {
            title: 'Xử lý lỗi kẹt lệnh in hóa đơn và máy in không nhận tín hiệu',
            document_code: 'DOC_RB1_003',
            category: 'RUNBOOK_L1',
            page: 15,
            note: 'Khởi động lại Print Spooler là bước chuẩn hóa L1[cite: 5, 15].'
          }
        ];
      } else if (lowerText.includes('bán') || lowerText.includes('pos')) {
        botResponseText = `Hướng dẫn tạo phiếu bán lẻ tại quầy POS MasterPro:\n\n1. Vào phân hệ **Bán hàng** -> Chọn **Thêm đơn bán lẻ** (hoặc nhấn phím tắt POS trên màn hình chính).\n2. Chọn đúng **Nhân viên thu ngân** và **Kho xuất bán**.\n3. Quét mã vạch sản phẩm qua máy quét barcode (hoặc gõ mã SKU/tên hàng).\n4. Nhập số lượng, chiết khấu khuyến mãi (nếu có).\n5. Bấm **Lưu và in (F4)** để hoàn tất hóa đơn bán hàng.`;
        citations = [
          {
            title: 'Tạo phiếu bán lẻ tại quầy POS',
            document_code: 'DOC_HDSD_029',
            category: 'HDSD',
            page: 29,
            note: 'Giao diện chuyên dùng cho thu ngân bán lẻ[cite: 29, 30].'
          }
        ];
      } else if (lowerText.includes('khóa sổ') || lowerText.includes('kết số')) {
        botResponseText = `Quy định cấu hình kết số và khóa sổ kế toán trong MasterPro:\n\n1. Vào phân hệ **Hệ thống** -> **Cấu hình tham số** -> **Khóa sổ kế toán**.\n2. Chọn ngày khóa sổ mong muốn rồi nhấn **Lưu (F2)**.\n3. Sau khi khóa sổ, toàn bộ chứng từ phát sinh trước ngày khóa sổ sẽ bị đóng băng, không cho phép sửa hay xóa.\n\n*Lưu ý*: Chỉ tài khoản Admin hoặc Kế toán trưởng mới có quyền thay đổi ngày khóa sổ.`;
        citations = [
          {
            title: 'Cấu hình kết số và khóa sổ trong MasterPro',
            document_code: 'DOC_HDSD_002',
            category: 'HDSD',
            page: 6,
            note: 'Chỉ tài khoản quyền Admin hoặc Kế toán trưởng mới có quyền đổi ngày khóa sổ[cite: 6].'
          },
          {
            title: 'Tại sao không xóa hay chỉnh sửa được hóa đơn đã khóa sổ?',
            document_code: 'DOC_FAQ_010',
            category: 'FAQ',
            page: 6,
            note: 'Liên hệ Kế toán trưởng nếu cần mở sổ tạm thời[cite: 6].'
          }
        ];
      } else if (lowerText.includes('tồn kho') || lowerText.includes('nhập kho') || lowerText.includes('âm kho')) {
        botResponseText = `Về quản lý tồn kho và nhập hàng MasterPro:\n\n1. **Nhập kho**: Vào Quản lý kho -> Nhập kho -> Thêm mới (F2) -> Chọn Nhà cung cấp -> Nhập danh mục mặt hàng -> Duyệt phiếu để tăng tồn kho thực tế.\n2. **Xử lý cảnh báo âm kho**: Nếu hệ thống báo không đủ tồn, kiểm tra lại thẻ kho và đảm bảo phiếu nhập đã được duyệt trước khi xuất bán.`;
        citations = [
          {
            title: 'Lập phiếu nhập kho từ nhà cung cấp',
            document_code: 'DOC_HDSD_035',
            category: 'HDSD',
            page: 18,
            note: 'Phiếu nhập kho sau khi duyệt sẽ tự động tăng số lượng tồn kho thực tế[cite: 18].'
          },
          {
            title: 'Xử lý lỗi lệch số liệu tồn kho và cảnh báo âm kho khi xuất bán',
            document_code: 'DOC_RB1_008',
            category: 'RUNBOOK_L1',
            page: 22,
            note: 'Quy trình đối soát tồn kho L1[cite: 22].'
          }
        ];
      } else {
        botResponseText = `Dựa trên tài liệu hệ thống MasterPro, về câu hỏi **"${text}"**:\n\n1. Truy cập đúng phân hệ chức năng tương ứng trên thanh điều hướng.\n2. Nhập đầy đủ các trường thông tin bắt buộc được đánh dấu.\n3. Nhấn **Lưu (F2)** hoặc **Lưu và in (F4)** để hoàn tất.\n\nNếu gặp lỗi kỹ thuật, hãy kiểm tra mã lỗi và tham chiếu tài liệu Runbook L1 tương ứng.`;
        citations = [
          {
            title: 'Tạo phiếu bán lẻ tại quầy POS',
            document_code: 'DOC_HDSD_029',
            category: 'HDSD',
            page: 29,
            note: 'Tài liệu hướng dẫn vận hành chuẩn MasterPro[cite: 29].'
          }
        ];
      }

      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: botResponseText,
        citations,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        feedback: null
      };

      setMessages((prev) => [...prev, botMessage]);
      setLoading(false);
    }, 1100);
  };

  // Open Citation Modal
  const handleCitationClick = (citation) => {
    const foundDoc = MOCK_KNOWLEDGE_DOCS.find(
      (d) => d.document_code === citation.document_code || d.title === citation.title
    ) || {
      title: citation.title,
      document_code: citation.document_code || 'DOC_CITE',
      category: citation.category || 'HDSD',
      module: 'Tài liệu hướng dẫn',
      content: 'Nội dung trích dẫn chi tiết từ bộ tài liệu vận hành chuẩn của MasterPro Copilot.',
      note: citation.note || 'Trích dẫn xác thực từ cơ sở tri thức gốc.',
      version: '1.0',
      source: 'Tài liệu vận hành MasterPro',
      status: 'APPROVED'
    };

    setSelectedCitationDoc(foundDoc);
    setIsModalOpen(true);
  };

  const handleResetChat = () => {
    setMessages([
      {
        id: `reset-${Date.now()}`,
        sender: 'bot',
        text: 'Phiên hội thoại đã được làm mới. Hãy nhập câu hỏi về nghiệp vụ hoặc mã lỗi bạn đang gặp phải.',
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        feedback: null
      }
    ]);
  };

  // Filtered knowledge docs for KB browser modal
  const filteredKbDocs = MOCK_KNOWLEDGE_DOCS.filter((doc) => {
    const matchCategory = activeCategoryFilter === 'ALL' || doc.category === activeCategoryFilter;
    const matchSearch =
      !kbSearchQuery.trim() ||
      doc.title.toLowerCase().includes(kbSearchQuery.toLowerCase()) ||
      doc.module.toLowerCase().includes(kbSearchQuery.toLowerCase()) ||
      doc.content.toLowerCase().includes(kbSearchQuery.toLowerCase());
    return matchCategory && matchSearch;
  });

  const currentSuggestions = SUGGESTIONS_BY_CATEGORY[activeCategoryFilter] || SUGGESTIONS_BY_CATEGORY.ALL;

  return (
    <div className="w-full max-w-5xl h-[92vh] sm:h-[88vh] flex flex-col rounded-2xl overflow-hidden border border-slate-800 bg-slate-900/95 shadow-2xl backdrop-blur-xl">
      {/* 1. Header Toolbar */}
      <header className="px-4 sm:px-6 py-3.5 bg-slate-950/70 border-b border-slate-800 flex items-center justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-600/30">
            <Bot className="w-5 h-5" />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <h2 className="text-sm sm:text-base font-bold text-slate-100 tracking-tight">
                MasterPro Copilot
              </h2>
              <Badge variant="APPROVED" size="sm">
                UI Kit Prototype
              </Badge>
            </div>
            <p className="text-[11px] text-slate-400">
              Trợ lý AI hỗ trợ vận hành & IT Support Cấp 1 • Tuần 3
            </p>
          </div>
        </div>

        {/* Top actions & Test toggles */}
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsKbBrowserOpen(true)}
            leftIcon={BookOpen}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            <span className="hidden sm:inline">Tra cứu tri thức</span>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowErrorBanner(!showErrorBanner)}
            className="text-xs text-slate-400 hover:text-amber-300"
            title="Thử nghiệm hiển thị Error Banner"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden md:inline">Test Error</span>
          </Button>

          <Button
            variant="secondary"
            size="sm"
            leftIcon={RefreshCw}
            onClick={handleResetChat}
            className="text-xs"
          >
            <span>Làm mới</span>
          </Button>
        </div>
      </header>

      {/* 2. Optional Error Banner Test */}
      {showErrorBanner && (
        <div className="p-3 border-b border-slate-800 bg-slate-950/50">
          <ErrorMessage
            title="Cảnh báo kiểm thử trạng thái lỗi (ErrorMessage Component)"
            message="Đây là component ErrorMessage chuẩn được hiển thị khi mất kết nối mạng hoặc truy vấn tri thức gặp lỗi timeout. Hãy nhấn nút 'Thử lại' để khôi phục."
            onRetry={() => setShowErrorBanner(false)}
          />
        </div>
      )}

      {/* 3. Knowledge Base Category Filter Pill Tabs */}
      <div className="px-4 sm:px-6 py-2 bg-slate-950/40 border-b border-slate-800/80 flex items-center justify-between gap-2 overflow-x-auto text-xs">
        <div className="flex items-center gap-1.5 shrink-0">
          <Filter className="w-3.5 h-3.5 text-slate-400 mr-1" />
          {[
            { id: 'ALL', label: 'Tất cả tri thức (100)' },
            { id: 'HDSD', label: 'HDSD (50)' },
            { id: 'FAQ', label: 'FAQ (30)' },
            { id: 'RUNBOOK_L1', label: 'Runbook L1 (20)' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveCategoryFilter(tab.id)}
              className={`
                px-2.5 py-1 rounded-lg font-medium transition-colors cursor-pointer
                ${
                  activeCategoryFilter === tab.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => setIsKbBrowserOpen(true)}
          className="text-[11px] text-blue-400 hover:text-blue-300 font-medium hidden sm:flex items-center gap-1 cursor-pointer"
        >
          <FolderOpen className="w-3.5 h-3.5" />
          <span>Duyệt danh mục tài liệu</span>
        </button>
      </div>

      {/* 4. Chat Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-3">
        {messages.map((msg) => (
          <ChatBubble
            key={msg.id}
            message={msg}
            onCitationClick={handleCitationClick}
            onFeedbackChange={(type, details) => handleFeedbackChange(msg.id, type, details)}
          />
        ))}

        {/* AI Typing / Retrieval Loading Indicator */}
        {loading && (
          <div className="flex items-start gap-3 my-3 text-left">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shrink-0 shadow-md">
              <Bot className="w-4 h-4" />
            </div>
            <div className="p-3.5 rounded-2xl rounded-tl-xs bg-slate-900 border border-slate-800 text-slate-300">
              <Loading type="dots" text="Đang tra cứu cơ sở tri thức MasterPro & đối chiếu citation..." />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 5. Chat Input Bar with Category-aware Suggestions */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={loading}
        suggestions={currentSuggestions}
        onSuggestionClick={(sug) => handleSendMessage(sug)}
      />

      {/* 6. Modal Xem Chi Tiết Trích Dẫn & Tài Liệu Gốc */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Trích Dẫn Tài Liệu Gốc"
        description="Thông tin chi tiết được lưu trữ trong cơ sở tri thức MasterPro"
        size="lg"
        footer={
          <div className="flex items-center justify-between w-full">
            <span className="text-xs text-slate-400">
              Trạng thái kiểm duyệt: <strong className="text-emerald-400">Đã kiểm duyệt (APPROVED)</strong>
            </span>
            <Button variant="secondary" size="sm" onClick={() => setIsModalOpen(false)}>
              Đóng hộp thoại
            </Button>
          </div>
        }
      >
        {selectedCitationDoc && (
          <div className="space-y-4 text-left">
            <SourceCard document={selectedCitationDoc} />

            <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Toàn văn quy trình nghiệp vụ:
              </h4>
              <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-line">
                {selectedCitationDoc.content}
              </p>
            </div>

            {selectedCitationDoc.note && (
              <div className="p-3 rounded-xl bg-blue-950/30 border border-blue-800/40 text-xs text-blue-200 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <strong className="font-semibold">Căn cứ trích dẫn:</strong>{' '}
                  <span>{selectedCitationDoc.note}</span>
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 7. Modal Duyệt Toàn Bộ Cơ Sở Tri Thức (Knowledge Base Explorer) */}
      <Modal
        isOpen={isKbBrowserOpen}
        onClose={() => setIsKbBrowserOpen(false)}
        title="Cơ Sở Tri Thức MasterPro"
        description="Tra cứu nhanh danh mục tài liệu theo nhóm HDSD, FAQ và Runbook L1"
        size="xl"
        footer={
          <div className="flex items-center justify-between w-full">
            <span className="text-xs text-slate-400">
              Đang hiển thị {filteredKbDocs.length} tài liệu
            </span>
            <Button variant="secondary" size="sm" onClick={() => setIsKbBrowserOpen(false)}>
              Đóng
            </Button>
          </div>
        }
      >
        <div className="space-y-4 text-left">
          <Input
            placeholder="Tìm theo tiêu đề, phân hệ, nội dung..."
            value={kbSearchQuery}
            onChange={(e) => setKbSearchQuery(e.target.value)}
            leftIcon={Search}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[50vh] overflow-y-auto pr-1">
            {filteredKbDocs.map((doc) => (
              <SourceCard
                key={doc.id}
                document={doc}
                onOpenDetail={(d) => {
                  setSelectedCitationDoc(d);
                  setIsModalOpen(true);
                }}
              />
            ))}
            {filteredKbDocs.length === 0 && (
              <div className="col-span-2 text-center py-8 text-slate-500 text-sm">
                Không tìm thấy tài liệu phù hợp với từ khóa "{kbSearchQuery}".
              </div>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
}
