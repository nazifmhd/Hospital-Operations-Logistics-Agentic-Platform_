#!/usr/bin/env python3
"""
Test Script: Verify Frontend API Endpoints
This script tests all the critical API endpoints that the frontend uses
"""
import asyncio
import requests
import json
from datetime import datetime

def test_endpoint(method, url, data=None, description=""):
    """Test a single endpoint"""
    try:
        print(f"\n🧪 Testing {method} {url}")
        print(f"   📋 {description}")
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ SUCCESS - Response received")
                # Print first few keys to verify structure
                if isinstance(data, dict):
                    keys = list(data.keys())[:3]
                    print(f"   🔑 Keys: {keys}")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"   📊 Array with {len(data)} items")
                return True
            except json.JSONDecodeError:
                print(f"   ⚠️  SUCCESS but invalid JSON response")
                return True
        else:
            print(f"   ❌ FAILED - {response.text[:100]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
        return False

def main():
    base_url = "http://localhost:8000"
    
    print("🏥 Hospital Frontend API Compatibility Test")
    print("=" * 50)
    
    # Test core endpoints that frontend uses
    tests = [
        # System endpoints
        ("GET", f"{base_url}/system/status", None, "System status for App.tsx"),
        ("GET", f"{base_url}/api/v2/notifications", None, "Notifications for NotificationContext"),
        
        # Bed Management
        ("POST", f"{base_url}/bed_management/query", {"query": "all beds"}, "Bed data for BedFloorPlanVisualization"),
        ("POST", f"{base_url}/bed_management/execute", {"action": "get_status", "data": {}}, "Bed actions for EnhancedBedManagementView"),
        
        # Equipment Tracker  
        ("POST", f"{base_url}/equipment_tracker/query", {"query": "all equipment"}, "Equipment data for EquipmentTrackerDashboard"),
        ("POST", f"{base_url}/equipment_tracker/execute", {"action": "update", "data": {}}, "Equipment execute for EquipmentTrackerDashboard"),
        ("GET", f"{base_url}/equipment_tracker/available_equipment", None, "Available equipment for dispatch interface"),
        ("GET", f"{base_url}/equipment_tracker/equipment_requests", None, "Equipment requests list"),
        ("GET", f"{base_url}/equipment_tracker/porter_status", None, "Porter status for dispatch interface"),
        ("POST", f"{base_url}/equipment_tracker/create_request", {"equipment_type": "test", "location": "test"}, "Create equipment request"),
        ("POST", f"{base_url}/equipment_tracker/assign_equipment/123", {"equipment_id": "456"}, "Assign equipment to request"),
        ("POST", f"{base_url}/equipment_tracker/dispatch_request/123", {"porter_id": "789"}, "Dispatch equipment request"),
        ("POST", f"{base_url}/equipment_tracker/complete_request/123", None, "Complete equipment request"),
        
        # Staff Allocation
        ("POST", f"{base_url}/staff_allocation/query", {"query": "current staffing"}, "Staff data for StaffAllocationDashboard"),
        ("POST", f"{base_url}/staff_allocation/execute", {"action": "reallocate", "data": {}}, "Staff execute for StaffAllocationDashboard"),
        ("GET", f"{base_url}/staff_allocation/real_time_status", None, "Real-time staff status"),
        ("GET", f"{base_url}/staff_allocation/reallocation_suggestions", None, "Staff reallocation suggestions"),
        ("GET", f"{base_url}/staff_allocation/shift_adjustments", None, "Staff shift adjustments"),
        ("POST", f"{base_url}/staff_allocation/emergency_reallocation", {"reason": "test"}, "Emergency staff reallocation"),
        ("POST", f"{base_url}/staff_allocation/approve_reallocation/123", None, "Approve reallocation suggestion"),
        ("POST", f"{base_url}/staff_allocation/reject_reallocation/123", None, "Reject reallocation suggestion"),
        ("POST", f"{base_url}/staff_allocation/approve_shift_adjustment/123", None, "Approve shift adjustment"),
        
        # Supply Inventory
        ("POST", f"{base_url}/supply_inventory/query", {"query": "inventory status"}, "Supply data for SupplyInventoryDashboard"),
        ("POST", f"{base_url}/supply_inventory/execute", {"action": "update", "data": {}}, "Supply execute for SupplyInventoryDashboard"),
        ("GET", f"{base_url}/supply_inventory/auto_reorder_status", None, "Auto-reorder status"),
        ("GET", f"{base_url}/supply_inventory/purchase_orders", None, "Purchase orders list"),
        ("POST", f"{base_url}/supply_inventory/trigger_auto_reorder", None, "Trigger auto reorder"),
        ("POST", f"{base_url}/supply_inventory/approve_purchase_order/123", None, "Approve purchase order"),
        ("POST", f"{base_url}/supply_inventory/reject_purchase_order/123", None, "Reject purchase order"),
        
        # Admission/Discharge
        ("GET", f"{base_url}/admission_discharge/patients", None, "Patient list for admission dashboard"),
        ("GET", f"{base_url}/admission_discharge/beds", None, "Available beds list"),
        ("GET", f"{base_url}/admission_discharge/tasks", None, "Admission/discharge tasks"),
        ("GET", f"{base_url}/admission_discharge/automation_rules", None, "Automation rules"),
        ("POST", f"{base_url}/admission_discharge/start_admission", {"patient_name": "Test"}, "Start admission process"),
        ("POST", f"{base_url}/admission_discharge/start_discharge/123", None, "Start discharge process"),
        ("POST", f"{base_url}/admission_discharge/complete_task/123", None, "Complete admission/discharge task"),
        ("POST", f"{base_url}/admission_discharge/assign_bed/123", {"bed_id": "456"}, "Assign bed to patient"),
        ("POST", f"{base_url}/admission_discharge/toggle_automation/123", None, "Toggle automation rule"),
        
        # Analytics
        ("POST", f"{base_url}/analytics/capacity_utilization", {"query": "capacity report"}, "Capacity analytics for reporting dashboard"),
        
        # Additional Frontend API Endpoints (from comprehensive analysis)
        # Dashboard Data Endpoints  
        ("GET", f"{base_url}/api/v2/dashboard", None, "Main dashboard data for SupplyDataContext"),
        ("GET", f"{base_url}/api/v2/inventory", None, "Inventory data for multiple components"),
        ("GET", f"{base_url}/api/v2/recent-activity", None, "Recent activities for ProfessionalDashboard"),
        
        # Analytics Endpoints
        ("GET", f"{base_url}/api/v2/analytics/compliance", None, "Compliance data for ProfessionalDashboard"),
        ("GET", f"{base_url}/api/v2/analytics/usage/item123", None, "Usage analytics for Analytics component"),
        
        # AI/ML Endpoints (AIMLDashboard)
        ("GET", f"{base_url}/api/v2/ai/status", None, "AI status for AIMLDashboard"),
        ("GET", f"{base_url}/api/v2/ai/forecast/item123?days=30", None, "AI forecasting for AIMLDashboard"),
        ("GET", f"{base_url}/api/v2/ai/anomalies", None, "AI anomaly detection"),
        ("GET", f"{base_url}/api/v2/ai/optimization", None, "AI optimization results"),
        ("GET", f"{base_url}/api/v2/ai/insights", None, "AI insights"),
        ("POST", f"{base_url}/api/v2/ai/initialize", None, "Initialize AI system"),
        
        # Workflow Automation Endpoints
        ("GET", f"{base_url}/api/v2/workflow/status", None, "Workflow status for WorkflowAutomation"),
        ("GET", f"{base_url}/api/v2/workflow/approval/all", None, "All approvals for workflow"),
        ("GET", f"{base_url}/api/v2/workflow/purchase_order/all", None, "All purchase orders for workflow"),
        ("GET", f"{base_url}/api/v2/workflow/supplier/all", None, "All suppliers for workflow"),
        ("GET", f"{base_url}/api/v2/workflow/analytics/dashboard", None, "Workflow analytics"),
        
        # User Management Endpoints
        ("GET", f"{base_url}/api/v2/users", None, "Users list for UserManagement"),
        ("GET", f"{base_url}/api/v2/users/roles", None, "User roles for UserManagement"),
        ("POST", f"{base_url}/api/v2/users", {"username": "test", "email": "test@test.com"}, "Create user"),
        ("PUT", f"{base_url}/api/v2/users/123", {"username": "test2"}, "Update user"),
        
        # Transfer Management Endpoints  
        ("GET", f"{base_url}/api/v2/transfers/history", None, "Transfer history for TransferManagement"),
        ("GET", f"{base_url}/api/v2/locations", None, "Locations for MultiLocationInventory"),
        ("GET", f"{base_url}/api/v2/test-transfers", None, "Test transfers for MultiLocationInventory"),
        ("GET", f"{base_url}/api/v2/transfers/surplus/item123?required_quantity=1", None, "Surplus stock check"),
        
        # Procurement Endpoints
        ("GET", f"{base_url}/api/v2/procurement/recommendations", None, "Procurement recommendations"),
        ("POST", f"{base_url}/api/purchase-orders/generate", {"items": []}, "Generate purchase orders"),
        
        # Inventory Management Endpoints
        ("GET", f"{base_url}/api/inventory", None, "All inventory items"),
        ("GET", f"{base_url}/api/inventory/item123", None, "Specific inventory item"),
        ("POST", f"{base_url}/api/inventory/update", {"item_id": "123", "quantity_change": 5}, "Update inventory"),
        
        # Alerts Endpoints
        ("GET", f"{base_url}/api/alerts", None, "All active alerts"),
        ("POST", f"{base_url}/api/alerts/resolve", {"alert_id": "123"}, "Resolve alert"),
        ("POST", f"{base_url}/api/v2/notifications/123/mark-read", None, "Mark notification as read"),
        
        # WebSocket Endpoint (will fail as it's not HTTP)
        # ("GET", f"{base_url.replace('http', 'ws')}/ws", None, "WebSocket connection for real-time data"),
    ]
    
    print(f"\n🚀 Running {len(tests)} API endpoint tests...")
    
    passed = 0
    failed = 0
    
    for method, url, data, description in tests:
        result = test_endpoint(method, url, data, description)
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS:")
    print(f"   ✅ PASSED: {passed}")
    print(f"   ❌ FAILED: {failed}")
    print(f"   📈 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED! Frontend should work perfectly!")
    elif failed <= 2:
        print(f"\n⚠️  Minor issues found. Most frontend components should work.")
    else:
        print(f"\n🚨 Multiple endpoints failing. Frontend may have issues.")
        
    print(f"\n💡 Recommendation:")
    if failed == 0:
        print("   - Frontend should display data correctly")
        print("   - All dashboard components should work")
    else:
        print("   - Check server is running: python professional_main.py")
        print("   - Check database connection")
        print("   - Review failed endpoints above")

if __name__ == "__main__":
    main()
