import pyodbc
import re

# Database connection
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=.\\MSSQLSERVER04;"
    "DATABASE=MasterDB;"
    "UID=haiquan;"
    "PWD=haiquan123;"
    "TrustServerCertificate=yes;"
)

raw_inserts = """
-- I. NHÓM 50 HƯỚNG DẪN SỬ DỤNG (HDSD)
('HDSD', 'Đăng nhập', 'Đăng nhập vào hệ thống', 'Khởi động phần mềm MasterPro, nhập Tên đăng nhập, Mật khẩu, lựa chọn đúng Chi nhánh làm việc từ danh sách thả xuống rồi nhấn Đăng nhập.', 'Bắt buộc chọn đúng chi nhánh được cấp quyền[cite: 4].'),
('HDSD', 'Hệ thống', 'Cấu hình kết số và khóa sổ', 'Vào mục Thiết lập cửa hàng -> Hệ thống -> chọn Khóa số hoặc Kết số để chốt kỳ dữ liệu và ngăn chặn các thay đổi hóa đơn trong kỳ đã đóng.', 'Chỉ tài khoản admin mới có quyền thực hiện[cite: 5].'),
('HDSD', 'Hệ thống', 'Theo dõi sự kiện hệ thống', 'Truy cập Hệ thống -> Theo dõi sự kiện để tra cứu nhật ký thao tác (log) của các tài khoản trên hệ thống.', 'Dùng để kiểm tra lịch sử thao tác người dùng[cite: 5].'),
('HDSD', 'Hệ thống', 'Thiết lập thông số hệ thống và cấu hình thêm', 'Truy cập Thiết lập cửa hàng -> Hệ thống -> Thiết lập hệ thống / Cấu hình thêm để cấu hình máy in, mẫu in và các tùy chọn chung.', 'Yêu cầu khởi động lại phần mềm sau khi lưu cấu hình[cite: 5].'),

('HDSD', 'Kho hàng', 'Thêm mới danh mục kho hàng', 'Vào Thiết lập cửa hàng -> Danh mục kho hàng -> Nhấn Thêm mới, điền Mã kho (viết liền không dấu), Tên kho, địa chỉ, chọn chi nhánh và Nhóm KH mặc định nếu cần, nhấn Lưu và thoát.', 'Mã kho bắt buộc viết liền không dấu[cite: 6].'),
('HDSD', 'Kho hàng', 'Chỉnh sửa thông tin kho hàng', 'Vào Thiết lập cửa hàng -> Danh mục kho hàng -> Chọn dòng kho cần chỉnh sửa -> Nhấn nút Sửa -> Cập nhật thông tin và nhấn Lưu.', 'Không thể đổi mã kho sau khi đã phát sinh chứng từ[cite: 6, 7].'),
('HDSD', 'Kho hàng', 'Tạo phương thức điều chỉnh kho tăng', 'Vào Kho hàng -> Phương thức điều chỉnh tăng -> Nhấn Thêm mới -> Nhập Mã phương thức, Tên phương thức -> Chọn đối tượng liên quan -> Lưu và thoát.', 'Áp dụng cho nghiệp vụ nhập kiểm kê, nhập khác thừa[cite: 7].'),
('HDSD', 'Kho hàng', 'Tạo phương thức điều chỉnh kho giảm', 'Vào Kho hàng -> Phương thức điều chỉnh giảm -> Thêm mới -> Nhập Mã phương thức, Tên phương thức, tích chọn giảm tồn -> Lưu.', 'Áp dụng khi hủy hàng hỏng, hàng hết date[cite: 8].'),
('HDSD', 'Sổ quỹ', 'Tạo phương thức giảm quỹ (Chi khác)', 'Vào Sổ quỹ -> Phương thức giảm quỹ -> Thêm mới -> Nhập Mã PT, Tên phương thức, tick chọn Cấp con và chọn Đối tượng liên quan (Nhân viên, Khách hàng, NCC) -> Lưu.', 'Phân cấp để dễ thống kê loại chi phí[cite: 8].'),
('HDSD', 'Sổ quỹ', 'Tạo phương thức tăng quỹ (Thu khác)', 'Vào Sổ quỹ -> Phương thức tăng quỹ -> Thêm mới -> Nhập Mã, Tên khoản thu, chọn Cấp con nếu có -> Nhấn Lưu.', 'Dùng để ghi nhận các khoản thu ngoài bán hàng[cite: 9].'),
('HDSD', 'Sổ quỹ', 'Thêm mới tài khoản ngân hàng / thẻ', 'Vào Thiết lập cửa hàng -> Sổ quỹ -> Tài khoản/Thẻ ngân hàng -> Nhấn Thêm mới -> Nhập Số tài khoản, Tên ngân hàng, Số dư đầu kỳ -> Lưu.', 'Số dư đầu kỳ là số tiền dư thực tế trước khi dùng phần mềm[cite: 9].'),
('HDSD', 'Sổ quỹ', 'Cập nhật danh mục tỷ giá tiền tệ', 'Vào Sổ quỹ -> Tiền tệ -> Thêm mới -> Nhập Mã đơn vị, Tên đơn vị tiền tệ, Tỷ giá tham khảo so với VNĐ -> Lưu (F2).', 'Tỷ giá dùng để quy đổi giao dịch ngoại tệ[cite: 10].'),
('HDSD', 'Sổ quỹ', 'Điều chuyển luân chuyển tiền', 'Vào mục Sổ quỹ -> Luân chuyển tiền để thiết lập chuyển quỹ tiền mặt vào tài khoản ngân hàng hoặc luân chuyển giữa các chi nhánh.', 'Cần xác nhận từ cả bên chuyển và bên nhận[cite: 10].'),
('HDSD', 'Sổ quỹ', 'Thiết lập kỳ hạn thanh toán', 'Vào Sổ quỹ -> Kỳ hạn thanh toán -> Thêm mới các quy tắc hạn nợ mặc định cho khách hàng và nhà cung cấp.', 'Phục vụ theo dõi cảnh báo tuổi nợ[cite: 10].'),
('HDSD', 'Cửa hàng', 'Quản lý ngành hàng và nhóm sản phẩm', 'Vào Cửa hàng -> Chọn Ngành hàng hoặc Nhóm sản phẩm -> Nhấn Thêm mới để tạo cây phân cấp sản phẩm theo danh mục.', 'Cần thiết lập trước khi tạo danh mục sản phẩm[cite: 10].'),
('HDSD', 'Cửa hàng', 'Quản lý danh mục nhân viên và chức vụ', 'Vào Cửa hàng -> Chọn Nhân viên, Chức vụ, Nhóm nhân viên -> Khai báo thông tin nhân viên bán hàng, thu ngân, kho.', 'Mỗi nhân viên sẽ được gắn tài khoản đăng nhập tương ứng[cite: 10].'),
('HDSD', 'Cửa hàng', 'Nhập danh mục cơ bản hàng loạt từ Excel', 'Vào Cửa hàng -> Nhập Excel -> Tải file mẫu -> Điền thông tin danh mục nhân viên/nhóm hàng -> Tải file lên và thực hiện map cột.', 'Giúp khởi tạo nhanh dữ liệu cơ bản[cite: 10].'),
('HDSD', 'Tài khoản', 'Tạo tài khoản và nhóm người dùng', 'Vào Tài khoản -> Nhóm người dùng / Tài khoản -> Thêm mới thông tin người dùng, mật khẩu và chi nhánh trực thuộc.', 'Tài khoản phải gắn liền với một nhân viên cụ thể[cite: 10].'),
('HDSD', 'Tài khoản', 'Phân quyền người dùng theo kho và chức năng', 'Vào Tài khoản -> Phân quyền -> Chọn người dùng -> Phân quyền thao tác chi tiết trên từng kho và phân hệ chức năng.', 'Nhân viên chỉ nhìn thấy kho và chức năng được phân quyền[cite: 6, 10].'),

('HDSD', 'Sản phẩm', 'Thêm mới một sản phẩm đơn lẻ', 'Vào mục Sản phẩm -> Thêm 1 sản phẩm mới -> Nhập Mã hàng, Tên hàng, ĐVT, Ngành hàng, Nhóm hàng, Giá nhập, Giá bán -> Nhấn Lưu.', 'Có thể tick chọn Hàng hóa, Dịch vụ hoặc Nguyên liệu[cite: 12].'),
('HDSD', 'Sản phẩm', 'Xem và hiệu chỉnh thông tin sản phẩm', 'Tại danh sách Sản phẩm, nhấp đúp vào sản phẩm hoặc chuột phải chọn Xem/Hiệu chỉnh -> Thay đổi thông tin cần sửa -> Bấm Cập nhật/Lưu.', 'Sản phẩm đã phát sinh giao dịch chỉ được sửa thông tin mô tả[cite: 12].'),
('HDSD', 'Sản phẩm', 'Xóa sản phẩm khỏi danh mục', 'Tại danh sách Sản phẩm -> Chọn sản phẩm cần xóa -> Nhấn nút Xóa phía trên hoặc click chuột phải chọn Xóa.', 'Chỉ áp dụng với sản phẩm chưa từng phát sinh chứng từ[cite: 13].'),
('HDSD', 'Sản phẩm', 'Nhập danh sách sản phẩm hàng loạt từ Excel', 'Vào Sản phẩm -> Nhập Hàng Loạt -> Thêm mới sản phẩm -> Tải file mẫu -> Nhập liệu vào file Excel -> Tải lên -> Map cột dữ liệu tương ứng -> Nhấn Thực hiện.', 'Các cột màu tím trên phần mềm là trường bắt buộc điền[cite: 13, 14].'),
('HDSD', 'Sản phẩm', 'Cập nhật giá bán danh mục từ Excel', 'Vào Sản phẩm -> Nhập Hàng Loạt -> Cập nhật giá -> Chọn file Excel -> Tick ô Cập nhật giá danh mục -> Map cột Giá mua, Giá bán -> Bấm Thực hiện.', 'Chỉ cần nhập thông tin giá mua và giá bán cần thay đổi[cite: 14].'),
('HDSD', 'Sản phẩm', 'Khai báo định mức nguyên liệu thành phẩm', 'Vào Sản phẩm -> Nhập Hàng Loạt -> Nhập thành phẩm -> Tải file Excel có cột Mã thành phẩm, Mã nguyên liệu, Số lượng -> Nhấn Thực hiện.', 'Mã thành phẩm phải được tick là thành phẩm trước trong phần mềm[cite: 15, 16].'),
('HDSD', 'Sản phẩm', 'Cập nhật thuộc tính phụ sản phẩm từ Excel', 'Vào Sản phẩm -> Nhập Hàng Loạt -> Cập nhật sản phẩm -> Tải file chứa các thuộc tính bổ sung (màu sắc, kích cỡ, số trang, vị trí) -> Map cột và Thực hiện.', 'Dùng để bổ sung thuộc tính phụ mà không tạo lại mã[cite: 16, 17].'),
('HDSD', 'Sản phẩm', 'Lọc và theo dõi trạng thái sản phẩm', 'Sử dụng các tab bộ lọc trên màn hình Sản phẩm: Tất Cả, Còn Hàng, Hết Hàng, Đã Bị Khóa để theo dõi nhanh tình trạng danh mục.', 'Giúp theo dõi hàng tồn kho âm hoặc hàng ngưng kinh doanh[cite: 17].'),

('HDSD', 'Khách hàng', 'Thêm mới khách hàng hoặc nhà cung cấp', 'Vào Khách hàng -> Thêm mới -> Nhập Mã, Tên, SĐT, Địa chỉ -> Tick chọn ô Khách hàng hoặc Nhà cung cấp (hoặc cả hai) -> Bấm Lưu.', 'Nếu vừa là KH vừa là NCC thì tick cả hai mục[cite: 18, 19].'),
('HDSD', 'Khách hàng', 'Xem và hiệu chỉnh hồ sơ đối tác', 'Chọn đối tác trong danh sách -> Bấm Sửa hoặc click chuột phải chọn Xem/hiệu chỉnh -> Chỉnh sửa hạn mức nợ, thông tin liên hệ -> Nhấn Sửa đổi và Lưu.', 'Kiểm tra lịch sử giao dịch tại tab Hồ sơ giao dịch[cite: 18].'),
('HDSD', 'Khách hàng', 'Nhập danh sách Khách hàng - NCC từ Excel', 'Vào Khách hàng -> Nhập Hàng Loạt -> Khách hàng-NCC -> Tải file mẫu -> Nhập thông tin, điền TRUE/FALSE cho cột KH và NCC -> Tải file lên và Thực hiện.', 'Cột chữ màu đỏ là bắt buộc nhập liệu[cite: 19].'),
('HDSD', 'Khách hàng', 'Nhập điểm tích lũy đầu kỳ cho khách hàng', 'Vào Khách hàng -> Nhập Hàng Loạt -> Nhập điểm đầu kỳ -> Chọn file Excel chứa mã KH và số điểm đầu kỳ -> Map cột -> Bấm Thực hiện.', 'Điểm đầu kỳ sẽ cộng dồn trực tiếp vào điểm hiện có[cite: 19, 20].'),
('HDSD', 'Khách hàng', 'Nhập số dư công nợ đầu kỳ đối tác', 'Vào Khách hàng -> Nhập Hàng Loạt -> Công nợ đầu kỳ -> Nhập trực tiếp số tiền phải thu/phải trả vào lưới hoặc tải qua file Excel -> Bấm Cập nhật.', 'Cần đối chiếu sổ sách kế toán trước khi chốt nợ đầu kỳ[cite: 20, 21].'),

('HDSD', 'Mua hàng', 'Tạo đơn đặt mua hàng từ nhà cung cấp', 'Vào Mua hàng -> Tab Đơn Đặt -> Thêm đơn đặt -> Chọn NCC, Kho nhập, Nhân viên, chọn sản phẩm, số lượng và giá -> Bấm Lưu (F2).', 'Đơn đặt hàng chưa làm thay đổi tồn kho thực tế[cite: 22, 23].'),
('HDSD', 'Mua hàng', 'Duyệt đơn đặt mua hàng', 'Tại tab Đơn Đặt -> Chọn đơn hàng cần duyệt -> Click chuột phải -> Cập nhật trạng thái -> Chọn Duyệt.', 'Đơn phải ở trạng thái Duyệt mới chuyển thành đơn nhập được[cite: 23].'),
('HDSD', 'Mua hàng', 'Chuyển đơn đặt hàng thành phiếu nhập kho', 'Tại tab Đơn Đặt -> Click chuột phải vào đơn đã duyệt -> Chọn Chuyển thành phiếu nhập hàng -> Kiểm tra lại số lượng thực giao -> Lưu lại.', 'Hệ thống tự động trừ lùi đơn đặt hàng[cite: 23].'),
('HDSD', 'Mua hàng', 'Tạo trực tiếp phiếu nhập kho mua hàng', 'Vào Mua hàng -> Tab Đơn Nhập -> Thêm đơn nhập hàng -> Điền NCC, Kho nhận, danh sách hàng -> Chọn hình thức thanh toán (Tiền mặt/Thanh toán trước/Công nợ) -> Bấm Lưu.', 'Tồn kho và công nợ NCC sẽ tăng ngay khi lưu[cite: 24, 25].'),
('HDSD', 'Mua hàng', 'Xuất trả hàng cho nhà cung cấp theo chứng từ', 'Vào Mua hàng -> Tab Trả Hàng -> Thêm đơn xuất trả -> Chọn NCC, Kho xuất -> Tick chọn ô Chứng từ và chọn đúng số hóa đơn nhập -> Xóa các mặt hàng không trả -> Nhấn Lưu.', 'Công nợ và tồn kho sẽ được giảm tương ứng[cite: 25, 26].'),

('HDSD', 'Bán hàng', 'Tạo đơn đặt hàng của khách (Báo giá)', 'Vào Bán hàng -> Tab Đơn Đặt -> Thêm đơn đặt -> Chọn Khách hàng, Kho bán, sản phẩm -> Nhập tiền đặt cọc nếu có -> Nhấn Lưu.', 'Tiền đặt cọc sẽ được ghi nhận vào quỹ tiền gối đầu[cite: 27, 28].'),
('HDSD', 'Bán hàng', 'Tạo phiếu bán lẻ tại quầy', 'Vào Bán hàng -> Thêm đơn bán lẻ (hoặc bấm icon máy tính) -> Chọn nhân viên bán, kho bán -> Quét mã vạch sản phẩm, nhập số lượng, giảm giá -> Bấm Lưu và in (F4).', 'Giao diện chuyên dùng cho thu ngân bán lẻ[cite: 29, 30].'),
('HDSD', 'Bán hàng', 'Tạo phiếu bán buôn (Hóa đơn xuất bán)', 'Vào Bán hàng -> Tab Đơn Bán -> Thêm đơn bán buôn -> Chọn Khách hàng, Kho hàng, gõ mã hàng hoặc chọn từ bảng -> Chọn phương thức thanh toán -> Bấm Lưu (F2).', 'Dùng cho xuất buôn số lượng lớn và theo dõi công nợ[cite: 29, 31].'),
('HDSD', 'Bán hàng', 'Nhận hàng trả lại từ khách theo hóa đơn', 'Vào Bán hàng -> Tab Trả Hàng -> Thêm đơn trả -> Chọn Khách hàng -> Nhập mã chứng từ xuất bán cũ -> Chọn sản phẩm trả -> Chọn hoàn tiền mặt hoặc cấn trừ công nợ -> Lưu.', 'Hàng hóa tự động quay trở lại tồn kho[cite: 31, 32].'),

('HDSD', 'Marketing', 'Thiết lập bảng giá riêng theo sản phẩm', 'Vào Kênh Marketing -> Bảng Giá Sản Phẩm -> Thêm mới -> Đặt tên bảng giá, tick Hiệu lực -> Thiết lập tỷ lệ chiết khấu công thức hoặc nhập trực tiếp -> Thêm đối tượng nhóm KH áp dụng -> Lưu.', 'Mỗi nhóm KH chỉ được gán cho 1 bảng giá duy nhất[cite: 33, 34].'),
('HDSD', 'Marketing', 'Thiết lập bảng giá chung theo nhóm hàng', 'Vào Kênh Marketing -> Bảng Giá Nhóm Sản Phẩm -> Thêm mới -> Tick chọn các nhóm hàng -> Điền tỷ lệ % hoặc giá áp dụng chung -> Gán nhóm khách hàng -> Lưu.', 'Áp dụng giảm đồng loạt cho toàn bộ nhóm hàng[cite: 35].'),
('HDSD', 'Marketing', 'Cài đặt KM 01: Mua hàng chiết khấu/tặng chính hàng đó', 'Vào Kênh Marketing -> Chương Trình Khuyến Mãi -> Thêm mới -> Chọn loại 01 -> Nhập khoảng SL Min-Max, % CK hoặc SL tặng -> Gán nhóm KH -> Lưu (F2).', 'Áp dụng dạng mua 10 tặng 1 hoặc chiết khấu trên số lượng[cite: 36, 37].'),
('HDSD', 'Marketing', 'Cài đặt KM 02: Tặng tiền, % theo giá trị hóa đơn', 'Vào Chương Trình Khuyến Mãi -> Thêm mới -> Chọn loại 02 -> Nhập khoảng Tiền từ... Tiền đến... và mức tiền giảm/ % giảm tương ứng -> Gán đối tượng áp dụng -> Lưu.', 'Áp dụng giảm giá hóa đơn khi đạt giá trị thanh toán[cite: 39, 40].'),
('HDSD', 'Marketing', 'Cài đặt KM 03: Mua hàng này tặng hàng khác', 'Vào Chương Trình Khuyến Mãi -> Chọn loại 03 -> Thêm sản phẩm mua (tick SP mua) và sản phẩm tặng kèm (bỏ tick SP mua) -> Điền chung mã Nhóm CK -> Gán nhóm KH -> Lưu.', 'Bắt buộc sản phẩm mua và tặng phải chung mã Nhóm CK[cite: 40, 41].'),
('HDSD', 'Marketing', 'Cài đặt KM 04: Tặng sản phẩm theo giá trị đơn hàng', 'Vào Chương Trình Khuyến Mãi -> Chọn loại 04 -> Thêm sản phẩm tặng, nhập số lượng tặng, điền khoảng Tiền Min và Tiền Max của hóa đơn -> Gán nhóm KH -> Lưu.', 'Khách mua hóa đơn đạt mức tiền sẽ được tặng hiện vật[cite: 42].'),
('HDSD', 'Marketing', 'Cài đặt KM 06: Mua theo nhóm sản phẩm nhận quà/giảm giá', 'Vào Chương Trình Khuyến Mãi -> Chọn loại 06 -> Thiết lập các mặt hàng thuộc nhóm, cài đặt số lượng mua bắt buộc và số tiền giảm -> Gán nhóm KH -> Lưu.', 'Yêu cầu giỏ hàng phải mua đủ số lượng quy định trong nhóm[cite: 43, 44].'),

('HDSD', 'Kho hàng', 'Nhập số tồn kho đầu kỳ', 'Vào Kho hàng -> Tồn Đầu -> Chọn kho hàng -> Nhập trực tiếp số lượng đầu kỳ vào danh sách hoặc bấm Cập nhật từ Excel -> Nhấn Cập nhật.', 'Chỉ cập nhật số dư đầu kỳ khi mới thiết lập hệ thống[cite: 45, 46].'),
('HDSD', 'Kho hàng', 'Xuất/Nhập điều chỉnh kho thủ công', 'Vào Kho hàng -> Chọn Điều Chỉnh Tăng hoặc Điều Chỉnh Giảm -> Nhấn Thêm mới -> Chọn kho, chọn lý do điều chỉnh, nhập hàng hóa số lượng -> Nhấn Lưu.', 'Dùng để cân đối tồn mà không sinh doanh thu hay công nợ[cite: 46, 47].'),

-- II. NHÓM 30 CÂU HỎI THƯỜNG GẶP (FAQ)
('FAQ', 'Hệ thống', 'Tôi có thể đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc không?', 'Không. Khi đăng nhập bạn bắt buộc phải chọn cố định 1 chi nhánh làm việc trong phiên đăng nhập để phần mềm quản lý sổ sách chính xác.', 'Phải đăng xuất ra để chuyển sang chi nhánh khác[cite: 4].'),
('FAQ', 'Kho hàng', 'Quy tắc đặt Mã kho hàng mới trên phần mềm như thế nào?', 'Mã kho hàng bắt buộc phải viết liền không dấu, không chứa ký tự đặc biệt hay dấu cách.', 'Sai định dạng sẽ phát sinh lỗi khi đồng bộ dữ liệu[cite: 6].'),
('FAQ', 'Kho hàng', 'Kho hàng đã phát sinh hóa đơn bán hoặc nhập có xóa được không?', 'Tuyệt đối không được phép xóa kho đã có phát sinh giao dịch. Chỉ những kho chưa có bất kỳ giao dịch nào mới được nhấn nút Xóa.', 'Để bảo toàn tính toàn vẹn dữ liệu kế toán và kho[cite: 7].'),
('FAQ', 'Kho hàng', 'Xóa phương thức điều chỉnh kho có ảnh hưởng gì không?', 'Hệ thống chỉ cho phép xóa những phương thức điều chỉnh tăng/giảm chưa từng được sử dụng trên bất kỳ phiếu nhập/xuất kho nào.', 'Không xóa được phương thức đã có chứng từ[cite: 7, 8].'),
('FAQ', 'Sổ quỹ', 'Có xóa được tài khoản ngân hàng hoặc phương thức thu chi đã dùng không?', 'Chỉ được phép xóa tài khoản ngân hàng hoặc phương thức thu/chi khi chưa từng phát sinh bất kỳ phiếu thu, chi hay luân chuyển tiền nào.', 'Tránh lỗi sai lệch tổng phát sinh sổ quỹ[cite: 8, 9, 10].'),
('FAQ', 'Sổ quỹ', 'Chỉ số Đầu kỳ trong khai báo Tài khoản ngân hàng có ý nghĩa gì?', 'Đó là số dư tiền thực tế còn lại trong tài khoản ngân hàng tại thời điểm trước khi bắt đầu vận hành phần mềm MasterPro.', 'Dùng để khớp sổ dư thực tế với sổ quỹ phần mềm[cite: 9].'),
('FAQ', 'Sản phẩm', 'Điều kiện để xóa vĩnh viễn một sản phẩm khỏi danh mục là gì?', 'Người dùng chỉ có thể xóa các sản phẩm chưa có bất kỳ giao dịch nào (nhập, bán, kiểm kê). Sản phẩm đã có giao dịch chỉ có thể chuyển sang trạng thái Đã Bị Khóa.', 'Không xóa sản phẩm đã có giao dịch phát sinh[cite: 13].'),
('FAQ', 'Sản phẩm', 'Khi import sản phẩm từ Excel, các cột màu nào là bắt buộc?', 'Khi import Excel trên MasterPro, các cột có tiêu đề hiển thị màu tím/đỏ là các cột dữ liệu bắt buộc phải có thông tin, không được để trống.', 'Thiếu các cột bắt buộc file sẽ báo lỗi import[cite: 13, 14, 19].'),
('FAQ', 'Sản phẩm', 'Muốn vừa cập nhật giá nhập vừa cập nhật giá bán từ Excel thì làm thế nào?', 'Vào Nhập hàng loạt -> Cập nhật giá -> Tick chọn ô Cập nhật giá danh mục/bảng giá, sau đó map cột tương ứng với Giá mua và Giá bán trên file Excel.', 'Bỏ chọn ô này nếu chỉ cập nhật cho bảng giá riêng[cite: 14].'),
('FAQ', 'Sản phẩm', 'Tại sao không import được định mức thành phẩm từ Excel?', 'Cột Mã thành phẩm trong file Excel bắt buộc phải là mã của sản phẩm đã được tick chọn thuộc tính Thành phẩm trong thông tin chi tiết trước đó.', 'Kiểm tra thuộc tính hàng hóa trước khi tạo BOM[cite: 15, 16].'),
('FAQ', 'Khách hàng', 'Làm sao để một đối tác vừa là khách mua hàng vừa là nhà cung ứng?', 'Khi tạo mới đối tác hoặc nhập Excel, tick chọn đồng thời cả 2 ô Khách hàng và Nhà cung cấp (trên Excel điền TRUE cho cả 2 cột).', 'Hệ thống sẽ theo dõi song song cả 2 sổ công nợ[cite: 18, 19].'),
('FAQ', 'Khách hàng', 'Sau khi import điểm đầu kỳ, điểm của khách hàng sẽ được tính thế nào?', 'Điểm tích lũy hiện tại của khách sẽ bằng: Điểm đầu kỳ vừa import + Số điểm hiện tại khách hàng đang có trước khi nhập.', 'Cộng dồn điểm lũy kế[cite: 20].'),
('FAQ', 'Mua hàng', 'Đơn đặt hàng nhà cung cấp (PO) có làm tăng tồn kho ngay không?', 'Không. Đơn đặt hàng chỉ là dự kiến, tồn kho chỉ thực sự tăng khi đơn đặt được duyệt và chuyển đổi thành Phiếu nhập hàng thành công.', 'Đơn đặt hàng không hạch toán số dư kho[cite: 23, 24].'),
('FAQ', 'Mua hàng', 'Tiền thanh toán trước cho nhà cung cấp vượt quá tiền đơn hàng sẽ đi đâu?', 'Phần mềm sẽ cảnh báo và số tiền thừa vượt quá giá trị đơn hàng nhập sẽ được tự động chuyển vào Quỹ tiền gối đầu của nhà cung cấp đó.', 'Tiền gối đầu dùng cấn trừ cho các đơn nhập kế tiếp[cite: 25].'),
('FAQ', 'Mua hàng', 'Muốn sửa hoặc xóa phiếu nhập hàng đã chi tiền thì làm thế nào?', 'Bạn phải sang phân hệ Sổ quỹ tìm và xóa phiếu chi tương ứng trước, sau đó mới quay lại phân hệ Mua hàng để sửa hoặc xóa phiếu nhập.', 'Bắt buộc xóa phiếu chi trước khi can thiệp đơn nhập[cite: 25].'),
('FAQ', 'Bán hàng', 'Khách hàng đặt cọc khi đặt mua hàng được ghi nhận vào đâu?', 'Khoản tiền đặt cọc (bằng tiền mặt hoặc chuyển khoản) sẽ được ghi nhận vào Tiền gối đầu của khách hàng để bù trừ khi xuất hóa đơn bán thức tế.', 'Tiền cọc hạch toán vào ví tiền gối đầu[cite: 27, 28].'),
('FAQ', 'Bán hàng', 'Đơn đặt bán hàng có thể chuyển thành các loại chứng từ nào?', 'Sau khi Cập nhật trạng thái sang Duyệt, đơn đặt có thể chuyển thành: Phiếu xuất hàng (Bán buôn) hoặc Phiếu bán lẻ.', 'Tùy đối tượng khách để chọn loại hóa đơn xuất[cite: 28, 29].'),
('FAQ', 'Bán hàng', 'Làm sao mở các tính năng mở rộng (nhập số lượng trước, quét mã...) tại màn hình bán lẻ?', 'Click vào biểu tượng 2 mũi tên nhỏ ở góc phải màn hình bán lẻ để mở rộng thanh tính năng nâng cao.', 'Cho phép cấu hình nhanh chế độ bán hàng[cite: 30].'),
('FAQ', 'Bán hàng', 'Nhập điểm đổi cho khách hàng tại ô Đổi điểm trên màn hình bán lẻ như thế nào?', 'Nhập số điểm cần tiêu vào ô Đổi điểm rồi nhấn Enter trên bàn phím, hệ thống sẽ tự động trừ điểm và quy đổi thành số tiền giảm giá tương ứng.', 'Tỷ lệ quy đổi cấu hình trong danh mục thẻ tích điểm[cite: 30].'),
('FAQ', 'Bán hàng', 'Khi khách trả hàng, làm thế nào để cấn trừ vào công nợ mà không trả tiền mặt?', 'Trên phiếu Đơn nhập hàng trả, bỏ tick ở ô Phát sinh thanh toán / Bù trừ theo công nợ. Đơn hàng sẽ tự động ghi giảm nợ cho khách.', 'Tick vào ô này nếu chi tiền mặt hoặc chuyển khoản trả lại[cite: 32].'),
('FAQ', 'Marketing', 'Một nhóm Khách hàng có thể được áp dụng cùng lúc nhiều bảng giá không?', 'Không. Một nhóm KH-NCC chỉ được phép gán vào một bảng giá sản phẩm duy nhất (hoặc một bảng giá nhóm sản phẩm duy nhất).', 'Ràng buộc để tránh xung đột đơn giá bán[cite: 34, 35].'),
('FAQ', 'Marketing', 'Khi tạo bảng giá riêng, cột Chọn trong file Excel import phải điền gì?', 'Cột đầu tiên (cột Chọn) trên file Excel bắt buộc phải điền giá trị TRUE thì phần mềm mới nhận diện và tick chọn các sản phẩm đó vào bảng giá.', 'Nếu để FALSE hoặc trống sẽ không import được[cite: 33, 34].'),
('FAQ', 'Marketing', 'Tại sao trên hóa đơn bán không tự động nhảy chương trình khuyến mãi?', 'Nhân viên bán hàng cần nhấn phím F10 (hoặc click nút Kiểm tra CK-KM), tick chọn chương trình muốn áp dụng rồi nhấn Đồng ý thì giá mới được chiết khấu.', 'Hệ thống yêu cầu xác nhận kiểm tra khuyến mãi chủ động[cite: 38, 39].'),
('FAQ', 'Marketing', 'Chương trình KM 03 (Hàng tặng hàng khác) yêu cầu cấu hình quan trọng nào?', 'Sản phẩm bán và sản phẩm tặng kèm bắt buộc phải nhập cùng một tên vào ô Nhóm CK để phần mềm hiểu chúng nằm trong một cặp khuyến mãi.', 'Sai lệch nhóm CK sẽ không tặng được hàng[cite: 41].'),
('FAQ', 'Kho hàng', 'Tồn đầu kỳ được cập nhật lại thì tồn kho hiện tại thay đổi thế nào?', 'Số hàng tồn hiện tại của sản phẩm sẽ bằng: Số lượng tồn đầu vừa cập nhật + Số lượng hàng biến động trước thời điểm cập nhật.', 'Hệ thống tự động cộng dồn số tồn[cite: 46].'),
('FAQ', 'Kho hàng', 'Quy định tần suất kiểm kê thông thường của mỗi kho hàng là bao nhiêu?', 'Với tính năng Kiểm kê thông thường, mỗi kho hàng chỉ được phép tạo phiếu kiểm kê 1 lần duy nhất trong ngày.', 'Muốn kiểm nhiều lần phải dùng Kiểm kê liên tục[cite: 48, 52].'),
('FAQ', 'Kho hàng', 'Hàng chuyển kho giữa các chi nhánh khi nào mới chính thức ghi tăng kho nhận?', 'Hàng hóa chỉ chính thức tăng tồn ở kho nhận khi phiếu chuyển kho được cập nhật trạng thái về Đã nhận hoặc Đã nhận có kiểm tra.', 'Trạng thái Đang chuyển chỉ ghi giảm kho xuất[cite: 48].'),
('FAQ', 'Kho hàng', 'Khi nào hệ thống sinh ra 2 phiếu Điều chỉnh tăng và Điều chỉnh giảm sau kiểm kê?', 'Sau khi lưu kỳ kiểm kho, vào mục Kiểm kê: những mã có tồn thực tế nhỏ hơn tồn sổ sách sẽ vào phiếu Giảm, mã lớn hơn sẽ vào phiếu Tăng.', 'Phải nhấn Lưu 2 phiếu này để cân bằng kho[cite: 51, 52].'),
('FAQ', 'Số quỹ', 'Phiếu thu công nợ khách hàng có hỗ trợ khấu trừ hóa đơn cũ không?', 'Có. Phần mềm hỗ trợ hạch toán tự động trừ lùi các hóa đơn nợ cũ nhất trước, hoặc người dùng có thể tự tay chọn đích danh số chứng từ cần thanh toán.', 'Giúp kiểm soát chi tiết công nợ từng hóa đơn[cite: 53].'),
('FAQ', 'Số quỹ', 'Chế độ Hạch toán bằng tay và Hạch toán tự động trên phiếu chi khác nhau thế nào?', 'Hạch toán tự động sẽ phân bổ tiền chi cho các hóa đơn nợ từ xa đến gần; Hạch toán bằng tay cho phép kế toán gõ số tiền thanh toán vào đúng chứng từ mong muốn.', 'Sử dụng linh hoạt khi thanh toán công nợ NCC[cite: 53].'),

-- III. NHÓM 20 RUNBOOK VẬN HÀNH CẤP 1 (RUNBOOK L1)
('RUNBOOK_L1', 'Đăng nhập', 'Sự cố không đăng nhập được phần mềm hoặc sai chi nhánh', '1. Kiểm tra lại kết nối mạng LAN/Internet đến máy chủ. 2. Nhập chính xác Username/Password (chú ý phím CapsLock). 3. Nhấp vào mục Thông tin kết nối để kiểm tra IP máy chủ. 4. Chọn đúng Chi nhánh được cấp quyền. 5. Bấm Đăng nhập.', 'Nếu vẫn lỗi liên hệ Hotline kỹ thuật 1900.2929.51[cite: 1, 4].'),
('RUNBOOK_L1', 'Kho hàng', 'Quy trình khởi tạo nhanh một kho hàng mới và cấp quyền sử dụng', '1. Vào Thiết lập cửa hàng -> Danh mục kho hàng -> Thêm mới, nhập Mã kho (viết liền), Tên kho -> Lưu và thoát. 2. Vào mục Hệ thống/Tài khoản -> Phân quyền -> Chọn User -> Tick chọn quyền được thao tác trên kho mới tạo -> Lưu.', 'Bắt buộc phân quyền thì User mới thấy kho để thao tác[cite: 6].'),
('RUNBOOK_L1', 'Sản phẩm', 'Quy trình import bảng giá mới áp dụng từ đầu tháng', '1. Vào Bảng Giá Sản Phẩm -> Thêm mới -> Điền tên mức giá, tick Hiệu lực. 2. Click phải chọn Xuất ra Excel để lấy file chuẩn. 3. Nhập giá điều chỉnh trên file Excel, đảm bảo cột Chọn để giá trị TRUE. 4. Click phải vào danh sách -> Nhập từ Excel -> Chọn file và map cột -> Bấm Thực hiện -> Lưu.', 'Phải kiểm tra kỹ cột Chọn là TRUE trước khi tải lên[cite: 33, 34].'),
('RUNBOOK_L1', 'Sản phẩm', 'Xử lý lỗi import Excel báo sai định dạng hoặc thiếu cột', '1. Nhấn nút Mở file mẫu trên cửa sổ import để tải mẫu chuẩn từ hệ thống. 2. Copy dữ liệu tương ứng dán dưới dạng Value (Paste Special Values) vào file mẫu. 3. Đảm bảo các cột tô màu tím/đỏ được điền đầy đủ dữ liệu. 4. Tắt file Excel trước khi bấm Chọn file và thực hiện import lại.', 'Không tự ý thay đổi tên dòng tiêu đề trên file mẫu[cite: 13, 14, 19].'),
('RUNBOOK_L1', 'Khách hàng', 'Quy trình khởi tạo dữ liệu công nợ đầu kỳ khi golive phần mềm', '1. Chốt công nợ đối soát trên sổ sách cũ. 2. Vào Khách hàng -> Nhập Hàng Loạt -> Công nợ đầu kỳ. 3. Tải file Excel mẫu hoặc nhập trực tiếp số tiền phải thu/phải trả vào lưới. 4. Nhấn Cập nhật để hệ thống ghi nhận số dư ban đầu.', 'Sau khi chốt không sửa trực tiếp mà phải dùng phiếu điều chỉnh[cite: 20, 21].'),
('RUNBOOK_L1', 'Mua hàng', 'Quy trình duyệt đơn đặt hàng nhập và chuyển thành phiếu nhập kho', '1. Vào Mua hàng -> Đơn Đặt -> Tìm đơn cần duyệt. 2. Click chuột phải chọn Cập nhật trạng thái -> Duyệt. 3. Click chuột phải lần nữa chọn Chuyển thành phiếu nhập hàng. 4. Kiểm tra số lượng và giá trên phiếu nhập, chọn hình thức thanh toán -> Bấm Lưu và đóng.', 'Đơn nhập hàng sẽ lập tức làm tăng tồn kho thực tế[cite: 23, 24, 25].'),
('RUNBOOK_L1', 'Mua hàng', 'Quy trình xuất trả hàng cho Nhà cung cấp bị lỗi/hỏng', '1. Vào Mua hàng -> Tab Trả Hàng -> Nhấn Thêm đơn xuất trả. 2. Chọn Kho xuất và Nhà cung cấp nhận lại hàng. 3. Tick chọn ô Chứng từ, chọn số hóa đơn nhập tương ứng. 4. Giữ lại mã hàng cần trả, chọn các mặt hàng khác bấm nút Delete trên bàn phím để xóa khỏi đơn. 5. Bấm Lưu và đóng.', 'Công nợ NCC sẽ tự động bù trừ giảm tương ứng[cite: 25, 26].'),
('RUNBOOK_L1', 'Bán hàng', 'Quy trình thu ngân xử lý hóa đơn bán lẻ có đổi điểm tích lũy', '1. Nhập SĐT hoặc Mã khách hàng để gọi thông tin khách. 2. Quét mã vạch các mặt hàng khách mua. 3. Xem số điểm hiện có tại ô Điểm, hỏi ý kiến khách và gõ số điểm cần đổi vào ô Đổi điểm -> Bấm Enter. 4. Nhập tiền khách đưa tại ô Khách Đưa (F3) -> Nhấn Lưu và in (F4).', 'Phần mềm tự trừ điểm và tính tiền giảm giá cho khách[cite: 30].'),
('RUNBOOK_L1', 'Bán hàng', 'Quy trình xử lý hóa đơn bán lẻ nhận đặt cọc giao hàng sau', '1. Vào Bán hàng -> Đơn Đặt -> Thêm đơn đặt. 2. Chọn Khách hàng, chọn sản phẩm đặt mua. 3. Tại mục Đặt cọc: tick chọn Tiền mặt hoặc Chuyển khoản, nhập số tiền cọc khách gửi. 4. Bấm Lưu (F2). Tiền cọc tự động lưu vào ví tiền gối đầu của khách.', 'Khi xuất hàng thực tế sẽ trừ dần vào tiền cọc[cite: 27, 28].'),
('RUNBOOK_L1', 'Bán hàng', 'Quy trình xử lý khách trả lại hàng đã mua bằng hóa đơn bán lẻ', '1. Vào Bán hàng -> Tab Trả Hàng -> Bấm Thêm đơn trả. 2. Chọn đúng tên Khách hàng. 3. Nhập số hóa đơn bán lẻ cũ vào ô Mã chứng từ và nhấn Enter. 4. Xóa các sản phẩm khách không trả bằng phím Delete. 5. Tick chọn Phát sinh thanh toán nếu hoàn tiền mặt ngay, hoặc bỏ tick để bù trừ vào công nợ -> Bấm Lưu.', 'Tồn kho được hoàn trả tự động ngay khi lưu đơn[cite: 31, 32].'),
('RUNBOOK_L1', 'Marketing', 'Quy trình áp dụng khuyến mãi Mua hàng tặng hàng kèm (KM 03)', '1. Vào Kênh Marketing -> Tạo KM loại 03, gắn chung Nhóm CK cho SP mua và SP tặng -> Gán nhóm khách -> Lưu. 2. Mở màn hình bán hàng, chọn khách thuộc diện khuyến mãi, chọn sản phẩm mua với số lượng đủ điều kiện. 3. Bấm F10 (Kiểm tra CK-KM) -> Tick chọn chương trình -> Bấm Đồng ý -> Kiểm tra sản phẩm tặng xuất hiện trên lưới -> Bấm Lưu.', 'Phải nhấn Đồng ý tại F10 thì quà tặng mới vào hóa đơn[cite: 41, 42].'),
('RUNBOOK_L1', 'Marketing', 'Khắc phục sự cố đơn hàng không hiển thị chiết khấu chương trình KM', '1. Kiểm tra lại thời gian áp dụng của chương trình KM có hiệu lực trong ngày không. 2. Kiểm tra nhóm đối tượng KH trên hóa đơn có nằm trong danh sách áp dụng không. 3. Kiểm tra số lượng sản phẩm trên đơn có đạt SL Min hoặc Tiền Min không. 4. Nhấn phím F10 trên màn hình bán hàng để kích hoạt chọn lại chương trình.', 'Nếu thiếu điều kiện phần mềm sẽ từ chối áp dụng[cite: 36, 38, 39].'),
('RUNBOOK_L1', 'Kho hàng', 'Quy trình điều chuyển kho liên chi nhánh chuẩn 4 bước', '1. Tại kho xuất: Tạo phiếu Chuyển kho, chọn kho đi/kho đến, chọn hàng hóa -> Bấm Lưu. 2. Click phải chọn Trạng thái -> 1. Đã duyệt. 3. Tiếp tục click phải chọn Trạng thái -> 2. Đang chuyển hàng (xác nhận ngày gửi). 4. Tại kho đích: Kiểm đếm thực tế, click phải chọn Trạng thái -> 3. Đã nhận hoặc Đã nhận có kiểm tra để ghi tăng tồn kho.', 'Hàng chưa tới nơi tuyệt đối không bấm Đã nhận[cite: 48].'),
('RUNBOOK_L1', 'Kho hàng', 'Quy trình kiểm kê kho định kỳ cuối ngày bằng file Excel', '1. Vào Kho hàng -> Kiểm kê -> Thêm kỳ kiểm kê, chọn kho hàng cần kiểm. 2. Click phải chọn Xuất ra Excel danh sách hàng hóa. 3. Nhập số lượng thực tế đếm được vào cột Hàng tồn thực tế, điền TRUE vào cột Chọn. 4. Trên phần mềm bấm Nhập từ file -> Chọn file vừa làm. 5. Bấm Lưu và thoát (F4).', 'Mỗi ngày chỉ kiểm kê định kỳ thường được 1 lần/kho[cite: 48, 50, 51].'),
('RUNBOOK_L1', 'Kho hàng', 'Cân đối chênh lệch thừa thiếu sau khi lập phiếu kiểm kho', '1. Sau khi lưu phiếu kiểm kê, quay lại danh sách Kiểm kê. 2. Bấm vào nút màu xanh Điều chỉnh tăng để kiểm tra các mã thừa -> Bấm Lưu. 3. Tiếp tục bấm nút Điều chỉnh giảm để kiểm tra các mã thiếu -> Bấm Lưu. 4. Kiểm tra lại thẻ kho để đảm bảo tồn thực tế đã khớp với phần mềm.', 'Bắt buộc lưu cả 2 phiếu tăng và giảm để cân bằng[cite: 51, 52].'),
('RUNBOOK_L1', 'Kho hàng', 'Xử lý xuất hủy hàng hóa hết hạn sử dụng (Date)', '1. Vào Thiết lập cửa hàng -> Kho hàng -> Phương thức điều chỉnh giảm -> Đảm bảo đã có phương thức Xuất hủy hết date. 2. Vào Kho hàng -> Điều Chỉnh Giảm -> Bấm Thêm mới. 3. Chọn kho chứa hàng hỏng, chọn đúng phương thức Xuất hủy hết date. 4. Chọn các mã hàng, nhập số lượng hủy -> Nhấn Lưu.', 'Nghiệp vụ này giảm kho nhưng không tính vào doanh thu[cite: 8, 46, 47].'),
('RUNBOOK_L1', 'Số quỹ', 'Quy trình thu tiền nợ khách hàng và hạch toán trừ chứng từ', '1. Vào Sổ quỹ -> Thu -> Bấm Thêm mới phiếu thu. 2. Chọn Khách hàng, chọn lý do Thu công nợ. 3. Nhập số tiền thu được. 4. Chọn chế độ Hoạch toán tự động (để máy tự trừ từ đơn cũ nhất) hoặc Hoạch toán theo chứng từ (để tick chọn đúng hóa đơn thanh toán). 5. Bấm Lưu (F2).', 'Số tiền hạch toán phải khớp với số tiền thực thu[cite: 53].'),
('RUNBOOK_L1', 'Số quỹ', 'Quy trình lập phiếu chi thanh toán nợ cho Nhà cung cấp', '1. Vào Sổ quỹ -> Chi -> Bấm Thêm mới phiếu chi. 2. Chọn Nhà cung cấp, chọn phương thức Chi công nợ. 3. Chọn hình thức chi: Tiền mặt hoặc Chuyển khoản (chọn tài khoản ngân hàng nguồn). 4. Nhập số tiền chi trả, tick chọn các phiếu nhập tương ứng tại danh sách chứng từ. 5. Nhấn Lưu và thoát (F4).', 'Giúp triệt tiêu công nợ phải trả theo từng hóa đơn[cite: 53].'),
('RUNBOOK_L1', 'Số quỹ', 'Xử lý lỗi không sửa được hóa đơn do đã phát sinh phiếu thu/chi', '1. Ghi nhận lại số chứng từ mua/bán cần sửa. 2. Vào Sổ quỹ -> Tab Thu (nếu là đơn bán) hoặc Tab Chi (nếu là đơn nhập). 3. Tìm đúng phiếu thu/chi liên quan đến chứng từ đó và nhấn Xóa. 4. Quay lại màn hình Đơn bán hoặc Đơn nhập để sửa lại thông tin hóa đơn. 5. Vào lại Sổ quỹ lập lại phiếu thu/chi đúng.', 'Phần mềm khóa chứng từ gốc khi đã có giao dịch tiền[cite: 25].'),
('RUNBOOK_L1', 'Hệ thống', 'Quy trình xử lý khóa sổ và kết sổ định kỳ kế toán', '1. Rà soát toàn bộ các hóa đơn bán, nhập, chuyển kho đảm bảo không còn đơn treo ở trạng thái nháp. 2. Hoàn tất kiểm kê kho và thu chi quỹ trong kỳ. 3. Vào Thiết lập cửa hàng -> Hệ thống -> Khóa số / Kết số. 4. Nhập ngày chốt kỳ và xác nhận thực hiện. Toàn bộ chứng từ trước ngày khóa sổ sẽ không thể chỉnh sửa.', 'Ngăn chặn nhân viên thay đổi số liệu kế toán quá khứ[cite: 5].');
"""

