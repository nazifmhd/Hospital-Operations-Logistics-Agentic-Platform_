#!/usr/bin/env python3
"""
Analyze the actual database structure and verify chatbot accuracy
"""

import asyncio
from comprehensive_ai_agent import ComprehensiveAIAgent

# Your actual database data (parsed from the table you provided)
database_items = {
    "ITEM-001": ["ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-002": ["ER-01", "ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-003": ["ER-01", "ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-004": ["CARDIOLOGY", "ER-01", "ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-005": ["CARDIOLOGY", "ER-01", "ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-006": ["ER-01", "ICU-01", "ICU-02", "PHARMACY", "SURGERY-01", "WAREHOUSE"],
    "ITEM-007": ["ER-01", "ICU-01", "ICU-02", "PHARMACY", "SURGERY-01", "WAREHOUSE"],
    "ITEM-008": ["ER-01", "ICU-01", "SURGERY-01", "SURGERY-02", "WAREHOUSE"],
    "ITEM-009": ["ER-01", "ICU-01", "LAB-01", "WAREHOUSE"],
    "ITEM-010": ["ICU-01", "ICU-02", "SURGERY-01", "WAREHOUSE"],
    "ITEM-011": ["ER-01", "ICU-01", "SURGERY-01", "SURGERY-02", "WAREHOUSE"],
    "ITEM-012": ["CARDIOLOGY", "ER-01", "ICU-01", "WAREHOUSE"],
    "ITEM-013": ["ER-01", "ICU-01", "PHARMACY"],
    "ITEM-014": ["ER-01", "ICU-01", "PHARMACY", "SURGERY-01"],
    "ITEM-015": ["ER-01", "ICU-01", "PHARMACY"],
    "ITEM-016": ["ER-01", "ICU-01", "PHARMACY"],
    "ITEM-017": ["ER-01", "ICU-01", "PHARMACY"],
    "ITEM-018": ["ER-01", "ICU-01", "PHARMACY", "SURGERY-01"],
    "ITEM-019": ["CARDIOLOGY", "ER-01", "ICU-01", "WAREHOUSE"],
    "ITEM-020": ["CARDIOLOGY", "ER-01", "ICU-01", "ICU-02", "WAREHOUSE"],
    "ITEM-021": ["CARDIOLOGY", "ER-01", "ICU-01", "ICU-02", "WAREHOUSE"],
    "ITEM-022": ["ER-01", "ICU-01", "SURGERY-01", "WAREHOUSE"],
    "ITEM-023": ["ER-01", "ICU-01", "LAB-01", "PHARMACY", "WAREHOUSE"],
    "ITEM-024": ["ER-01", "ICU-01", "LAB-01", "PHARMACY", "WAREHOUSE"],
    "ITEM-025": ["ER-01", "ICU-01", "LAB-01", "PHARMACY", "WAREHOUSE"],
    "ITEM-026": ["ICU-01", "WAREHOUSE"],
    "ITEM-027": ["ICU-01", "PEDIATRICS", "WAREHOUSE"],
    "ITEM-028": ["ICU-01", "ICU-02", "WAREHOUSE"],
    "ITEM-029": ["ICU-01", "ONCOLOGY", "WAREHOUSE"],
    "ITEM-030": ["ICU-01", "MATERNITY", "WAREHOUSE"],
    "IV_BAGS_1000ML": ["ER-01", "ICU-01"]
}

async def verify_database_accuracy():
    """Verify that the chatbot accurately reflects the actual database"""
    agent = ComprehensiveAIAgent()
    await agent._initialize_components()
    
    print("DATABASE ACCURACY VERIFICATION")
    print("=" * 70)
    print(f"📊 Database contains: 31 unique items across 12 locations")
    print(f"📊 Total item-location pairs: {sum(len(locations) for locations in database_items.values())}")
    
    # Count items per location from actual database
    location_counts = {}
    for item_id, locations in database_items.items():
        for location in locations:
            location_counts[location] = location_counts.get(location, 0) + 1
    
    print(f"\n📍 ACTUAL DATABASE DISTRIBUTION:")
    print("-" * 50)
    for location in sorted(location_counts.keys()):
        count = location_counts[location]
        print(f"{location:<12} | {count:2d} items")
    
    # Test a few key locations to verify chatbot accuracy
    test_locations = ["ICU-01", "ER-01", "WAREHOUSE", "PHARMACY"]
    
    print(f"\n🔍 CHATBOT VERIFICATION:")
    print("-" * 50)
    
    for location in test_locations:
        expected_count = location_counts.get(location, 0)
        
        query = f"What's the current inventory status in {location}?"
        
        try:
            result = await agent.process_conversation(query)
            response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
            
            # Extract reported count
            reported_count = 0
            if "Total Items" in response:
                for line in response.split('\n'):
                    if "Total Items" in line and ":" in line:
                        count_text = line.split(":")[-1].strip()
                        numbers = [int(s) for s in count_text.split() if s.isdigit()]
                        if numbers:
                            reported_count = numbers[0]
                        break
            
            # Compare
            status = "✅" if reported_count == expected_count else "⚠️"
            print(f"{location:<12} | Expected: {expected_count:2d} | Reported: {reported_count:2d} | {status}")
            
        except Exception as e:
            print(f"{location:<12} | ERROR: {e}")
    
    # Show detailed breakdown for one location
    print(f"\n📋 DETAILED VERIFICATION - ICU-01:")
    print("-" * 50)
    icu_items = [item_id for item_id, locations in database_items.items() if "ICU-01" in locations]
    print(f"Expected items in ICU-01: {len(icu_items)}")
    print("Items that should be in ICU-01:")
    for i, item in enumerate(icu_items, 1):
        print(f"{i:2d}. {item}")
    
    # Test ICU-01 specifically
    query = "Show me the detailed inventory for ICU-01"
    try:
        result = await agent.process_conversation(query)
        response = result.get('response', str(result)) if isinstance(result, dict) else str(result)
        
        print(f"\nChatbot response preview:")
        preview_lines = response.split('\n')[:10]
        for line in preview_lines:
            if line.strip():
                print(f"  {line}")
        print("  ...")
        
    except Exception as e:
        print(f"Error getting detailed ICU-01 data: {e}")

if __name__ == "__main__":
    asyncio.run(verify_database_accuracy())
