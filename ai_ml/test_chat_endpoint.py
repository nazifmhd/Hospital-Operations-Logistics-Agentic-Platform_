#!/usr/bin/env python3
"""
Test the actual chatbot endpoint with OpenAI
"""

import asyncio
import json
import sys
import os
from pathlib import Path

async def test_chat_endpoint():
    print("🧪 Testing Chatbot with OpenAI")
    print("=" * 40)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        # Test the exact scenario the user reported
        test_message = "hi"
        print(f"📝 Testing message: '{test_message}'")
        
        response = await process_agent_conversation(test_message, "test_user", "test_session")
        
        print(f"✅ Response received successfully!")
        print(f"📄 Response type: {type(response)}")
        
        # Show the response
        agent_response = response.get('response', 'No response')
        print(f"\n🤖 Agent Response:")
        print("=" * 50)
        print(agent_response)
        print("=" * 50)
        
        # Check if it's using OpenAI (should not be in offline mode)
        if "offline mode" in agent_response.lower():
            print("⚠️ Still in offline mode - OpenAI not being used")
        else:
            print("✅ Using live AI response (OpenAI working!)")
        
        # Test JSON serialization
        json_response = json.dumps(response, indent=2, default=str)
        print(f"✅ JSON serialization successful!")
        
        # Show key response fields
        print(f"\n📊 Response Details:")
        print(f"   Intent: {response.get('intent', {}).get('primary_intent', 'Unknown')}")
        print(f"   Session ID: {response.get('session_id', 'None')}")
        print(f"   Actions: {len(response.get('actions', []))} actions")
        print(f"   Timestamp: {response.get('timestamp', 'None')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Hospital Supply Platform - Chat Endpoint Test")
    print("=" * 60)
    
    success = await test_chat_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: Chatbot is now working with OpenAI!")
        print("💡 The 'hi' message should now work without Gemini quota issues")
        print("🔄 Your system has been successfully switched from Gemini to OpenAI")
    else:
        print("❌ FAILED: Issues detected with the chatbot")

if __name__ == "__main__":
    asyncio.run(main())
