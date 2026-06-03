-- ============================================================
-- FILE    : 03_SampleData_Demo.sql
-- MỤC ĐÍCH: Dữ liệu mẫu để chạy Flask App Demo
-- CHẠY SAU: 01_Create_Database.sql + 02_SP_Functions.sql
-- ============================================================
USE QuanLyBenhVien;
GO

-- ─────────────────────────────────────────────────────────────
-- 1. NHÂN VIÊN (có tài khoản để đăng nhập Flask app)
-- MatKhau lưu plain text cho demo — thực tế phải hash
-- ─────────────────────────────────────────────────────────────
INSERT INTO NhanVien (MaNV, HoTen, VaiTro, TaiKhoan, MatKhau) VALUES
('NV001', N'Trần Văn Minh',    N'Bác sĩ',  'bacsi01',  '123456'),
('NV002', N'Lê Thị Hoa',       N'Bác sĩ',  'bacsi02',  '123456'),
('NV003', N'Nguyễn Thị Lan',   N'Y tá',    'yta01',    '123456'),
('NV004', N'Phạm Quang Hùng',  N'Kế toán', 'ketoan01', '123456'),
('NV005', N'Admin Hệ Thống',   N'Admin',   'admin',    'admin123');
GO

-- ─────────────────────────────────────────────────────────────
-- 2. BÁC SĨ
-- ─────────────────────────────────────────────────────────────
INSERT INTO BacSi (MaBS, HoTen, ChuyenKhoa, SDT, Email, TrinhDo) VALUES
('BS001', N'Trần Văn Minh',    N'Nội tổng quát',   '0901111111', 'minh.bs@bvdemo.vn',  N'Tiến sĩ Y khoa'),
('BS002', N'Lê Thị Hoa',       N'Nhi khoa',         '0902222222', 'hoa.bs@bvdemo.vn',   N'Thạc sĩ Y khoa'),
('BS003', N'Nguyễn Quốc Tuấn', N'Tim mạch',         '0903333333', 'tuan.bs@bvdemo.vn',  N'Tiến sĩ Y khoa'),
('BS004', N'Phạm Thị Bích',    N'Da liễu',          '0904444444', 'bich.bs@bvdemo.vn',  N'Bác sĩ CKII'),
('BS005', N'Huỳnh Văn Khoa',   N'Chấn thương chỉnh hình', '0905555555', 'khoa.bs@bvdemo.vn', N'Bác sĩ CKI');
GO

-- ─────────────────────────────────────────────────────────────
-- 3. THUỐC
-- ─────────────────────────────────────────────────────────────
INSERT INTO Thuoc (MaThuoc, TenThuoc, DonVi, GiaBan, SoLuongTon, HanSuDung) VALUES
('TH001', N'Paracetamol 500mg',     N'Viên',  2000,   500, '2027-12-31'),
('TH002', N'Amoxicillin 500mg',     N'Viên',  5000,   300, '2027-06-30'),
('TH003', N'Omeprazole 20mg',       N'Viên',  8000,   200, '2027-09-30'),
('TH004', N'Metformin 500mg',       N'Viên',  3000,   400, '2027-12-31'),
('TH005', N'Amlodipine 5mg',        N'Viên', 12000,   150, '2027-08-31'),
('TH006', N'Vitamin C 500mg',       N'Viên',  1500,   600, '2028-01-31'),
('TH007', N'Ibuprofen 400mg',       N'Viên',  4000,   250, '2027-11-30'),
('TH008', N'Cetirizine 10mg',       N'Viên',  6000,   180, '2027-10-31'),
('TH009', N'Dung dịch NaCl 0.9%',  N'Chai',  25000,   80, '2026-12-31'),
('TH010', N'Azithromycin 500mg',    N'Viên', 18000,    15, '2027-03-31');
GO

