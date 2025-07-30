#!/usr/bin/env python3
"""
Debug action results for get_overall_inventory
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import ComprehensiveAIAgent

async def debug_action_results():
    """Debug what get_overall_inventory action actually returns"""
    
    print("DEBUG: get_overall_inventory ACTION RESULTS")
    print("=" * 50)
    
    agent = ComprehensiveAIAgent()
    
    # Test the query processing
    query = "what are the Inventory Items I have"
    
    print(f"🔍 Query: '{query}'")
    
    try:
        result = await agent.process_conversation(query, "test_user")
        
        if isinstance(result, dict):
            print(f"\n📋 Full Result Keys: {list(result.keys())}")
            
            # Check actions
            actions = result.get('actions', [])
            print(f"\n🎯 Actions ({len(actions)}):")
            for i, action in enumerate(actions):
                if hasattr(action, 'action_type'):
                    print(f"  {i+1}. {action.action_type}: {action.description}")
                else:
                    print(f"  {i+1}. {action}")
            
            # Check context (action results)
            context = result.get('context', [])
            print(f"\n📊 Context/Action Results ({len(context)}):")
            for i, ctx in enumerate(context):
                print(f"  {i+1}. {type(ctx)}: {str(ctx)[:200]}...")
                
                # If it's a dict, show its structure
                if isinstance(ctx, dict):
                    print(f"      Keys: {list(ctx.keys())}")
                    if 'get_overall_inventory' in ctx:
                        overall_inv = ctx['get_overall_inventory']
                        print(f"      get_overall_inventory status: {overall_inv.get('status')}")
                        print(f"      get_overall_inventory items: {len(overall_inv.get('items', []))}")
                        print(f"      get_overall_inventory total: {overall_inv.get('total_items', 0)}")
        
        else:
            print(f"   ❌ Unexpected result type: {type(result)}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_action_results())
