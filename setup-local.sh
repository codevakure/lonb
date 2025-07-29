#!/bin/bash

# Local Development Setup Script for Commercial Loan Service
# This script sets up and runs the API locally without Docker

echo "🚀 Setting up Commercial Loan Service for Local Development"

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
python_version=$(python --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
if [[ $(echo "$python_version < 3.8" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version: $(python --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Copy local environment file
if [ ! -f ".env" ]; then
    echo "📋 Copying local environment configuration..."
    cp .env.local .env
    echo "✅ Created .env file from .env.local"
else
    echo "ℹ️  Using existing .env file"
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs

echo ""
echo "🎉 Setup complete! You can now run the API locally."
echo ""
echo "To start the API server:"
echo "  python main.py"
echo ""
echo "Or with uvicorn directly:"
echo "  uvicorn main:app --reload --host 127.0.0.1 --port 8000"
echo ""
echo "API will be available at:"
echo "  • API: http://127.0.0.1:8000"
echo "  • Docs: http://127.0.0.1:8000/docs"
echo "  • Health: http://127.0.0.1:8000/health"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To run with coverage:"
echo "  pytest --cov=. --cov-report=html"
