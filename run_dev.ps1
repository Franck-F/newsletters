# Dev script to launch Backend and Frontend simultaneously

# 1. Kill any existing processes (optional, but prevents port conflicts)
Stop-Process -Name "uvicorn" -ErrorAction SilentlyContinue
Stop-Process -Name "next-dev" -ErrorAction SilentlyContinue

Write-Host "🚀 Starting Newsletter System..." -ForegroundColor Cyan

# 2. Start Backend
Write-Host "Starting Backend on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload --port 8000"

# 3. Start Frontend
Write-Host "Starting Frontend on port 3000..." -ForegroundColor Yellow
cd frontend
npm run dev
