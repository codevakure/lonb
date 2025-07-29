@echo off
REM Local Development Setup Script for Commercial Loan Service (Windows)
REM This script sets up and runs the API locally without Docker

echo 🚀 Setting up Commercial Loan Service for Local Development

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo ✅ Python version:
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Copy local environment file
if not exist ".env" (
    echo 📋 Copying local environment configuration...
    copy .env.local .env
    echo ✅ Created .env file from .env.local
) else (
    echo ℹ️  Using existing .env file
)

REM Install dependencies
echo 📚 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo 🎉 Setup complete! You can now run the API locally.
echo.
echo To start the API server:
echo   python main.py
echo.
echo Or with uvicorn directly:
echo   uvicorn main:app --reload --host 127.0.0.1 --port 8000
echo.
echo API will be available at:
echo   • API: http://127.0.0.1:8000
echo   • Docs: http://127.0.0.1:8000/docs
echo   • Health: http://127.0.0.1:8000/health
echo.
echo To run tests:
echo   pytest
echo.
echo To run with coverage:
echo   pytest --cov=. --cov-report=html
echo.
pause
