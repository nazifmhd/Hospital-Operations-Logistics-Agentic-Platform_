#!/usr/bin/env python3
import requests

try:
    response = requests.put('http://localhost:8000/api/v2/users/123', json={'username': 'test'}, timeout=5)
    print(f"PUT Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
        print("✅ PUT endpoint works!")
    else:
        print(f"❌ PUT failed: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
