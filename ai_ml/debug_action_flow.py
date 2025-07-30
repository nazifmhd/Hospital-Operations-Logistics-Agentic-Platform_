#!/usr/bin/env python3
"""
Debug test to see exactly what actions are being triggered
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import ComprehensiveAIAgent

async def debug_action_flow():
    """Debug what actions are triggered for general inventory queries"""
    
    print("DEBUGGING ACTION FLOW")
    print("=" * 30)
    
    # Create agent instance
    agent = ComprehensiveAIAgent()
    
    # Wait a moment for initialization
    await asyncio.sleep(2)
    
    query = "what are the Inventory Items I have"
    print(f"🔍 Query: '{query}'")
    
    try:
        # Analyze intent
        print(f"\n1️⃣ INTENT ANALYSIS:")
        from comprehensive_ai_agent import ConversationMemory, ConversationContext
        from datetime import datetime
        
        memory = ConversationMemory(
            user_id="test_user",
            session_id="debug_session",
            context_type=ConversationContext.INVENTORY_INQUIRY,
            entities_mentioned=[],
            actions_performed=[],
            preferences={},
            last_updated=datetime.now()
        )
        
        intent_analysis = await agent._analyze_user_intent(query, memory)
        print(f"   Intent: {intent_analysis.get('intent', 'unknown')}")
        print(f"   Entities: {intent_analysis.get('entities', [])}")
        print(f"   Keywords: {intent_analysis.get('keywords', [])}")
        
        # Determine actions
        print(f"\n2️⃣ ACTION DETERMINATION:")
        required_actions = await agent._determine_required_actions(query, intent_analysis, memory)
        
        print(f"   Found {len(required_actions)} actions:")
        for i, action in enumerate(required_actions, 1):
            print(f"   {i}. {action.action_type} - {action.description}")
            print(f"      Parameters: {action.parameters}")
        
        # Execute actions
        print(f"\n3️⃣ ACTION EXECUTION:")
        action_results = {}
        for action in required_actions:
            result = await agent._execute_action(action)
            action_results[action.action_type] = result
            
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"   ❌ {action.action_type}: {result['error']}")
                elif 'inventory' in result:
                    inventory = result['inventory']
                    if isinstance(inventory, dict) and 'items' in inventory:
                        items = inventory['items']
                        print(f"   ✅ {action.action_type}: {len(items)} items")
                    else:
                        print(f"   ✅ {action.action_type}: {type(inventory)}")
                else:
                    print(f"   ✅ {action.action_type}: {list(result.keys()) if isinstance(result, dict) else type(result)}")
        
        print(f"\n4️⃣ SUMMARY:")
        if any('get_overall_inventory' in key for key in action_results.keys()):
            print(f"   ✅ SUCCESS: get_overall_inventory action was triggered")
        elif any('get_inventory_by_location' in key for key in action_results.keys()):
            print(f"   ⚠️  ISSUE: get_inventory_by_location triggered instead")
        else:
            print(f"   ❌ PROBLEM: No inventory actions triggered")
            
        print(f"   Action results keys: {list(action_results.keys())}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_action_flow())
