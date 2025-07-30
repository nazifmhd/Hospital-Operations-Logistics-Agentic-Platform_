#!/usr/bin/env python3
"""Test script to check Maternity Ward inventory"""

import asyncio
import sys
sys.path.insert(0, '.')
from fixed_database_integration import FixedDatabaseIntegration

async def check_maternity_inventory():
    db = FixedDatabaseIntegration()
    await db.initialize()
    
    # Test location-based query for Maternity Ward
    print("Testing 'Maternity Ward'...")
    result = await db.get_inventory_by_location('Maternity Ward')
    items = result.get('items', [])
    
    print(f'Items found in Maternity Ward: {len(items)}')
    for item in items:
        print(f'  - {item.get("item_name", "Unknown")} (Stock: {item.get("current_stock", 0)})')
    
    # Also try 'MATERNITY' location ID
    print("\nTesting 'MATERNITY'...")
    result2 = await db.get_inventory_by_location('MATERNITY')
    items2 = result2.get('items', [])
    
    print(f'Items found in MATERNITY location: {len(items2)}')
    for item in items2:
        print(f'  - {item.get("item_name", "Unknown")} (Stock: {item.get("current_stock", 0)})')
    
    # Also try 'maternity' (lowercase)
    print("\nTesting 'maternity'...")
    result3 = await db.get_inventory_by_location('maternity')
    items3 = result3.get('items', [])
    
    print(f'Items found in maternity location: {len(items3)}')
    for item in items3:
        print(f'  - {item.get("item_name", "Unknown")} (Stock: {item.get("current_stock", 0)})')

if __name__ == "__main__":
    asyncio.run(check_maternity_inventory())
