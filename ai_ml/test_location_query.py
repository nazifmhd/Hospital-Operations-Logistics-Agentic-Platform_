#!/usr/bin/env python3
"""
Test script for location-based inventory queries
"""
import asyncio
import json
from comprehensive_ai_agent import ComprehensiveAIAgent

async def test_location_query():
    """Test the comprehensive AI agent with location-based inventory query"""
    try:
        print("🤖 Initializing ComprehensiveAIAgent...")
        agent = ComprehensiveAIAgent()
        
        print("🔍 Testing location-based inventory query...")
        response = await agent.process_conversation(
            'what are the inventory items I have in Clinical Laboratory location?'
        )
        
        print("✅ Agent Response:")
        print("=" * 80)
        print(response.get('response', 'No response received'))
        print("=" * 80)
        
        print("\n🔍 Debug Information:")
        print(f"Session ID: {response.get('session_id', 'None')}")
        print(f"Actions Executed: {len(response.get('actions_executed', []))}")
        print(f"Intent Analysis: {response.get('intent_analysis', {}).get('primary_intent', 'Unknown')}")
        
        if response.get('actions_executed'):
            print("\nActions Details:")
            for action in response.get('actions_executed', []):
                print(f"  - {action.get('action_type', 'Unknown')}: {action.get('description', 'No description')}")
                if action.get('parameters'):
                    print(f"    Parameters: {action.get('parameters')}")
        
        # Also test with LAB-01 which we know exists in the database
        print("\n" + "="*80)
        print("🔍 Testing with LAB-01 location...")
        response2 = await agent.process_conversation(
            'show me inventory in LAB-01 location'
        )
        
        print("✅ LAB-01 Response:")
        print("=" * 80)
        print(response2.get('response', 'No response received'))
        print("=" * 80)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_location_query())
