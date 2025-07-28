#!/usr/bin/env python3
"""
Test Supply Inventory Reorder Function
"""
import requests
import json

def test_supply_reorder():
    try:
        # First, get supply items to find one that needs reordering
        response = requests.post('http://localhost:8000/supply_inventory/query', 
                                json={
                                    "query": "Show all supply items with their current stock levels and status"
                                }, timeout=10)
        
        print(f"=== Supply Inventory Query ===")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            supply_items = data.get('supply_items', [])
            print(f"Found {len(supply_items)} supply items")
            
            # Find a low stock item to test reorder
            low_stock_item = None
            for item in supply_items:
                if item['status'] == 'low_stock':
                    low_stock_item = item
                    break
            
            if low_stock_item:
                print(f"\nTesting reorder for low stock item:")
                print(f"Item: {low_stock_item['name']}")
                print(f"Current Stock: {low_stock_item['current_stock']}")
                print(f"Minimum Stock: {low_stock_item['minimum_stock']}")
                
                # Test the reorder function
                reorder_response = requests.post('http://localhost:8000/supply_inventory/execute',
                                               json={
                                                   "action": "create_purchase_order",
                                                   "parameters": {
                                                       "supply_item_id": low_stock_item['id'],
                                                       "quantity": 100,
                                                       "urgent": True
                                                   }
                                               }, timeout=10)
                
                print(f"\n=== Reorder Test ===")
                print(f"Status: {reorder_response.status_code}")
                print(f"Response: {reorder_response.text[:500]}")
                
            else:
                print("No low stock items found for testing")
                
        else:
            print(f"Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing supply reorder: {e}")

def test_analytics_data():
    try:
        response = requests.post('http://localhost:8000/analytics/capacity_utilization', 
                                json={
                                    "query": "Generate comprehensive capacity utilization report",
                                    "parameters": {"include_trends": True, "include_forecasts": True}
                                }, timeout=10)
        
        print(f"\n=== Analytics Data Test ===")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            # Check bed utilization data
            if 'bed_utilization' in data:
                bed_data = data['bed_utilization']
                print(f"\nBed Utilization Data:")
                print(f"Records: {len(bed_data)}")
                if bed_data:
                    print(f"First record: {bed_data[0]}")
                    # Check if all required fields are present for charts
                    required_fields = ['department_name', 'total_beds', 'occupied_beds', 'available_beds', 'utilization_rate']
                    missing_fields = [field for field in required_fields if field not in bed_data[0]]
                    if missing_fields:
                        print(f"Missing fields for bed charts: {missing_fields}")
                    else:
                        print("✅ All required fields present for bed utilization charts")
            
            # Check staff utilization data
            if 'staff_utilization' in data:
                staff_data = data['staff_utilization']
                print(f"\nStaff Utilization Data:")
                print(f"Records: {len(staff_data)}")
                if staff_data:
                    print(f"First record: {staff_data[0]}")
                    # Check required fields for staff charts
                    required_fields = ['department_name', 'total_staff', 'active_staff', 'utilization_rate']
                    missing_fields = [field for field in required_fields if field not in staff_data[0]]
                    if missing_fields:
                        print(f"Missing fields for staff charts: {missing_fields}")
                    else:
                        print("✅ All required fields present for staff utilization charts")
                        
        else:
            print(f"Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing analytics: {e}")

if __name__ == "__main__":
    test_supply_reorder()
    test_analytics_data()
