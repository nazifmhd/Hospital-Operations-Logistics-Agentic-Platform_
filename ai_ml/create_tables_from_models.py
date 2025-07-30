#!/usr/bin/env python3
"""
Initialize database using your existing SQLAlchemy models
"""

import sys
import os
import asyncio
import logging

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database.init_db import db_initializer

async def create_tables_from_models():
    """Create all tables using your SQLAlchemy models"""
    
    print("CREATING TABLES FROM YOUR SQLALCHEMY MODELS")
    print("=" * 60)
    
    try:
        # Initialize database using your existing system
        await db_initializer.initialize_database()
        
        print("✅ Tables created successfully!")
        
        # Verify tables were created
        from database.database import db_manager
        await db_manager.initialize()
        
        async with await db_manager.get_async_session() as session:
            from sqlalchemy import text
            
            # Check all tables
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            
            print(f"\n📋 Created {len(tables)} tables:")
            for table in tables:
                print(f"   ✅ {table}")
            
            # Specifically check the key tables
            key_tables = ['item_locations', 'inventory_items', 'locations']
            print(f"\n🔍 Checking key tables:")
            
            for table in key_tables:
                if table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"   ✅ {table}: {count} records (ready for data)")
                else:
                    print(f"   ❌ {table}: NOT FOUND")
        
        print(f"\n🎉 Database is now ready for your 31-item inventory data!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run async function
    asyncio.run(create_tables_from_models())
