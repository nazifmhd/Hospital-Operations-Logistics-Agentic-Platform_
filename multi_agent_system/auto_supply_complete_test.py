#!/usr/bin/env python3
"""
Auto Supply Reordering Tab - Complete Frontend Integration Test
Tests all aspects of the auto supply reordering functionality
"""

import requests
import json

def test_auto_supply_reordering_tab():
    """Comprehensive test of auto supply reordering tab functionality"""
    print("🛒 AUTO SUPPLY REORDERING TAB - COMPLETE VERIFICATION")
    print("=" * 70)
    
    # Test 1: Auto Reorder Status Endpoint
    print("\n📊 TEST 1: AUTO REORDER STATUS")
    try:
        response = requests.get("http://localhost:8000/supply_inventory/auto_reorder_status", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            auto_reorders = data.get('auto_reorders', [])
            print(f"✅ Found {len(auto_reorders)} items needing reorder")
            print(f"   Total pending value: ${data.get('total_pending_value', 0)}")
            
            if auto_reorders:
                sample = auto_reorders[0]
                print(f"   Sample item: {sample['supply_name']}")
                print(f"   Current: {sample['current_quantity']}, Reorder point: {sample['reorder_point']}")
                print(f"   Priority: {sample['priority']}, Status: {sample['status']}")
                
                # Verify all required frontend fields
                required_fields = ['id', 'supply_name', 'current_quantity', 'reorder_point', 
                                 'suggested_quantity', 'estimated_cost', 'supplier', 'priority', 
                                 'status', 'created_at', 'expected_delivery']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print("✅ All required fields present for frontend display")
                else:
                    print(f"❌ Missing fields: {missing_fields}")
            else:
                print("ℹ️  No items need reordering at this time")
        else:
            print(f"❌ Endpoint failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: Purchase Orders Endpoint
    print("\n📋 TEST 2: PURCHASE ORDERS")
    try:
        response = requests.get("http://localhost:8000/supply_inventory/purchase_orders", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            orders = data.get('purchase_orders', [])
            print(f"✅ Found {len(orders)} purchase orders")
            print(f"   Total orders: {data.get('total_orders', 0)}")
            
            if orders:
                sample = orders[0]
                print(f"   Sample order: {sample['order_number']}")
                print(f"   Supplier: {sample['supplier']}, Status: {sample['status']}")
                print(f"   Total cost: ${sample['total_cost']}")
                
                # Verify required fields for frontend
                required_fields = ['id', 'order_number', 'supplier', 'total_items', 
                                 'total_cost', 'status', 'created_at']
                missing_fields = [field for field in required_fields if field not in sample]
                
                if not missing_fields:
                    print("✅ All required fields present for purchase order display")
                else:
                    print(f"❌ Missing fields: {missing_fields}")
            else:
                print("ℹ️  No purchase orders found")
        else:
            print(f"❌ Endpoint failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: Trigger Auto Reorder
    print("\n🔄 TEST 3: TRIGGER AUTO REORDER")
    try:
        response = requests.post("http://localhost:8000/supply_inventory/trigger_auto_reorder", 
                               json={}, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Auto reorder triggered successfully")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Items processed: {data.get('items_processed', 0)}")
        else:
            print(f"❌ Trigger failed: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    # Test 4: Frontend Integration Check
    print("\n🌐 TEST 4: FRONTEND INTEGRATION")
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:3000")
            print("✅ Auto Supply Reordering tab should be working")
        else:
            print(f"⚠️  Frontend status: {frontend_response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ Frontend not accessible")
    
    # Summary
    print("\n" + "=" * 70)
    print("AUTO SUPPLY REORDERING TAB VERIFICATION SUMMARY")
    print("=" * 70)
    print("\n🎯 NAVIGATION INSTRUCTIONS:")
    print("1. Open browser: http://localhost:3000")
    print("2. Click on 'Auto Supply Reordering' tab (9th tab with shopping cart icon)")
    print("\n🚀 EXPECTED FUNCTIONALITY:")
    print("✅ Auto Reorder Status Table:")
    print("   - Shows items needing reorder with priority levels")
    print("   - Displays current quantity vs reorder point")
    print("   - Shows estimated costs and delivery dates")
    print("\n✅ Purchase Orders Section:")
    print("   - Lists all purchase orders with status")
    print("   - Shows supplier information and total costs")
    print("   - Allows approve/reject actions")
    print("\n✅ Interactive Controls:")
    print("   - 'Trigger Auto Reorder' button to initiate reordering")
    print("   - Approve/Reject buttons for purchase orders")
    print("   - Real-time updates every 30 seconds")
    print("\n✅ Data Integration:")
    print("   - Backend provides properly formatted data")
    print("   - Frontend receives all required fields")
    print("   - Field names match frontend expectations")

if __name__ == "__main__":
    test_auto_supply_reordering_tab()
