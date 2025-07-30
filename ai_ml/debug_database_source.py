#!/usr/bin/env python3
"""
Check what's actually in the database to see if there are additional items
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def debug_database_source():
    """Debug what the database integration is actually returning"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    print("DEBUGGING: What's the actual data source?")
    print("=" * 60)
    
    # Get the raw database data to see what's being returned
    try:
        # Import the database integration directly
        import sys
        sys.path.append('../backend')
        from fixed_database_integration import get_fixed_db_integration
        
        db_instance = await get_fixed_db_integration()
        
        # Get raw inventory data
        raw_data = await db_instance.get_inventory_data()
        
        print(f"📊 RAW DATABASE RESPONSE:")
        print(f"   Total items returned: {len(raw_data.get('inventory', []))}")
        
        # Show first few items to see structure
        inventory_items = raw_data.get('inventory', [])
        
        print(f"\n📦 FIRST 10 ITEMS FROM DATABASE:")
        print("-" * 50)
        for i, item in enumerate(inventory_items[:10], 1):
            item_id = item.get('item_id', 'Unknown')
            item_name = item.get('name', 'No Name')
            location = item.get('location_id', 'No Location')
            print(f"{i:2d}. ID: {item_id} | Name: {item_name} | Location: {location}")
        
        # Check ICU-01 specifically
        icu_items = [item for item in inventory_items if item.get('location_id') == 'ICU-01']
        print(f"\n🏥 ICU-01 ITEMS COUNT: {len(icu_items)}")
        
        if len(icu_items) > 31:
            print(f"⚠️  Found {len(icu_items)} items in ICU-01, but you only have 31 in your database")
            print(f"📋 ALL ICU-01 ITEMS:")
            for i, item in enumerate(icu_items, 1):
                item_id = item.get('item_id', 'Unknown')
                item_name = item.get('name', 'No Name')
                print(f"{i:2d}. {item_id} - {item_name}")
                
    except Exception as e:
        print(f"Error accessing database directly: {e}")
        
        # Alternative: Check if there's mock data generation
        print(f"\n🔍 ALTERNATIVE CHECK:")
        print(f"The chatbot might be generating additional descriptive names")
        print(f"for your ITEM-001, ITEM-002, etc. format")

if __name__ == "__main__":
    asyncio.run(debug_database_source())
