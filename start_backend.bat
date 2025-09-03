@echo off
echo 🚀 Starting Wand AI Backend Server...
echo.

cd backend
if not exist "app\main.py" (
    echo ❌ Error: Backend directory not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Please create one with your OpenAI API key.
    echo.
)

echo ✅ Backend directory found
echo 🌐 Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo ----------------------------------------
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
