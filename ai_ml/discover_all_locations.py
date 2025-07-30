#!/usr/bin/env python3
"""
Comprehensive test to discover all working locations from the AI agent
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def discover_all_locations():
    """Test various location queries to discover all working locations"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    # Test cases based on your original list + common hospital locations
    test_locations = [
        # Your original list
        "ONCOLOGY", "CARDIOLOGY", "PHARMACY", "LAB-01", "ER-01", "ICU-02", "ICU-01", 
        "WAREHOUSE", "MATERNITY", "SURGERY-01", "SURGERY-02", "PEDIATRICS", 
        "SURGERY-03", "RADIOLOGY",
        
        # Additional common variations
        "Clinical Laboratory", "Emergency Room", "Emergency Department", "ER", "ICU",
        "Surgery", "Surgical", "Operating Room", "OR", "Lab", "Laboratory",
        "Maternity Ward", "Pediatric Ward", "Oncology Department", "Cardiology Department",
        "Radiology Department", "Central Warehouse", "Main Warehouse", "Storage",
        "Critical Care", "Intensive Care", "Neonatal", "NICU"
    ]
    
    working_locations = []
    failed_locations = []
    
    print("DISCOVERING ALL WORKING HOSPITAL LOCATIONS")
    print("=" * 70)
    
    for i, location in enumerate(test_locations, 1):
        print(f"\nTest {i:2d}/{len(test_locations)}: {location}")
        print("-" * 50)
        
        query = f"What items are available in {location}?"
        
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            
            # Check if response contains specific inventory data
            if any(keyword in response.lower() for keyword in ["stock", "quantity", "available", "items", "inventory", "supplies"]):
                # Further check if it's not just generic
                if not ("I'd be happy to help" in response or "Let me assist you" in response):
                    working_locations.append(location)
                    print(f"✅ WORKING - Specific inventory data returned")
                    print(f"   Preview: {response[:80]}...")
                else:
                    failed_locations.append(location)
                    print(f"❌ GENERIC - Still returns generic response")
            else:
                failed_locations.append(location)
                print(f"❌ NO INVENTORY - No inventory keywords found")
                
        except Exception as e:
            failed_locations.append(location)
            print(f"❌ ERROR: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"DISCOVERY RESULTS")
    print("=" * 70)
    
    print(f"\n✅ WORKING LOCATIONS ({len(working_locations)}):")
    for i, location in enumerate(working_locations, 1):
        print(f"{i:2d}. {location}")
    
    if failed_locations:
        print(f"\n❌ FAILED LOCATIONS ({len(failed_locations)}):")
        for i, location in enumerate(failed_locations, 1):
            print(f"{i:2d}. {location}")
    
    print(f"\nSUMMARY: {len(working_locations)}/{len(test_locations)} locations working ({len(working_locations)/len(test_locations)*100:.1f}%)")
    
    return working_locations

if __name__ == "__main__":
    asyncio.run(discover_all_locations())
