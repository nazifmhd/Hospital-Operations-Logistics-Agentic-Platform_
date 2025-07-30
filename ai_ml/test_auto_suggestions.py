#!/usr/bin/env python3
"""Test script to debug auto-suggestions functionality"""

import asyncio
import json
from comprehensive_ai_agent import get_comprehensive_agent

async def test_auto_suggestions_debug():
    """Test and debug the auto-suggestions functionality"""
    
    print("=== Testing Auto-Suggestions Debug ===")
    
    agent = await get_comprehensive_agent()
    
    # Test query that should trigger auto-suggestions
    test_query = 'Reduce 15 units of surgical gloves in ICU'
    print(f"Query: {test_query}")
    print("-" * 50)
    
    # Process the conversation
    response = await agent.process_conversation(test_query, 'test_user')
    
    # Check the actions performed
    print(f"Actions performed: {len(response['actions'])}")
    for i, action in enumerate(response['actions']):
        print(f"  Action {i+1}: {action['action_type']}")
    
    print("-" * 50)
    
    # Check the response
    response_text = response['response']
    print(f"Response length: {len(response_text)}")
    
    # Look for auto-suggestion keywords
    keywords_to_check = [
        'AUTOMATIC SUGGESTIONS',
        'Inter-Department Transfer',
        'Automatic Reorder',
        'auto_suggestions',
        'Transfer',
        'Reorder'
    ]
    
    print("\nKeyword search in response:")
    for keyword in keywords_to_check:
        found = keyword in response_text
        print(f"  {keyword}: {'✅' if found else '❌'}")
    
    # Print a sample of the response
    print(f"\nFirst 800 characters of response:")
    print(response_text[:800])
    print("...")

if __name__ == "__main__":
    asyncio.run(test_auto_suggestions_debug())
