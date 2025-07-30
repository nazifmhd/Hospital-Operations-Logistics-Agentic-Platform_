#!/usr/bin/env python3
"""
Test script to verify the previously failed locations now work correctly
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def test_failed_locations():
    """Test the two locations that were failing before"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    # Test cases that were previously failing
    test_cases = [
        "What items do we have in Cardiology?",
        "What's available in Radiology department?"
    ]
    
    print("Testing previously failed locations:")
    print("=" * 50)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 30)
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            print(f"Response: {response[:200]}...")  # Truncate for readability
            
            # Check if response is generic or specific
            if "I'd be happy to help" in response or "Let me assist you" in response:
                print("❌ STILL GENERIC - Fix needed")
            elif any(keyword in response.lower() for keyword in ["stock", "quantity", "available", "items", "inventory"]):
                print("✅ SPECIFIC INVENTORY DATA - Working correctly")
            else:
                print("⚠️  UNCLEAR - Response type unclear")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
        print()

if __name__ == "__main__":
    asyncio.run(test_failed_locations())
