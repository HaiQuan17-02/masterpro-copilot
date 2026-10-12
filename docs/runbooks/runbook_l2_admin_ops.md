# SỔ TAY VẬN HÀNH DÀNH CHO QUẢN TRỊ VIÊN & KỸ THUẬT VIÊN L2 (RUNBOOK L2 ADMIN & OPS)
**Dự án**: MasterPro Copilot — Trợ lý AI Hỗ trợ Vận hành ERP & Bán lẻ POS  
**Đối tượng áp dụng**: Kỹ sư IT Helpdesk L2, Chuyên viên Quản trị Tri thức, DevOps & Quản trị Hệ thống (System Admins).  
**Phiên bản**: v1.0.0 — Tuần 12 (Gate 4 Final Handover)  
**Ngày phát hành**: 13/10/2026  

---

## 1. TỔNG QUAN KIẾN TRÚC KỸ THUẬT

MasterPro Copilot được thiết kế theo mô hình Micro-service module hóa cao, đảm bảo tính sẵn sàng cao (High Availability), bảo mật dữ liệu doanh nghiệp và khả năng hoạt động ngoại tuyến:

```
[ Frontend: React 19 + Vite ] 
          │  (SSE Streaming & JWT RBAC)
          ▼
[ Backend: FastAPI Async Engine ]
  ├── [ Core Security ]: JWT RBAC (Cashier, Inventory, Accountant, Admin)
  ├── [ Knowledge Engine ]: HeadingAwareChunker + Lifecycle State Machine
  ├── [ Retrieval Engine ]: Multilingual E5 + Qdrant Vector Store (Role-filtered)
  └── [ Hybrid AI Provider ]: Online LLM (Gemini/OpenAI) + Circuit Breaker + Offline Fallback
```

---

## 2. QUY TRÌNH TIẾP NHẬN & XỬ LÝ PHIẾU HỖ TRỢ L2 (ESCALATION TICKETS)

### 2.1. Truy cập Bảng điều khiển L2
1. Đăng nhập với quyền `admin` hoặc tài khoản thuộc bộ phận kỹ thuật L2.
2. Trên thanh điều hướng, chọn tab **"Hỗ trợ L2"** (`/admin/escalation`).

### 2.2. Xử lý yêu cầu theo mức độ ưu tiên (SLA)
| Mức độ | Thời gian phản hồi tối đa (SLA) | Loại sự cố |
| :--- | :--- | :--- |
| **Critical** | < 15 phút | Quầy thu ngân ngừng hoạt động toàn diện, két tiền kẹt, lỗi thanh toán hàng loạt. |
| **High** | < 1 giờ | Lỗi tra cứu quy trình ảnh hưởng trực tiếp đến 1 giao dịch khách hàng lớn. |
| **Medium** | < 4 giờ | Câu hỏi nghiệp vụ chưa có tài liệu, cần bổ sung tri thức mới vào hệ thống. |
| **Low** | < 24 giờ | Đề xuất tối ưu giao diện hoặc góp ý văn phong câu trả lời. |

### 2.3. Quy trình Đóng phiếu (Ticket Resolution)
1. Kiểm tra ngữ cảnh chat kèm theo phiếu (câu hỏi của nhân viên, câu trả lời của bot, tài liệu trích dẫn).
2. Nếu do **thiếu tài liệu tri thức**:
   - Soạn thảo tài liệu chuẩn theo định dạng Markdown.
   - Nạp vào hệ thống qua tab **Vòng đời Tri thức** hoặc **Nạp Tri thức**.
3. Cập nhật trạng thái phiếu: `pending` ➔ `in_progress` ➔ `resolved` kèm lời giải thích gửi lại cho điểm bán.

---

## 3. QUẢN TRỊ VÒNG ĐỜI TRI THỨC (KNOWLEDGE LIFECYCLE & VERSIONING)

### 3.1. Vòng đời Tài liệu 5 Trạng thái (Lifecycle State Machine)
Hệ thống quản lý tài liệu chặt chẽ qua 5 trạng thái để đảm bảo dữ liệu luôn được kiểm duyệt trước khi đưa vào tìm kiếm vector:
```
[ DRAFT ] ──(Gửi duyệt)──> [ UNDER_REVIEW ] ──(Admin duyệt)──> [ APPROVED ] (Vectorized)
                                                                    │
                                                        (Có bản v2.0 thay thế)
                                                                    ▼
                                                            [ SUPERSEDED ] (Vector removed)
                                                                    │
                                                              (Lưu trữ cũ)
                                                                    ▼
                                                             [ ARCHIVED ]
```

