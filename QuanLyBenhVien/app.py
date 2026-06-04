"""
app.py — Flask Demo: Hệ thống Quản lý Bệnh viện
Môn IE103.Q22 | Thực hiện: Trần Lê Thiên Bảo

Lưu ý: sp_KeDonThuoc dùng TVP không hỗ trợ qua pyodbc,
nên phần kê đơn được thực hiện bằng SQL trực tiếp (logic tương đương SP).
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
from db import get_connection, query_all, query_one, execute
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = "qlbv_ie103_2026_secret"


# ─────────────────────────────────────────────────────────────
# Helper: kiểm tra đăng nhập
# ─────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def role_required(roles):
    """Decorator kiểm tra vai trò. Đặt bên dưới @login_required.
    roles: list các VaiTro được phép, ví dụ ["Bác sĩ"] hoặc ["Kế toán", "Admin"].
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            vai_tro = session.get("user", {}).get("VaiTro", "")
            if vai_tro not in roles:
                flash(f"Chức năng này chỉ dành cho: {', '.join(roles)}.", "danger")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─────────────────────────────────────────────────────────────
# ĐĂNG NHẬP / ĐĂNG XUẤT
# ─────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        tai_khoan = request.form["tai_khoan"]
        mat_khau  = request.form["mat_khau"]

        nv = query_one(
            "SELECT MaNV, HoTen, VaiTro, TaiKhoan FROM NhanVien "
            "WHERE TaiKhoan = ? AND MatKhau = ?",
            (tai_khoan, mat_khau)
        )
        if nv:
            session["user"] = nv
            flash(f"Chào mừng, {nv['HoTen']}!", "success")
            return redirect(url_for("index"))
        flash("Tài khoản hoặc mật khẩu không đúng.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────────────────────
# TRANG CHỦ / DASHBOARD
# ─────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def index():
    today = date.today().strftime("%Y-%m-%d")

    so_benh_nhan  = query_one("SELECT COUNT(*) AS n FROM BenhNhan")["n"]
    so_bac_si     = query_one("SELECT COUNT(*) AS n FROM BacSi")["n"]
    lich_hom_nay  = query_one(
        "SELECT COUNT(*) AS n FROM LichHen WHERE CAST(NgayGio AS DATE) = ?", (today,)
    )["n"]
    cho_kham      = query_one(
        "SELECT COUNT(*) AS n FROM LichHen "
        "WHERE CAST(NgayGio AS DATE) = ? AND TrangThai = N'Chờ khám'", (today,)
    )["n"]
    hoa_don_chua_tt = query_one(
        "SELECT COUNT(*) AS n FROM HoaDon WHERE TrangThaiTT = N'Chưa thanh toán'"
    )["n"]

    recent_lich = query_all(
        """
        SELECT TOP 5 lh.MaLich, bn.HoTen AS TenBN, bs.HoTen AS TenBS,
               lh.NgayGio, lh.TrangThai, lh.LyDoKham
        FROM LichHen lh
        JOIN BenhNhan bn ON lh.MaBN = bn.MaBN
        JOIN BacSi    bs ON lh.MaBS = bs.MaBS
        WHERE CAST(lh.NgayGio AS DATE) = ?
        ORDER BY lh.NgayGio
        """, (today,)
    )

    return render_template("index.html",
        so_benh_nhan=so_benh_nhan,
        so_bac_si=so_bac_si,
        lich_hom_nay=lich_hom_nay,
        cho_kham=cho_kham,
        hoa_don_chua_tt=hoa_don_chua_tt,
        recent_lich=recent_lich,
        today=today
    )


# ─────────────────────────────────────────────────────────────
# TIẾP NHẬN BỆNH NHÂN — gọi sp_TiepNhanBenhMoi
# ─────────────────────────────────────────────────────────────
@app.route("/tiep-nhan", methods=["GET", "POST"])
@login_required
def tiep_nhan():
    bac_si_list = query_all("SELECT MaBS, HoTen, ChuyenKhoa FROM BacSi ORDER BY HoTen")

    if request.method == "POST":
        cccd     = request.form.get("cccd", "").strip()
        ho_ten   = request.form.get("ho_ten", "").strip()
        ngay_sinh= request.form.get("ngay_sinh", "")
        gioi_tinh= request.form.get("gioi_tinh", "")
        dia_chi  = request.form.get("dia_chi", "")
        sdt      = request.form.get("sdt", "")
        nhom_mau = request.form.get("nhom_mau", "")
        tien_su  = request.form.get("tien_su_benh", "")
        ma_bs    = request.form.get("ma_bs", "")
        ngay_gio = request.form.get("ngay_gio", "")
        ly_do    = request.form.get("ly_do_kham", "")

        try:
            sql = """
                DECLARE @MaBN_Out  VARCHAR(20), @MaLich_Out VARCHAR(20);
                EXEC sp_TiepNhanBenhMoi
                    @CCCD        = ?,
                    @HoTen       = ?,
                    @NgaySinh    = ?,
                    @GioiTinh    = ?,
                    @DiaChi      = ?,
                    @SDT         = ?,
                    @NhomMau     = ?,
                    @TienSuBenh  = ?,
                    @MaBS        = ?,
                    @NgayGio     = ?,
                    @LyDoKham    = ?,
                    @MaBN_Out    = @MaBN_Out  OUTPUT,
                    @MaLich_Out  = @MaLich_Out OUTPUT;
                SELECT @MaBN_Out AS MaBN, @MaLich_Out AS MaLich;
            """
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    cccd, ho_ten or None, ngay_sinh or None, gioi_tinh or None,
                    dia_chi or None, sdt or None, nhom_mau or None, tien_su or None,
                    ma_bs, ngay_gio, ly_do or None
                ))
                # Bỏ qua PRINT messages, tìm result set
                result = None
                while True:
                    if cursor.description:
                        row = cursor.fetchone()
                        if row:
                            result = row
                            break
                    if not cursor.nextset():
                        break
                conn.commit()

            if result:
                flash(f"Tiếp nhận thành công! Mã BN: {result[0]} | Mã lịch hẹn: {result[1]}", "success")
                return redirect(url_for("lich_hen"))
            else:
                flash("Tạo lịch hẹn thất bại.", "danger")

        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")

    # Kiểm tra CCCD nếu có (AJAX-like lookup qua query param)
    cccd_lookup = request.args.get("cccd", "")
    bn_cu = None
    if cccd_lookup:
        bn_cu = query_one("SELECT * FROM BenhNhan WHERE CCCD = ?", (cccd_lookup,))

    return render_template("tiep_nhan.html",
        bac_si_list=bac_si_list,
        cccd_lookup=cccd_lookup,
        bn_cu=bn_cu
    )


