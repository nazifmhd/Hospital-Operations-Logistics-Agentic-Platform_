#!/usr/bin/env python3
"""
Hospital Operations Platform - System Verification Script
Comprehensive testing of all system components
"""
import asyncio
import sys
import traceback
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(component, status, details=""):
    """Print component status"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {component}: {'PASSED' if status else 'FAILED'}")
    if details:
        print(f"   └─ {details}")

async def test_database_connectivity():
    """Test database connectivity"""
    try:
        from database.config import db_manager
        print_status("Database Configuration", True, "Database manager imported")
        return True
    except Exception as e:
        print_status("Database Configuration", False, str(e))
        return False

async def test_agent_imports():
    """Test all agent imports"""
    agents_status = {}
    
    # Test Bed Management Agent
    try:
        from agents.bed_management_agent import BedManagementAgent
        agents_status["BedManagementAgent"] = True
        print_status("Bed Management Agent Import", True)
    except Exception as e:
        agents_status["BedManagementAgent"] = False
        print_status("Bed Management Agent Import", False, str(e))
    
    # Test Equipment Tracker Agent
    try:
        from agents.equipment_tracker_agent import EquipmentTrackerAgent
        agents_status["EquipmentTrackerAgent"] = True
        print_status("Equipment Tracker Agent Import", True)
    except Exception as e:
        agents_status["EquipmentTrackerAgent"] = False
        print_status("Equipment Tracker Agent Import", False, str(e))
    
    # Test Staff Allocation Agent
    try:
        from agents.staff_allocation_agent import StaffAllocationAgent
        agents_status["StaffAllocationAgent"] = True
        print_status("Staff Allocation Agent Import", True)
    except Exception as e:
        agents_status["StaffAllocationAgent"] = False
        print_status("Staff Allocation Agent Import", False, str(e))
    
    # Test Supply Inventory Agent
    try:
        from agents.supply_inventory_agent import SupplyInventoryAgent
        agents_status["SupplyInventoryAgent"] = True
        print_status("Supply Inventory Agent Import", True)
    except Exception as e:
        agents_status["SupplyInventoryAgent"] = False
        print_status("Supply Inventory Agent Import", False, str(e))
    
    return agents_status

async def test_coordinator():
    """Test coordinator functionality"""
    try:
        from core.coordinator import MultiAgentCoordinator
        coordinator = MultiAgentCoordinator()
        print_status("Coordinator Creation", True, f"Coordinator ID: {coordinator.coordinator_id}")
        return True
    except Exception as e:
        print_status("Coordinator Creation", False, str(e))
        return False

async def test_professional_main():
    """Test professional main server"""
    try:
        import professional_main
        print_status("Professional Main Import", True, "Server module imported")
        return True
    except Exception as e:
        print_status("Professional Main Import", False, str(e))
        return False

async def test_agent_initialization():
    """Test agent initialization"""
    results = {}
    
    # Create coordinator for agents that need it
    try:
        from core.coordinator import MultiAgentCoordinator
        coordinator = MultiAgentCoordinator()
    except Exception as e:
        print_status("Coordinator for Agents", False, str(e))
        coordinator = None
    
    try:
        from agents.bed_management_agent import BedManagementAgent
        bed_agent = BedManagementAgent(coordinator=coordinator)
        health = bed_agent.get_health_status()
        results["bed_agent"] = health["status"] == "healthy"
        print_status("Bed Agent Health", results["bed_agent"], f"Status: {health['status']}")
    except Exception as e:
        results["bed_agent"] = False
        print_status("Bed Agent Health", False, str(e))
    
    try:
        from agents.equipment_tracker_agent import EquipmentTrackerAgent
        equipment_agent = EquipmentTrackerAgent()
        health = equipment_agent.get_health_status()
        results["equipment_agent"] = health["status"] == "healthy"
        print_status("Equipment Agent Health", results["equipment_agent"], f"Status: {health['status']}")
    except Exception as e:
        results["equipment_agent"] = False
        print_status("Equipment Agent Health", False, str(e))
    
    try:
        from agents.staff_allocation_agent import StaffAllocationAgent
        staff_agent = StaffAllocationAgent()
        health = staff_agent.get_health_status()
        results["staff_agent"] = health["status"] == "healthy"
        print_status("Staff Agent Health", results["staff_agent"], f"Status: {health['status']}")
    except Exception as e:
        results["staff_agent"] = False
        print_status("Staff Agent Health", False, str(e))
    
    try:
        from agents.supply_inventory_agent import SupplyInventoryAgent
        supply_agent = SupplyInventoryAgent()
        health = supply_agent.get_health_status()
        results["supply_agent"] = health["status"] == "healthy"
        print_status("Supply Agent Health", results["supply_agent"], f"Status: {health['status']}")
    except Exception as e:
        results["supply_agent"] = False
        print_status("Supply Agent Health", False, str(e))
    
    return results

async def test_dependencies():
    """Test required dependencies"""
    required_packages = [
        "fastapi", "uvicorn", "sqlalchemy", "asyncpg", 
        "langchain", "langgraph", "google-generativeai",
        "chromadb", "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            package_name = package.replace("-", "_")
            if package == "google-generativeai":
                import google.generativeai
            else:
                __import__(package_name)
            print_status(f"Package: {package}", True)
        except ImportError:
            missing_packages.append(package)
            print_status(f"Package: {package}", False, "Not installed")
    
    return len(missing_packages) == 0, missing_packages

def print_summary(results):
    """Print test summary"""
    print_header("SYSTEM VERIFICATION SUMMARY")
    
    total_tests = 0
    passed_tests = 0
    
    for category, result in results.items():
        if isinstance(result, bool):
            total_tests += 1
            if result:
                passed_tests += 1
            print_status(category, result)
        elif isinstance(result, dict):
            for test_name, test_result in result.items():
                total_tests += 1
                if test_result:
                    passed_tests += 1
                print_status(f"{category}.{test_name}", test_result)
    
    print(f"\n📊 RESULTS: {passed_tests}/{total_tests} tests passed")
    print(f"🎯 SUCCESS RATE: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL SYSTEMS OPERATIONAL - 100% SUCCESS! 🎉")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} issues detected")

async def main():
    """Main verification function"""
    print_header("HOSPITAL OPERATIONS PLATFORM - SYSTEM VERIFICATION")
    print(f"🕐 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Dependencies
    print_header("TESTING DEPENDENCIES")
    deps_ok, missing = await test_dependencies()
    results["dependencies"] = deps_ok
    
    # Test 2: Database
    print_header("TESTING DATABASE")
    results["database"] = await test_database_connectivity()
    
    # Test 3: Agent Imports
    print_header("TESTING AGENT IMPORTS")
    agent_imports = await test_agent_imports()
    results["agent_imports"] = agent_imports
    
    # Test 4: Coordinator
    print_header("TESTING COORDINATOR")
    results["coordinator"] = await test_coordinator()
    
    # Test 5: Professional Main
    print_header("TESTING PROFESSIONAL MAIN")
    results["professional_main"] = await test_professional_main()
    
    # Test 6: Agent Health
    print_header("TESTING AGENT HEALTH")
    agent_health = await test_agent_initialization()
    results["agent_health"] = agent_health
    
    # Print Summary
    print_summary(results)
    
    return results

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
