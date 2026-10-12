"""
Demo HeadingAwareChunker for MasterPro Copilot (Week 3).

Demonstrates the chunking process on realistic MasterPro ERP/POS operational
documentation with nested Markdown headings, tables, lists, and code blocks.
"""

import sys
import io
import json

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from heading_aware_chunker import HeadingAwareChunker

sample_document = """
# Hướng Dẫn Vận Hành Phần Cứng & Xử Lý Lỗi MasterPro POS [cite: 25]

Tài liệu hướng dẫn kỹ thuật dành cho đội ngũ hỗ trợ vận hành L1 và thu ngân tại các chuỗi cửa hàng bán lẻ.
Mọi thao tác cần tuân thủ quy trình an toàn nguồn điện và đối soát dữ liệu bán hàng.

## 1. Cấu hình Máy In Hóa Đơn (Thermal Printer K80)
Máy in hóa đơn nhiệt kết nối trực tiếp với máy bán hàng POS qua cổng USB hoặc mạng LAN.

### 1.1. Các bước kiểm tra ban đầu:
1. Kiểm tra giắc cắm nguồn 24V vào máy in, đèn LED xanh POWER phải sáng cố định.
2. Kiểm tra cuộn giấy in nhiệt khổ K80 đã đặt đúng chiều (mặt cảm nhiệt hướng lên).
3. Đóng chặt nắp máy in, đảm bảo đèn ERROR màu đỏ không nhấp nháy.

### 1.2. Danh mục mã lỗi máy in thường gặp:
| Mã lỗi | Triệu chứng | Nguyên nhân kỹ thuật | Hướng khắc phục |
| :--- | :--- | :--- | :--- |
| ERR_PRN_01 | Máy in không ra bill | Kẹt dao cắt tự động | Tắt nguồn, xoay bánh răng giải phóng dao cắt |
| ERR_PRN_02 | Chữ in bị mờ | Bụi bẩn bám đầu in nhiệt | Dùng bông cồn y tế 90 độ lau nhẹ thanh nhiệt |
| ERR_PRN_03 | Mất kết nối LAN | Trùng IP hoặc nhảy DHCP | Gán IP tĩnh và cấu hình lại file pos_config.json |

### 1.3. Lệnh kiểm tra kết nối qua CLI:
Để kiểm tra cổng in 9100 của máy in từ máy POS:
```bash
# Ping kiểm tra thông mạng tới IP máy in hóa đơn
ping 192.168.1.200 -n 4

# Test kết nối cổng in qua telnet / Test-NetConnection
Test-NetConnection -ComputerName 192.168.1.200 -Port 9100
```

## 2. Quy trình Kết Ca & Khóa Sổ Bán Hàng Cuối Ngày
Nhân viên thu ngân bắt buộc thực hiện kết ca trước khi bàn giao tiền mặt cho quản lý cửa hàng:
- In báo cáo tổng kết doanh thu ca làm việc (Báo cáo Z).
- Kiểm đếm thực tế tiền mặt trong két tiền POS.
- Khóa sổ quỹ và ghi nhận số chênh lệch nếu có vào hệ thống ERP MasterPro.
<!-- page: 26 -->
"""

def run_demo():
    chunker = HeadingAwareChunker(chunk_size=450, chunk_overlap=80)
    
    metadata = {
        "document_id": "DOC_POS_HARDWARE_025",
        "version_id": "v2.4",
        "category": "RUNBOOK_L1",
        "module": "Hardware_POS",
        "title": "Hướng Dẫn Vận Hành Phần Cứng & Xử Lý Lỗi MasterPro POS",
        "source": "Tài liệu kỹ thuật nội bộ MasterPro",
        "note": "Tham khảo tài liệu trích dẫn [cite: 25]"
    }

    chunks = chunker.chunk_document(sample_document, metadata)

    print("=" * 80)
    print(f"MASTERPRO COPILOT - KẾT QUẢ CHUNKING TÀI LIỆU (Tổng số: {len(chunks)} chunks)")
    print("=" * 80)

    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- [CHUNK {i}/{len(chunks)}] ---")
        print(f"ID           : {chunk['chunk_id']}")
        print(f"Document ID  : {chunk['document_id']} | Version: {chunk['version_id']}")
        print(f"Module       : {chunk['module']} | Category: {chunk['category']}")
        print(f"Heading Path : {chunk['heading_path']}")
        print(f"Trang (Page) : {chunk['page']}")
        print(f"Kích thước   : {chunk['char_count']} ký tự | Ước tính {chunk['approx_tokens']} tokens")
        print("-" * 50)
        print("NỘI DUNG CHUNK:")
        print(chunk['content'])
        print("-" * 50)

if __name__ == "__main__":
    run_demo()
