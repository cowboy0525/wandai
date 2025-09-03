#!/usr/bin/env python3
"""
Run script for Wand AI Backend
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add the app directory to Python path
backend_dir = Path(__file__).parent
app_dir = backend_dir / "app"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Warning: .env file not found. Please create one based on env_example.txt")
        print("Required environment variables:")
        print("- OPENAI_API_KEY: Your OpenAI API key")
        print("- OPENAI_MODEL: Model to use (default: gpt-4)")
        print("- CHROMA_DB_PATH: Path for ChromaDB (default: ./chroma_db)")
        print("- UPLOAD_DIR: Path for uploads (default: ./uploads)")
        print("- MAX_FILE_SIZE: Max file size in bytes (default: 10485760)")
        print()
    
    # Run the application
    print("Starting Wand AI Backend...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
