#!/usr/bin/env python3
"""
Test the supply inventory query directly
"""
import asyncio
from database.config import db_manager
from sqlalchemy import text

async def test_supply_query():
    try:
        async with db_manager.get_async_session() as session:
            # Test the exact query from the endpoint
            result = await session.execute(text("""
                SELECT 
                    si.id,
                    si.name,
                    si.sku,
                    si.category,
                    si.unit_of_measure,
                    si.unit_cost,
                    si.reorder_point,
                    si.max_stock_level,
                    si.manufacturer,
                    COALESCE(SUM(il.current_quantity), 0) as current_stock,
                    COALESCE(SUM(il.available_quantity), 0) as available_stock,
                    COUNT(il.id) as location_count
                FROM supply_items si
                LEFT JOIN inventory_locations il ON si.id = il.supply_item_id
                GROUP BY si.id, si.name, si.sku, si.category, si.unit_of_measure, 
                         si.unit_cost, si.reorder_point, si.max_stock_level, si.manufacturer
                ORDER BY si.name
                LIMIT 5
            """))
            
            print("Supply query results:")
            rows = result.fetchall()
            print(f"Number of rows returned: {len(rows)}")
            
            for i, row in enumerate(rows):
                print(f"Row {i+1}: {dict(row._mapping)}")
                
            # Also test a simple query to make sure data exists
            result2 = await session.execute(text("SELECT COUNT(*) FROM supply_items"))
            supply_count = result2.scalar()
            print(f"\nTotal supply_items: {supply_count}")
            
            result3 = await session.execute(text("SELECT COUNT(*) FROM inventory_locations"))
            inventory_count = result3.scalar()
            print(f"Total inventory_locations: {inventory_count}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_supply_query())
