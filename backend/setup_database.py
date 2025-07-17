"""
Database Setup Script for Hospital Supply Management System
Installs dependencies and initializes PostgreSQL database
"""

import subprocess
import sys
import os
import asyncio
import logging

def install_dependencies():
    """Install PostgreSQL dependencies"""
    print("📦 Installing PostgreSQL dependencies...")
    
    requirements = [
        "asyncpg==0.29.0",
        "sqlalchemy[asyncio]==2.0.23", 
        "alembic==1.13.1",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "greenlet==3.0.1"
    ]
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✅ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {requirement}: {e}")
            return False
    
    print("✅ All PostgreSQL dependencies installed successfully")
    return True

def create_env_file():
    """Create .env file with database configuration"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(backend_dir, ".env")
    
    env_content = """# PostgreSQL Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/hospital_supply_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=hospital_supply_db
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# Optional: Async Database URL
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres:password@localhost:5432/hospital_supply_db

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_path}")
        print("📝 Please update the database credentials in .env file as needed")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

async def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        print("🗄️ Initializing database...")
        
        # Add backend directory to path
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Import database modules
        from database.init_db import init_database
        
        # Initialize database
        await init_database()
        print("✅ Database initialized successfully with sample data")
        return True
        
    except ImportError as e:
        print(f"❌ Database modules not found: {e}")
        print("Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("Please ensure PostgreSQL is running and credentials are correct")
        return False

def check_postgresql():
    """Check if PostgreSQL is running"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="password"
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("Please ensure PostgreSQL is installed and running")
        print("Default connection: localhost:5432 with user 'postgres' and password 'password'")
        return False

async def main():
    """Main setup function"""
    print("🚀 Setting up Hospital Supply Management Database System...")
    print("=" * 60)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed. Exiting...")
        return False
    
    print("\n" + "=" * 60)
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Environment file creation failed. Exiting...")
        return False
    
    print("\n" + "=" * 60)
    
    # Step 3: Check PostgreSQL connection
    print("🔍 Checking PostgreSQL connection...")
    if not check_postgresql():
        print("\n📋 PostgreSQL Setup Instructions:")
        print("1. Install PostgreSQL: https://www.postgresql.org/download/")
        print("2. Create database 'hospital_supply_db'")
        print("3. Update credentials in .env file if needed")
        print("4. Run this script again")
        return False
    
    print("\n" + "=" * 60)
    
    # Step 4: Initialize database
    if not await initialize_database():
        print("❌ Database initialization failed")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Start the API server: python professional_main_db.py")
    print("2. Access the API at: http://localhost:8000")
    print("3. View API docs at: http://localhost:8000/docs")
    print("4. Check health status at: http://localhost:8000/health")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
