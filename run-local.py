#!/usr/bin/env python3
"""
Local Development Runner for Commercial Loan Service
Run this script to start the API locally without Docker.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def setup_environment():
    """Set up the local development environment"""
    print("🔧 Setting up local development environment...")
    
    # Copy local env file if .env doesn't exist
    if not Path(".env").exists():
        if Path(".env.local").exists():
            import shutil
            shutil.copy(".env.local", ".env")
            print("✅ Created .env from .env.local")
        else:
            print("⚠️  No .env.local found, using environment variables")
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

def install_dependencies():
    """Install required dependencies"""
    print("📚 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Commercial Loan Service API...")
    print("📍 API will be available at: http://127.0.0.1:8000")
    print("📖 API Documentation: http://127.0.0.1:8000/docs")
    print("🏥 Health Check: http://127.0.0.1:8000/health")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except ImportError:
        print("❌ uvicorn not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "uvicorn[standard]"], check=True)
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")

def main():
    """Main function to run local development setup"""
    print("🎯 Commercial Loan Service - Local Development")
    print("=" * 50)
    
    check_python_version()
    setup_environment()
    
    # Check if user wants to install dependencies
    if "--install" in sys.argv or not Path("venv").exists():
        install_dependencies()
    
    start_server()

if __name__ == "__main__":
    main()
