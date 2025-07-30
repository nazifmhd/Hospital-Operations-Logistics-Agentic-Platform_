#!/usr/bin/env python3
"""
Test the specific 12 database locations mentioned by the user
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def test_12_database_locations():
    """Test the exact 12 locations the user mentioned"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    # Your exact 12 locations
    locations = [
        "ONCOLOGY",
        "CARDIOLOGY", 
        "PHARMACY",
        "LAB-01",
        "ER-01",
        "ICU-02",
        "ICU-01",
        "WAREHOUSE",
        "MATERNITY",
        "SURGERY-01",
        "SURGERY-02",
        "PEDIATRICS"
    ]
    
    print("TESTING 12 DATABASE LOCATIONS FOR ACTUAL DATA")
    print("=" * 65)
    
    for i, location in enumerate(locations, 1):
        print(f"\n📍 Location {i:2d}/12: {location}")
        print("-" * 50)
        
        query = f"What's the current inventory status in {location}?"
        
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            
            # Extract key data from response
            if "INVENTORY REPORT" in response:
                # Parse structured response
                lines = response.split('\n')
                total_items = "Unknown"
                items_found = []
                
                for line in lines:
                    if "Total Items" in line and ":" in line:
                        total_items = line.split(":")[-1].strip()
                    elif "**" in line and any(word in line.lower() for word in ["stock:", "quantity:", "unit"]):
                        # Extract item names
                        if "✅" in line:
                            item_name = line.split("✅")[-1].split("**")[1] if "**" in line else line.split("✅")[-1].strip()
                            items_found.append(item_name.strip())
                
                print(f"✅ STRUCTURED DATA FOUND")
                print(f"   📊 Total Items: {total_items}")
                if items_found:
                    print(f"   📦 Sample Items:")
                    for item in items_found[:3]:  # Show first 3 items
                        print(f"      • {item}")
                    if len(items_found) > 3:
                        print(f"      ... and {len(items_found) - 3} more items")
                else:
                    print(f"   📦 Items: Data structure detected")
                    
            elif any(keyword in response.lower() for keyword in ["supplies", "equipment", "items", "inventory"]):
                # Parse general response
                print(f"✅ GENERAL INVENTORY DATA")
                if "range of" in response.lower():
                    print("   📦 Equipment and supplies available")
                if any(item in response.lower() for item in ["equipment", "supplies", "devices", "materials"]):
                    print("   🔧 Medical equipment and supplies listed")
                    
            else:
                print(f"❌ NO INVENTORY DATA DETECTED")
                
            # Show response preview
            preview = response[:150].replace('\n', ' ')
            print(f"   💬 Preview: {preview}...")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n" + "=" * 65)
    print("✅ TEST COMPLETED - All 12 locations checked for actual data")
    print("=" * 65)

if __name__ == "__main__":
    asyncio.run(test_12_database_locations())
