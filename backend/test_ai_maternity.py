#!/usr/bin/env python3
"""Test AI agent with Maternity Ward query"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
from comprehensive_ai_agent import process_agent_conversation

async def test_maternity_query():
    print("Testing AI agent with Maternity Ward query...")
    
    result = await process_agent_conversation(
        user_message="What's the current inventory status in the Maternity Ward?",
        user_id="test_user",
        session_id="maternity_test"
    )
    
    print(f"Response type: {type(result)}")
    print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    
    if isinstance(result, dict):
        # Print debug information
        print(f"\nIntent detected: {result.get('intent', 'Unknown')}")
        print(f"Context: {result.get('context', {})}")
        
        response = result.get("response", "")
        print(f"\nResponse length: {len(response)} characters")
        print(f"Response: {response}")
        
        # Check if actions were performed
        actions = result.get("actions", [])
        print(f"\nActions performed: {len(actions)}")
        for i, action in enumerate(actions):
            print(f"  Action {i+1}:")
            print(f"    - Type: {action.get('action_type', 'Unknown')}")
            print(f"    - Description: {action.get('description', 'No description')}")
            print(f"    - Parameters: {action.get('parameters', {})}")
        
        # Check if response contains specific data
        specific_indicators = ["Birthing Kit Supplies", "36", "stock"]
        contains_specific = any(indicator.lower() in response.lower() for indicator in specific_indicators)
        
        generic_indicators = ["typically", "generally", "can be accessed", "would find"]
        contains_generic = any(indicator.lower() in response.lower() for indicator in generic_indicators)
        
        print(f"\nContains specific data: {contains_specific}")
        print(f"Contains generic language: {contains_generic}")
    else:
        print(f"Unexpected result format: {result}")

if __name__ == "__main__":
    asyncio.run(test_maternity_query())
