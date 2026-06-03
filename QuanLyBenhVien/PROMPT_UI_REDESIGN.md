# PROMPT CHO CLAUDE CODE — REDESIGN UI WEB APP QUẢN LÝ BỆNH VIỆN

---

## Bối cảnh dự án

Tôi đang có một web app Flask kết nối SQL Server (database tên `QuanLyBenhVien`) để demo
đồ án môn IE103 — Quản lý Thông tin. App hiện tại đã chạy được các chức năng chính
nhưng giao diện còn thô. Yêu cầu của tôi là **redesign toàn bộ giao diện** để trông
giống một hệ thống quản lý bệnh viện thực thụ, **không thay đổi logic backend**.

---

## Yêu cầu tổng thể

Hãy đọc toàn bộ code trong thư mục hiện tại, hiểu cấu trúc Flask app (routes, templates,
db connection), rồi redesign phần **HTML/CSS/JS** theo chuẩn UI bệnh viện hiện đại.
**Không được sửa file Python (app.py, db.py, routes)** — chỉ sửa templates và static files.

---

## Design System cần áp dụng

### Framework
- **Bootstrap 5.3** (CDN) — dùng cho grid, component, utility
- **Bootstrap Icons** (CDN) — icon cho menu và button
- **Google Fonts: Inter** — font chính (clean, professional)

### Bảng màu
```
Primary (Navy-Blue) : #1A3C5E  — sidebar, header, heading chính
Accent (Teal)       : #17A2B8  — button, badge, highlight
Success (Green)     : #28A745  — trạng thái hoàn thành, thanh toán
Warning (Amber)     : #FFC107  — chờ khám, cảnh báo
Danger (Red)        : #DC3545  — lỗi, hủy, quá hạn
Background          : #F4F6F9  — nền trang chính
Card background     : #FFFFFF
Sidebar text        : #FFFFFF / opacity 0.85
Border              : #E2E8F0
```

### Typography
```
Font: Inter (Google Fonts)
Heading trang  : 20px, bold, #1A3C5E
Section title  : 15px, semibold, #1A3C5E
Label/caption  : 12px, #6C757D
Body text      : 14px, #343A40
Table text     : 13px
```

---

## Cấu trúc layout chung (áp dụng cho MỌI trang)