# ─────────────────────────────────────────────────────────────
# DANH SÁCH LỊCH HẸN
# ─────────────────────────────────────────────────────────────
@app.route("/lich-hen")
@login_required
def lich_hen():
    ngay = request.args.get("ngay", date.today().strftime("%Y-%m-%d"))

    lich_list = query_all(
        """
        SELECT lh.MaLich, bn.HoTen AS TenBN, bn.MaBN,
               bs.HoTen AS TenBS, bs.ChuyenKhoa,
               lh.NgayGio, lh.LyDoKham, lh.TrangThai,
               hs.MaHoSo
        FROM LichHen lh
        JOIN BenhNhan bn ON lh.MaBN = bn.MaBN
        JOIN BacSi    bs ON lh.MaBS = bs.MaBS
        LEFT JOIN HoSoBenhAn hs ON hs.MaBN = lh.MaBN
            AND CAST(hs.NgayKham AS DATE) = CAST(lh.NgayGio AS DATE)
        WHERE CAST(lh.NgayGio AS DATE) = ?
        ORDER BY lh.NgayGio
        """, (ngay,)
    )

    return render_template("lich_hen.html", lich_list=lich_list, ngay=ngay)


# ─────────────────────────────────────────────────────────────
# KHÁM BỆNH — tạo Hồ Sơ Bệnh Án
# ─────────────────────────────────────────────────────────────
@app.route("/kham-benh/<ma_lich>", methods=["GET", "POST"])
@login_required
def kham_benh(ma_lich):
    lich = query_one(
        """
        SELECT lh.*, bn.HoTen AS TenBN, bn.NgaySinh, bn.GioiTinh,
               bn.NhomMau, bn.TienSuBenh, bn.SDT, bn.DiaChi,
               bs.HoTen AS TenBS, bs.ChuyenKhoa, bs.MaBS
        FROM LichHen lh
        JOIN BenhNhan bn ON lh.MaBN = bn.MaBN
        JOIN BacSi    bs ON lh.MaBS = bs.MaBS
        WHERE lh.MaLich = ?
        """, (ma_lich,)
    )
    if not lich:
        flash("Không tìm thấy lịch hẹn.", "danger")
        return redirect(url_for("lich_hen"))

    # Kiểm tra đã có HSBA chưa
    hsba = query_one(
        "SELECT MaHoSo FROM HoSoBenhAn WHERE MaBN = ? "
        "AND CAST(NgayKham AS DATE) = CAST(? AS DATE)",
        (lich["MaBN"], lich["NgayGio"])
    )

    if request.method == "POST":
        chan_doan  = request.form.get("chan_doan", "")
        trieu_chung= request.form.get("trieu_chung", "")
        ghi_chu    = request.form.get("ghi_chu", "")

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Sinh MaHoSo tự động
                cursor.execute(
                    """SELECT ISNULL(MAX(CAST(SUBSTRING(MaHoSo,3,LEN(MaHoSo)) AS INT)),0)+1
                       FROM HoSoBenhAn WHERE MaHoSo LIKE 'HS%'
                       AND ISNUMERIC(SUBSTRING(MaHoSo,3,LEN(MaHoSo)))=1"""
                )
                stt = cursor.fetchone()[0]
                ma_ho_so = f"HS{stt:03d}"

                cursor.execute(
                    """INSERT INTO HoSoBenhAn
                       (MaHoSo, MaBN, MaBS, NgayKham, ChanDoan, TrieuChung, GhiChu, TrangThai)
                       VALUES (?, ?, ?, GETDATE(), ?, ?, ?, N'Đang xử lý')""",
                    (ma_ho_so, lich["MaBN"], lich["MaBS"], chan_doan, trieu_chung, ghi_chu)
                )

                # Cập nhật trạng thái lịch hẹn
                cursor.execute(
                    "UPDATE LichHen SET TrangThai = N'Đang khám' WHERE MaLich = ?",
                    (ma_lich,)
                )
                conn.commit()

            flash(f"Đã tạo hồ sơ bệnh án {ma_ho_so}.", "success")
            return redirect(url_for("ke_don", ma_ho_so=ma_ho_so))

        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")

    return render_template("kham_benh.html", lich=lich, hsba=hsba)


