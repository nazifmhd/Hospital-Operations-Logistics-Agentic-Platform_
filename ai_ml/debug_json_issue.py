#!/usr/bin/env python3
"""
Debug JSON Serialization Issue
"""

import asyncio
import json
import sys
import os
from pathlib import Path

async def debug_json_issue():
    print("🔍 Debugging JSON Serialization Issue")
    print("=" * 50)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        # Test the exact "hi" message that's causing issues
        print("📝 Testing message: 'hi'")
        
        # Get the response
        response = await process_agent_conversation("hi", "test_user", "test_session")
        
        print(f"✅ Response received: {type(response)}")
        print(f"📊 Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # Check each field for JSON serializability
        if isinstance(response, dict):
            for key, value in response.items():
                try:
                    json.dumps({key: value})
                    print(f"   ✅ {key}: {type(value)} - JSON serializable")
                except Exception as e:
                    print(f"   ❌ {key}: {type(value)} - NOT JSON serializable: {e}")
                    if hasattr(value, '__dict__'):
                        print(f"      Object details: {value.__dict__}")
                    else:
                        print(f"      Value: {value}")
        
        # Try full JSON serialization
        try:
            json_response = json.dumps(response, indent=2)
            print(f"✅ Full JSON serialization successful!")
        except Exception as e:
            print(f"❌ Full JSON serialization failed: {e}")
            
            # Try with default=str
            try:
                json_response = json.dumps(response, indent=2, default=str)
                print(f"✅ JSON serialization with default=str successful!")
            except Exception as e2:
                print(f"❌ Even with default=str failed: {e2}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(debug_json_issue())