-- ─────────────────────────────────────────────────────────────
-- 4. BỆNH NHÂN
-- ─────────────────────────────────────────────────────────────
INSERT INTO BenhNhan (MaBN, HoTen, NgaySinh, GioiTinh, CCCD, DiaChi, SDT, NhomMau, TienSuBenh) VALUES
('BN001', N'Nguyễn Văn An',     '1985-03-15', N'Nam',  '079085001234', N'123 Nguyễn Trãi, Q5, TP.HCM',     '0901234567', 'A+',  N'Không có'),
('BN002', N'Trần Thị Bích',     '1992-07-22', N'Nữ',   '079092002345', N'45 Lê Lợi, Q1, TP.HCM',          '0912345678', 'O+',  N'Dị ứng Penicillin'),
('BN003', N'Lê Văn Cường',      '1978-11-08', N'Nam',  '079078003456', N'67 Đinh Tiên Hoàng, Bình Thạnh',  '0923456789', 'B+',  N'Tiểu đường type 2'),
('BN004', N'Phạm Thị Dung',     '2000-01-30', N'Nữ',   '079000004567', N'89 Cách Mạng Tháng 8, Q10',       '0934567890', 'AB-', N'Không có'),
('BN005', N'Hoàng Văn Em',      '1965-09-12', N'Nam',  '079065005678', N'12 Võ Văn Tần, Q3, TP.HCM',       '0945678901', 'O-',  N'Tăng huyết áp, tim mạch'),
('BN006', N'Nguyễn Thị Fân',    '1990-05-25', N'Nữ',   '079090006789', N'34 Phan Xích Long, Phú Nhuận',    '0956789012', 'A-',  N'Không có'),
('BN007', N'Đỗ Văn Giang',      '2015-08-18', N'Nam',  '079115007890', N'56 Trần Hưng Đạo, Q1',            '0967890123', 'B-',  N'Hen suyễn'),
('BN008', N'Bùi Thị Hương',     '1955-12-03', N'Nữ',   '079055008901', N'78 Nguyễn Đình Chiểu, Q3',        '0978901234', 'AB+', N'Tiểu đường, tăng huyết áp');
GO

-- ─────────────────────────────────────────────────────────────
-- 5. LỊCH HẸN HÔM NAY (để dashboard/lich_hen hiển thị)
-- ─────────────────────────────────────────────────────────────
INSERT INTO LichHen (MaLich, MaBN, MaBS, NgayGio, LyDoKham, TrangThai) VALUES
('LH001', 'BN001', 'BS001', CAST(GETDATE() AS DATE) + CAST('08:00' AS TIME), N'Khám tổng quát định kỳ',       N'Chờ khám'),
('LH002', 'BN002', 'BS002', CAST(GETDATE() AS DATE) + CAST('08:30' AS TIME), N'Sốt, đau họng 3 ngày',         N'Chờ khám'),
('LH003', 'BN003', 'BS001', CAST(GETDATE() AS DATE) + CAST('09:00' AS TIME), N'Kiểm tra đường huyết',         N'Chờ khám'),
('LH004', 'BN005', 'BS003', CAST(GETDATE() AS DATE) + CAST('09:30' AS TIME), N'Đau ngực, khó thở',            N'Hoàn thành'),
('LH005', 'BN007', 'BS002', CAST(GETDATE() AS DATE) + CAST('10:00' AS TIME), N'Hen suyễn tái phát',           N'Chờ khám'),
('LH006', 'BN004', 'BS004', CAST(GETDATE() AS DATE) + CAST('10:30' AS TIME), N'Mẩn ngứa, dị ứng da',         N'Chờ khám'),
('LH007', 'BN008', 'BS001', CAST(GETDATE() AS DATE) + CAST('11:00' AS TIME), N'Tái khám tiểu đường tháng 6', N'Chờ khám'),
('LH008', 'BN006', 'BS004', CAST(GETDATE() AS DATE) + CAST('14:00' AS TIME), N'Mụn trứng cá, chăm sóc da',   N'Chờ khám');
GO

PRINT N'';
PRINT N'=== Dữ liệu mẫu đã được chèn thành công! ===';
PRINT N'';
PRINT N'Tài khoản demo để đăng nhập Flask app:';
PRINT N'  Bác sĩ : bacsi01  / 123456  (Trần Văn Minh — Nội tổng quát)';
PRINT N'  Bác sĩ : bacsi02  / 123456  (Lê Thị Hoa    — Nhi khoa)';
PRINT N'  Y tá   : yta01    / 123456';
PRINT N'  Kế toán: ketoan01 / 123456';
PRINT N'  Admin  : admin    / admin123';
GO