# ─────────────────────────────────────────────────────────────
# KÊ ĐƠN THUỐC
# (pyodbc không hỗ trợ TVP nên thực hiện logic tương đương SP trực tiếp)
# ─────────────────────────────────────────────────────────────
@app.route("/ke-don/<ma_ho_so>", methods=["GET", "POST"])
@login_required
@role_required(["Bác sĩ"])
def ke_don(ma_ho_so):

    hsba = query_one(
        """
        SELECT hs.*, bn.HoTen AS TenBN, bs.HoTen AS TenBS
        FROM HoSoBenhAn hs
        JOIN BenhNhan bn ON hs.MaBN = bn.MaBN
        JOIN BacSi    bs ON hs.MaBS = bs.MaBS
        WHERE hs.MaHoSo = ?
        """, (ma_ho_so,)
    )
    if not hsba:
        flash("Không tìm thấy hồ sơ bệnh án.", "danger")
        return redirect(url_for("lich_hen"))

    # Kiểm tra đã có đơn thuốc chưa
    don_cu = query_one("SELECT MaDon FROM DonThuoc WHERE MaHoSo = ?", (ma_ho_so,))

    thuoc_list = query_all(
        """SELECT MaThuoc, TenThuoc, DonVi, GiaBan, SoLuongTon, HanSuDung
           FROM Thuoc WHERE SoLuongTon > 0 AND HanSuDung > GETDATE()
           ORDER BY TenThuoc"""
    )

    if request.method == "POST":
        huong_dan    = request.form.get("huong_dan", "")
        ma_thuoc_arr = request.form.getlist("ma_thuoc[]")
        so_luong_arr = request.form.getlist("so_luong[]")
        lieu_dung_arr= request.form.getlist("lieu_dung[]")
        tan_suat_arr = request.form.getlist("tan_suat[]")

        if not ma_thuoc_arr:
            flash("Vui lòng chọn ít nhất một loại thuốc.", "warning")
            return render_template("ke_don.html", hsba=hsba, thuoc_list=thuoc_list, don_cu=don_cu)

        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Kiểm tra tồn kho
                for i, ma_thuoc in enumerate(ma_thuoc_arr):
                    so_luong = int(so_luong_arr[i])
                    cursor.execute(
                        "SELECT SoLuongTon, TenThuoc FROM Thuoc WHERE MaThuoc = ?", (ma_thuoc,)
                    )
                    row = cursor.fetchone()
                    if not row or row[0] < so_luong:
                        flash(f"Thuốc {row[1] if row else ma_thuoc} không đủ số lượng trong kho.", "danger")
                        return render_template("ke_don.html", hsba=hsba, thuoc_list=thuoc_list, don_cu=don_cu)

                # Sinh MaDon
                cursor.execute(
                    """SELECT ISNULL(MAX(CAST(SUBSTRING(MaDon,3,LEN(MaDon)) AS INT)),0)+1
                       FROM DonThuoc WHERE MaDon LIKE 'DT%'
                       AND ISNUMERIC(SUBSTRING(MaDon,3,LEN(MaDon)))=1"""
                )
                stt = cursor.fetchone()[0]
                ma_don = f"DT{stt:03d}"

                # Tạo đơn thuốc
                cursor.execute(
                    """INSERT INTO DonThuoc (MaDon, MaHoSo, MaNV_KeDon, NgayKe, HuongDanSuDung)
                       VALUES (?, ?, ?, GETDATE(), ?)""",
                    (ma_don, ma_ho_so, session["user"]["MaNV"], huong_dan)
                )

                # Thêm chi tiết và trừ kho
                for i, ma_thuoc in enumerate(ma_thuoc_arr):
                    so_luong  = int(so_luong_arr[i])
                    lieu_dung = lieu_dung_arr[i] if i < len(lieu_dung_arr) else ""
                    tan_suat  = tan_suat_arr[i]  if i < len(tan_suat_arr)  else ""

                    cursor.execute(
                        """INSERT INTO ChiTietDonThuoc (MaDon, MaThuoc, SoLuong, LieuDung, TanSuat)
                           VALUES (?, ?, ?, ?, ?)""",
                        (ma_don, ma_thuoc, so_luong, lieu_dung, tan_suat)
                    )
                    cursor.execute(
                        "UPDATE Thuoc SET SoLuongTon = SoLuongTon - ? WHERE MaThuoc = ?",
                        (so_luong, ma_thuoc)
                    )

                conn.commit()

            flash(f"Đã kê đơn thuốc {ma_don} thành công.", "success")
            return redirect(url_for("hoa_don", ma_ho_so=ma_ho_so))

        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")

    return render_template("ke_don.html", hsba=hsba, thuoc_list=thuoc_list, don_cu=don_cu)


