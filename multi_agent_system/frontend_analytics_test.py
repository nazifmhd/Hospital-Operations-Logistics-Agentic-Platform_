#!/usr/bin/env python3
"""
Frontend Analytics Charts Verification
Tests if bed utilization and staff allocation charts are displaying correctly
"""

import requests
import json

def test_frontend_data_compatibility():
    """Test if backend data matches frontend expectations"""
    print("🏥 FRONTEND ANALYTICS CHARTS VERIFICATION")
    print("=" * 60)
    
    # Test the backend endpoint that frontend calls
    backend_url = "http://localhost:8000/analytics/capacity_utilization"
    frontend_request = {
        "query": "Generate comprehensive capacity utilization report",
        "parameters": {"include_trends": True, "include_forecasts": True}
    }
    
    try:
        print("📡 Testing Backend API Endpoint...")
        response = requests.post(backend_url, json=frontend_request, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API Response: SUCCESS")
            
            # Test bed utilization data
            print("\n🛏️  BED UTILIZATION SUB-TAB ANALYSIS:")
            bed_data = data.get('bed_utilization', [])
            print(f"Records found: {len(bed_data)}")
            
            if bed_data:
                sample_bed = bed_data[0]
                print("Available fields:", list(sample_bed.keys()))
                
                # Check required fields for frontend chart
                required_bed_fields = ['department_name', 'total_beds', 'occupied_beds', 'available_beds', 'utilization_rate']
                missing_bed_fields = [field for field in required_bed_fields if field not in sample_bed]
                
                if not missing_bed_fields:
                    print("✅ BED UTILIZATION CHART: All required fields present")
                    print(f"   Chart X-Axis: department_name = '{sample_bed['department_name']}'")
                    print(f"   Chart Data: {sample_bed['total_beds']} total, {sample_bed['occupied_beds']} occupied")
                else:
                    print(f"❌ BED UTILIZATION CHART: Missing fields {missing_bed_fields}")
            else:
                print("❌ BED UTILIZATION CHART: No data available")
            
            # Test staff utilization data
            print("\n👥 STAFF ALLOCATION SUB-TAB ANALYSIS:")
            staff_data = data.get('staff_utilization', [])
            print(f"Records found: {len(staff_data)}")
            
            if staff_data:
                sample_staff = staff_data[0]
                print("Available fields:", list(sample_staff.keys()))
                
                # Check required fields for frontend chart
                required_staff_fields = ['department_name', 'total_staff', 'active_staff']
                missing_staff_fields = [field for field in required_staff_fields if field not in sample_staff]
                
                if not missing_staff_fields:
                    print("✅ STAFF ALLOCATION CHART: All required fields present")
                    print(f"   Chart X-Axis: department_name = '{sample_staff['department_name']}'")
                    print(f"   Chart Data: {sample_staff['total_staff']} total, {sample_staff['active_staff']} active")
                    
                    # Check for deprecated fields that frontend no longer uses
                    deprecated_fields = ['on_break', 'off_duty']
                    found_deprecated = [field for field in deprecated_fields if field in sample_staff]
                    if found_deprecated:
                        print(f"ℹ️  Note: Deprecated fields found (not used in charts): {found_deprecated}")
                else:
                    print(f"❌ STAFF ALLOCATION CHART: Missing fields {missing_staff_fields}")
            else:
                print("❌ STAFF ALLOCATION CHART: No data available")
            
            # Test frontend connectivity
            print("\n🌐 FRONTEND CONNECTIVITY TEST:")
            try:
                frontend_response = requests.get("http://localhost:3000", timeout=5)
                if frontend_response.status_code == 200:
                    print("✅ FRONTEND: Running on http://localhost:3000")
                    print("📋 NAVIGATION: Go to tab 'Analytics & Reports' (index 8)")
                    print("   🛏️  Sub-tab: 'Bed Utilization' should show charts with department data")
                    print("   👥 Sub-tab: 'Staff Allocation' should show active staff charts")
                else:
                    print(f"⚠️  FRONTEND: Unexpected status {frontend_response.status_code}")
            except requests.exceptions.RequestException:
                print("❌ FRONTEND: Not running on http://localhost:3000")
                print("   Start with: cd hospital-frontend && npm start")
            
        else:
            print(f"❌ Backend API Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 60)
    print("FRONTEND CHART VERIFICATION COMPLETE")
    print("Expected behavior:")
    print("1. Navigate to 'Analytics & Reports' tab")
    print("2. Bed Utilization sub-tab: Shows bar charts by department")
    print("3. Staff Allocation sub-tab: Shows active staff charts by department")
    print("4. Charts should display data without errors")

if __name__ == "__main__":
    test_frontend_data_compatibility()
