# MasterPro Copilot — Chiến Lược & Nghiên Cứu Chunking Tài Liệu

## 1. Tổng Quan Kiến Trúc RAG
Quy trình xử lý tri thức tài liệu trong MasterPro Copilot:
```text
Tài liệu nghiệp vụ (PDF/DOCX/MD) 
  ──▶ Tiền xử lý (Cleaning & Parsing)
  ──▶ Chunking (Phân đoạn thông minh)
  ──▶ Metadata Injection (Document, Page, Section, Role)
  ──▶ Embedding Model (text-embedding-3-small / bge-m3)
  ──▶ Vector Database (Qdrant / Milvus / pgvector)
  ──▶ Hybrid Retrieval (Dense Vector + BM25 Fulltext)
  ──▶ Re-ranking (Cross-Encoder / Cohere Rerank)
  ──▶ LLM (Answer Generation with Citations)
```

## 2. Bảng Tham Số Chunking Nghiên Cứu & Benchmark

| Nội dung | Thông số đề xuất (Baseline) | Khoảng thử nghiệm (Benchmark) | Ghi chú kỹ thuật |
| :--- | :--- | :--- | :--- |
| **Chunk Size** | **600 tokens** (~1800 - 2400 ký tự tiếng Việt) | 300 - 1000 tokens | Quá nhỏ (<300): Mất ngữ cảnh quy trình phức tạp. Quá lớn (>1000): Loãng thông tin, tốn context window và tăng chi phí. |
| **Chunk Overlap** | **100 tokens** (~15% chunk size) | 50 - 150 tokens | Giữ tính liên tục giữa các bước trong quy trình xử lý lỗi (troubleshooting steps). |
| **Theo Heading (Markdown / PDF Outline)** | Có (Priority 1) | H1 -> H2 -> H3 | Ngăn chặn việc cắt ngang chừng một section quan trọng (VD: "Bước 1", "Bước 2"). |
| **Theo Paragraph** | Có (Priority 2) | Ký tự xuống dòng kép (`\n\n`) | Giữ toàn vẹn một đoạn văn mô tả trước khi split đệ quy. |
| **Metadata Injection** | Đầy đủ | `doc_name`, `page_number`, `heading_path`, `version`, `role_access`, `created_at` | Giúp lọc trước tìm kiếm (Metadata filtering theo phân quyền người dùng). |
| **Citation Traceability** | Bắt buộc | `chunk_id`, `doc_name`, `page`, `anchor_text` | Cho phép người dùng bấm vào xem trực tiếp trang tài liệu gốc. |
| **Top-K Retrieval** | **4 chunks** | 3 - 7 chunks | Đủ dữ liệu trả lời mà không vượt quá context budget của prompt LLM. |
| **Similarity Threshold** | **Cosine Score ≥ 0.70** | 0.65 - 0.78 | Dưới ngưỡng này: Hệ thống thông báo *"Không tìm thấy thông tin đủ tin cậy trong tài liệu"* thay vì bịa đặt (hallucination). |

## 3. Các Chiến Lược Phân Đoạn (Chunking Strategies)

### 3.1. Recursive Character Chunking
- Chia tài liệu theo thứ tự ưu tiên: Heading (`#`, `##`) ➔ Đoạn văn (`\n\n`) ➔ Câu (`.`, `!`, `?`) ➔ Từ.
- Đảm bảo độ dài không vượt quá `chunk_size` nhưng ưu tiên giữ nguyên khối ngữ nghĩa tự nhiên.

### 3.2. Semantic / Header-based Chunking cho Tài liệu MasterPro
- Các tài liệu MasterPro gồm: Hướng dẫn sử dụng POS, cấu hình thiết bị phần cứng (máy in, máy quét, két tiền), xử lý lỗi bán hàng.
- Quy tắc: Mỗi bước thao tác kèm điều kiện được đóng gói chung một chunk, mang theo heading cha (ví dụ: `[Phần cứng > Máy in hóa đơn > Khắc phục lỗi kẹt giấy]`).

## 4. Cấu Trúc Chunk Chuẩn Trong Hệ Thống
```json
{
  "chunk_id": "doc_printer_v1_c014",
  "content": "Bước 3: Kiểm tra driver máy in. Truy cập Control Panel > Devices and Printers...",
  "metadata": {
    "document": "HDSD_ThietBi_MasterPro_v1.2.pdf",
    "version": "1.2",
    "module": "Hardware_Printer",
    "page": 15,
    "heading_path": "Xử lý lỗi thiết bị > Máy in hóa đơn > Kiểm tra driver",
    "role_access": ["cashier", "admin", "tech_support"]
  }
}
```