```
┌─────────────────────────────────────────────────────────────┐
│  TOPBAR (64px)   Logo | Tên trang | Thông tin user / logout │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   SIDEBAR    │           MAIN CONTENT                       │
│   (240px)    │           padding: 24px                      │
│              │                                              │
│  - Menu      │                                              │
│    items     │                                              │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### Sidebar (240px, nền #1A3C5E)
- Logo bệnh viện (icon 🏥 + chữ **BV Quản Lý**) ở đầu, padding 20px
- Các menu item với icon Bootstrap Icons:
  - 🏠 `bi-house-fill` — Tổng quan
  - 👤 `bi-person-plus-fill` — Tiếp nhận bệnh nhân
  - 📅 `bi-calendar-check-fill` — Lịch hẹn hôm nay
  - 🗂️ `bi-folder2-open` — Hồ sơ bệnh án
  - 💊 `bi-capsule` — Kê đơn thuốc
  - 🧾 `bi-receipt` — Hóa đơn
  - 📊 `bi-bar-chart-fill` — Báo cáo
- Active item: nền trắng mờ (rgba(255,255,255,0.15)), border-left 3px solid #17A2B8
- Hover: nền trắng mờ (rgba(255,255,255,0.08))
- Text: trắng, font-size 14px

### Topbar (64px, nền trắng, shadow nhẹ)
- Bên trái: tên trang hiện tại (breadcrumb dạng "Tổng quan" hoặc "Tiếp nhận > Bệnh nhân mới")
- Bên phải: avatar icon + tên nhân viên đang đăng nhập + nút Đăng xuất

### Main content
- Nền: #F4F6F9
- Padding: 24px
- Max-width: 100% (fluid)

---

## Thiết kế từng trang cụ thể

### 1. Trang Dashboard (Tổng quan) — `/`

**Stats row** — 4 card ngang:
```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  👥 Bệnh nhân│ │ 📅 Lịch hôm  │ │ 📋 HSBA đang │ │ 💰 Hóa đơn  │
│   [số]       │ │   nay [số]   │ │   xử lý [số] │ │   chưa TT[số]│
│  +X so hôm   │ │              │ │              │ │              │
│   qua        │ │              │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```
Mỗi card: icon lớn bên trái (teal), con số nổi bật (28px bold), sub-text nhỏ.

**Bên dưới** — 2 cột:
- Trái (60%): Bảng **Lịch hẹn hôm nay** — cột: Giờ | Bệnh nhân | Bác sĩ | Trạng thái (badge màu)
- Phải (40%): Bảng **Hóa đơn chưa thanh toán** — cột: Mã HD | Bệnh nhân | Số tiền

---

### 2. Trang Tiếp nhận bệnh nhân — `/tiep-nhan`

Layout 2 bước rõ ràng:

**Step indicator** ở đầu trang:
```
● Bước 1: Kiểm tra bệnh nhân  →  ○ Bước 2: Đặt lịch hẹn
```

**Form card** (nền trắng, border-radius 12px, shadow):
- Tiêu đề: "Tiếp nhận bệnh nhân mới / cũ"
- Input CCCD lớn ở đầu + nút "Kiểm tra"
- Nếu bệnh nhân mới: hiện form đầy đủ (chia 2 cột: HoTen/NgaySinh | GioiTinh/SDT | DiaChi/NhomMau)
- Nếu bệnh nhân cũ: hiện info card màu xanh nhạt với thông tin đã có
- Phần dưới: chọn Bác sĩ (dropdown), Ngày giờ hẹn (datetime), Lý do khám
- Nút submit: "Tạo lịch hẹn" — màu #1A3C5E, full-width

---

### 3. Trang Lịch hẹn hôm nay — `/lich-hen`

**Header row**: "Lịch hẹn — [ngày hôm nay]" + badge tổng số lịch

**Bảng danh sách** kiểu timeline card:
```
┌─────────────────────────────────────────────────────────────┐
│ 08:30  │ [Avatar initials]  Nguyễn Văn A    │ BS. Trần B   │
│        │ Lý do: Khám tổng quát              │ [Chờ khám]   │
├─────────────────────────────────────────────────────────────┤
│ 09:00  │ [Avatar]  Lê Thị C                 │ BS. Phạm D   │
│        │ Lý do: Đau đầu                     │ [Đang khám]  │
└─────────────────────────────────────────────────────────────┘
```
Badge trạng thái: "Chờ khám" (warning/amber), "Đang khám" (teal), "Hoàn thành" (green), "Đã hủy" (gray)

Nút hành động trên mỗi dòng: **"Bắt đầu khám"** (mở sang trang HSBA)

---

### 4. Trang Khám bệnh / Hồ sơ bệnh án — `/kham-benh/<MaLich>`

Layout 2 cột:

**Cột trái (35%) — Patient card** (sticky):
- Avatar tên viết tắt (circle, màu teal)
- Tên, tuổi, nhóm máu — nổi bật
- CCCD, SDT, Địa chỉ — text nhỏ hơn
- "Tiền sử bệnh" — box xám nhạt

**Cột phải (65%) — Form khám**:
- Card "Chẩn đoán" — textarea lớn (5 rows)
- Card "Triệu chứng" — textarea (4 rows)
- Card "Ghi chú" — textarea (3 rows)
- Nút: "Lưu hồ sơ" (primary) + "Kê đơn thuốc" (outline teal)

---

### 5. Trang Kê đơn thuốc — `/ke-don/<MaHoSo>`

**Bên trái (40%)** — Danh sách thuốc trong kho:
- Thanh search thuốc
- List card: Tên thuốc | Đơn vị | Tồn kho | Giá
- Mỗi item có nút **"+ Thêm vào đơn"**
- Badge đỏ nếu tồn kho thấp (<10)

**Bên phải (60%)** — Đơn thuốc đang soạn:
- Tiêu đề "Đơn thuốc — [tên bệnh nhân]"
- Bảng thuốc đã chọn: Tên | Liều dùng | Tần suất | SL | Thành tiền | Xóa
- Hướng dẫn sử dụng chung (textarea)
- Footer: Tổng tiền thuốc + Nút **"Hoàn tất kê đơn"**

---

### 6. Trang Hóa đơn — `/hoa-don/<MaHoSo>`

Layout giống phiếu hóa đơn thực tế:

```
┌─────────────────────────────────────────────────────────────┐
│           🏥 BỆNH VIỆN QUẢN LÝ          Mã HD: HD001       │
│           HÓA ĐƠN THANH TOÁN           Ngày: 01/06/2026    │
├─────────────────────────────────────────────────────────────┤
│ Bệnh nhân: Nguyễn Văn A    |  Mã BN: BN001                 │
│ Bác sĩ: BS. Trần B         |  Mã HSBA: HS001               │
├─────────────────────────────────────────────────────────────┤
│ CHI TIẾT THUỐC                                              │
│ STT | Tên thuốc | ĐVT | SL | Đơn giá | Thành tiền         │
│ 1   | Paracetamol | Viên | 10 | 2,000 | 20,000            │
├─────────────────────────────────────────────────────────────┤
│                         TỔNG CỘNG: 20,000 VNĐ             │
│                         [Xác nhận đã thanh toán]           │
└─────────────────────────────────────────────────────────────┘
```
- Nền trắng, border nhẹ, có thể in được
- Nút "Xác nhận đã thanh toán" — màu success (#28A745), lớn

---

## CSS conventions

```css
/* Card chuẩn */
.card-hospital {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 24px;
}

