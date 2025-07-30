#!/usr/bin/env python3
"""
Test the improved low stock conversation flow
"""

import asyncio
import json
import sys
from pathlib import Path

async def test_low_stock_conversation():
    print("🧪 Testing Low Stock Conversation Flow")
    print("=" * 60)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        # Test 1: Initial low stock query
        print("1️⃣ Testing: 'do we have any low stock today?'")
        print("-" * 40)
        
        response1 = await process_agent_conversation("do we have any low stock today?", "test_user", "test_session_1")
        
        print(f"✅ Response received: {type(response1)}")
        print(f"📝 Agent response preview: {response1.get('response', 'No response')[:200]}...")
        
        if 'actions' in response1:
            print(f"🔧 Actions performed: {len(response1['actions'])} action(s)")
            for action in response1['actions']:
                print(f"   • {action.get('action_type', 'unknown')}: {action.get('description', 'No description')}")
        
        print(f"🎯 Intent: {response1.get('intent', {}).get('primary_intent_str', 'unknown')}")
        
        # Test JSON serialization
        try:
            json.dumps(response1)
            print(f"✅ JSON serialization: SUCCESS")
        except Exception as e:
            print(f"❌ JSON serialization: FAILED - {e}")
        
        print("\n" + "=" * 60)
        
        # Test 2: Follow-up "yes" response
        print("2️⃣ Testing follow-up: 'yes'")
        print("-" * 40)
        
        response2 = await process_agent_conversation("yes", "test_user", "test_session_1")
        
        print(f"✅ Response received: {type(response2)}")
        print(f"📝 Agent response preview: {response2.get('response', 'No response')[:200]}...")
        
        if 'actions' in response2:
            print(f"🔧 Actions performed: {len(response2['actions'])} action(s)")
            for action in response2['actions']:
                print(f"   • {action.get('action_type', 'unknown')}: {action.get('description', 'No description')}")
        
        print(f"🎯 Intent: {response2.get('intent', {}).get('primary_intent_str', 'unknown')}")
        
        # Test JSON serialization
        try:
            json.dumps(response2)
            print(f"✅ JSON serialization: SUCCESS")
        except Exception as e:
            print(f"❌ JSON serialization: FAILED - {e}")
        
        print("\n" + "=" * 60)
        
        # Test 3: Direct detailed low stock query
        print("3️⃣ Testing direct query: 'show me detailed low stock items'")
        print("-" * 40)
        
        response3 = await process_agent_conversation("show me detailed low stock items", "test_user", "test_session_2")
        
        print(f"✅ Response received: {type(response3)}")
        print(f"📝 Agent response preview: {response3.get('response', 'No response')[:200]}...")
        
        if 'actions' in response3:
            print(f"🔧 Actions performed: {len(response3['actions'])} action(s)")
            for action in response3['actions']:
                print(f"   • {action.get('action_type', 'unknown')}: {action.get('description', 'No description')}")
        
        print(f"🎯 Intent: {response3.get('intent', {}).get('primary_intent_str', 'unknown')}")
        
        # Test JSON serialization
        try:
            json.dumps(response3)
            print(f"✅ JSON serialization: SUCCESS")
        except Exception as e:
            print(f"❌ JSON serialization: FAILED - {e}")
        
        print("\n" + "🎉 LOW STOCK CONVERSATION TEST COMPLETED!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_low_stock_conversation())
