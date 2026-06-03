"""
04_Import_Excel.py
Nhập dữ liệu từ file Excel vào SQL Server (QuanLyBenhVien)
Xử lý:
  - VaiTro mapping  : Quản lý→Admin | Tiếp tân→Y tá | Dược sĩ→Kế toán
  - MaNV_KeDon      : Thêm NV00 'Bác sĩ Hệ Thống' cho DonThuoc
  - Triggers        : Tắt trong lúc import bulk, bật lại sau
  - LichHen hôm nay : Thêm 8 lịch hẹn ngày hôm nay để demo Dashboard
"""

import sys, os
sys.stdout.reconfigure(encoding='utf-8')

import openpyxl
import pyodbc
from datetime import datetime, date

# ─── CẤU HÌNH ────────────────────────────────────────────────
EXCEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data_PhongKham.xlsx')
if not os.path.exists(EXCEL_PATH):
    EXCEL_PATH = r'D:\IE103\Data_PhongKham.xlsx'

CONN_STR = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;DATABASE=QuanLyBenhVien;'
    'Trusted_Connection=yes;TrustServerCertificate=yes;'
)

# Map VaiTro từ Excel sang giá trị hợp lệ trong DB
VAITRO_MAP = {
    'Quản lý' : 'Admin',
    'Tiếp tân': 'Y tá',
    'Dược sĩ' : 'Kế toán',
    'Admin'   : 'Admin',
    'Bác sĩ'  : 'Bác sĩ',
    'Y tá'    : 'Y tá',
    'Kế toán' : 'Kế toán',
}

# ─── HELPERS ─────────────────────────────────────────────────
def parse_date(val):
    if val is None: return None
    if isinstance(val, (date, datetime)): return val
    s = str(val).strip()
    for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
        try: return datetime.strptime(s, fmt)
        except: pass
    return None

def safe(val):
    if val is None: return None
    s = str(val).strip()
    return s if s else None

def load_sheet(wb, name):
    ws = wb[name]
    rows = list(ws.iter_rows(values_only=True))
    headers = [str(h).strip() for h in rows[0]]
    return [dict(zip(headers, r)) for r in rows[1:] if any(v is not None for v in r)]

def section(msg):
    print(f"\n  {msg}")

def done(n, extra=''):
    print(f"    → {n} dòng{(' ' + extra) if extra else ''}")

