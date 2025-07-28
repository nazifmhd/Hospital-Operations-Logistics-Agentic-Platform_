#!/usr/bin/env python3
"""
Reorder Process Debugging
Identifies and fixes issues with the supply reorder process
"""

import requests
import json

def debug_reorder_process():
    """Debug the complete reorder process to identify issues"""
    print("🔧 REORDER PROCESS DEBUGGING")
    print("=" * 50)
    
    # Test 1: Check if supply inventory query works
    print("\n📋 TEST 1: Supply Inventory Access")
    try:
        response = requests.post("http://localhost:8000/supply_inventory/query", 
                               json={"query": "Show all supply items"}, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('supply_items', [])
            print(f"✅ Found {len(items)} supply items")
            
            low_stock_items = [item for item in items if item.get('status') == 'low_stock']
            print(f"📉 Low stock items: {len(low_stock_items)}")
            
            if low_stock_items:
                sample = low_stock_items[0]
                print(f"   Sample: {sample['name']} (Stock: {sample['current_stock']}, Min: {sample['minimum_stock']})")
        else:
            print(f"❌ Supply inventory query failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Supply inventory error: {e}")
    
    # Test 2: Check reorder execution endpoint
    print("\n🛒 TEST 2: Reorder Execution")
    try:
        test_data = {
            "action": "create_purchase_order",
            "parameters": {
                "supply_item_id": "supply_1", 
                "quantity": 100,
                "urgent": True
            }
        }
        
        response = requests.post("http://localhost:8000/supply_inventory/execute", 
                               json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Reorder execution successful")
            print(f"   Workflow ID: {result.get('result', {}).get('workflow_id', 'N/A')}")
        else:
            print(f"❌ Reorder execution failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Reorder execution error: {e}")
    
    # Test 3: Check auto reorder status
    print("\n📊 TEST 3: Auto Reorder Status Check")
    try:
        response = requests.get("http://localhost:8000/supply_inventory/auto_reorder_status", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('auto_reorders', [])
            print(f"✅ Auto reorder status accessible")
            print(f"   Items in queue: {len(items)}")
            
            for item in items:
                print(f"   - {item.get('supply_name', 'Unknown')}: {item.get('status', 'Unknown')}")
        else:
            print(f"❌ Auto reorder status failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Auto reorder status error: {e}")
    
    # Test 4: Check purchase orders
    print("\n📋 TEST 4: Purchase Orders Check")
    try:
        response = requests.get("http://localhost:8000/supply_inventory/purchase_orders", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('purchase_orders', [])
            print(f"✅ Purchase orders accessible")
            print(f"   Orders found: {len(orders)}")
            
            if orders:
                for order in orders:
                    print(f"   - Order {order.get('order_number', 'N/A')}: {order.get('status', 'Unknown')}")
            else:
                print("   ℹ️  No purchase orders in system")
        else:
            print(f"❌ Purchase orders failed: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Purchase orders error: {e}")
    
    # Test 5: Frontend accessibility
    print("\n🌐 TEST 5: Frontend Auto Reordering Tab")
    try:
        # Test if we can access the frontend
        response = requests.get("http://localhost:3000", timeout=5)
        print(f"Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Frontend accessible")
            print("   Navigate to: Auto Supply Reordering tab (Tab #9)")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    
    # Test 6: Check if reorder data flows to frontend
    print("\n🔄 TEST 6: Data Flow Verification")
    try:
        # Trigger auto reorder
        trigger_response = requests.post("http://localhost:8000/supply_inventory/trigger_auto_reorder", 
                                       json={}, timeout=10)
        print(f"Trigger Status: {trigger_response.status_code}")
        
        if trigger_response.status_code == 200:
            trigger_data = trigger_response.json()
            print(f"✅ Auto reorder triggered")
            print(f"   Items processed: {trigger_data.get('message', 'N/A')}")
            
            # Check if data appears in auto reorder status
            status_response = requests.get("http://localhost:8000/supply_inventory/auto_reorder_status", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                items = status_data.get('auto_reorders', [])
                print(f"   Items now in auto reorder queue: {len(items)}")
        else:
            print(f"❌ Trigger failed: {trigger_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Data flow error: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNOSIS & SOLUTIONS")
    print("=" * 50)
    
    print("\n🎯 COMMON ISSUES & FIXES:")
    print("\n1. ❌ Can't see reorders in frontend:")
    print("   ✅ Solution: Navigate to Tab #9 'Auto Supply Reordering'")
    print("   ✅ Check: Auto Reorder Status Table (top section)")
    
    print("\n2. ❌ No items in Auto Reorder Status:")
    print("   ✅ Solution: Trigger auto reorder manually")
    print("   ✅ Click: 'Trigger Auto Reorder' button in the tab")
    
    print("\n3. ❌ Purchase orders not appearing:")
    print("   ✅ Solution: Approve items from Auto Reorder Status first") 
    print("   ✅ Then: Check Purchase Orders section")
    
    print("\n4. ❌ Frontend not loading data:")
    print("   ✅ Solution: Refresh browser page")
    print("   ✅ Check: Browser console for errors (F12)")
    
    print("\n📋 STEP-BY-STEP PROCESS:")
    print("1. Open: http://localhost:3000")
    print("2. Navigate: Tab #9 'Auto Supply Reordering'")
    print("3. Click: 'Trigger Auto Reorder' button")
    print("4. Check: Auto Reorder Status table updates")
    print("5. Approve: Items from the status table")
    print("6. Verify: Purchase orders appear in bottom section")

if __name__ == "__main__":
    debug_reorder_process()
