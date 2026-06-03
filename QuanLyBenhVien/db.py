import pyodbc

# ============================================================
# Kết nối SQL Server — dùng Windows Authentication
# Đổi SERVER= thành tên máy/instance của bạn nếu cần
# Ví dụ: "SERVER=DESKTOP-XYZ\\SQLEXPRESS;" hoặc "SERVER=localhost;"
# ============================================================

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=QuanLyBenhVien;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def get_connection():
    """Trả về kết nối pyodbc tới SQL Server."""
    return pyodbc.connect(CONNECTION_STRING)


def query_all(sql, params=()):
    """Thực thi SELECT, trả danh sách dict."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]


def query_one(sql, params=()):
    """Thực thi SELECT, trả một dict (hoặc None)."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


def execute(sql, params=()):
    """Thực thi INSERT/UPDATE/DELETE, commit và trả rowcount."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
