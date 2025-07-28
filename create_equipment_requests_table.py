#!/usr/bin/env python3
"""
Create equipment_requests table in the database
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system.database.config import db_manager
from multi_agent_system.database.models import Base, EquipmentRequest

async def create_equipment_requests_table():
    """Create the equipment_requests table"""
    try:
        print("🔧 Initializing database connection...")
        db_manager.initialize_async_engine()
        
        print("📋 Creating equipment_requests table...")
        await db_manager.create_tables()
        
        print("✅ Equipment requests table created successfully!")
        
        # Test the table by checking if it exists
        async with db_manager.get_async_session() as session:
            from sqlalchemy import text
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'equipment_requests'
            """))
            table_exists = result.fetchone()
            
            if table_exists:
                print("✅ Verified: equipment_requests table exists in database")
            else:
                print("❌ Warning: equipment_requests table not found")
                
    except Exception as e:
        print(f"❌ Error creating equipment_requests table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(create_equipment_requests_table())
    if success:
        print("\n🎉 Database setup completed successfully!")
    else:
        print("\n💥 Database setup failed!")
        sys.exit(1)
