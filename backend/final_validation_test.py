#!/usr/bin/env python3
"""Final validation test for both locations"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
from comprehensive_ai_agent import process_agent_conversation

async def test_both_locations():
    print("🧪 FINAL VALIDATION TEST")
    print("=" * 50)
    
    # Test 1: Clinical Laboratory (previously working)
    print("\n1️⃣ Testing Clinical Laboratory:")
    result1 = await process_agent_conversation(
        user_message="What are the inventory items I have in Clinical Laboratory location?",
        user_id="test_user",
        session_id="test_clinical"
    )
    
    response1 = result1.get("response", "")
    actions1 = result1.get("actions", [])
    print(f"   Actions: {len(actions1)} executed")
    print(f"   Contains 'Blood Collection Tubes': {'Blood Collection Tubes' in response1}")
    print(f"   Contains 'CLINICAL LABORATORY': {'CLINICAL LABORATORY' in response1.upper()}")
    print(f"   Generic response: {'typically' in response1.lower() or 'generally' in response1.lower()}")
    
    # Test 2: Maternity Ward (newly fixed)
    print("\n2️⃣ Testing Maternity Ward:")
    result2 = await process_agent_conversation(
        user_message="What's the current inventory status in the Maternity Ward?",
        user_id="test_user", 
        session_id="test_maternity"
    )
    
    response2 = result2.get("response", "")
    actions2 = result2.get("actions", [])
    print(f"   Actions: {len(actions2)} executed")
    print(f"   Contains 'Birthing Kit Supplies': {'Birthing Kit Supplies' in response2}")
    print(f"   Contains 'MATERNITY WARD': {'MATERNITY WARD' in response2.upper()}")
    print(f"   Generic response: {'typically' in response2.lower() or 'generally' in response2.lower()}")
    
    # Summary
    print(f"\n🎯 VALIDATION RESULTS:")
    clinical_working = ('Blood Collection Tubes' in response1 and 'CLINICAL LABORATORY' in response1.upper())
    maternity_working = ('Birthing Kit Supplies' in response2 and 'MATERNITY WARD' in response2.upper())
    
    print(f"   ✅ Clinical Laboratory: {'WORKING' if clinical_working else 'FAILED'}")
    print(f"   ✅ Maternity Ward: {'WORKING' if maternity_working else 'FAILED'}")
    print(f"   🏆 Overall Status: {'ALL TESTS PASSED' if clinical_working and maternity_working else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    asyncio.run(test_both_locations())
