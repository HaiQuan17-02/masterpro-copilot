import sys
import io

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from chunker import DocumentChunker


sample_document = """
# Hướng Dẫn Xử Lý Lỗi Thiết Bị Bán Hàng & Máy In MasterPro

## 1. Kiểm tra nguồn điện và cáp kết nối
Khi máy in hóa đơn không in được hoặc mất kết nối:
- Đảm bảo cáp nguồn 24V được cắm chắc chắn vào máy in và ổ điện.
- Đèn nguồn LED màu xanh trên máy in phải sáng cố định.
- Nếu đèn báo đỏ nhấp nháy, kiểm tra xem nắp máy in đã được đóng chặt hay chưa.

## 2. Kiểm tra kết nối USB hoặc mạng LAN
- Với máy in kết nối USB: Rút giắc cắm USB phía sau máy in và cắm sang cổng USB khác trên máy POS bán hàng.
- Với máy in mạng LAN / Wifi: Đảm bảo địa chỉ IP máy in cùng lớp mạng với máy POS (ví dụ: 192.168.1.200). Thử gửi lệnh ping đến địa chỉ IP này từ Command Prompt.

## 3. Khởi động lại dịch vụ Print Spooler
Trong trường hợp có nhiều lệnh in bị kẹt trong hàng đợi Windows:
- Mở menu Start, gõ `services.msc` và nhấn Enter.
- Tìm dịch vụ `Print Spooler`, bấm chuột phải chọn `Restart`.
- Kiểm tra lại phần mềm MasterPro POS xem biểu tượng máy in đã chuyển sang màu xanh hay chưa.
"""

def main():
    chunker = DocumentChunker(chunk_size=350, chunk_overlap=80)
    metadata = {
        "document": "HDSD_ThietBi_MasterPro_v1.2.pdf",
        "module": "Hardware_POS",
        "version": "1.2",
        "author": "KyThuat_MasterPro"
    }

    chunks = chunker.split_text(sample_document, metadata=metadata)

    print("=" * 60)
    print(f"KẾT QUẢ CHUNKING TÀI LIỆU (Tổng số chunks: {len(chunks)})")
    print("=" * 60)

    for i, c in enumerate(chunks, 1):
        print(f"\n[CHUNK {i}] - ID: {c['chunk_id']}")
        print(f"Ký tự: {c['char_count']} | Ước tính Tokens: {c['approx_tokens']}")
        print(f"Metadata: {c['metadata']}")
        print("-" * 40)
        print(c['content'])
        print("-" * 40)

if __name__ == "__main__":
    main()
