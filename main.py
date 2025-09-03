#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def check_prerequisites():
    print("🔍 Checking prerequisites...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found!")
        print("   Please ensure you're in the project root directory.")
        return False
    
    app_path = backend_path / "app"
    if not app_path.exists():
        print("❌ App directory not found in backend!")
        return False
    
    main_path = app_path / "main.py"
    if not main_path.exists():
        print("❌ main.py not found in backend/app!")
        return False
    
    env_path = Path(".env")
    if not env_path.exists():
        print("⚠️  .env file not found!")
        print("   Please create .env file with your OpenAI API key.")
        print("   Example format:")
        print("   OPENAI_API_KEY=your_api_key_here")
        return False
    
    print("✅ All prerequisites met!")
    return True

def start_server():
    print("🚀 Starting Wand AI Backend Server...")
    
    try:
        os.chdir("backend")
        print(f"📁 Working directory: {os.getcwd()}")
        
        print("🌐 Starting server on http://localhost:8000")
        print("📚 API docs will be available at http://localhost:8000/docs")
        print("🏥 Health check at http://localhost:8000/health")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user.")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def show_help():
    print("""
🚀 Wand AI - Multi-Agent Knowledge Base with Task Execution

USAGE:
    python main.py                    # Start the backend server
    python main.py --help            # Show this help message
    python main.py --check           # Check prerequisites only

ALTERNATIVE STARTUP METHODS:
    PowerShell: .\\start_backend.ps1
    Windows:    start_backend.bat
    Manual:     cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

FEATURES:
    ✅ Multi-Agent Task Solver (Challenge 1)
    ✅ AI-Powered Knowledge Base (Challenge 2)
    ✅ Real Tool Integration (7 tools)
    ✅ Context Sharing & Hallucination Prevention
    ✅ Progress Tracking & Real-time Updates

QUICK TEST:
    1. Start server: python main.py
    2. Open browser: http://localhost:8000/health
    3. Expected: {"status": "healthy"}

NEED HELP?
    - Check README.md for detailed documentation
    - Check QUICKSTART.md for quick setup
    - Use startup scripts for easiest experience
""")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            show_help()
            return
        elif sys.argv[1] == "--check":
            if check_prerequisites():
                print("✅ All checks passed! Ready to start server.")
            else:
                print("❌ Prerequisites check failed!")
            return
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            show_help()
            return
    
    print("🎯 Wand AI - Multi-Agent Knowledge Base with Task Execution")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n❌ Cannot start server. Please fix the issues above.")
        print("\n💡 Try these solutions:")
        print("   1. Ensure you're in the project root directory")
        print("   2. Create .env file with your OpenAI API key")
        print("   3. Use startup scripts: .\\start_backend.ps1")
        return
    
    success = start_server()
    
    if success:
        print("✅ Server stopped successfully.")
    else:
        print("❌ Server encountered an error.")

if __name__ == "__main__":
    main()
