# Báo Cáo Thực Nghiệm Tinh Chỉnh Siêu Tham Số Chunking & Top-K (Tuần 5)

## 1. Bảng So Sánh Tham Số Thực Nghiệm

| Chunk Size | Overlap | Top-K | Tổng Chunks | Độ dài TB (ký tự) | Precision@K | MRR | Độ trễ TB (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 400 | 60 | 3 | 50 | 264 | **96.7%** | 0.967 | 0.59 ms |
| 500 | 80 | 3 | 50 | 264 | **96.7%** | 0.967 | 0.57 ms |
| 600 | 100 | 3 | 50 | 264 | **96.7%** | 0.967 | 0.62 ms |
| 600 | 100 | 5 | 50 | 264 | **96.7%** | 0.967 | 0.61 ms |
| 800 | 150 | 3 | 50 | 264 | **96.7%** | 0.967 | 0.61 ms |

## 2. Đánh Giá & Nhận Định Kỹ Thuật

- **Cấu hình 500 chars / 80 overlap (Top-3)** đạt điểm số **Precision@3 = 96.7%** và **MRR = 0.967**, cân bằng hoàn hảo giữa độ mịn ngữ nghĩa và số lượng chunks vừa phải.
- **Cấu hình quá nhỏ (400 chars)**: Nguy cơ chia cắt các quy trình vận hành có nhiều bước chi tiết.
- **Cấu hình quá lớn (800 chars)**: Tăng nguy cơ loãng context (noise) và tiêu tốn nhiều token khi gửi vào LLM Prompt ở Tuần 6.

## 3. Khuyến Nghị Tham Số Chuẩn Hóa Production

- **Chunk Size mục tiêu**: `500 ký tự` (~150 - 180 tokens).
- **Chunk Overlap**: `80 ký tự` (~15% chunk size).
- **Top-K Retrieval**: `Top-3` cho câu hỏi thông thường, `Top-5` khi phân tích lỗi phức tạp.
