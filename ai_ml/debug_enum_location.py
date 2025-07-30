#!/usr/bin/env python3
"""
Find the exact source of ConversationContext enum in response
"""

import asyncio
import json
import sys
import os
from pathlib import Path

def find_enum_in_object(obj, path="root"):
    """Recursively find ConversationContext enums in an object"""
    from comprehensive_ai_agent import ConversationContext
    
    if isinstance(obj, ConversationContext):
        print(f"🎯 FOUND ConversationContext enum at: {path} = {obj}")
        return True
    
    if isinstance(obj, dict):
        found = False
        for key, value in obj.items():
            if find_enum_in_object(value, f"{path}.{key}"):
                found = True
        return found
    
    if isinstance(obj, list):
        found = False
        for i, value in enumerate(obj):
            if find_enum_in_object(value, f"{path}[{i}]"):
                found = True
        return found
    
    if hasattr(obj, '__dict__'):
        found = False
        for key, value in obj.__dict__.items():
            if find_enum_in_object(value, f"{path}.{key}"):
                found = True
        return found
    
    return False

async def debug_enum_location():
    print("🔍 Finding ConversationContext enum in response structure")
    print("=" * 60)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        # Test the message that causes the error
        print("📝 Testing: 'what's the inventory status?'")
        
        response = await process_agent_conversation("what's the inventory status?", "test_user", "test_session")
        
        print(f"✅ Response received: {type(response)}")
        
        # Find where the enum is hiding
        print(f"\n🔍 Searching for ConversationContext enums...")
        found = find_enum_in_object(response)
        
        if found:
            print(f"❌ ConversationContext enums found in response structure!")
        else:
            print(f"✅ No ConversationContext enums found in response structure")
            print(f"🤔 This is strange - the error might be elsewhere")
        
        # Try JSON serialization to see exactly where it fails
        try:
            json.dumps(response)
            print(f"✅ JSON serialization successful")
        except Exception as e:
            print(f"❌ JSON serialization failed: {e}")
            
            # Try to identify the specific problematic field
            for key, value in response.items():
                try:
                    json.dumps({key: value})
                    print(f"   ✅ {key}: OK")
                except Exception as e2:
                    print(f"   ❌ {key}: FAILED - {e2}")
                    find_enum_in_object(value, key)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_enum_location())
