#!/usr/bin/env python3
"""Test script to check available inventory items"""

import asyncio
import sys
sys.path.append('../backend')
from fixed_database_integration import get_fixed_db_integration

async def check_available_items():
    """Check what items are available in the database"""
    
    print("=== Checking Available Inventory Items ===")
    
    try:
        db_instance = await get_fixed_db_integration()
        inventory_data = await db_instance.get_inventory_data()
        
        items = inventory_data.get('items', [])
        print(f"Total items in database: {len(items)}")
        
        if items:
            print("\nFirst 10 items in database:")
            for i, item in enumerate(items[:10]):
                item_name = item.get('item_name', 'Unknown')
                location = item.get('location_id', 'Unknown')
                current_stock = item.get('current_stock', 0)
                min_stock = item.get('minimum_stock', 0)
                print(f"  {i+1}. {item_name} - {location} (Stock: {current_stock}, Min: {min_stock})")
            
            # Look for items in ICU specifically
            icu_items = [item for item in items if 'ICU' in item.get('location_id', '').upper()]
            print(f"\nItems in ICU: {len(icu_items)}")
            for item in icu_items[:5]:
                item_name = item.get('item_name', 'Unknown')
                current_stock = item.get('current_stock', 0)
                min_stock = item.get('minimum_stock', 0)
                print(f"  - {item_name} (Stock: {current_stock}, Min: {min_stock})")
                
        else:
            print("No items found in database")
            
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    asyncio.run(check_available_items())
