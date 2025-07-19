"""
Auto Approval Workflow Demonstration Script
This script demonstrates the complete automatic approval workflow
"""

import asyncio
import requests
import json
import time

BASE_URL = "http://localhost:8000"

async def demonstrate_auto_approval_workflow():
    """Demonstrate the complete auto approval workflow"""
    
    print("🔄 Auto Approval Workflow Demonstration")
    print("=" * 50)
    
    # 1. Check auto approval status
    print("\n1. Checking Auto Approval Service Status...")
    response = requests.get(f"{BASE_URL}/api/v2/workflow/auto-approval/status")
    status = response.json()
    print(f"   ✅ Service Enabled: {status['enabled']}")
    print(f"   📊 Low Stock Items: {status['low_stock_items']}")
    print(f"   🚨 Emergency Items: {status['emergency_items']}")
    print(f"   📋 Pending Requests: {status['pending_requests']}")
    
    # 2. Check monitored inventory
    print("\n2. Checking Monitored Inventory...")
    response = requests.get(f"{BASE_URL}/api/v2/workflow/auto-approval/inventory")
    inventory = response.json()
    
    emergency_items = [item for item in inventory['inventory_items'] if item['is_emergency']]
    low_stock_items = [item for item in inventory['inventory_items'] if item['is_low_stock'] and not item['is_emergency']]
    
    print(f"   🚨 Emergency Items Found: {len(emergency_items)}")
    for item in emergency_items:
        print(f"      - {item['name']}: {item['current_quantity']}/{item['minimum_threshold']} ({item['location']})")
    
    print(f"   ⚠️  Low Stock Items Found: {len(low_stock_items)}")
    for item in low_stock_items:
        print(f"      - {item['name']}: {item['current_quantity']}/{item['minimum_threshold']} ({item['location']})")
    
    # 3. Check current approval requests
    print("\n3. Checking Auto-Generated Approval Requests...")
    response = requests.get(f"{BASE_URL}/api/v2/workflow/approval/all")
    approvals = response.json()
    
    auto_requests = [req for req in approvals['approvals'] if req['requester_id'] == 'system_auto_approval']
    print(f"   📋 Auto-Generated Requests: {len(auto_requests)}")
    
    for req in auto_requests:
        print(f"      - {req['id']}: {req['status']} (${req['amount']:.2f}) - Current Approver: {req['current_approver']}")
    
    # 4. Demonstrate approval process
    if auto_requests:
        print("\n4. Demonstrating Approval Process...")
        test_request = auto_requests[0]  # Take the first request
        
        print(f"   Processing: {test_request['id']}")
        print(f"   Current Status: {test_request['status']}")
        print(f"   Current Approver: {test_request['current_approver']}")
        
        # Approve with demo endpoint
        approval_data = {
            "action": "approve",
            "comments": "Approved for emergency restocking - auto approval demo"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v2/workflow/approval/{test_request['id']}/demo-action",
            json=approval_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Approval Successful!")
            print(f"   📄 New Status: {result['status']}")
            print(f"   👤 Next Approver: {result.get('current_approver', 'None (Completed)')}")
            
            # If fully approved, check for purchase order creation
            if result['status'] == 'approved':
                print("   🎉 Request Fully Approved - Ready for Purchase Order Creation!")
        else:
            print(f"   ❌ Approval Failed: {response.text}")
    
    # 5. Trigger manual check
    print("\n5. Triggering Manual Inventory Check...")
    response = requests.post(f"{BASE_URL}/api/v2/workflow/auto-approval/trigger-check")
    if response.status_code == 200:
        print("   ✅ Manual check completed")
    else:
        print(f"   ❌ Manual check failed: {response.text}")
    
    # 6. Show workflow analytics
    print("\n6. Workflow Analytics Summary...")
    response = requests.get(f"{BASE_URL}/api/v2/workflow/analytics/dashboard")
    if response.status_code == 200:
        analytics = response.json()
        metrics = analytics.get('analytics', {})
        approval_metrics = metrics.get('approval_metrics', {})
        
        print(f"   📊 Total Requests: {approval_metrics.get('total_requests', 0)}")
        print(f"   ✅ Approved: {approval_metrics.get('approved_requests', 0)}")
        print(f"   ⏳ Pending: {approval_metrics.get('pending_requests', 0)}")
        print(f"   📈 Approval Rate: {(approval_metrics.get('approval_rate', 0) * 100):.1f}%")
    
    print(f"\n🎉 Auto Approval Workflow Demonstration Complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(demonstrate_auto_approval_workflow())
