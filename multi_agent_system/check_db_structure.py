#!/usr/bin/env python3
"""
Check database table structure
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import db_manager
from sqlalchemy import text

async def check_table_structure():
    db_manager.initialize()
    async with db_manager.get_async_session() as session:
        # Check beds table structure
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'beds'
            ORDER BY ordinal_position;
        """))
        columns = result.fetchall()
        print('Beds table structure:')
        for col in columns:
            print(f'  {col.column_name}: {col.data_type}')
        
        # Check if there are any beds
        result = await session.execute(text("SELECT COUNT(*) as count FROM beds"))
        count = result.scalar()
        print(f'\nTotal beds in database: {count}')
        
        if count > 0:
            # Show a sample bed record
            result = await session.execute(text("SELECT * FROM beds LIMIT 1"))
            bed = result.fetchone()
            if bed:
                print(f'Sample bed record: {dict(bed._mapping)}')
    
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(check_table_structure())
