#!/usr/bin/env python3
"""Test action execution directly"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from comprehensive_ai_agent import ComprehensiveAIAgent
from fixed_database_integration import FixedDatabaseIntegration

async def test_action_execution():
    print("Testing action execution directly...")
    
    # Create the AI agent instance
    ai_agent = ComprehensiveAIAgent()
    
    # Create the action object
    from comprehensive_ai_agent import AgentAction
    action = AgentAction(
        action_id="test-action",
        action_type="get_inventory_by_location",
        description="Get inventory items for location: maternity ward",
        parameters={
            "location_name": "maternity ward",
            "include_details": True,
            "include_summary": True
        },
        priority="high"
    )
    
    print(f"Executing action: {action.action_type}")
    print(f"Parameters: {action.parameters}")
    
    # Execute the action
    result = await ai_agent._execute_action(action)
    
    print(f"\nAction result type: {type(result)}")
    print(f"Action result: {result}")
    
    # Also test the database directly
    print("\n" + "="*50)
    print("Testing database directly:")
    
    db = FixedDatabaseIntegration()
    await db.initialize()
    
    inventory_data = await db.get_inventory_by_location("maternity ward")
    print(f"Database result: {inventory_data}")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_action_execution())