### 3.2. Cơ chế Thay thế Phiên bản (Superseded & Vector Eviction)
Khi ban hành quy chế hoặc phiên bản quy trình mới (ví dụ `v2.0` thay thế `v1.0`):
1. Khi tạo tài liệu mới, chỉ định trường `supersedes_doc_id` bằng ID của tài liệu cũ.
2. Khi tài liệu mới được duyệt (`approved`), hệ thống tự động:
   - Chuyển tài liệu cũ sang trạng thái `superseded`.
   - Thực thi hàm xóa vector `store.delete_by_document_id(old_doc_id)` trong Qdrant.
   - Băm nhỏ (chunk) và lập chỉ mục các vector của phiên bản mới vào Qdrant.
3. **Kết quả**: Nhân viên quầy không bao giờ bị trả về quy trình cũ đã hết hiệu lực (Zero Outdated Knowledge).

---

## 4. QUẢN LÝ HYBRID AI PROVIDER & BẢO VỆ MẠNG (CIRCUIT BREAKER)

### 4.1. Cấu hình Chế độ Hoạt động (Provider Modes)
Truy cập qua API `/api/v1/provider/mode` hoặc thanh trạng thái Admin:
* `auto` *(Mặc định)*: Ưu tiên Online LLM, nếu gặp lỗi mạng hoặc vượt ngưỡng thời gian chờ sẽ tự động kích hoạt Circuit Breaker và chuyển sang Offline Fallback.
* `online_preferred`: Cố gắng thử lại Online LLM trước khi fallback.
* `offline_only`: Ép hệ thống chạy hoàn toàn ở chế độ nội bộ, không gửi bất kỳ yêu cầu nào ra ngoài Internet (phù hợp cho các chi nhánh bảo mật cách ly).

### 4.2. Khôi phục Circuit Breaker
Khi mạng Internet phục hồi:
* Circuit breaker tự động chuyển sang trạng thái `half-open` sau 60 giây và thử gửi 1 yêu cầu kiểm tra.
* Nếu thành công, hệ thống tự động quay lại trạng thái `online` mà không cần khởi động lại dịch vụ.

---

## 5. SAO LƯU & PHỤC HỒI VECTOR STORE (QDRANT OPERATIONS)

### 5.1. Vị trí lưu trữ dữ liệu
* Thư mục lưu trữ Qdrant cục bộ: `ai/qdrant_storage`
* Collection mặc định: `masterpro_knowledge_base`
* Vector size: 384 dimensions (chuẩn mô hình đa ngữ `intfloat/multilingual-e5-small`).

### 5.2. Lệnh Sao lưu Định kỳ (Backup Routine)
Đối với môi trường chạy tệp cục bộ (Local Storage Mode):
```powershell
# Dừng backend trước khi copy để đảm bảo tính toàn vẹn (hoặc dùng snapshot)
Stop-Service masterpro-backend -ErrorAction SilentlyContinue

# Nén thư mục dữ liệu Qdrant
Compress-Archive -Path "e:\thuc tap\masterpro-copilot\ai\qdrant_storage" -DestinationPath "e:\backups\qdrant_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"

# Khởi động lại backend
Start-Service masterpro-backend -ErrorAction SilentlyContinue
```

Đối với môi trường Docker Qdrant Server:
```bash
# Tạo snapshot qua REST API
curl -X POST "http://localhost:6333/collections/masterpro_knowledge_base/snapshots"
```

### 5.3. Phục hồi Dữ liệu khi lỗi hỏng Index (Reindexing)
Nếu xảy ra sự cố hỏng index vector:
1. Xóa thư mục `ai/qdrant_storage`.
2. Chạy lại script nạp tự động toàn bộ 50+ tài liệu chuẩn:
```powershell
cd "e:\thuc tap\masterpro-copilot"
.\backend\.venv\Scripts\python.exe ai/test_qdrant_ingest.py
```

---

## 6. KIỂM THỬ HIỆU NĂNG & BENCHMARK ĐỊNH KỲ (GATE 3 AUDIT)

Để đảm bảo hệ thống duy trì các chỉ số chất lượng cao nhất:
1. Chạy bài kiểm thử chuẩn 30 câu hỏi Pilot UAT:
```powershell
.\backend\.venv\Scripts\python.exe ai/benchmark_t11_stress_uat.py
```
2. Kiểm tra các chỉ số KPI cam kết:
   * **Groundedness Score**: $\ge 90\%$ (Thực tế đạt: **100%**).
   * **Zero-Hallucination Rate**: $\ge 95\%$ (Thực tế đạt: **100%**).
   * **P95 Latency**: $< 2000$ ms (Thực tế đạt: **1.37 ms**).
   * **Throughput**: $\ge 50$ req/s (Thực tế đạt: **1,193 req/s**).
