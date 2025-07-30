#!/usr/bin/env python3
"""
Verify the total inventory count across all 12 locations
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def verify_total_inventory_count():
    """Check total inventory across all 12 locations"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    # Your 12 database locations
    locations = [
        "ONCOLOGY", "CARDIOLOGY", "PHARMACY", "LAB-01", "ER-01", 
        "ICU-02", "ICU-01", "WAREHOUSE", "MATERNITY", "SURGERY-01", 
        "SURGERY-02", "PEDIATRICS"
    ]
    
    print("INVENTORY COUNT VERIFICATION ACROSS 12 LOCATIONS")
    print("=" * 65)
    
    total_reported_items = 0
    location_details = []
    
    for i, location in enumerate(locations, 1):
        print(f"\n📍 {i:2d}/12: {location}")
        print("-" * 40)
        
        query = f"What's the current inventory status in {location}?"
        
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            
            # Extract item count from response
            item_count = 0
            if "Total Items" in response:
                for line in response.split('\n'):
                    if "Total Items" in line and ":" in line:
                        count_text = line.split(":")[-1].strip()
                        # Extract number from text like "47 different items"
                        numbers = [int(s) for s in count_text.split() if s.isdigit()]
                        if numbers:
                            item_count = numbers[0]
                        break
            
            total_reported_items += item_count
            location_details.append({
                'location': location,
                'count': item_count
            })
            
            print(f"   📦 Items reported: {item_count}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            location_details.append({
                'location': location,
                'count': 0
            })
    
    print(f"\n" + "=" * 65)
    print("INVENTORY DISTRIBUTION SUMMARY")
    print("=" * 65)
    
    # Sort by item count for better visualization
    location_details.sort(key=lambda x: x['count'], reverse=True)
    
    for detail in location_details:
        bar = "█" * (detail['count'] // 5) if detail['count'] > 0 else ""
        print(f"{detail['location']:<12} | {detail['count']:2d} items | {bar}")
    
    print(f"\n📊 TOTAL ITEMS REPORTED: {total_reported_items}")
    print(f"📊 YOUR DATABASE SIZE: 30 items")
    
    if total_reported_items > 30:
        print(f"⚠️  DISCREPANCY DETECTED:")
        print(f"   • Reported: {total_reported_items} items")
        print(f"   • Expected: 30 items")
        print(f"   • This suggests items may be counted multiple times across locations")
        print(f"   • OR the same items exist in multiple locations")
    elif total_reported_items == 30:
        print(f"✅ PERFECT MATCH: Reported count matches your database size")
    else:
        print(f"⚠️  UNDER-REPORTING: Some items may not be captured")
    
    print(f"\n💡 NOTE: In hospital inventory systems, the same item type")
    print(f"   can exist in multiple locations with different quantities.")

if __name__ == "__main__":
    asyncio.run(verify_total_inventory_count())
