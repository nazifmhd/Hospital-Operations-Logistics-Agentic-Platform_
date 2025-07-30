#!/usr/bin/env python3
"""
Final comprehensive test
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import process_agent_conversation

async def final_comprehensive_test():
    """Final test of your query with full response"""
    
    print("FINAL COMPREHENSIVE TEST")
    print("=" * 40)
    
    query = "what are the Inventory Items I have"
    
    print(f"🔍 Query: '{query}'")
    
    try:
        response = await process_agent_conversation(query, user_id="test_user")
        
        if isinstance(response, dict):
            print(f"\n📋 Response Structure:")
            for key, value in response.items():
                if key == 'response':
                    continue  # We'll show this separately
                print(f"   {key}: {type(value)}")
            
            if 'response' in response:
                response_text = response['response']
                print(f"\n💬 FULL RESPONSE:")
                print(f"{response_text}")
                
                # Analysis
                print(f"\n📊 ANALYSIS:")
                if 'Total Items' in response_text:
                    import re
                    total_match = re.search(r'Total Items[:\s]*(\d+)', response_text)
                    if total_match:
                        total = total_match.group(1)
                        print(f"   ✅ Shows {total} total items")
                        
                        if int(total) >= 100:
                            print(f"   🎉 SUCCESS: Comprehensive inventory ({total} items from your database)")
                        else:
                            print(f"   ⚠️  Limited inventory shown")
                
                if any(keyword in response_text.upper() for keyword in ['ITEM-001', 'ITEM-030', 'SURGICAL GLOVES', 'BIRTHING KIT']):
                    print(f"   🎯 Contains your actual database items!")
                
                if 'SURGERY INVENTORY REPORT' in response_text.upper():
                    print(f"   ❌ Still showing Surgery-specific instead of all inventory")
                elif any(dept in response_text.upper() for dept in ['ICU INVENTORY', 'ER INVENTORY', 'PHARMACY INVENTORY']):
                    print(f"   ⚠️  Showing department-specific instead of all inventory")
                else:
                    print(f"   ✅ Not showing department-specific inventory")
        
        else:
            print(f"   ❌ Unexpected response type: {type(response)}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(final_comprehensive_test())
