#!/usr/bin/env python3
"""
Test comprehensive follow-up conversation handling across different query types
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_comprehensive_followups():
    print("🧪 Testing Comprehensive Follow-up Conversation Handling")
    print("=" * 70)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        # Test scenarios with different query types
        test_scenarios = [
            {
                "name": "Low Stock Query",
                "initial": "do we have any low stock today?",
                "followup": "yes",
                "session": "session_1"
            },
            {
                "name": "Department Query", 
                "initial": "show me ICU inventory status",
                "followup": "yes",
                "session": "session_2"
            },
            {
                "name": "General Inventory Query",
                "initial": "what's our current inventory status?",
                "followup": "give me details", 
                "session": "session_3"
            },
            {
                "name": "Analytics Request",
                "initial": "can you generate an analytics report?",
                "followup": "sure",
                "session": "session_4"
            },
            {
                "name": "Alert Query",
                "initial": "are there any active alerts?",
                "followup": "show me",
                "session": "session_5"
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"{i}️⃣ Testing: {scenario['name']}")
            print("-" * 50)
            
            # Initial query
            print(f"📝 Initial: '{scenario['initial']}'")
            response1 = await process_agent_conversation(
                scenario['initial'], 
                "test_user", 
                scenario['session']
            )
            
            print(f"✅ Response received")
            print(f"🎯 Intent: {response1.get('intent', {}).get('primary_intent_str', 'unknown')}")
            if 'actions' in response1:
                print(f"🔧 Actions: {len(response1['actions'])} action(s)")
                for action in response1['actions']:
                    print(f"   • {action.get('action_type', 'unknown')}")
            
            # Follow-up query
            print(f"📝 Follow-up: '{scenario['followup']}'")
            response2 = await process_agent_conversation(
                scenario['followup'], 
                "test_user", 
                scenario['session']
            )
            
            print(f"✅ Follow-up response received")
            print(f"🎯 Intent: {response2.get('intent', {}).get('primary_intent_str', 'unknown')}")
            if 'actions' in response2:
                print(f"🔧 Actions: {len(response2['actions'])} action(s)")
                for action in response2['actions']:
                    action_desc = action.get('description', 'No description')
                    is_followup = '(follow-up)' in action_desc or '(context follow-up)' in action_desc
                    print(f"   • {action.get('action_type', 'unknown')}: {action_desc}")
                    if is_followup:
                        print(f"     ✅ FOLLOW-UP DETECTED!")
                    else:
                        print(f"     ❌ No follow-up context detected")
            else:
                print(f"     ❌ No actions triggered for follow-up")
            
            # Test JSON serialization
            try:
                json.dumps(response1)
                json.dumps(response2)
                print(f"✅ JSON serialization: SUCCESS")
            except Exception as e:
                print(f"❌ JSON serialization: FAILED - {e}")
            
            print()
        
        print("🎉 COMPREHENSIVE FOLLOW-UP TEST COMPLETED!")
        print("\n📊 SUMMARY:")
        print("This test checks if follow-up context handling works for:")
        print("• Low stock queries")
        print("• Department-specific queries") 
        print("• General inventory queries")
        print("• Analytics requests")
        print("• Alert queries")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comprehensive_followups())
