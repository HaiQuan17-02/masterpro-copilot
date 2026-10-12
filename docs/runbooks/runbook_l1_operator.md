# SỔ TAY VẬN HÀNH DÀNH CHO NHÂN VIÊN VẬN HÀNH (RUNBOOK L1 OPERATOR)
**Dự án**: MasterPro Copilot — Trợ lý AI Hỗ trợ Vận hành ERP & Bán lẻ POS  
**Đối tượng áp dụng**: Thu ngân (Cashier), Nhân viên Kho (Inventory), Kế toán viên (Accountant), Quản lý Cửa hàng (Store Manager).  
**Phiên bản**: v1.0.0 — Tuần 12 (Gate 4 Final Handover)  
**Ngày phát hành**: 13/10/2026  

---

## 1. TỔNG QUAN HỆ THỐNG MASTERPRO COPILOT

MasterPro Copilot là trợ lý AI thông minh chuyên sâu cho chuỗi bán lẻ và hệ thống ERP MasterPro. Hệ thống sử dụng công nghệ RAG (Retrieval-Augmented Generation) kết hợp cơ chế **Zero-Hallucination Guardrail**, đảm bảo mọi câu trả lời đều có trích dẫn nguồn văn bản pháp quy, sổ tay quy trình và tài liệu kỹ thuật đã được phê duyệt.

### 1.1. Địa chỉ truy cập
* **Giao diện Web App**: `http://localhost:5173` (hoặc domain nội bộ do IT cấp)
* **API Backend**: `http://127.0.0.1:8000`

### 1.2. Đăng nhập theo Phân quyền Vai trò (RBAC)
Hệ thống áp dụng chính sách bảo mật đa cấp (RBAC), mỗi vai trò chỉ truy cập được tài liệu nghiệp vụ tương ứng:

| Vai trò | Mã định danh | Phạm vi truy cập dữ liệu |
| :--- | :--- | :--- |
| **Thu ngân** | `cashier` | Quy trình thu ngân, xử lý hóa đơn, đổi trả, POS terminal, ca bán hàng. |
| **Thủ kho** | `inventory` | Nhập xuất kho, kiểm kê, chuyển kho, xử lý hàng lỗi/hỏng. |
| **Kế toán** | `accountant` | Hạch toán, báo cáo thuế, chiết khấu, công nợ, đối soát tiền mặt. |
| **Quản trị viên** | `admin` | Toàn quyền truy cập tất cả tài liệu, quản trị vòng đời và cấu hình AI. |

> **Lưu ý**: Khi đăng nhập thử nghiệm, bạn có thể chọn nhanh vai trò từ thanh trạng thái góc trên bên phải giao diện để kiểm tra quyền truy cập.

---

## 2. HƯỚNG DẪN SỬ DỤNG CHAT COPILOT TẠI QUẦY

### 2.1. Đặt câu hỏi tra cứu nghiệp vụ
1. Chọn tab **"Trợ lý Copilot"** trên thanh điều hướng.
2. Nhập câu hỏi rõ ràng, chứa từ khóa nghiệp vụ vào ô chat (Ví dụ: *"Quy trình xử lý hóa đơn khi máy in hết giấy?", "Làm thế nào để đổi trả hàng cho khách trong vòng 7 ngày?"*).
3. Bấm nút **Gửi (Send)** hoặc nhấn phím `Enter`.
4. Câu trả lời sẽ xuất hiện tức thì qua cơ chế Stream từng từ.

### 2.2. Kiểm tra Nguồn trích dẫn (Citation Tags)
* Mỗi câu trả lời của Copilot đều đi kèm các thẻ trích dẫn dạng `[SRC-1]`, `[SRC-2]`, ...
* **Xem toàn văn tài liệu**: Bấm trực tiếp vào thẻ `[SRC-X]`, thanh trượt **Citation Drawer** bên phải màn hình sẽ mở ra, hiển thị:
  * Tiêu đề tài liệu gốc (`title`)
  * Đường dẫn phân mục (`heading_path`)
  * Trích đoạn văn bản chính xác (`matched_text`)
  * Điểm tương đồng dữ liệu (`relevance_score`)

### 2.3. Đánh giá chất lượng câu trả lời
* Bấm biểu tượng **Like (Thích)** nếu câu trả lời chính xác, giúp bạn xử lý công việc nhanh chóng.
* Bấm biểu tượng **Dislike (Chưa đúng)** nếu câu trả lời chưa rõ ràng hoặc không khớp với thực tế tại quầy. Hệ thống sẽ ghi nhận để chuyên viên AI tinh chỉnh tài liệu tri thức.

