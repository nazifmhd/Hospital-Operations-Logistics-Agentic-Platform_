#!/usr/bin/env python3
"""
Comprehensive test script to verify all hospital locations work correctly
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

async def test_all_locations():
    """Test all major hospital locations"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    # Test cases for all major hospital locations
    test_cases = [
        "What's the current inventory status in the ICU?",
        "What items are available in the Emergency Room?", 
        "Show me inventory for Surgery department",
        "What supplies do we have in the Pharmacy?",
        "What's in the Oncology department?",
        "Show me Pediatrics inventory",
        "What items are in the Warehouse?",
        "What items do we have in Cardiology?",
        "What's available in Radiology department?"
    ]
    
    print("COMPREHENSIVE HOSPITAL LOCATION TEST")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for i, query in enumerate(test_cases, 1):
        print(f"\nTest {i}/{total}: {query}")
        print("-" * 40)
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            
            # Check if response is generic or specific
            if "I'd be happy to help" in response or "Let me assist you" in response:
                print("❌ GENERIC RESPONSE - Still failing")
                print(f"Response preview: {response[:150]}...")
            elif any(keyword in response.lower() for keyword in ["stock", "quantity", "available", "items", "inventory", "supplies"]):
                print("✅ SPECIFIC INVENTORY DATA - Working correctly")
                print(f"Response preview: {response[:100]}...")
                passed += 1
            else:
                print("⚠️  UNCLEAR - Response type unclear")
                print(f"Response preview: {response[:150]}...")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
    print(f"\n" + "=" * 60)
    print(f"FINAL RESULTS: {passed}/{total} locations working correctly ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 SUCCESS: All hospital locations are working correctly!")
        print("The AI agent now provides specific inventory data for ALL locations.")
    else:
        failed = total - passed
        print(f"⚠️  {failed} locations still need fixes.")
        
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_all_locations())
