"""
Start script for Hospital Supply Management System with Database Integration
"""

import sys
import os
import asyncio
import logging

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
api_dir = os.path.join(backend_dir, "api")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

def check_dependencies():
    """Check if all dependencies are installed"""
    required_packages = ["asyncpg", "sqlalchemy", "fastapi", "uvicorn"]
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Run setup_database.py first to install dependencies")
        return False
    
    return True

def start_system():
    """Start the hospital supply system"""
    print("🚀 Starting Hospital Supply Management System with Database Integration...")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    try:
        # Import and run the database-integrated API
        os.chdir(api_dir)
        
        # Import the main application
        from professional_main_db import app
        import uvicorn
        
        print("✅ Starting server on http://localhost:8000")
        print("📊 Dashboard: http://localhost:8000/api/v3/dashboard")
        print("📚 API Docs: http://localhost:8000/docs")
        print("❤️ Health Check: http://localhost:8000/health")
        print("\nPress Ctrl+C to stop the server")
        
        # Start the server
        uvicorn.run(
            "professional_main_db:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("Make sure PostgreSQL is running and database is set up")

if __name__ == "__main__":
    start_system()
