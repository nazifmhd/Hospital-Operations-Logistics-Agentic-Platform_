#!/usr/bin/env python3
"""
Check supply_items table structure
"""
import asyncio
from database.config import db_manager
from sqlalchemy import text

async def check_supply_structure():
    try:
        async with db_manager.get_async_session() as session:
            # Check table structure
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'supply_items'
                ORDER BY ordinal_position
            """))
            print("Supply items table structure:")
            for row in result:
                print(f"  {row.column_name}: {row.data_type} ({'NULL' if row.is_nullable == 'YES' else 'NOT NULL'})")
                
            # Get sample data
            result = await session.execute(text("SELECT * FROM supply_items LIMIT 3"))
            print("\nSample supply items data:")
            for row in result:
                print(f"  {dict(row._mapping)}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_supply_structure())
