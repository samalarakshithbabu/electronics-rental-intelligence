@echo off
REM AI-Powered Electronics Rental and Revenue Intelligence - Server Startup Script
echo Starting AI-Powered Electronics Rental and Revenue Intelligence servers...

REM Start backend in background
start /B python backend\main.py > backend\server.log 2>&1
echo Backend started on port 8000

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend preview
npx vite preview --port 4173 --host 0.0.0.0 > frontend\server.log 2>&1
echo Frontend started on port 4173

echo.
echo Servers running:
echo - Backend API: http://localhost:8000
echo - Frontend: http://localhost:4173
echo.
echo Press Ctrl+C to stop all servers