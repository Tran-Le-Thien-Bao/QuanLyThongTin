# Hướng Dẫn Chạy Demo — Hệ Thống Quản Lý Bệnh Viện
**Môn:** IE103.Q22 | **Nhóm:** Trần Lê Thiên Bảo

---

## Yêu Cầu Hệ Thống

| Phần mềm | Phiên bản | Ghi chú |
|---|---|---|
| Python | 3.13+ | Tải tại [python.org](https://python.org/downloads) |
| SQL Server | 2019+ | Express edition là đủ |
| SSMS | Bất kỳ | Để chạy file SQL |
| ODBC Driver 17 | for SQL Server | Thường đi kèm SQL Server |

---

## Lần Đầu Cài Đặt (Chỉ Làm 1 Lần)

### Bước 1 — Tạo Database trong SSMS
Mở SSMS, chạy lần lượt 2 file SQL:
```
01_Create_Database.sql   ← Tạo database + 10 bảng + 4 triggers
02_SP_Functions.sql      ← Tạo 3 Stored Procedure + 2 Function
```

### Bước 2 — Đặt file Excel đúng vị trí
Đảm bảo file `Data_PhongKham.xlsx` nằm tại:
```
D:\IE103\Data_PhongKham.xlsx
```

### Bước 3 — Chạy Demo
**Cách nhanh nhất:** Double-click vào file:
```
D:\IE103\QuanLyBenhVien\start.bat
```
File này sẽ tự động:
1. Cài thư viện Python (flask, pyodbc, openpyxl)
2. Import toàn bộ data từ Excel vào SQL Server
3. Khởi động Flask server
4. Mở trình duyệt tại `http://localhost:5000`

---

## Chạy Thủ Công (Nếu Cần)

```bash
cd D:\IE103\QuanLyBenhVien

# Cài thư viện
py -3.13 -m pip install flask pyodbc openpyxl

# Import data từ Excel
py -3.13 04_Import_Excel.py

# Khởi động server
py -3.13 app.py
```

---

## Tài Khoản Đăng Nhập Demo

| Tài khoản | Mật khẩu | Vai trò | Quyền đặc biệt |
|---|---|---|---|
| `bacsi` | `123456` | Bác sĩ | **Kê đơn thuốc** |
| `nv01` | `123456aA@` | Admin | Quản lý hệ thống |
| `nv02` | `123456aA@` | Y tá | Tiếp nhận, lịch hẹn |
| `nv05` | `123456aA@` | Kế toán | Xuất hóa đơn |

> **Lưu ý:** Chỉ tài khoản `bacsi` mới được vào trang `/ke-don` (kê đơn thuốc).

---

## Các Trang Chức Năng

| URL | Chức năng | Thao tác demo |
|---|---|---|
| `/` | Dashboard tổng quan | Xem số liệu thống kê |
| `/tiep-nhan` | Tiếp nhận bệnh nhân | Nhập CCCD → tra cứu hoặc tạo mới |
| `/lich-hen` | Lịch hẹn hôm nay | Xem danh sách, bấm "Khám" |
| `/kham-benh/<MaLich>` | Ghi hồ sơ bệnh án | Điền chẩn đoán, triệu chứng |
| `/ke-don/<MaHoSo>` | Kê đơn thuốc | Chọn thuốc, số lượng, liều dùng |
| `/hoa-don/<MaHoSo>` | Xuất & thanh toán | Xuất hóa đơn → thanh toán |
| `/bao-cao` | Báo cáo tháng | Doanh thu, top bác sĩ, tồn kho |

---

## Luồng Demo Đầy Đủ (5 Phút)

```
Đăng nhập bacsi
    ↓
Dashboard → thấy lịch hẹn hôm nay (8 lịch)
    ↓
Lịch Hẹn → bấm [Khám] một lịch
    ↓
Khám Bệnh → điền chẩn đoán → [Lưu & Chuyển Kê Đơn]
    ↓
Kê Đơn → chọn thuốc → [Xác Nhận Kê Đơn]
    ↓
Hóa Đơn → [Xuất Hóa Đơn] → [Xác Nhận Thanh Toán]
    ↓
Báo Cáo → xem doanh thu tháng
```

---

## Xử Lý Sự Cố

**Lỗi kết nối SQL Server:**
- Kiểm tra SQL Server đang chạy: `services.msc` → SQL Server (MSSQLSERVER)
- Thử đổi `SERVER=localhost` thành tên máy trong [db.py](db.py)

**Lỗi ODBC Driver:**
- Tải và cài: [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

**Import Excel thất bại:**
- Kiểm tra file `Data_PhongKham.xlsx` tại `D:\IE103\`
- Đảm bảo đã chạy `01_Create_Database.sql` trước

**Port 5000 đã bị dùng:**
- Đổi port trong [app.py](app.py) dòng cuối: `app.run(debug=True, port=5001)`

---

*Thực hiện: Trần Lê Thiên Bảo — IE103.Q22*
