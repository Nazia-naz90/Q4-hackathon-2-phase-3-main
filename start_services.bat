@echo off
REM Start all services for the AI Todo Assistant

echo Starting AI Todo Assistant services...

REM Start backend API
echo Starting backend API...
cd backend
python main.py