def parse_tuples(text):
    # Regex pattern to match SQL insert tuples ('val1', 'val2', 'val3', 'val4', 'val5')
    pattern = r"\(\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*\)"
    matches = re.findall(pattern, text)
    return matches

rows = parse_tuples(raw_inserts)
print(f"Total parsed records: {len(rows)}")

conn = pyodbc.connect(conn_str, autocommit=True)
cur = conn.cursor()

# 1. Create table with structured columns
create_table_sql = """
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='masterpro_documents' AND xtype='U')
BEGIN
    CREATE TABLE masterpro_documents (
        id INT IDENTITY(1,1) PRIMARY KEY,
        category NVARCHAR(50) NOT NULL,
        module NVARCHAR(100) NOT NULL,
        title NVARCHAR(255) NOT NULL,
        content NVARCHAR(MAX) NOT NULL,
        note NVARCHAR(MAX) NULL,
        source NVARCHAR(255) NOT NULL DEFAULT N'Tài liệu vận hành MasterPro',
        version NVARCHAR(50) NOT NULL DEFAULT N'1.0',
        review_status NVARCHAR(50) NOT NULL DEFAULT N'Đã kiểm duyệt',
        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
    );
    CREATE INDEX IX_masterpro_documents_category ON masterpro_documents(category);
    CREATE INDEX IX_masterpro_documents_module ON masterpro_documents(module);
    CREATE INDEX IX_masterpro_documents_status ON masterpro_documents(review_status);
    PRINT 'Created masterpro_documents table with indexes.';
END
ELSE
BEGIN
    PRINT 'masterpro_documents table already exists.';
END
"""
cur.execute(create_table_sql)

