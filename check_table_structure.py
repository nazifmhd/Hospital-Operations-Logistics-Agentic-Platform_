#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('./multi_agent_system')
from database.config import db_manager
from sqlalchemy import text

async def check_table_structure():
    try:
        await db_manager.initialize()
        async with db_manager.get_async_session() as session:
            
            # Get purchase_orders structure
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'purchase_orders' 
                ORDER BY ordinal_position
            """))
            print("=== PURCHASE_ORDERS TABLE ===")
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]})")
            
            # Get purchase_order_items structure  
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'purchase_order_items' 
                ORDER BY ordinal_position
            """))
            print("\n=== PURCHASE_ORDER_ITEMS TABLE ===")
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]})")
                
            # Get supply_items structure
            result = await session.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'supply_items' 
                ORDER BY ordinal_position
            """))
            print("\n=== SUPPLY_ITEMS TABLE ===")
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]})")
                
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_table_structure())
