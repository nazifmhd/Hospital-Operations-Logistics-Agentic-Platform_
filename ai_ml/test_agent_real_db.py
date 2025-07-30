#!/usr/bin/env python3
"""
Test the AI agent with your real database using correct credentials
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import process_agent_conversation

async def test_ai_agent_with_real_db():
    """Test the AI agent with your real database"""
    
    print("TESTING AI AGENT WITH YOUR REAL DATABASE")
    print("=" * 60)
    
    try:
        # Test a maternity ward query (the original issue)
        print(f"\n🔍 Testing: 'What's the current inventory status in the Maternity Ward?'")
        
        response = await process_agent_conversation(
            "What's the current inventory status in the Maternity Ward?",
            user_id="test_user"
        )
        
        print(f"\n📋 AI Agent Response:")
        print(f"   Status: {response.get('status', 'unknown')}")
        print(f"   Type: {response.get('response_type', 'unknown')}")
        
        if 'data' in response:
            data = response['data']
            if isinstance(data, dict) and 'inventory' in data:
                inventory_items = data['inventory']
                print(f"   📦 Found {len(inventory_items)} inventory items")
                
                # Show first few items
                for i, item in enumerate(inventory_items[:3], 1):
                    item_id = item.get('item_id', 'unknown')
                    name = item.get('name', 'unknown')
                    quantity = item.get('quantity', 'unknown')
                    location = item.get('location_id', 'unknown')
                    print(f"      {i}. {item_id}: {name} - {quantity} units @ {location}")
                
                # Check if this is real data or mock data
                if len(inventory_items) > 0:
                    first_item = inventory_items[0]
                    if first_item.get('item_id', '').startswith('ITEM-'):
                        print(f"   ✅ SUCCESS: Using REAL database data!")
                    else:
                        print(f"   ⚠️  WARNING: Still using mock/demo data")
            else:
                print(f"   ⚠️  No inventory data in response")
        
        # Show the actual response message
        response_message = response.get('message', 'No message')
        print(f"\n💬 Full Response Message:")
        print(f"   {response_message[:200]}...")
        
        # Test another location to verify
        print(f"\n🔍 Testing: 'Show me inventory in ICU-01'")
        
        response2 = await process_agent_conversation(
            "Show me inventory in ICU-01",
            user_id="test_user"
        )
        
        print(f"\n📋 ICU-01 Response:")
        if 'data' in response2 and 'inventory' in response2['data']:
            icu_items = response2['data']['inventory']
            print(f"   📦 Found {len(icu_items)} items in ICU-01")
            if len(icu_items) > 0:
                first_icu_item = icu_items[0]
                print(f"   📄 Sample: {first_icu_item.get('item_id')} - {first_icu_item.get('name')}")
        
        print(f"\n🎉 AI Agent is now connected to your real database!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_agent_with_real_db())