# 2. Insert records using parameterized query to preserve Unicode (Vietnamese accents)
insert_sql = """
INSERT INTO masterpro_documents (category, module, title, content, note, source, version, review_status)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
"""

# Default values requested by user: structured, source, version, review_status
DEFAULT_SOURCE = "Tài liệu vận hành MasterPro"
DEFAULT_VERSION = "1.0"
DEFAULT_REVIEW_STATUS = "Đã kiểm duyệt"

# Truncate existing if any to avoid duplication
cur.execute("TRUNCATE TABLE masterpro_documents")

records_to_insert = [
    (cat, mod, title, content, note, DEFAULT_SOURCE, DEFAULT_VERSION, DEFAULT_REVIEW_STATUS)
    for (cat, mod, title, content, note) in rows
]

cur.executemany(insert_sql, records_to_insert)
print(f"Successfully inserted {len(records_to_insert)} records into masterpro_documents.")

# Verification queries
cur.execute("SELECT COUNT(*) FROM masterpro_documents")
count = cur.fetchone()[0]
print(f"Verified row count in database: {count}")

cur.execute("SELECT category, COUNT(*) FROM masterpro_documents GROUP BY category")
for cat, cnt in cur.fetchall():
    print(f" - {cat}: {cnt} items")

cur.execute("SELECT review_status, version, source, COUNT(*) FROM masterpro_documents GROUP BY review_status, version, source")
for st, ver, src, cnt in cur.fetchall():
    print(f" - Status: '{st}', Version: '{ver}', Source: '{src}' ({cnt} items)")

conn.close()
