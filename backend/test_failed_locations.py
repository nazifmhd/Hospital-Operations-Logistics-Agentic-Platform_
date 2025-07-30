#!/usr/bin/env python3
"""Test the two failed locations"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
from comprehensive_ai_agent import process_agent_conversation

async def test_failed_locations():
    print("🔧 TESTING PREVIOUSLY FAILED LOCATIONS")
    print("=" * 50)
    
    # Test the two that failed before
    test_cases = [
        ("Cardiology", "What items do we have in Cardiology?"),
        ("Radiology", "What's available in Radiology department?")
    ]
    
    for location, query in test_cases:
        print(f"\n🔍 Testing {location}:")
        print(f"   Query: {query}")
        
        result = await process_agent_conversation(
            user_message=query,
            user_id="test_user",
            session_id=f"test_{location.lower()}"
        )
        
        response = result.get("response", "")
        actions = result.get("actions", [])
        intent = result.get("intent", {})
        entities = intent.get("entities", [])
        
        print(f"   Intent: {intent.get('primary_intent_str', 'unknown')}")
        print(f"   Entities: {entities}")
        print(f"   Actions: {len(actions)} executed")
        
        if actions:
            for action in actions:
                print(f"     - {action.get('action_type', 'unknown')}: {action.get('description', '')}")
        
        # Check if specific data
        has_specific = any([
            "INVENTORY REPORT" in response.upper(),
            "Total Items:" in response,
            "Stock:" in response
        ])
        
        has_generic = any([
            "typically" in response.lower(),
            "generally" in response.lower(),
            "would find" in response.lower()
        ])
        
        status = "✅ WORKING" if has_specific and not has_generic else "❌ GENERIC"
        print(f"   Status: {status}")
        
        if not has_specific:
            print(f"   Response preview: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_failed_locations())