# ─────────────────────────────────────────────────────────────
# HÓA ĐƠN — gọi sp_XuatHoaDon, hiển thị và thanh toán
# ─────────────────────────────────────────────────────────────
@app.route("/hoa-don/<ma_ho_so>", methods=["GET", "POST"])
@login_required
@role_required(["Bác sĩ", "Kế toán", "Admin"])
def hoa_don(ma_ho_so):
    hsba = query_one(
        """
        SELECT hs.*, bn.HoTen AS TenBN, bn.SDT, bn.DiaChi,
               bs.HoTen AS TenBS
        FROM HoSoBenhAn hs
        JOIN BenhNhan bn ON hs.MaBN = bn.MaBN
        JOIN BacSi    bs ON hs.MaBS = bs.MaBS
        WHERE hs.MaHoSo = ?
        """, (ma_ho_so,)
    )
    if not hsba:
        flash("Không tìm thấy hồ sơ bệnh án.", "danger")
        return redirect(url_for("lich_hen"))

    # Kiểm tra hóa đơn đã tồn tại chưa
    hd = query_one("SELECT * FROM HoaDon WHERE MaHoSo = ?", (ma_ho_so,))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "xuat" and not hd:
            # Gọi sp_XuatHoaDon
            try:
                sql = """
                    DECLARE @MaHD_Out VARCHAR(20), @TongTien_Out DECIMAL(18,2);
                    EXEC sp_XuatHoaDon
                        @MaHoSo       = ?,
                        @MaHD_Out     = @MaHD_Out     OUTPUT,
                        @TongTien_Out = @TongTien_Out OUTPUT;
                    SELECT @MaHD_Out AS MaHD, @TongTien_Out AS TongTien;
                """
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(sql, (ma_ho_so,))
                    result = None
                    while True:
                        if cursor.description:
                            result = cursor.fetchone()
                            break
                        if not cursor.nextset():
                            break
                    conn.commit()

                if result:
                    flash(f"Xuất hóa đơn {result[0]} thành công! Tổng tiền: {result[1]:,.0f} VNĐ", "success")
                    hd = query_one("SELECT * FROM HoaDon WHERE MaHoSo = ?", (ma_ho_so,))

            except Exception as e:
                flash(f"Lỗi xuất hóa đơn: {str(e)}", "danger")

        elif action == "thanh_toan" and hd:
            try:
                execute(
                    "UPDATE HoaDon SET TrangThaiTT = N'Đã thanh toán' WHERE MaHoSo = ?",
                    (ma_ho_so,)
                )
                execute(
                    "UPDATE LichHen SET TrangThai = N'Hoàn thành' "
                    "WHERE MaBN = (SELECT MaBN FROM HoSoBenhAn WHERE MaHoSo = ?) "
                    "AND CAST(NgayGio AS DATE) = (SELECT CAST(NgayKham AS DATE) FROM HoSoBenhAn WHERE MaHoSo = ?)",
                    (ma_ho_so, ma_ho_so)
                )
                flash("Thanh toán thành công!", "success")
                hd = query_one("SELECT * FROM HoaDon WHERE MaHoSo = ?", (ma_ho_so,))

            except Exception as e:
                flash(f"Lỗi thanh toán: {str(e)}", "danger")

        return redirect(url_for("hoa_don", ma_ho_so=ma_ho_so))

    # Chi tiết đơn thuốc
    chi_tiet = query_all(
        """
        SELECT t.TenThuoc, t.DonVi, ct.SoLuong, ct.LieuDung, ct.TanSuat,
               t.GiaBan, ct.SoLuong * t.GiaBan AS ThanhTien
        FROM DonThuoc dt
        JOIN ChiTietDonThuoc ct ON dt.MaDon  = ct.MaDon
        JOIN Thuoc            t  ON ct.MaThuoc = t.MaThuoc
        WHERE dt.MaHoSo = ?
        """, (ma_ho_so,)
    )

    xet_nghiem = query_all(
        "SELECT LoaiXN, KetQua, NgayThucHien FROM XetNghiem WHERE MaHoSo = ?",
        (ma_ho_so,)
    )

    return render_template("hoa_don.html",
        hsba=hsba, hd=hd, chi_tiet=chi_tiet, xet_nghiem=xet_nghiem
    )


