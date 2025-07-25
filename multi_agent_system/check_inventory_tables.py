#!/usr/bin/env python3
"""
Check for inventory-related tables
"""
import asyncio
from database.config import db_manager
from sqlalchemy import text

async def check_inventory_tables():
    try:
        async with db_manager.get_async_session() as session:
            # Check for tables that might contain inventory quantities
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%inventory%'
                ORDER BY table_name
            """))
            inventory_tables = [row[0] for row in result.fetchall()]
            print(f"Inventory-related tables: {inventory_tables}")
            
            # Check if there's a supply_usage_records table
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND (table_name LIKE '%supply%' OR table_name LIKE '%stock%')
                ORDER BY table_name
            """))
            supply_tables = [row[0] for row in result.fetchall()]
            print(f"Supply-related tables: {supply_tables}")
            
            # Check inventory_locations table structure if it exists
            if 'inventory_locations' in inventory_tables:
                result = await session.execute(text("""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name = 'inventory_locations'
                    ORDER BY ordinal_position
                """))
                print("\nInventory locations table structure:")
                for row in result:
                    print(f"  {row.column_name}: {row.data_type}")
                    
                # Sample data
                result = await session.execute(text("SELECT * FROM inventory_locations LIMIT 3"))
                print("\nSample inventory locations data:")
                for row in result:
                    print(f"  {dict(row._mapping)}")
                    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_inventory_tables())
