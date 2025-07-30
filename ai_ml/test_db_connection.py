#!/usr/bin/env python3
"""
Simple test to verify database connection works
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

async def test_database_connection():
    """Test database connection directly"""
    
    print("TESTING DATABASE CONNECTION")
    print("=" * 40)
    
    try:
        from fixed_database_integration import get_fixed_db_integration
        
        # Get database instance
        db_instance = await get_fixed_db_integration()
        print("✅ Database integration loaded")
        
        # Test get_inventory_data method
        inventory_data = await db_instance.get_inventory_data()
        
        print(f"📊 Database Response:")
        print(f"   Type: {type(inventory_data)}")
        
        if isinstance(inventory_data, dict):
            print(f"   Keys: {list(inventory_data.keys())}")
            
            if 'inventory' in inventory_data:
                inventory_items = inventory_data['inventory']
                print(f"   📦 Inventory items: {len(inventory_items)}")
                
                if len(inventory_items) > 0:
                    first_item = inventory_items[0]
                    print(f"   📄 Sample item: {first_item}")
                    
                    # Check if this is your real data
                    if first_item.get('item_id', '').startswith('ITEM-'):
                        print(f"   ✅ SUCCESS: Using your real database!")
                        
                        # Show locations represented
                        locations = set(item.get('location_id', 'unknown') for item in inventory_items)
                        print(f"   📍 Locations found: {sorted(locations)}")
                        
                        # Show items for Maternity Ward specifically
                        maternity_items = [item for item in inventory_items if 'MATERNITY' in item.get('location_id', '').upper()]
                        print(f"   🏥 Maternity Ward items: {len(maternity_items)}")
                        
                        if maternity_items:
                            print(f"   📋 Maternity Ward inventory:")
                            for item in maternity_items[:3]:
                                print(f"      • {item.get('item_id')}: {item.get('name')} - {item.get('quantity')} units")
                    else:
                        print(f"   ⚠️  WARNING: Still using mock data")
            else:
                print(f"   ❌ No 'inventory' key in response")
        else:
            print(f"   ⚠️  Response is not a dictionary: {inventory_data}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database_connection())