# ─────────────────────────────────────────────────────────────
# BÁO CÁO TỔNG HỢP
# ─────────────────────────────────────────────────────────────
@app.route("/bao-cao")
@login_required
def bao_cao():
    thang = request.args.get("thang", datetime.now().strftime("%Y-%m"))

    try:
        nam, thang_num = thang.split("-")
        nam, thang_num = int(nam), int(thang_num)
    except Exception:
        nam, thang_num = datetime.now().year, datetime.now().month

    # Doanh thu theo tháng
    doanh_thu = query_one(
        """SELECT ISNULL(SUM(TongTien),0) AS Tong, COUNT(*) AS SoHoaDon
           FROM HoaDon
           WHERE YEAR(NgayLap)=? AND MONTH(NgayLap)=? AND TrangThaiTT=N'Đã thanh toán'""",
        (nam, thang_num)
    )

    # Bác sĩ khám nhiều nhất
    top_bac_si = query_all(
        """SELECT TOP 5 bs.HoTen, bs.ChuyenKhoa, COUNT(*) AS SoLuot
           FROM HoSoBenhAn hs JOIN BacSi bs ON hs.MaBS = bs.MaBS
           WHERE YEAR(hs.NgayKham)=? AND MONTH(hs.NgayKham)=?
           GROUP BY bs.HoTen, bs.ChuyenKhoa ORDER BY SoLuot DESC""",
        (nam, thang_num)
    )

    # Thuốc dùng nhiều nhất
    top_thuoc = query_all(
        """SELECT TOP 5 t.TenThuoc, t.DonVi, SUM(ct.SoLuong) AS TongDung
           FROM ChiTietDonThuoc ct
           JOIN DonThuoc dt ON ct.MaDon = dt.MaDon
           JOIN Thuoc t ON ct.MaThuoc = t.MaThuoc
           WHERE YEAR(dt.NgayKe)=? AND MONTH(dt.NgayKe)=?
           GROUP BY t.TenThuoc, t.DonVi ORDER BY TongDung DESC""",
        (nam, thang_num)
    )

    # Tồn kho thuốc sắp hết / sắp hết hạn
    thuoc_ton_it = query_all(
        "SELECT TenThuoc, SoLuongTon, HanSuDung FROM Thuoc "
        "WHERE SoLuongTon < 20 ORDER BY SoLuongTon"
    )

    # Thống kê lịch hẹn theo trạng thái
    trang_thai_stat = query_all(
        """SELECT TrangThai, COUNT(*) AS SoLuong FROM LichHen
           WHERE YEAR(NgayGio)=? AND MONTH(NgayGio)=?
           GROUP BY TrangThai""",
        (nam, thang_num)
    )

    return render_template("bao_cao.html",
        doanh_thu=doanh_thu,
        top_bac_si=top_bac_si,
        top_thuoc=top_thuoc,
        thuoc_ton_it=thuoc_ton_it,
        trang_thai_stat=trang_thai_stat,
        thang=thang, nam=nam, thang_num=thang_num
    )


