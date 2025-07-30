#!/usr/bin/env python3
"""
Debug items with missing names/categories
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fixed_database_integration import get_fixed_db_integration

async def debug_missing_data():
    """Debug items with missing names or categories"""
    
    print("DEBUG: Items with Missing Data")
    print("=" * 40)
    
    try:
        db_instance = await get_fixed_db_integration()
        inventory_data = await db_instance.get_inventory_data()
        
        if inventory_data and 'items' in inventory_data:
            items = inventory_data['items']
            print(f"📊 Total items: {len(items)}")
            
            # Find items with missing names
            missing_name_items = []
            missing_category_items = []
            
            for item in items:
                name = item.get('name', '')
                category = item.get('category', '')
                
                if not name or name.strip() == '':
                    missing_name_items.append(item)
                
                if not category or category.strip() == '':
                    missing_category_items.append(item)
            
            print(f"\n🔍 Items with missing names: {len(missing_name_items)}")
            for i, item in enumerate(missing_name_items[:5]):  # Show first 5
                print(f"   {i+1}. Item ID: {item.get('item_id', 'N/A')}")
                print(f"      Name: '{item.get('name', 'NULL')}'")
                print(f"      Category: '{item.get('category', 'NULL')}'")
                print(f"      Location: {item.get('location_id', 'N/A')}")
                print(f"      Stock: {item.get('current_stock', 0)}")
                print()
            
            print(f"\n🔍 Items with missing categories: {len(missing_category_items)}")
            for i, item in enumerate(missing_category_items[:5]):  # Show first 5
                print(f"   {i+1}. Item ID: {item.get('item_id', 'N/A')}")
                print(f"      Name: '{item.get('name', 'NULL')}'")
                print(f"      Category: '{item.get('category', 'NULL')}'")
                print(f"      Location: {item.get('location_id', 'N/A')}")
                print(f"      Stock: {item.get('current_stock', 0)}")
                print()
            
            # Check for any patterns
            all_categories = [item.get('category', '') for item in items]
            unique_categories = list(set(all_categories))
            print(f"\n📋 All unique categories found:")
            for cat in sorted(unique_categories):
                if cat.strip() == '':
                    print(f"   '' (EMPTY) - {all_categories.count(cat)} items")
                else:
                    print(f"   '{cat}' - {all_categories.count(cat)} items")
        
        else:
            print("❌ No inventory data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_missing_data())
