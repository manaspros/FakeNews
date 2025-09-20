#!/usr/bin/env python3
"""
AI Corporate Hypocrisy Detector - Startup Script
Starts both the FastAPI backend and React frontend
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if required dependencies are installed"""
    import uvicorn
    import fastapi
    print("✅ Backend dependencies found")

    return True

def start_backend():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend...")
    backend_env = os.environ.copy()
    backend_env.update({
        'PYTHONPATH': str(Path.cwd()),
        'APP_HOST': '0.0.0.0',
        'APP_PORT': '8000',
        'DEBUG': 'True'
    })

    backend_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
    ], env=backend_env, cwd=Path.cwd())

    return backend_process



def wait_for_services():
    """Wait for services to start"""
    print("⏳ Waiting for services to start...")
    time.sleep(5)

    # Check backend
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running at http://localhost:8000")
        else:
            print("⚠️ Backend health check failed")
    except Exception as e:
        print(f"⚠️ Backend connection failed: {e}")


def main():
    """Main startup function"""
    print("=" * 60)
    print("🕵️ AI Corporate Hypocrisy Detector")
    print("=" * 60)

    if not check_requirements():
        return 1

    try:
        # Start backend
        backend_process = start_backend()
        time.sleep(2)  # Give backend time to start

        # Wait for services
        wait_for_services()

        # Open browser
        print("\n🌐 Opening browser...")
        time.sleep(3)
        webbrowser.open("http://localhost:5173")

        print("\n" + "=" * 60)
        print("✅ All services started successfully!")
        print("🔗 Frontend: http://localhost:5173")
        print("🔗 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\n💡 Press Ctrl+C to stop all services")
        print("=" * 60)

        # Wait for user to stop
        try:
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping services...")
            backend_process.terminate()
            frontend_process.terminate()

            # Wait for processes to stop
            backend_process.wait()
            frontend_process.wait()

            print("✅ All services stopped")

    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())