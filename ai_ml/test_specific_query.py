#!/usr/bin/env python3
"""
Test your specific query: "what are the Inventory Items I have"
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import process_agent_conversation

async def test_your_specific_query():
    """Test your exact query to see if it now returns all inventory"""
    
    print("TESTING YOUR SPECIFIC QUERY")
    print("=" * 40)
    
    query = "what are the Inventory Items I have"
    
    print(f"🔍 Query: '{query}'")
    
    try:
        response = await process_agent_conversation(query, user_id="test_user")
        
        if isinstance(response, dict) and 'response' in response:
            response_text = response['response']
            
            print(f"\n📋 Response Analysis:")
            
            # Check if it's showing location-specific or general inventory
            if 'SURGERY INVENTORY REPORT' in response_text.upper():
                print(f"   ❌ STILL BROKEN: Showing Surgery inventory")
            elif 'INVENTORY REPORT' in response_text.upper():
                if any(dept in response_text.upper() for dept in ['ICU', 'ER', 'PHARMACY', 'WAREHOUSE', 'SURGERY', 'MATERNITY']):
                    dept_match = next((dept for dept in ['ICU', 'ER', 'PHARMACY', 'WAREHOUSE', 'SURGERY', 'MATERNITY'] if dept in response_text.upper()), 'UNKNOWN')
                    print(f"   ❌ Location-specific: {dept_match} department (should be ALL inventory)")
                else:
                    print(f"   ✅ FIXED: General inventory response")
            else:
                print(f"   📄 General response (no specific inventory report)")
            
            # Extract total items if mentioned
            import re
            total_match = re.search(r'Total Items:\s*(\d+)', response_text)
            if total_match:
                total_items = int(total_match.group(1))
                print(f"   📊 Total items mentioned: {total_items}")
                
                if total_items >= 25:
                    print(f"   ✅ GOOD: Comprehensive count (likely all inventory)")
                elif total_items <= 20:
                    print(f"   ⚠️  LIMITED: Only {total_items} items (likely single department)")
            
            # Show first part of response
            print(f"\n💬 Response Preview:")
            print(f"   {response_text[:300]}...")
            
            # Check if response mentions your actual data
            if 'ITEM-001' in response_text or 'ITEM-030' in response_text:
                print(f"\n🎯 SUCCESS: Response includes your actual database items!")
            elif any(item in response_text.upper() for item in ['SURGICAL GLOVES', 'BIRTHING KIT', 'IV BAGS']):
                print(f"\n✅ GOOD: Response includes real inventory items")
            else:
                print(f"\n⚠️  Response may not include specific inventory data")
        
        else:
            print(f"   ❌ Unexpected response format: {type(response)}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_your_specific_query())
