#!/usr/bin/env python3
"""
Auto Supply Reordering Tab Verification
Tests the auto supply reordering functionality and frontend integration
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auto_reorder_endpoints():
    """Test all auto supply reordering endpoints"""
    print("🛒 AUTO SUPPLY REORDERING TAB VERIFICATION")
    print("=" * 60)
    
    endpoints_to_test = [
        {
            "name": "Auto Reorder Status",
            "method": "GET",
            "url": f"{BASE_URL}/supply_inventory/auto_reorder_status",
            "description": "Fetches items that need reordering"
        },
        {
            "name": "Purchase Orders",
            "method": "GET", 
            "url": f"{BASE_URL}/supply_inventory/purchase_orders",
            "description": "Lists all purchase orders"
        },
        {
            "name": "Trigger Auto Reorder",
            "method": "POST",
            "url": f"{BASE_URL}/supply_inventory/trigger_auto_reorder",
            "data": {},
            "description": "Triggers automatic reorder process"
        }
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testing: {endpoint['name']}")
        print(f"Description: {endpoint['description']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], timeout=10)
            else:
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ ENDPOINT: Working")
                
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   Records returned: {len(data)}")
                        if data:
                            print(f"   Sample fields: {list(data[0].keys())}")
                    elif isinstance(data, dict):
                        print(f"   Response keys: {list(data.keys())}")
                        if 'success' in data:
                            print(f"   Success: {data['success']}")
                except json.JSONDecodeError:
                    print(f"   Response: {response.text[:100]}...")
                    
            elif response.status_code == 404:
                print("❌ ENDPOINT: Not Found")
            elif response.status_code == 500:
                print("❌ ENDPOINT: Server Error")
                print(f"   Error: {response.text[:200]}")
            else:
                print(f"⚠️  ENDPOINT: Unexpected status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ CONNECTION: Failed to reach endpoint")
            print(f"   Error: {e}")

def test_supply_reorder_integration():
    """Test the supply reorder workflow that powers the auto reordering"""
    print(f"\n🔄 SUPPLY REORDER WORKFLOW TEST:")
    
    # Test the core supply reorder functionality
    try:
        # First get supply items
        query_response = requests.post(f"{BASE_URL}/supply_inventory/query", 
                                     json={"query": "Show items that need reordering"}, 
                                     timeout=10)
        
        if query_response.status_code == 200:
            data = query_response.json()
            supply_items = data.get('supply_items', [])
            low_stock_items = [item for item in supply_items if item.get('status') == 'low_stock']
            
            print(f"✅ SUPPLY QUERY: Found {len(supply_items)} total items")
            print(f"   Low stock items: {len(low_stock_items)}")
            
            if low_stock_items:
                test_item = low_stock_items[0]
                print(f"   Testing reorder for: {test_item['name']}")
                
                # Test reorder execution
                reorder_response = requests.post(f"{BASE_URL}/supply_inventory/reorder",
                                               json={
                                                   "action": "create_purchase_order",
                                                   "parameters": {
                                                       "supply_item_id": test_item['id'],
                                                       "quantity": 100,
                                                       "urgent": True
                                                   }
                                               }, timeout=10)
                
                if reorder_response.status_code == 200:
                    print("✅ REORDER WORKFLOW: Working")
                    result = reorder_response.json()
                    if 'result' in result and 'workflow_id' in result['result']:
                        print(f"   Workflow ID: {result['result']['workflow_id']}")
                else:
                    print("❌ REORDER WORKFLOW: Failed")
            else:
                print("ℹ️  REORDER WORKFLOW: No low stock items to test")
        else:
            print("❌ SUPPLY QUERY: Failed")
            
    except Exception as e:
        print(f"❌ WORKFLOW TEST: {e}")

def test_frontend_connectivity():
    """Test if the auto reordering tab is accessible"""
    print(f"\n🌐 FRONTEND AUTO REORDERING TAB TEST:")
    
    try:
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ FRONTEND: Running on http://localhost:3000")
            print("📋 NAVIGATION: Go to 'Auto Supply Reordering' tab (index 9)")
            print("   Features expected:")
            print("   - Auto reorder status table")
            print("   - Purchase orders list")
            print("   - Trigger auto reorder button")
            print("   - Approve/Reject purchase order actions")
        else:
            print(f"⚠️  FRONTEND: Unexpected status {frontend_response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ FRONTEND: Not running on http://localhost:3000")

def main():
    """Run all auto supply reordering tests"""
    test_auto_reorder_endpoints()
    test_supply_reorder_integration() 
    test_frontend_connectivity()
    
    print("\n" + "=" * 60)
    print("AUTO SUPPLY REORDERING VERIFICATION COMPLETE")
    print("\nExpected Tab Functionality:")
    print("1. Display items needing reorder")
    print("2. Show purchase order status")
    print("3. Allow triggering auto reorder")
    print("4. Enable purchase order approval/rejection")
    print("5. Real-time status updates")

if __name__ == "__main__":
    main()
