# MasterPro Copilot 1-Click Launch Script for PowerShell
$Host.UI.RawUI.WindowTitle = "MasterPro Copilot - Launcher"
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "         MASTERPRO COPILOT - HỆ THỐNG TRỢ LÝ AI ERP & POS            " -ForegroundColor Yellow
Write-Host "              KHỞI ĐỘNG HỆ THỐNG TRỌN GÓI (1-CLICK RUN)              " -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Cyan

$WorkspaceRoot = $PSScriptRoot
Set-Location $WorkspaceRoot

# 1. Kiểm tra Python
$PythonExe = Join-Path $WorkspaceRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[LỖI] Không tìm thấy virtualenv tại: $PythonExe" -ForegroundColor Red
    Read-Host "Nhấn Enter để thoát..."
    exit 1
}

# 2. Khởi chạy Backend
Write-Host "[1/3] Đang khởi động Backend FastAPI (Port 8000)..." -ForegroundColor Green
Start-Process -FilePath $PythonExe -ArgumentList "-m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory $WorkspaceRoot

# 3. Khởi chạy Frontend
Write-Host "[2/3] Đang khởi động Frontend React Vite (Port 5173)..." -ForegroundColor Green
$FrontendDir = Join-Path $WorkspaceRoot "frontend"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev -- --host 127.0.0.1" -WorkingDirectory $FrontendDir

# 4. Mở trình duyệt
Write-Host "[3/3] Đang kết nối giao diện Web..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:5173"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "[THÀNH CÔNG] MasterPro Copilot đang chạy nền!" -ForegroundColor Yellow
Write-Host "  - Frontend: http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  - Swagger API: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "=====================================================================" -ForegroundColor Cyan
