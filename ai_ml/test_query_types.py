#!/usr/bin/env python3
"""
Test different query types to understand agent behavior
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import process_agent_conversation

async def test_query_interpretation():
    """Test how the agent interprets different types of inventory queries"""
    
    print("TESTING QUERY INTERPRETATION")
    print("=" * 50)
    
    test_queries = [
        # General inventory queries (should show ALL items)
        "what are the Inventory Items I have",
        "show me all inventory items",
        "list all items in the hospital",
        "what inventory do we have",
        "show me the complete inventory",
        
        # Location-specific queries (should show specific location)
        "what inventory is in the surgery department",
        "show me ICU inventory",
        "what items are in the maternity ward"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: '{query}'")
        
        try:
            response = await process_agent_conversation(query, user_id="test_user")
            
            if isinstance(response, dict) and 'response' in response:
                response_text = response['response']
                
                # Check what type of response we got
                if 'SURGERY INVENTORY REPORT' in response_text.upper():
                    print(f"   ❌ ISSUE: Showing Surgery inventory instead of all items")
                elif 'INVENTORY REPORT' in response_text.upper() and any(dept in response_text.upper() for dept in ['ICU', 'ER', 'PHARMACY', 'WAREHOUSE']):
                    dept_match = next((dept for dept in ['ICU', 'ER', 'PHARMACY', 'WAREHOUSE', 'SURGERY', 'MATERNITY'] if dept in response_text.upper()), 'UNKNOWN')
                    print(f"   📍 Location-specific: {dept_match} department")
                elif 'Total Items:' in response_text:
                    # Extract total items count
                    import re
                    total_match = re.search(r'Total Items:\s*(\d+)', response_text)
                    if total_match:
                        total_items = total_match.group(1)
                        print(f"   📊 Shows {total_items} items")
                        
                        # Check if it's comprehensive (should be ~30 items total, not 15 from surgery)
                        if int(total_items) >= 25:
                            print(f"   ✅ GOOD: Comprehensive inventory (likely all items)")
                        elif int(total_items) <= 20:
                            print(f"   ⚠️  LIMITED: Only {total_items} items (likely single location)")
                    else:
                        print(f"   📄 Response format unclear")
                else:
                    print(f"   📄 Response: {response_text[:100]}...")
            else:
                print(f"   ❌ Unexpected response format")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n💡 ANALYSIS:")
    print(f"   If general queries like 'what are the Inventory Items I have' are")
    print(f"   showing Surgery inventory instead of ALL items, then the agent's")
    print(f"   intent detection needs to be fixed to distinguish between:")
    print(f"   • General inventory queries → Show ALL items")
    print(f"   • Location-specific queries → Show specific department")

if __name__ == "__main__":
    asyncio.run(test_query_interpretation())
