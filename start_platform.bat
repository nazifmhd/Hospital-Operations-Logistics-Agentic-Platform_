@echo off
echo Starting Hospital Supply Platform with LLM Integration...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo 1. Starting Backend Server...
cd backend\api
start cmd /k "python professional_main_smart.py"
echo.
echo 2. Starting Frontend...
cd ..\..\dashboard\supply_dashboard
start cmd /k "npm start"
echo.
echo ✅ Both servers starting...
echo Your chatbot is ready with REAL Gemini API responses!
echo.
pause
