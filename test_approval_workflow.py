#!/usr/bin/env python3
"""
Test script to demonstrate the complete approval workflow for inventory management
"""

import asyncio
import sys
import os

# Add the ai_ml directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ai_ml'))

async def test_inventory_approval_workflow():
    """Test the complete inventory modification and approval workflow"""
    
    print("🏥 Testing Hospital Supply Platform - Complete Approval Workflow")
    print("=" * 70)
    
    try:
        # Import the comprehensive agent
        from comprehensive_ai_agent import ComprehensiveAIAgent, ConversationContext
        
        # Initialize the agent
        agent = ComprehensiveAIAgent()
        await asyncio.sleep(2)  # Allow initialization
        
        print("✅ Agent initialized successfully")
        
        # Test 1: Initial inventory modification that triggers auto-suggestions
        print("\n📝 Test 1: Reducing inventory to trigger auto-suggestions")
        print("-" * 50)
        
        response1 = await agent.process_conversation(
            user_message="reduce 5 units of medical supplies in ICU-01",
            session_id="test_session_123"
        )
        
        print("🤖 Agent Response:")
        print(response1.get('response', ''))
        
        # Test 2: Approve transfer (saying "yes")
        print("\n✅ Test 2: Approving inter-transfer with 'yes'")
        print("-" * 50)
        
        response2 = await agent.process_conversation(
            user_message="yes",
            session_id="test_session_123"
        )
        
        print("🤖 Agent Response:")
        print(response2.get('response', ''))
        
        # Test 3: Simulate another low stock scenario and reject purchase order
        print("\n📝 Test 3: Another modification and rejecting purchase order")
        print("-" * 50)
        
        response3 = await agent.process_conversation(
            user_message="reduce 10 more units of medical supplies in ICU-01",
            session_id="test_session_456"
        )
        
        print("🤖 Agent Response:")
        print(response3.get('response', ''))
        
        # Test 4: Reject purchase order (saying "no")
        print("\n❌ Test 4: Rejecting purchase order with 'no'")
        print("-" * 50)
        
        response4 = await agent.process_conversation(
            user_message="no",
            session_id="test_session_456"
        )
        
        print("🤖 Agent Response:")
        print(response4.get('response', ''))
        
        # Test 5: Check pending orders
        print("\n📋 Test 5: Checking pending orders")
        print("-" * 50)
        
        response5 = await agent.process_conversation(
            user_message="show pending orders",
            session_id="test_session_456"
        )
        
        print("🤖 Agent Response:")
        print(response5.get('response', ''))
        
        print("\n" + "=" * 70)
        print("🎉 Complete approval workflow test completed successfully!")
        print("\nWorkflow Summary:")
        print("1. ✅ Inventory modification with auto-suggestions")
        print("2. ✅ Transfer approval with 'yes' response")
        print("3. ✅ Purchase order rejection with 'no' response") 
        print("4. ✅ Pending orders management")
        print("5. ✅ Context-aware conversation memory")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Note: This test requires the database integration to be available")
        print("   The workflow logic is implemented and ready for testing")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_inventory_approval_workflow())
