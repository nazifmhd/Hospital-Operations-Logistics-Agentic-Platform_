#!/usr/bin/env python3
"""
Check actual location names in your database
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

async def check_actual_locations():
    """Check what location names actually exist in your database"""
    
    print("CHECKING ACTUAL LOCATION NAMES")
    print("=" * 50)
    
    try:
        from fixed_database_integration import get_fixed_db_integration
        
        # Get database instance
        db_instance = await get_fixed_db_integration()
        
        # Get all inventory data
        inventory_data = await db_instance.get_inventory_data()
        items = inventory_data.get('items', [])
        
        print(f"📊 Total items: {len(items)}")
        
        # Extract all unique location names
        locations = set()
        location_item_count = {}
        
        for item in items:
            location = item.get('location_id', 'Unknown')
            locations.add(location)
            
            if location not in location_item_count:
                location_item_count[location] = 0
            location_item_count[location] += 1
        
        print(f"\n📍 ACTUAL LOCATIONS IN YOUR DATABASE:")
        for location in sorted(locations):
            count = location_item_count[location]
            print(f"   ✅ {location}: {count} items")
        
        # Look for maternity-related locations
        print(f"\n🏥 MATERNITY-RELATED LOCATIONS:")
        maternity_locations = [loc for loc in locations if 'MATERNITY' in loc.upper()]
        
        if maternity_locations:
            for loc in maternity_locations:
                count = location_item_count[loc]
                print(f"   🎯 {loc}: {count} items")
                
                # Show items in this location
                maternity_items = [item for item in items if item.get('location_id') == loc]
                print(f"      📋 Items:")
                for item in maternity_items[:5]:  # Show first 5
                    print(f"         • {item.get('item_id')}: {item.get('name')} - {item.get('current_stock', 'N/A')} units")
        else:
            print(f"   ❌ No locations contain 'MATERNITY'")
            
            # Look for similar names
            similar = [loc for loc in locations if any(keyword in loc.upper() for keyword in ['BIRTH', 'OBSTETRIC', 'LABOR', 'DELIVERY', 'MOTHER', 'MATERNAL'])]
            if similar:
                print(f"   🔍 Similar locations found: {similar}")
            else:
                print(f"   💡 Suggestion: Your maternity ward might be named differently")
                print(f"      Common alternatives: OBSTETRICS, LABOR_DELIVERY, BIRTHING_CENTER")
        
        # Check what the AI agent location mapping expects
        print(f"\n🤖 AI AGENT LOCATION MAPPING CHECK:")
        print(f"   The AI agent might be looking for: MATERNITY-01, MATERNITY_WARD, OBSTETRICS")
        print(f"   Your actual locations: {sorted(locations)}")
        
        # Show mapping suggestions
        suggestions = []
        for actual_loc in locations:
            if any(keyword in actual_loc.upper() for keyword in ['BIRTH', 'MATERNITY', 'OBSTETRIC', 'LABOR']):
                suggestions.append(f"'{actual_loc}' could be the maternity ward")
        
        if suggestions:
            print(f"\n💡 MAPPING SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_actual_locations())
