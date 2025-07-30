#!/usr/bin/env python3
"""Test with actual database items"""

import asyncio
from comprehensive_ai_agent import get_comprehensive_agent

async def test_with_real_item():
    """Test modification with an actual item from the database"""
    
    print("=== Testing with Real Database Item ===")
    
    agent = await get_comprehensive_agent()
    
    # Test with a generic query that should match "Unknown" items
    test_query = 'Reduce 20 units from ICU-01'  # This should match items in ICU-01
    print(f"Query: {test_query}")
    print("-" * 50)
    
    response = await agent.process_conversation(test_query, 'test_user')
    
    print(f"Actions performed: {len(response['actions'])}")
    for i, action in enumerate(response['actions']):
        print(f"  Action {i+1}: {action['action_type']}")
    
    # Check the response
    response_text = response['response']
    print(f"Response length: {len(response_text)}")
    
    # Look for auto-suggestion keywords
    has_suggestions = any(keyword in response_text for keyword in [
        'AUTOMATIC SUGGESTIONS', 'Transfer', 'Reorder', 'auto_suggestions'
    ])
    
    print(f"Has auto-suggestions: {'✅' if has_suggestions else '❌'}")
    
    # Print first part of response
    print(f"\nFirst 600 characters:")
    print(response_text[:600])
    print("...")

if __name__ == "__main__":
    asyncio.run(test_with_real_item())
