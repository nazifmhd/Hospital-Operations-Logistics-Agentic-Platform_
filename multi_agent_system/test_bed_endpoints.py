#!/usr/bin/env python3
"""
Test the bed endpoints to see what data is returned
"""
import asyncio
import requests
import json

def test_bed_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing bed endpoints...")
    
    # Test the GET endpoint that frontend likely uses
    try:
        response = requests.get(f"{base_url}/admission_discharge/beds")
        print(f"\n/admission_discharge/beds endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            if 'beds' in data and len(data['beds']) > 0:
                bed = data['beds'][0]
                print(f"\nFirst bed structure:")
                for key, value in bed.items():
                    print(f"  {key}: {value}")
                if 'floor' in bed:
                    print(f"✅ Floor field present: {bed['floor']}")
                else:
                    print("❌ Floor field missing!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing /admission_discharge/beds: {e}")
    
    # Test the POST endpoint for bed management query
    try:
        response = requests.post(f"{base_url}/bed_management/query", 
                               json={"query": "all beds"})
        print(f"\n/bed_management/query endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if 'beds' in data and len(data['beds']) > 0:
                bed = data['beds'][0]
                print(f"First bed from query:")
                for key, value in bed.items():
                    print(f"  {key}: {value}")
                if 'floor' in bed:
                    print(f"✅ Floor field present: {bed['floor']}")
                else:
                    print("❌ Floor field missing!")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error testing /bed_management/query: {e}")

if __name__ == "__main__":
    test_bed_endpoints()
