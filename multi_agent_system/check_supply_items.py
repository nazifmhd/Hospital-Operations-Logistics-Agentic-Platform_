#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import db_manager
from sqlalchemy import text

async def check_supply_items():
    db_manager.initialize()
    async with db_manager.get_async_session() as session:
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'supply_items'
            ORDER BY ordinal_position;
        """))
        columns = result.fetchall()
        print('Supply_items table structure:')
        for col in columns:
            print(f'  {col.column_name}: {col.data_type}')
    await db_manager.close()

asyncio.run(check_supply_items())
