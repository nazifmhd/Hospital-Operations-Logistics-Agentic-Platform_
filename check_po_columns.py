#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('.')
from database.config import db_manager
from sqlalchemy import text

async def check_columns():
    try:
        await db_manager.initialize()
        async with db_manager.get_async_session() as session:
            # Check purchase_orders columns
            result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'purchase_orders'"))
            po_columns = [row[0] for row in result.fetchall()]
            print('Purchase Orders Columns:', po_columns)
            
            # Check purchase_order_items columns  
            result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'purchase_order_items'"))
            poi_columns = [row[0] for row in result.fetchall()]
            print('Purchase Order Items Columns:', poi_columns)
            
            # Check supply_items columns
            result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'supply_items'"))
            si_columns = [row[0] for row in result.fetchall()]
            print('Supply Items Columns:', si_columns)
            
    except Exception as e:
        print('Error:', e)

if __name__ == "__main__":
    asyncio.run(check_columns())
