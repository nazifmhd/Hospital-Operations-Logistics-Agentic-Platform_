#!/usr/bin/env python3
"""
Debug database field names
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fixed_database_integration import get_fixed_db_integration

async def debug_db_fields():
    """Debug actual database field names"""
    
    print("DEBUG: Database Field Names")
    print("=" * 40)
    
    try:
        db_instance = await get_fixed_db_integration()
        inventory_data = await db_instance.get_inventory_data()
        
        if inventory_data and 'items' in inventory_data:
            items = inventory_data['items']
            print(f"📊 Total items: {len(items)}")
            
            if items:
                first_item = items[0]
                print(f"\n🔍 First item structure:")
                print(f"   Type: {type(first_item)}")
                print(f"   Keys: {list(first_item.keys())}")
                
                print(f"\n📋 Field values:")
                for key, value in first_item.items():
                    print(f"   {key}: {value} ({type(value)})")
                
                # Check a few more items to see consistency
                if len(items) > 5:
                    print(f"\n🔍 Sample of other items (fields present):")
                    for i in range(1, min(6, len(items))):
                        item = items[i]
                        print(f"   Item {i+1} keys: {list(item.keys())}")
        
        else:
            print("❌ No inventory data found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_db_fields())
