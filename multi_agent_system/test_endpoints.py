#!/usr/bin/env python3
"""
Test script to debug the endpoints
"""
import requests
import json

def test_endpoint(url, data=None):
    try:
        if data:
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        print(f"\n=== Testing {url} ===")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            json_data = response.json()
            print(f"Response Keys: {list(json_data.keys())}")
            
            # Check specific data
            if 'supply_items' in json_data:
                print(f"Supply Items Count: {len(json_data['supply_items'])}")
            if 'staff_members' in json_data:
                print(f"Staff Members Count: {len(json_data['staff_members'])}")
            if 'equipment' in json_data:
                print(f"Equipment Count: {len(json_data['equipment'])}")
            if 'bed_utilization' in json_data:
                print(f"Bed Utilization Count: {len(json_data['bed_utilization'])}")
                
        else:
            print(f"Error Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error testing {url}: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:8000"
    
    # Test supply inventory only
    test_endpoint(f"{base_url}/supply_inventory/query", {
        "query": "Show all supply items with their current stock levels and status"
    })