---

## 3. QUY TRÌNH CHUYỂN TIẾP SỰ CỐ LÊN HỖ TRỢ L2 (ESCALATION)

Khi gặp các sự cố vượt quá thẩm quyền hoặc Copilot cảnh báo không đủ thẩm quyền giải quyết:

### 3.1. Các trường hợp cần tạo Ticket L2
1. Khách hàng khiếu nại tranh chấp hóa đơn phức tạp vượt quá quy chế cửa hàng.
2. Hệ thống POS phát sinh mã lỗi kỹ thuật phần mềm chưa có trong tài liệu quy trình.
3. Két tiền tự động không mở được khi thanh toán hoặc mất đồng bộ số liệu doanh thu.

### 3.2. Thao tác gửi yêu cầu L2 từ Chat
1. Dưới tin nhắn của Copilot, bấm nút **"Chuyển tiếp L2" (Escalate)**.
2. Trên cửa sổ **Yêu cầu hỗ trợ kỹ thuật L2**, điền các thông tin:
   * **Mức độ ưu tiên**: `Low` (Thắc mắc), `Medium` (Nghiệp vụ chậm), `High` (Ảnh hưởng thanh toán), `Critical` (Đình trệ quầy).
   * **Ghi chú hiện trường**: Mô tả chi tiết mã lỗi, mã hóa đơn, thông tin khách hàng.
3. Bấm **"Gửi yêu cầu"**. Hệ thống sẽ trả về mã phiếu hỗ trợ (Ví dụ: `ESC-8F329A`).
4. Nhân viên tiếp tục thông báo cho Kỹ thuật viên L2 hoặc Quản lý ca trực.

---

## 4. XỬ LÝ CÁC TÌNH HUỐNG SỰ CỐ PHỔ BIẾN TẠI QUẦY

### 4.1. Sự cố Mất kết nối Internet (Chế độ Ngoại tuyến)
* **Hiện tượng**: Mạng Internet tại cửa hàng bị gián đoạn, không gọi được các mô hình AI trực tuyến.
* **Cơ chế hoạt động**: MasterPro Copilot được tích hợp bộ điều phối **Hybrid Provider với Circuit Breaker**. Khi mất kết nối mạng, hệ thống **tự động chuyển sang Offline Fallback Rule Engine**.
* **Hành động của thu ngân**: Tiếp tục tra cứu quy trình bình thường. Hệ thống sẽ hiển thị nhãn `[Chế độ Ngoại tuyến - Offline Rule-Based]` và cung cấp đầy đủ các quy trình khẩn cấp từ cơ sở tri thức cục bộ đã tải trước.

### 4.2. Sự cố Máy in Hóa đơn kẹt giấy / Không in
1. Tra cứu trên Copilot: *"Xử lý máy in POS bị kẹt giấy"*.
2. Quy trình xử lý nhanh:
   - Tắt nguồn máy in (công tắc bên hông).
   - Mở nắp khay nhiệt, gỡ phần giấy kẹt, xé phẳng mép giấy.
   - Đặt cuộn giấy nhiệt đúng chiều (mặt cảm nhiệt hướng lên trên).
   - Đóng chặt nắp đến khi nghe tiếng "tách", bật lại nguồn.
   - Trên phần mềm POS, vào mục *Lịch sử hóa đơn* -> chọn hóa đơn gần nhất -> Bấm *In lại (Re-print)*.

### 4.3. Sự cố Khách hàng yêu cầu Đổi trả khác Chi nhánh
1. Kiểm tra điều kiện:
   - Hóa đơn còn trong thời hạn 7 ngày kể từ ngày mua.
   - Hàng hóa còn nguyên tem mác, chưa qua sử dụng.
2. Tra cứu trên Copilot: *"Quy trình đổi trả liên chi nhánh"*.
3. Thực hiện trên POS:
   - Chọn chức năng *Nhập hàng trả lại từ chi nhánh khác*.
   - Nhập số điện thoại khách hàng hoặc quét mã vạch hóa đơn gốc để đồng bộ dữ liệu bảo hành.

---

## 5. ĐƯỜNG DÂY NÓNG HỖ TRỢ
* **Hotline IT Helpdesk MasterPro**: 1900-xxxx (Nhánh 1: POS & Két tiền, Nhánh 2: Mạng & Đường truyền)
* **Kênh Chat Hỗ trợ Nội bộ**: Kênh Telegram / Zalo OA `MasterPro Retail Operations L2`.
