#!/usr/bin/env python3
"""
Run Script for Health & Fitness Monitor
Starts both backend and frontend servers simultaneously.

Usage:
    python run.py

This will:
1. Start the FastAPI backend on http://localhost:8000
2. Start the Dash frontend on http://localhost:8050
"""

import subprocess
import sys
import time
import os
import signal

# Store process references
processes = []


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n🛑 Shutting down servers...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    print("✅ Servers stopped.")
    sys.exit(0)


def main():
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, "backend")
    frontend_dir = os.path.join(project_root, "frontend")
    
    print("=" * 60)
    print("🏃 Health & Fitness Monitor - Starting Servers")
    print("=" * 60)
    
    # Start Backend
    print("\n📦 Starting Backend (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(backend_process)
    print("   ✅ Backend starting on http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    
    # Wait a moment for backend to initialize
    time.sleep(2)
    
    # Start Frontend
    print("\n🎨 Starting Frontend (Dash)...")
    frontend_process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    processes.append(frontend_process)
    print("   ✅ Frontend starting on http://localhost:8050")
    
    print("\n" + "=" * 60)
    print("🚀 Both servers are running!")
    print("=" * 60)
    print("\n📊 Dashboard: http://localhost:8050")
    print("🔌 API Docs:  http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop both servers\n")
    
    # Keep the script running
    try:
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("⚠️  Backend stopped unexpectedly!")
                break
            if frontend_process.poll() is not None:
                print("⚠️  Frontend stopped unexpectedly!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