/* Badge trạng thái */
.badge-cho-kham   { background: #FFF3CD; color: #856404; border: 1px solid #FFC107; }
.badge-dang-kham  { background: #D1ECF1; color: #0C5460; border: 1px solid #17A2B8; }
.badge-hoan-thanh { background: #D4EDDA; color: #155724; border: 1px solid #28A745; }
.badge-da-huy     { background: #E2E3E5; color: #383D41; border: 1px solid #6C757D; }

/* Button primary */
.btn-hospital {
  background: #1A3C5E;
  color: white;
  border-radius: 8px;
  padding: 10px 24px;
  font-weight: 600;
  border: none;
}
.btn-hospital:hover { background: #152f4a; }
```

---

## Flash messages

Thay thế alert mặc định bằng toast notification (Bootstrap 5 toast, góc trên bên phải):
- Success → nền #D4EDDA, icon ✅
- Error → nền #F8D7DA, icon ❌
- Info → nền #D1ECF1, icon ℹ️
- Auto-dismiss sau 4 giây

---

## Base template (`base.html`)

Tạo một `templates/base.html` với sidebar + topbar đầy đủ. Tất cả các trang khác
`{% extends "base.html" %}` và chỉ override block `{% block content %}`.

Sidebar phải highlight đúng menu item đang active dựa trên `request.endpoint`.

---

## Lưu ý quan trọng

1. **Không sửa routes, logic Python, hoặc SQL queries** — chỉ sửa HTML/CSS/JS
2. **Responsive**: trang phải dùng được ở màn hình 1280px trở lên (không cần mobile)
3. **Tất cả form** phải giữ nguyên action URL và field names để không phá vỡ backend
4. **Tiếng Việt** toàn bộ — không dùng text tiếng Anh trong UI
5. **Không dùng thư viện nặng** ngoài Bootstrap 5 + Bootstrap Icons (load qua CDN)
6. Sau khi redesign xong, hãy **chạy thử** `python app.py` và kiểm tra từng route
   có render đúng không, không có lỗi Jinja2 template

---

## Thứ tự thực hiện

1. Đọc toàn bộ code trong thư mục, đặc biệt: `app.py`, `db.py`, `templates/`
2. Tạo `templates/base.html` với layout sidebar + topbar
3. Redesign từng template theo spec trên (bắt đầu từ `index.html` / dashboard)
4. Tạo `static/style.css` cho custom CSS
5. Kiểm tra tất cả trang render đúng

Hãy bắt đầu bằng cách đọc cấu trúc thư mục hiện tại trước khi viết bất kỳ code nào.