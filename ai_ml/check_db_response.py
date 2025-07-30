#!/usr/bin/env python3
"""
Check the actual database response format
"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

async def check_database_response():
    """Check what the database actually returns"""
    
    print("CHECKING DATABASE RESPONSE FORMAT")
    print("=" * 50)
    
    try:
        from fixed_database_integration import get_fixed_db_integration
        
        # Get database instance
        db_instance = await get_fixed_db_integration()
        print("✅ Database integration loaded")
        
        # Test get_inventory_data method
        inventory_data = await db_instance.get_inventory_data()
        
        print(f"📊 Full Database Response:")
        print(f"   Type: {type(inventory_data)}")
        print(f"   Keys: {list(inventory_data.keys())}")
        
        # Show each key's content
        for key, value in inventory_data.items():
            print(f"\n📋 Key: '{key}'")
            print(f"   Type: {type(value)}")
            
            if key == 'items' and isinstance(value, list):
                print(f"   Count: {len(value)}")
                if len(value) > 0:
                    print(f"   First item: {value[0]}")
                    print(f"   Sample items:")
                    for i, item in enumerate(value[:3], 1):
                        print(f"      {i}. {item}")
                        
                    # Check if items have your real data
                    if value[0].get('item_id', '').startswith('ITEM-'):
                        print(f"   ✅ SUCCESS: Contains your real data!")
                        
                        # Check for Maternity Ward
                        maternity_items = [item for item in value if 'MATERNITY' in str(item.get('location_id', '')).upper()]
                        print(f"   🏥 Maternity Ward items: {len(maternity_items)}")
                        
                        if maternity_items:
                            print(f"   📋 Maternity inventory:")
                            for item in maternity_items:
                                print(f"      • {item.get('item_id')}: {item.get('name')} - Qty: {item.get('quantity')}")
                    else:
                        print(f"   ⚠️  Still using mock data")
            elif isinstance(value, str):
                print(f"   Value: {value}")
            else:
                print(f"   Value: {str(value)[:100]}...")
        
        # Also test location-specific query
        print(f"\n🔍 Testing location-specific query...")
        
        try:
            # Check if there's a method for location-specific data
            if hasattr(db_instance, 'get_location_inventory'):
                location_data = await db_instance.get_location_inventory('MATERNITY-01')
                print(f"📍 Location-specific data: {location_data}")
            elif hasattr(db_instance, 'get_inventory_by_location'):
                location_data = await db_instance.get_inventory_by_location('MATERNITY-01')
                print(f"📍 Location-specific data: {location_data}")
            else:
                print(f"   ⚠️  No location-specific method found")
        except Exception as e:
            print(f"   ⚠️  Location query failed: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_database_response())
