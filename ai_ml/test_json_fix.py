#!/usr/bin/env python3
"""
Test JSON Serialization Fix
"""

import asyncio
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_ai_agent import process_agent_conversation

async def test_json_serialization():
    """Test that the agent response is JSON serializable"""
    
    print("🧪 Testing JSON Serialization Fix")
    print("=" * 50)
    
    test_message = "hi"
    
    try:
        # Process the conversation
        print(f"📝 Testing message: '{test_message}'")
        response = await process_agent_conversation(test_message, "test_user", "test_session")
        
        print(f"✅ Response generated successfully")
        print(f"📄 Response type: {type(response)}")
        
        # Test JSON serialization
        json_response = json.dumps(response, indent=2)
        print(f"✅ JSON serialization successful!")
        print(f"📊 JSON length: {len(json_response)} characters")
        
        # Test specific fields
        print(f"\n🔍 Response structure:")
        for key, value in response.items():
            print(f"   {key}: {type(value)} - {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
        
        # Show the actual response
        print(f"\n🤖 Agent Response:")
        print(f"   {response.get('response', 'No response')}")
        
        print(f"\n🎯 Intent Analysis:")
        intent = response.get('intent', {})
        print(f"   Primary Intent: {intent.get('primary_intent', 'Unknown')}")
        print(f"   Entities: {intent.get('entities', [])}")
        
        print(f"\n🎉 SUCCESS: JSON serialization issue is fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_serialization())
