#!/usr/bin/env python3
"""
Check what's actually in the supply_items table
"""
import asyncio
import os
import sys

# Import from local database module
from database.config import db_manager
from sqlalchemy import text

async def check_supply_data():
    
    try:
        # db_manager is already initialized
        print("Database connection successful!")
        
        async with db_manager.get_async_session() as session:
            # Check what tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"Available tables: {tables}")
            
            # Check if supply_items table exists and has data
            if 'supply_items' in tables:
                result = await session.execute(text("SELECT COUNT(*) FROM supply_items"))
                count = result.scalar()
                print(f"Supply items count: {count}")
                
                # Get a few sample records
                if count > 0:
                    result = await session.execute(text("""
                        SELECT id, name, sku, category, current_quantity, reorder_point 
                        FROM supply_items 
                        LIMIT 5
                    """))
                    print("Sample supply items:")
                    for row in result:
                        print(f"  {row}")
                else:
                    print("Supply items table is empty!")
                    
                    # Check table structure
                    result = await session.execute(text("""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = 'supply_items'
                        ORDER BY ordinal_position
                    """))
                    print("Supply items table structure:")
                    for row in result:
                        print(f"  {row}")
            else:
                print("supply_items table does not exist!")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_supply_data())
