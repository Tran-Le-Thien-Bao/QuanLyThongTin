@echo off
chcp 65001 > nul
set PYTHONUTF8=1
title Quan Ly Benh Vien - IE103.Q22

echo.
echo  =====================================================
echo    HE THONG QUAN LY BENH VIEN - IE103.Q22
echo  =====================================================
echo.

:: Kiem tra Python 3.13
py -3.13 --version > nul 2>&1
if %errorlevel% neq 0 (
    echo  [LOI] Khong tim thay Python 3.13!
    echo        Tai ve tai: https://python.org/downloads
    pause
    exit /b 1
)

:: Cai dat thu vien (bo qua neu da co)
echo  [1/3] Kiem tra thu vien Python...
py -3.13 -m pip install -q flask pyodbc openpyxl 2>nul
if %errorlevel% neq 0 (
    echo  [LOI] Khong the cai dat thu vien. Kiem tra ket noi mang.
    pause
    exit /b 1
)
echo        OK - flask, pyodbc, openpyxl san sang.

:: Import du lieu Excel
echo.
echo  [2/3] Import du lieu tu Data_PhongKham.xlsx...
echo.
py -3.13 "%~dp0\04_Import_Excel.py"
if %errorlevel% neq 0 (
    echo.
    echo  [LOI] Import du lieu that bai!
    echo        Kiem tra:
    echo          - SQL Server dang chay chua?
    echo          - Database QuanLyBenhVien da duoc tao chua?
    echo          - File Data_PhongKham.xlsx co dung vi tri khong?
    pause
    exit /b 1
)

:: Khoi dong Flask trong cua so moi
echo.
echo  [3/3] Khoi dong Flask server...
echo.
start "Flask - Quan Ly Benh Vien" /MIN py -3.13 "%~dp0\app.py"

:: Cho Flask khoi dong xong roi mo trinh duyet
timeout /T 2 /NOBREAK > nul

echo  Mo trinh duyet: http://localhost:5000
echo.
echo  =====================================================
echo    TAI KHOAN DEMO
echo  =====================================================
echo    bacsi     / 123456      ^<-- Bac si (ke don thuoc)
echo    nv01      / 123456aA@   ^<-- Admin
echo    nv02      / 123456aA@   ^<-- Y ta
echo    nv05      / 123456aA@   ^<-- Ke toan
echo  =====================================================
echo.
echo  Nhan phim bat ky de dong cua so nay.
echo  Server van chay trong nen (cua so Flask thu nho).
echo  De dung server: dong cua so 'Flask - Quan Ly Benh Vien'.
echo.

start "" "http://localhost:5000"
pause