# ─────────────────────────────────────────────────────────────
# DANH SÁCH BÁC SĨ
# ─────────────────────────────────────────────────────────────
@app.route("/bac-si")
@login_required
def bac_si():
    search = request.args.get("q", "").strip()
    if search:
        ds = query_all(
            """SELECT *, (SELECT COUNT(*) FROM HoSoBenhAn WHERE MaBS=b.MaBS) AS SoLuotKham
               FROM BacSi b WHERE HoTen LIKE ? OR ChuyenKhoa LIKE ? OR MaBS LIKE ?
               ORDER BY MaBS""",
            (f"%{search}%", f"%{search}%", f"%{search}%")
        )
    else:
        ds = query_all(
            """SELECT *, (SELECT COUNT(*) FROM HoSoBenhAn WHERE MaBS=b.MaBS) AS SoLuotKham
               FROM BacSi b ORDER BY MaBS"""
        )
    return render_template("bac_si.html", ds=ds, search=search)


# ─────────────────────────────────────────────────────────────
# DANH SÁCH NHÂN VIÊN
# ─────────────────────────────────────────────────────────────
@app.route("/nhan-vien")
@login_required
def nhan_vien():
    ds = query_all("SELECT MaNV, HoTen, VaiTro, TaiKhoan FROM NhanVien ORDER BY MaNV")
    return render_template("nhan_vien.html", ds=ds)


# ─────────────────────────────────────────────────────────────
# AJAX: Tra cứu CCCD
# ─────────────────────────────────────────────────────────────
@app.route("/api/tra-cuu-cccd")
@login_required
def tra_cuu_cccd():
    from flask import jsonify
    cccd = request.args.get("cccd", "").strip()
    bn = query_one("SELECT * FROM BenhNhan WHERE CCCD = ?", (cccd,))
    if bn:
        # Chuyển date thành string
        for k, v in bn.items():
            if hasattr(v, "strftime"):
                bn[k] = v.strftime("%Y-%m-%d")
        return jsonify({"found": True, "data": bn})
    return jsonify({"found": False})


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)
