#!/usr/bin/env python3

import sys
import os
import subprocess
import requests
import json
from pathlib import Path

def check_python_version():
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Too old (3.8+ required)")
        return False

def check_dependencies():
    print("\n📦 Checking Python dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'chromadb', 
        'sentence_transformers', 'PyPDF2', 'pandas', 'matplotlib'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install -r backend/requirements.txt")
        return False
    
    return True

def check_project_structure():
    print("\n📁 Checking project structure...")
    
    required_paths = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/services/enhanced_agent_orchestrator.py",
        "backend/app/services/enhanced_knowledge_base.py",
        "backend/requirements.txt",
        ".env"
    ]
    
    missing_paths = []
    for path in required_paths:
        if Path(path).exists():
            print(f"✅ {path} - OK")
        else:
            print(f"❌ {path} - Missing")
            missing_paths.append(path)
    
    if missing_paths:
        print(f"\n⚠️  Missing files: {', '.join(missing_paths)}")
        return False
    
    return True

def check_environment():
    print("\n🔧 Checking environment configuration...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ OPENAI_API_KEY - Set")
            return True
        else:
            print("❌ OPENAI_API_KEY - Not set")
            print("   Please add your OpenAI API key to the .env file")
            return False
    except ImportError:
        print("❌ python-dotenv - Not installed")
        return False

def check_backend_imports():
    print("\n🔍 Checking backend imports...")
    
    try:
        # Add backend to path
        sys.path.insert(0, str(Path("backend")))
        
        # Test imports
        from app.main import app
        print("✅ app.main - OK")
        
        from app.core.config import settings
        print("✅ app.core.config - OK")
        
        from app.services.enhanced_agent_orchestrator import EnhancedAgentOrchestrator
        print("✅ EnhancedAgentOrchestrator - OK")
        
        from app.services.enhanced_knowledge_base import EnhancedKnowledgeBase
        print("✅ EnhancedKnowledgeBase - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def check_server_startup():
    """Check if server can start"""
    print("\n🚀 Checking server startup...")
    
    try:
        # Change to backend directory
        original_dir = os.getcwd()
        os.chdir("backend")
        
        # Try to start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8001",  # Use different port to avoid conflicts
            "--log-level", "error"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        import time
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            # Try to connect to server
            try:
                response = requests.get("http://127.0.0.1:8001/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Server started successfully")
                    # Kill the test server
                    process.terminate()
                    process.wait()
                    os.chdir(original_dir)
                    return True
                else:
                    print(f"❌ Server responded with status {response.status_code}")
            except requests.exceptions.RequestException:
                print("❌ Could not connect to server")
            
            # Kill the test server
            process.terminate()
            process.wait()
        else:
            print("❌ Server failed to start")
        
        os.chdir(original_dir)
        return False
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def run_health_check():
    """Run the complete health check"""
    print("🏥 Wand AI - System Health Check")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Environment", check_environment),
        ("Backend Imports", check_backend_imports),
        ("Server Startup", check_server_startup)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All systems operational! Your Wand AI is ready to go!")
        print("\n🚀 To start the system:")
        print("   PowerShell: .\\start_backend.ps1")
        print("   Windows:    start_backend.bat")
        print("   Manual:     python main.py")
    else:
        print("⚠️  Some issues detected. Please fix them before starting the system.")
        print("\n💡 Common solutions:")
        print("   1. Install missing packages: pip install -r backend/requirements.txt")
        print("   2. Create .env file with your OpenAI API key")
        print("   3. Ensure you're in the project root directory")
    
    return passed == total

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
