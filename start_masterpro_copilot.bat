@echo off
chcp 65001 >nul
echo =====================================================================
echo          MASTERPRO COPILOT - HỆ THỐNG TRỢ LÝ AI ERP & POS
echo               KHỞI ĐỘNG HỆ THỐNG TRỌN GÓI (1-CLICK RUN)
echo =====================================================================
echo.

cd /d "%~dp0"

echo [1/3] Kiểm tra môi trường Python Backend...
if not exist "backend\.venv\Scripts\python.exe" (
    echo [LỖI] Không tìm thấy virtualenv tại backend\.venv!
    echo Vui lòng tạo virtualenv và cài đặt dependencies trước.
    pause
    exit /b 1
)

echo [2/3] Đang khởi chạy Backend API (FastAPI) trên cổng 8000...
start "MasterPro Copilot - Backend API (Port 8000)" cmd /k "backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Đang khởi chạy Giao diện Frontend (Vite) trên cổng 5173...
cd frontend
start "MasterPro Copilot - Frontend (Port 5173)" cmd /k "npm run dev -- --host 127.0.0.1"

cd ..
echo.
echo =====================================================================
echo [THÀNH CÔNG] Hệ thống MasterPro Copilot đã được khởi động!
echo.
echo - Web App UI:  http://127.0.0.1:5173
echo - API Docs:    http://127.0.0.1:8000/docs
echo - Healthcheck: http://127.0.0.1:8000/health
echo =====================================================================
echo.
echo Đang mở trình duyệt web...
timeout /t 3 >nul
start http://127.0.0.1:5173

pause