# ─── MAIN ────────────────────────────────────────────────────
def main():
    print()
    print("=" * 60)
    print("  IMPORT EXCEL → QuanLyBenhVien")
    print(f"  File: {EXCEL_PATH}")
    print("=" * 60)

    if not os.path.exists(EXCEL_PATH):
        print(f"\n  [LỖI] Không tìm thấy file: {EXCEL_PATH}")
        sys.exit(1)

    wb = openpyxl.load_workbook(EXCEL_PATH)
    conn = pyodbc.connect(CONN_STR)
    cur = conn.cursor()

    # ── 1. Xóa dữ liệu cũ (đúng thứ tự FK) ─────────────────
    section("[1/11] Xóa dữ liệu cũ...")
    for t in ['HoaDon','XetNghiem','ChiTietDonThuoc','DonThuoc',
              'HoSoBenhAn','LichHen','BenhNhan','BacSi','NhanVien','Thuoc']:
        cur.execute(f'DELETE FROM {t}')
    conn.commit()
    print("         Xong.")

    # ── TẮT TRIGGERS để import bulk không bị chặn ───────────
    section("Tắt triggers tạm thời...")
    cur.execute("DISABLE TRIGGER trg_Check_NgayKham       ON HoSoBenhAn")
    cur.execute("DISABLE TRIGGER trg_Check_HanSuDung_Thuoc ON ChiTietDonThuoc")
    cur.execute("DISABLE TRIGGER trg_Check_Quyen_KeDon    ON DonThuoc")
    cur.execute("DISABLE TRIGGER trg_Check_Dong_HSBA      ON HoSoBenhAn")
    conn.commit()
    print("         Xong.")

    try:
        # ── 2. NhanVien ──────────────────────────────────────
        section("[2/11] NhanVien...")
        rows = load_sheet(wb, 'NhanVien')
        # Thêm NV00: Bác sĩ hệ thống — dùng làm MaNV_KeDon cho DonThuoc
        cur.execute(
            "INSERT INTO NhanVien(MaNV,HoTen,VaiTro,TaiKhoan,MatKhau) VALUES(?,?,?,?,?)",
            ('NV00', 'Bác sĩ Hệ Thống', 'Bác sĩ', 'bacsi', '123456')
        )
        for r in rows:
            vt = VAITRO_MAP.get(str(r['VaiTro']).strip(), 'Y tá')
            cur.execute(
                "INSERT INTO NhanVien(MaNV,HoTen,VaiTro,TaiKhoan,MatKhau) VALUES(?,?,?,?,?)",
                (r['MaNV'], r['HoTen'], vt, r['TaiKhoan'], r['MatKhau'])
            )
        conn.commit()
        done(len(rows) + 1, "(bao gồm NV00 Bác sĩ Hệ Thống)")

        # ── 3. BacSi ─────────────────────────────────────────
        section("[3/11] BacSi...")
        rows = load_sheet(wb, 'BacSi')
        for r in rows:
            cur.execute(
                "INSERT INTO BacSi(MaBS,HoTen,ChuyenKhoa,SDT,Email,TrinhDo) VALUES(?,?,?,?,?,?)",
                (r['MaBS'], r['HoTen'], safe(r['ChuyenKhoa']),
                 safe(r['SDT']), safe(r['Email']), safe(r['TrinhDo']))
            )
        conn.commit()
        done(len(rows))

        # ── 4. Thuoc ─────────────────────────────────────────
        section("[4/11] Thuoc...")
        rows = load_sheet(wb, 'Thuoc')
        for r in rows:
            han = parse_date(r['HanSuDung'])
            cur.execute(
                "INSERT INTO Thuoc(MaThuoc,TenThuoc,DonVi,GiaBan,SoLuongTon,HanSuDung) VALUES(?,?,?,?,?,?)",
                (r['MaThuoc'], r['TenThuoc'], safe(r['DonVi']),
                 float(r['GiaBan']) if r['GiaBan'] else 0,
                 int(float(r['SoLuongTon'])) if r['SoLuongTon'] else 0,
                 han)
            )
        conn.commit()
        done(len(rows))

        # ── 5. BenhNhan ──────────────────────────────────────
        section("[5/11] BenhNhan...")
        rows = load_sheet(wb, 'BenhNhan')
        for r in rows:
            ns = parse_date(r['NgaySinh'])
            cur.execute(
                "INSERT INTO BenhNhan(MaBN,HoTen,NgaySinh,GioiTinh,CCCD,DiaChi,SDT,NhomMau,TienSuBenh)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (r['MaBN'], r['HoTen'], ns, safe(r['GioiTinh']), r['CCCD'],
                 safe(r['DiaChi']), safe(r['SDT']), safe(r['NhomMau']), safe(r['TienSuBenh']))
            )
        conn.commit()
        done(len(rows))

        # ── 6. LichHen (+ thêm lịch hôm nay để demo) ────────
        section("[6/11] LichHen...")
        rows = load_sheet(wb, 'LichHen')
        for r in rows:
            ng = parse_date(r['NgayGio'])
            cur.execute(
                "INSERT INTO LichHen(MaLich,MaBN,MaBS,NgayGio,LyDoKham,TrangThai) VALUES(?,?,?,?,?,?)",
                (r['MaLich'], r['MaBN'], r['MaBS'], ng,
                 safe(r['LyDoKham']), r['TrangThai'] or 'Chờ khám')
            )

        # Thêm lịch hẹn hôm nay — dùng BS21-BS25 (bác sĩ nhóm)
        cur.execute("SELECT TOP 8 MaBN FROM BenhNhan ORDER BY MaBN")
        bn_today = [x[0] for x in cur.fetchall()]
        bs_today = ['BS21', 'BS22', 'BS23', 'BS24', 'BS25',
                    'BS21', 'BS22', 'BS23']  # lặp lại cho đủ 8

        today = datetime.now()
        demo_lich = [
            ('Khám tổng quát định kỳ',  8,  0 ),
            ('Đau đầu, chóng mặt',       8,  30),
            ('Sốt cao 3 ngày',           9,  0 ),
            ('Kiểm tra tim mạch',        9,  30),
            ('Tái khám tiểu đường',      10, 0 ),
            ('Đau bụng, buồn nôn',       10, 30),
            ('Dị ứng, mẩn ngứa da',     11, 0 ),
            ('Kiểm tra huyết áp định kỳ',14, 0 ),
        ]
        offset = len(rows) + 1
        for i, (ly_do, h, m) in enumerate(demo_lich):
            mbn = bn_today[i % len(bn_today)]
            mbs = bs_today[i % len(bs_today)]
            ma  = f'LH{(offset + i):03d}'
            ng  = today.replace(hour=h, minute=m, second=0, microsecond=0)
            cur.execute(
                "INSERT INTO LichHen(MaLich,MaBN,MaBS,NgayGio,LyDoKham,TrangThai) VALUES(?,?,?,?,?,?)",
                (ma, mbn, mbs, ng, ly_do, 'Chờ khám')
            )
        conn.commit()
        done(len(rows), f"+ {len(demo_lich)} lịch hẹn hôm nay (demo)")

        # ── 7. HoSoBenhAn ────────────────────────────────────
        section("[7/11] HoSoBenhAn...")
        rows = load_sheet(wb, 'HoSoBenhAn')
        for r in rows:
            ng = parse_date(r['NgayKham'])
            cur.execute(
                "INSERT INTO HoSoBenhAn(MaHoSo,MaBN,MaBS,NgayKham,ChanDoan,TrieuChung,GhiChu)"
                " VALUES(?,?,?,?,?,?,?)",
                (r['MaHoSo'], r['MaBN'], r['MaBS'], ng,
                 safe(r['ChanDoan']), safe(r['TrieuChung']), safe(r['GhiChu']))
            )
        conn.commit()
        done(len(rows))

        # ── 8. DonThuoc (MaNV_KeDon = NV00) ─────────────────
        section("[8/11] DonThuoc...")
        rows = load_sheet(wb, 'DonThuoc')
        for r in rows:
            ng = parse_date(r['NgayKe'])
            cur.execute(
                "INSERT INTO DonThuoc(MaDon,MaHoSo,MaNV_KeDon,NgayKe,HuongDanSuDung)"
                " VALUES(?,?,?,?,?)",
                (r['MaDon'], r['MaHoSo'], 'NV00', ng, safe(r['HuongDanSuDung']))
            )
        conn.commit()
        done(len(rows), "(MaNV_KeDon = NV00 Bác sĩ Hệ Thống)")

        # ── 9. ChiTietDonThuoc ───────────────────────────────
        section("[9/11] ChiTietDonThuoc...")
        rows = load_sheet(wb, 'ChiTietDonThuoc')
        ok = skip = 0
        for r in rows:
            try:
                cur.execute(
                    "INSERT INTO ChiTietDonThuoc(MaDon,MaThuoc,SoLuong,LieuDung,TanSuat)"
                    " VALUES(?,?,?,?,?)",
                    (r['MaDon'], r['MaThuoc'],
                     int(float(r['SoLuong'])) if r['SoLuong'] else 1,
                     safe(r['LieuDung']), safe(r['TanSuat']))
                )
                ok += 1
            except Exception:
                skip += 1
        conn.commit()
        done(ok, f"({skip} bỏ qua do lỗi FK)")

        # ── 10. XetNghiem ────────────────────────────────────
        section("[10/11] XetNghiem...")
        rows = load_sheet(wb, 'XetNghiem')
        for r in rows:
            ng = parse_date(r['NgayThucHien'])
            cur.execute(
                "INSERT INTO XetNghiem(MaXN,MaHoSo,LoaiXN,KetQua,NgayThucHien)"
                " VALUES(?,?,?,?,?)",
                (r['MaXN'], r['MaHoSo'], safe(r['LoaiXN']), safe(r['KetQua']), ng)
            )
        conn.commit()
        done(len(rows))

        # ── 11. HoaDon ───────────────────────────────────────
        section("[11/11] HoaDon...")
        rows = load_sheet(wb, 'HoaDon')
        for r in rows:
            ng = parse_date(r['NgayLap'])
            cur.execute(
                "INSERT INTO HoaDon(MaHD,MaBN,MaHoSo,NgayLap,TongTien,TrangThaiTT)"
                " VALUES(?,?,?,?,?,?)",
                (r['MaHD'], r['MaBN'], r['MaHoSo'], ng,
                 float(r['TongTien']) if r['TongTien'] else 0,
                 r['TrangThaiTT'] or 'Chưa thanh toán')
            )
        conn.commit()
        done(len(rows))

    finally:
        # ── BẬT LẠI TRIGGERS ─────────────────────────────────
        section("Bật lại triggers...")
        cur.execute("ENABLE TRIGGER trg_Check_NgayKham        ON HoSoBenhAn")
        cur.execute("ENABLE TRIGGER trg_Check_HanSuDung_Thuoc ON ChiTietDonThuoc")
        cur.execute("ENABLE TRIGGER trg_Check_Quyen_KeDon     ON DonThuoc")
        cur.execute("ENABLE TRIGGER trg_Check_Dong_HSBA       ON HoSoBenhAn")
        conn.commit()
        conn.close()
        print("         Xong.")

    print()
    print("=" * 60)
    print("  IMPORT HOÀN TẤT!")
    print("=" * 60)
    print()
    print("  Tài khoản đăng nhập Flask app:")
    print("  ┌─────────────┬────────────┬──────────────────────┐")
    print("  │ Tài khoản   │ Mật khẩu  │ Vai trò              │")
    print("  ├─────────────┼────────────┼──────────────────────┤")
    print("  │ bacsi       │ 123456     │ Bác sĩ (kê đơn)      │")
    print("  │ nv01        │ 123456aA@  │ Admin (Quản lý)      │")
    print("  │ nv02        │ 123456aA@  │ Y tá  (Tiếp tân)     │")
    print("  │ nv05        │ 123456aA@  │ Kế toán (Dược sĩ)   │")
    print("  └─────────────┴────────────┴──────────────────────┘")
    print()


if __name__ == '__main__':
    main()
