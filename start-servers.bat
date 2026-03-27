@echo off
echo ========================================
echo   TaskFlow - Starting Servers
echo ========================================
echo.

:: Check if backend is running
echo [1/3] Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" cmd /k "uv run uvicorn main:app --reload --port 8000"
timeout /t 5 /nobreak > nul

:: Start AI Agent Server
echo [2/3] Starting AI Agent Server...
cd /d "%~dp0ai-agent"
start "AI Agent Server" cmd /k "uv run uvicorn main:app --reload --port 8001"
timeout /t 5 /nobreak > nul

:: Check if frontend is running
echo [3/3] Starting Frontend Server...
cd /d "%~dp0frontend"
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo   Servers Starting...
echo ========================================
echo.
echo Backend:     http://localhost:8000
echo AI Agent:    http://localhost:8001
echo Frontend:    http://localhost:3000
echo.
echo All servers are running in separate windows.
echo Close those windows to stop the servers.
echo ========================================
echo.
pause
