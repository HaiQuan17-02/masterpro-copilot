"""
Unit tests for HeadingAwareChunker (MasterPro Copilot - Week 3).

Test cases covered:
1. Markdown nhiều cấp heading (H1 đến H6, heading_path breadcrumbs, stack popping).
2. Tài liệu không có heading (fallback title / empty heading path).
3. Section quá dài (chia thành nhiều chunk, đảm bảo chunk_size, có overlap giữa các chunk).
4. Bullet list và numbered list (giữ nguyên cấu trúc list, chia theo item khi quá dài).
5. Bảng Markdown (giữ nguyên bảng, lặp lại header khi bảng bị chia nhỏ).
6. Code block (giữ nguyên code fence, không nhầm lẫn '#' trong comment là heading).
7. Nội dung tiếng Việt (Unicode NFC, dấu tiếng Việt, thuật ngữ POS/ERP).
8. Tài liệu rỗng (chuỗi rỗng, chuỗi chỉ có khoảng trắng).
9. Bảo toàn metadata (đủ 10 trường: document_id, version_id, category, module, title, heading_path, chunk_index, content, source, page).
"""

import sys
import os
import unittest
import unicodedata

# Ensure paths
test_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.abspath(os.path.join(test_dir, ".."))
ai_dir = os.path.abspath(os.path.join(workspace_dir, "ai"))

if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)
if workspace_dir not in sys.path:
    sys.path.insert(0, workspace_dir)

from heading_aware_chunker import HeadingAwareChunker


class TestHeadingAwareChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = HeadingAwareChunker(chunk_size=500, chunk_overlap=80)
        self.base_metadata = {
            "document_id": "doc_pos_001",
            "version_id": "v1.2",
            "category": "HDSD",
            "module": "POS_BanHang",
            "title": "Hướng Dẫn Bán Hàng MasterPro POS",
            "source": "Tài liệu đào tạo MasterPro 2026",
            "page": 10
        }

    # =========================================================================
    # 1. MARKDOWN NHIỀU CẤP HEADING (H1 ĐẾN H6)
    # =========================================================================
    def test_multiple_heading_levels(self):
        markdown_text = """
# MasterPro POS
Tổng quan hệ thống bán hàng đa kênh.

## 1. Quản lý Đơn hàng
Các thao tác với đơn hàng tại quầy thu ngân.

### 1.1. Bán hàng trực tiếp
Quét mã vạch sản phẩm và chọn phương thức thanh toán.

#### 1.1.1. Thanh toán QR Code
Khách hàng quét mã VietQR hoặc VNPAY để chuyển khoản.

##### Cấu hình cổng thanh toán
Chọn tài khoản ngân hàng thụ hưởng mặc định.

###### Mã ngân hàng hợp lệ
BIDV, VCB, MBBank, Techcombank.

## 2. Quản lý Trả hàng
Quy trình nhận lại sản phẩm lỗi và hoàn tiền cho khách.
"""
        chunker = HeadingAwareChunker(chunk_size=400, chunk_overlap=60)
        chunks = chunker.chunk_document(markdown_text, self.base_metadata)

        self.assertGreater(len(chunks), 0)

        # Kiểm tra sự xuất hiện của các heading_path theo cấu trúc phân cấp
        heading_paths = [c["heading_path"] for c in chunks]

        self.assertIn("MasterPro POS", heading_paths)
        self.assertIn("MasterPro POS > 1. Quản lý Đơn hàng", heading_paths)
        self.assertIn("MasterPro POS > 1. Quản lý Đơn hàng > 1.1. Bán hàng trực tiếp", heading_paths)
        self.assertIn("MasterPro POS > 1. Quản lý Đơn hàng > 1.1. Bán hàng trực tiếp > 1.1.1. Thanh toán QR Code", heading_paths)
        self.assertIn("MasterPro POS > 1. Quản lý Đơn hàng > 1.1. Bán hàng trực tiếp > 1.1.1. Thanh toán QR Code > Cấu hình cổng thanh toán", heading_paths)
        self.assertIn("MasterPro POS > 1. Quản lý Đơn hàng > 1.1. Bán hàng trực tiếp > 1.1.1. Thanh toán QR Code > Cấu hình cổng thanh toán > Mã ngân hàng hợp lệ", heading_paths)

        # Kiểm tra khi quay lại H2 "2. Quản lý Trả hàng" thì stack đã pop hết các con của H2 trước
        self.assertIn("MasterPro POS > 2. Quản lý Trả hàng", heading_paths)

    # =========================================================================
    # 2. TÀI LIỆU KHÔNG CÓ HEADING
    # =========================================================================
    def test_document_without_headings(self):
        markdown_text = """
Đây là tài liệu ghi chú nhanh không sử dụng bất kỳ thẻ tiêu đề Markdown nào.
Hệ thống MasterPro Copilot hỗ trợ nhân viên bán hàng tra cứu thông tin sản phẩm và chính sách giá.

Đoạn văn thứ hai mô tả về quy định kết ca bán hàng và nộp tiền vào két an toàn trước 22h00.
Nhân viên cần đối soát số dư sổ quỹ tiền mặt với báo cáo doanh thu thực tế.
"""
        chunks = self.chunker.chunk_document(markdown_text, self.base_metadata)

        self.assertGreater(len(chunks), 0)
        for c in chunks:
            # Fallback heading_path lấy theo title trong metadata
            self.assertEqual(c["heading_path"], self.base_metadata["title"])
            self.assertIn("MasterPro Copilot", c["content"])

        # Trường hợp không có cả title trong metadata
        chunks_no_title = self.chunker.chunk_document(markdown_text, metadata={})
        self.assertGreater(len(chunks_no_title), 0)
        for c in chunks_no_title:
            self.assertEqual(c["heading_path"], "")

    # =========================================================================
    # 3. SECTION QUÁ DÀI (OVERSIZED SECTION)
    # =========================================================================
    def test_oversized_section(self):
        # Tạo section có độ dài ~1400 ký tự với cấu hình chunk_size=350, chunk_overlap=80
        paragraph = (
            "Hệ thống bán lẻ MasterPro ERP quản lý luồng dữ liệu thời gian thực giữa hàng trăm điểm bán lẻ. "
            "Khi có giao dịch phát sinh tại quầy POS, dữ liệu đơn hàng ngay lập tức được mã hóa và đồng bộ lên máy chủ đám mây. "
            "Nếu mất kết nối mạng Internet, POS tự động chuyển sang chế độ hoạt động ngoại tuyến Offline Mode. "
            "Mọi chứng từ bán lẻ, hóa đơn điện tử và số dư công nợ khách hàng được lưu trữ tạm thời trong cơ sở dữ liệu SQLite cục bộ. "
            "Khi kết nối mạng được khôi phục, dịch vụ đồng bộ nền sẽ đẩy tuần tự các giao dịch lên SQL Server trung tâm theo cơ chế hàng đợi. "
            "Điều này đảm bảo quầy thu ngân hoạt động liên tục không gián đoạn, tránh thất thoát doanh thu trong giờ cao điểm."
        )
        long_markdown = f"""
## Quy trình Vận hành Chế độ Offline và Đồng bộ Dữ liệu

{paragraph}

{paragraph}
"""
        chunker = HeadingAwareChunker(chunk_size=350, chunk_overlap=80)
        chunks = chunker.chunk_document(long_markdown, self.base_metadata)

        # Phải được chia thành nhiều chunk
        self.assertGreaterEqual(len(chunks), 3)

        # Tất cả chunk trong section này phải có cùng heading_path
        expected_path = "Quy trình Vận hành Chế độ Offline và Đồng bộ Dữ liệu"
        for c in chunks:
            self.assertEqual(c["heading_path"], expected_path)

        # Kiểm tra có sự tồn tại của overlap giữa 2 chunk liên tiếp
        has_overlap = False
        for i in range(len(chunks) - 1):
            c1_text = chunks[i]["content"]
            c2_text = chunks[i + 1]["content"]
            # Lấy 30 ký tự cuối của c1 xem có xuất hiện ở c2 không
            tail_sample = c1_text[-40:].strip()
            # Tìm xem có từ ngữ chung lặp lại ở phần đầu c2 không
            words_c1 = tail_sample.split()
            if any(w in c2_text[:120] for w in words_c1 if len(w) > 4):
                has_overlap = True
                break
        self.assertTrue(has_overlap, "Cần có overlap từ ngữ hợp lệ giữa các chunk liên tiếp trong section dài")

        # Kiểm tra chỉ số chunk tăng dần
        for idx, c in enumerate(chunks, 1):
            self.assertEqual(c["chunk_index"], idx)

    # =========================================================================
    # 4. BULLET LIST VÀ NUMBERED LIST
    # =========================================================================
    def test_bullet_and_numbered_lists(self):
        markdown_text = """
## Quy định Đổi trả & Hướng dẫn Thao tác

### Danh sách điều kiện áp dụng:
- Sản phẩm còn nguyên tem mác, mã vạch (barcode) và bao bì đóng gói.
- Có hóa đơn mua hàng MasterPro hợp lệ trong vòng 7 ngày kể từ ngày mua.
- Sản phẩm không thuộc danh mục hàng thanh lý hoặc khuyến mãi đặc biệt giảm > 50%.
- Khách hàng có thông tin tích điểm trên hệ thống CRM.

### Các bước thực hiện trên phần mềm POS:
1. Đăng nhập tài khoản thu ngân và bấm chọn chức năng "Đổi trả hàng".
2. Quét mã hóa đơn gốc hoặc nhập số điện thoại khách hàng để tra cứu lịch sử mua.
3. Chọn các mã SKU sản phẩm cần đổi trả và nhập lý do trả hàng tương ứng.
4. Bấm "Xác nhận phiếu nhập trả" và in biên lai hoàn tiền cho khách hàng.
"""
        chunker = HeadingAwareChunker(chunk_size=700, chunk_overlap=100)
        chunks = chunker.chunk_document(markdown_text, self.base_metadata)

        # Toàn bộ danh sách phải nằm trọn vẹn trong chunk tương ứng
        bullet_chunk = next((c for c in chunks if "- Sản phẩm còn nguyên tem mác" in c["content"]), None)
        self.assertIsNotNone(bullet_chunk)
        self.assertIn("- Có hóa đơn mua hàng", bullet_chunk["content"])
        self.assertIn("- Khách hàng có thông tin tích điểm", bullet_chunk["content"])

        numbered_chunk = next((c for c in chunks if "1. Đăng nhập tài khoản" in c["content"]), None)
        self.assertIsNotNone(numbered_chunk)
        self.assertIn("2. Quét mã hóa đơn gốc", numbered_chunk["content"])
        self.assertIn("3. Chọn các mã SKU", numbered_chunk["content"])
        self.assertIn("4. Bấm \"Xác nhận phiếu nhập trả\"", numbered_chunk["content"])

    # =========================================================================
    # 5. BẢNG MARKDOWN
    # =========================================================================
    def test_markdown_table(self):
        markdown_text = """
## Bảng Mã Lỗi Máy In & Thiết Bị POS

| Mã lỗi | Tên lỗi | Nguyên nhân phổ biến | Hướng xử lý |
| :--- | :--- | :--- | :--- |
| ERR_PRN_01 | Kẹt giấy in bill | Cuộn giấy K80 lắp lệch trục hoặc dao cắt bị kẹt | Mở nắp máy in, kéo thẳng giấy và đóng chặt nắp |
| ERR_PRN_02 | Mất kết nối LAN | Dây mạng lỏng hoặc IP máy in bị nhảy DHCP | Cố định IP máy in tĩnh và ping kiểm tra cổng 9100 |
| ERR_SCAN_01 | Máy quét không sáng | Cáp USB tiếp xúc kém hoặc thiếu nguồn cấp | Đổi sang cổng USB 3.0 phía sau máy POS |
"""
        chunks = self.chunker.chunk_document(markdown_text, self.base_metadata)
        self.assertGreater(len(chunks), 0)

        # Kiểm tra bảng được giữ nguyên cấu trúc
        table_chunk = chunks[0]
        self.assertIn("| Mã lỗi | Tên lỗi | Nguyên nhân phổ biến | Hướng xử lý |", table_chunk["content"])
        self.assertIn("| :--- | :--- | :--- | :--- |", table_chunk["content"])
        self.assertIn("ERR_PRN_01", table_chunk["content"])
        self.assertIn("ERR_SCAN_01", table_chunk["content"])

        # Kiểm tra khi bảng rất dài vượt quá chunk_size thì header phải được lặp lại
        long_table_text = """
## Danh mục lỗi chi tiết

| Mã lỗi | Mô tả chi tiết | Xử lý |
| :--- | :--- | :--- |
"""
        for i in range(1, 15):
            long_table_text += f"| ERR_{i:03d} | Mô tả lỗi thiết bị số {i} trong vận hành bán lẻ quầy thu ngân | Khởi động lại thiết bị {i} |\n"

        small_chunker = HeadingAwareChunker(chunk_size=250, chunk_overlap=40)
        table_chunks = small_chunker.chunk_document(long_table_text, self.base_metadata)

        self.assertGreater(len(table_chunks), 1)
        for tc in table_chunks:
            # Mỗi chunk bảng đều có dòng tiêu đề cột
            self.assertIn("| Mã lỗi | Mô tả chi tiết | Xử lý |", tc["content"])
            self.assertIn("| :--- | :--- | :--- |", tc["content"])

    # =========================================================================
    # 6. CODE BLOCK
    # =========================================================================
    def test_code_block(self):
        markdown_text = """
## Cấu hình Tự động In Bill qua Python Script

Đoạn mã mẫu gửi lệnh in trực tiếp đến máy in hóa đơn ESC/POS:

```python
# Đây là comment bắt đầu với dấu thăng
# Tuyệt đối không được nhận diện nhầm comment này thành Heading Markdown!
import socket

def send_to_printer(printer_ip: str, port: int, raw_data: bytes):
    # Kết nối TCP socket tới máy in
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5.0)
        sock.connect((printer_ip, port))
        sock.sendall(raw_data)
    print("In bill thành công!")
```

Sau khi cấu hình, hãy khởi động lại dịch vụ Print Spooler.
"""
        chunks = self.chunker.chunk_document(markdown_text, self.base_metadata)
        self.assertGreater(len(chunks), 0)

        code_chunk = next((c for c in chunks if "def send_to_printer" in c["content"]), None)
        self.assertIsNotNone(code_chunk)

        # Đảm bảo code block nguyên vẹn với cặp dấu backtick
        self.assertIn("```python", code_chunk["content"])
        self.assertIn("```", code_chunk["content"])

        # Kiểm tra các comment '# ...' không bị biến thành heading_path
        all_paths = [c["heading_path"] for c in chunks]
        self.assertNotIn("Đây là comment bắt đầu với dấu thăng", all_paths)
        self.assertNotIn("Kết nối TCP socket tới máy in", all_paths)
        self.assertEqual(code_chunk["heading_path"], "Cấu hình Tự động In Bill qua Python Script")

    # =========================================================================
    # 7. NỘI DUNG TIẾNG VIỆT VÀ UNICODE
    # =========================================================================
    def test_vietnamese_content_and_unicode(self):
        # Tạo chuỗi tiếng Việt chứa cả ký tự dạng tổ hợp (NFD) để kiểm tra chuẩn hóa sang NFC
        nfd_text = unicodedata.normalize('NFD', "Phiếu xuất kho kiêm vận chuyển nội bộ")
        markdown_text = f"""
# Quản Lý Kho & Công Nợ Khách Hàng

## 1. Nghiệp vụ {nfd_text}
Hệ thống cho phép lập phiếu xuất kho điều chuyển giữa các chi nhánh:
- Kiểm tra số lượng tồn kho khả dụng trước khi xuất.
- Áp dụng chương trình khuyến mãi và chiết khấu thương mại.
- Cập nhật số dư công nợ phải thu của đại lý phân phối.
- Thực hiện khóa sổ kế toán và đối soát sổ quỹ cuối ngày.

Lưu ý: Mọi giao dịch xuất hàng đều yêu cầu chữ ký số của thủ kho và kế toán trưởng.
"""
        chunks = self.chunker.chunk_document(markdown_text, self.base_metadata)
        self.assertGreater(len(chunks), 0)

        for c in chunks:
            # Kiểm tra text là chuẩn Unicode NFC
            content = c["content"]
            self.assertEqual(content, unicodedata.normalize('NFC', content))

            # Kiểm tra các từ khóa nghiệp vụ tiếng Việt có dấu được giữ nguyên 100%
            if "Quản Lý Kho" in c["heading_path"]:
                self.assertTrue(
                    any(term in content for term in [
                        "Phiếu xuất kho", "khuyến mãi", "công nợ", "khóa sổ", "sổ quỹ"
                    ])
                )

    # =========================================================================
    # 8. TÀI LIỆU RỖNG
    # =========================================================================
    def test_empty_document(self):
        self.assertEqual(self.chunker.chunk_document(""), [])
        self.assertEqual(self.chunker.chunk_document("   "), [])
        self.assertEqual(self.chunker.chunk_document("\n\n\t  \n"), [])
        self.assertEqual(self.chunker.split_text(""), [])

    # =========================================================================
    # 9. BẢO TOÀN METADATA & TRÍCH XUẤT TRANG
    # =========================================================================
    def test_metadata_preservation_and_citations(self):
        markdown_text = """
# HDSD Thiết Bị Bán Hàng
Tài liệu hướng dẫn kỹ thuật thiết bị bán hàng MasterPro.

## Máy in hóa đơn [cite: 18]
Hướng dẫn thay giấy in và vệ sinh đầu in nhiệt.
<!-- page: 19 -->
"""
        metadata = {
            "document_id": "DOC_MASTER_99",
            "version_id": "v3.0.1",
            "category": "RUNBOOK_L1",
            "module": "HARDWARE",
            "title": "Tài Liệu Phần Cứng POS",
            "source": "MasterPro Internal KB",
            "note": "Tham khảo tài liệu hướng dẫn tại [cite: 18]"
        }

        chunks = self.chunker.chunk_document(markdown_text, metadata)
        self.assertGreater(len(chunks), 0)

        c = chunks[0]
        # Kiểm tra đầy đủ 10 trường bắt buộc
        self.assertEqual(c["document_id"], "DOC_MASTER_99")
        self.assertEqual(c["version_id"], "v3.0.1")
        self.assertEqual(c["category"], "RUNBOOK_L1")
        self.assertEqual(c["module"], "HARDWARE")
        self.assertEqual(c["title"], "Tài Liệu Phần Cứng POS")
        self.assertEqual(c["heading_path"], "HDSD Thiết Bị Bán Hàng")
        self.assertEqual(c["chunk_index"], 1)
        self.assertEqual(c["source"], "MasterPro Internal KB")
        self.assertEqual(c["page"], "18")  # Trích xuất từ citation [cite: 18]
        self.assertIsInstance(c["content"], str)


if __name__ == "__main__":
    unittest.main()
