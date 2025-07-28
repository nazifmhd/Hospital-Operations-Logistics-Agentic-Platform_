#!/usr/bin/env python3
"""
Supply Reorder Tracking Test
Tests where reorders appear after being created in the supply inventory
"""

import requests
import json

def test_reorder_workflow():
    """Test the complete reorder workflow and track where orders appear"""
    print("🔍 SUPPLY REORDER TRACKING TEST")
    print("=" * 50)
    
    print("\n📋 STEP 1: Check initial state")
    
    # Check initial purchase orders
    po_response = requests.get("http://localhost:8000/supply_inventory/purchase_orders")
    initial_orders = po_response.json().get('purchase_orders', []) if po_response.status_code == 200 else []
    print(f"Initial purchase orders: {len(initial_orders)}")
    
    # Check auto reorder status
    auto_response = requests.get("http://localhost:8000/supply_inventory/auto_reorder_status")
    auto_orders = auto_response.json().get('auto_reorders', []) if auto_response.status_code == 200 else []
    print(f"Auto reorder items: {len(auto_orders)}")
    
    print("\n🛒 STEP 2: Create a supply reorder")
    
    # Get supply items to find one to reorder
    query_response = requests.post("http://localhost:8000/supply_inventory/query", 
                                 json={"query": "Show all supply items"})
    
    if query_response.status_code == 200:
        supply_data = query_response.json()
        supply_items = supply_data.get('supply_items', [])
        
        if supply_items:
            # Find a low stock item
            test_item = None
            for item in supply_items:
                if item.get('status') == 'low_stock':
                    test_item = item
                    break
            
            if not test_item and supply_items:
                test_item = supply_items[0]  # Use first item if no low stock
            
            if test_item:
                print(f"Testing reorder for: {test_item['name']}")
                print(f"Current stock: {test_item['current_stock']}")
                
                # Try different reorder endpoints
                reorder_attempts = [
                    {
                        "url": "http://localhost:8000/supply_inventory/execute",
                        "data": {
                            "action": "create_purchase_order",
                            "parameters": {
                                "supply_item_id": test_item['id'],
                                "quantity": 100,
                                "urgent": True
                            }
                        }
                    },
                    {
                        "url": "http://localhost:8000/supply_inventory/trigger_auto_reorder",
                        "data": {}
                    }
                ]
                
                for attempt in reorder_attempts:
                    print(f"\nTrying: {attempt['url']}")
                    try:
                        reorder_response = requests.post(attempt['url'], json=attempt['data'], timeout=10)
                        print(f"Status: {reorder_response.status_code}")
                        
                        if reorder_response.status_code == 200:
                            result = reorder_response.json()
                            print(f"✅ Success: {result}")
                            break
                        else:
                            print(f"❌ Failed: {reorder_response.text[:100]}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                print("\n📊 STEP 3: Check where the order appears")
                
                # Check purchase orders again
                po_response2 = requests.get("http://localhost:8000/supply_inventory/purchase_orders")
                new_orders = po_response2.json().get('purchase_orders', []) if po_response2.status_code == 200 else []
                print(f"Purchase orders after reorder: {len(new_orders)}")
                
                if len(new_orders) > len(initial_orders):
                    print("✅ New purchase order created!")
                    new_order = new_orders[0]
                    print(f"   Order ID: {new_order.get('id', 'N/A')}")
                    print(f"   Order Number: {new_order.get('order_number', 'N/A')}")
                    print(f"   Status: {new_order.get('status', 'N/A')}")
                    print(f"   🎯 LOCATION: Auto Supply Reordering Tab > Purchase Orders Section")
                
                # Check auto reorder status again
                auto_response2 = requests.get("http://localhost:8000/supply_inventory/auto_reorder_status")
                auto_orders2 = auto_response2.json().get('auto_reorders', []) if auto_response2.status_code == 200 else []
                
                print(f"Auto reorder items after trigger: {len(auto_orders2)}")
                if auto_orders2:
                    print("📋 Items in Auto Reorder Status:")
                    for item in auto_orders2:
                        print(f"   - {item.get('supply_name', 'Unknown')} (Status: {item.get('status', 'Unknown')})")
                    print(f"   🎯 LOCATION: Auto Supply Reordering Tab > Auto Reorder Status Table")
    
    print("\n" + "=" * 50)
    print("🎯 WHERE TO FIND YOUR REORDER:")
    print("=" * 50)
    print("\n1. 📍 NAVIGATE TO: Auto Supply Reordering Tab")
    print("   - This is Tab #9 with the shopping cart icon")
    print("   - Located at: http://localhost:3000")
    
    print("\n2. 📋 CHECK THESE SECTIONS:")
    print("   ✅ Auto Reorder Status Table (Top section)")
    print("      - Shows items that need reordering")
    print("      - Displays priority and status")
    print("      - Shows estimated costs and delivery dates")
    
    print("\n   ✅ Purchase Orders Section (Bottom section)")
    print("      - Shows actual purchase orders created")
    print("      - Displays order numbers and suppliers")
    print("      - Allows approve/reject actions")
    
    print("\n3. 🔄 WORKFLOW STAGES:")
    print("   Stage 1: Item appears in 'Auto Reorder Status' (when stock is low)")
    print("   Stage 2: Purchase order created in 'Purchase Orders' (after approval)")
    print("   Stage 3: Order status updates (pending → approved → sent → delivered)")

if __name__ == "__main__":
    test_reorder_workflow()
