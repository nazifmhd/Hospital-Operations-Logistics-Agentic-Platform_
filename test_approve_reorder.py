#!/usr/bin/env python3
"""
Test script for the approve reorder functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_approve_workflow():
    """Test the complete auto reorder approval workflow"""
    print("🧪 Testing Auto Reorder Approval Workflow")
    print("=" * 50)
    
    # Step 1: Get current auto reorder status
    print("\n1. Getting current auto reorder status...")
    response = requests.get(f"{BASE_URL}/supply_inventory/auto_reorder_status")
    if response.status_code == 200:
        auto_reorders = response.json().get("auto_reorders", [])
        print(f"   Found {len(auto_reorders)} items in auto reorder queue")
        for item in auto_reorders:
            print(f"   - {item['supply_name']} (ID: {item['id']}) - Status: {item['status']}")
    else:
        print(f"   ❌ Failed to get auto reorder status: {response.status_code}")
        return
    
    # Step 2: Get current purchase orders (before approval)
    print("\n2. Getting current purchase orders (before approval)...")
    response = requests.get(f"{BASE_URL}/supply_inventory/purchase_orders")
    if response.status_code == 200:
        purchase_orders = response.json().get("purchase_orders", [])
        print(f"   Current purchase orders: {len(purchase_orders)}")
    else:
        print(f"   ❌ Failed to get purchase orders: {response.status_code}")
        return
    
    # Step 3: Approve the first pending reorder item
    if auto_reorders:
        pending_items = [item for item in auto_reorders if item['status'] == 'pending']
        if pending_items:
            item_to_approve = pending_items[0]
            print(f"\n3. Approving reorder for '{item_to_approve['supply_name']}'...")
            
            response = requests.post(f"{BASE_URL}/supply_inventory/approve_reorder/{item_to_approve['id']}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Approval successful!")
                print(f"   📦 Order ID: {result.get('order_id')}")
                print(f"   📊 Quantity ordered: {result.get('quantity_ordered')}")
                print(f"   🏷️ Item: {result.get('item_name')}")
                print(f"   📈 Current quantity: {result.get('current_quantity')}")
            else:
                print(f"   ❌ Approval failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return
        else:
            print("\n3. No pending items to approve")
            return
    else:
        print("\n3. No auto reorder items found")
        return
    
    # Step 4: Wait a moment and check purchase orders again
    print("\n4. Checking purchase orders after approval...")
    time.sleep(1)
    response = requests.get(f"{BASE_URL}/supply_inventory/purchase_orders")
    if response.status_code == 200:
        new_purchase_orders = response.json().get("purchase_orders", [])
        print(f"   Purchase orders after approval: {len(new_purchase_orders)}")
        
        # Show any new purchase orders
        if len(new_purchase_orders) > len(purchase_orders):
            print(f"   ✅ New purchase orders created!")
            for order in new_purchase_orders[-1:]:  # Show the latest one
                print(f"   - Order: {order.get('order_number', order.get('id'))}")
                print(f"     Supplier: {order.get('supplier')}")
                print(f"     Status: {order.get('status')}")
                print(f"     Cost: ${order.get('total_cost', 0)}")
        else:
            print(f"   ⚠️ No new purchase orders detected")
    else:
        print(f"   ❌ Failed to get updated purchase orders: {response.status_code}")
    
    # Step 5: Check updated auto reorder status
    print("\n5. Checking updated auto reorder status...")
    response = requests.get(f"{BASE_URL}/supply_inventory/auto_reorder_status")
    if response.status_code == 200:
        updated_auto_reorders = response.json().get("auto_reorders", [])
        print(f"   Auto reorder items after approval: {len(updated_auto_reorders)}")
        pending_count = len([item for item in updated_auto_reorders if item['status'] == 'pending'])
        print(f"   Pending items remaining: {pending_count}")
    else:
        print(f"   ❌ Failed to get updated auto reorder status: {response.status_code}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_approve_workflow()
