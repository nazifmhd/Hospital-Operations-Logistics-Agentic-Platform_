#!/usr/bin/env python3
"""
Test specific endpoints to debug the tabs
"""
import requests
import json

def test_analytics():
    try:
        response = requests.post('http://localhost:8000/analytics/capacity_utilization', 
                                json={
                                    "query": "Generate comprehensive capacity utilization report",
                                    "parameters": {"include_trends": True, "include_forecasts": True}
                                }, timeout=10)
        
        print(f"=== Analytics Endpoint ===")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            if 'bed_utilization' in data:
                print(f"Bed Utilization Records: {len(data['bed_utilization'])}")
                if data['bed_utilization']:
                    print(f"First bed record: {data['bed_utilization'][0]}")
                    
            if 'equipment_utilization' in data:
                print(f"Equipment Utilization Records: {len(data['equipment_utilization'])}")
                if data['equipment_utilization']:
                    print(f"First equipment record: {data['equipment_utilization'][0]}")
                    
        else:
            print(f"Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing analytics: {e}")

def test_supply():
    try:
        response = requests.post('http://localhost:8000/supply_inventory/query', 
                                json={
                                    "query": "Show all supply items with their current stock levels and status"
                                }, timeout=10)
        
        print(f"\n=== Supply Inventory Endpoint ===")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Keys: {list(data.keys())}")
            
            if 'supply_items' in data:
                print(f"Supply Items Count: {len(data['supply_items'])}")
                if data['supply_items']:
                    print(f"First supply item: {data['supply_items'][0]}")
            else:
                print("No 'supply_items' key found!")
                
        else:
            print(f"Error: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing supply inventory: {e}")

if __name__ == "__main__":
    test_analytics()
    test_supply()
