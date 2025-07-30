#!/usr/bin/env python3
"""Comprehensive test for all hospital locations"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
from comprehensive_ai_agent import process_agent_conversation

# Test locations from the user's list
TEST_LOCATIONS = [
    ("ICU", "What's the current inventory status in the ICU?"),
    ("Emergency Room", "What are the inventory items in the Emergency Room?"),
    ("Surgery", "Show me the inventory for Surgery department"),
    ("Pharmacy", "What supplies are available in the Pharmacy?"),
    ("Oncology", "What's the inventory status in Oncology?"),
    ("Cardiology", "What items do we have in Cardiology?"),
    ("Pediatrics", "Show inventory for Pediatrics department"),
    ("Radiology", "What's available in Radiology department?"),
    ("Warehouse", "What's the inventory in the Main Warehouse?"),
]

async def test_all_locations():
    print("🏥 COMPREHENSIVE LOCATION TEST")
    print("=" * 70)
    print("Testing AI agent responses for all hospital departments...")
    print()
    
    results = {}
    
    for location, query in TEST_LOCATIONS:
        print(f"🔍 Testing {location}:")
        print(f"   Query: {query}")
        
        try:
            result = await process_agent_conversation(
                user_message=query,
                user_id="test_user",
                session_id=f"test_{location.lower().replace(' ', '_')}"
            )
            
            response = result.get("response", "")
            actions = result.get("actions", [])
            intent = result.get("intent", {}).get("primary_intent_str", "unknown")
            
            # Check if it's using specific data vs generic response
            has_specific_data = any([
                "INVENTORY REPORT" in response.upper(),
                "Total Items:" in response,
                "Stock:" in response,
                "Categories:" in response
            ])
            
            has_generic_language = any([
                "typically" in response.lower(),
                "generally" in response.lower(),
                "would find" in response.lower(),
                "usually contains" in response.lower()
            ])
            
            # Check action type
            action_types = [action.get("action_type", "") for action in actions]
            
            results[location] = {
                "working": has_specific_data and not has_generic_language,
                "actions": len(actions),
                "action_types": action_types,
                "intent": intent,
                "has_specific_data": has_specific_data,
                "has_generic": has_generic_language,
                "response_length": len(response)
            }
            
            status = "✅ WORKING" if results[location]["working"] else "❌ GENERIC"
            print(f"   Status: {status}")
            print(f"   Actions: {len(actions)} ({', '.join(action_types)})")
            print(f"   Intent: {intent}")
            print(f"   Specific data: {has_specific_data}, Generic: {has_generic_language}")
            print()
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[location] = {"working": False, "error": str(e)}
            print()
    
    # Summary Report
    print("📊 SUMMARY REPORT")
    print("=" * 70)
    
    working_count = sum(1 for result in results.values() if result.get("working", False))
    total_count = len(results)
    
    print(f"✅ Working Locations: {working_count}/{total_count}")
    print(f"❌ Failed Locations: {total_count - working_count}/{total_count}")
    print()
    
    print("📈 DETAILED RESULTS:")
    for location, result in results.items():
        if result.get("working", False):
            print(f"   ✅ {location}: WORKING ({result.get('actions', 0)} actions)")
        else:
            print(f"   ❌ {location}: FAILED ({result.get('error', 'Generic response')})")
    
    print()
    print(f"🎯 OVERALL STATUS: {'ALL SYSTEMS WORKING' if working_count == total_count else f'{working_count}/{total_count} LOCATIONS WORKING'}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_all_locations())
