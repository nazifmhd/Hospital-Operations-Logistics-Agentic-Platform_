#!/usr/bin/env python3
"""
Add Sample Equipment Requests to Database
Creates sample equipment requests for testing the Equipment Request & Dispatch functionality.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system.database.config import db_manager
from multi_agent_system.database.models import EquipmentRequest, Department, MedicalEquipment, StaffMember
from sqlalchemy import select

async def add_sample_equipment_requests():
    """Add sample equipment requests to the database"""
    print("🔧 Initializing database connection...")
    db_manager.initialize_async_engine()
    
    async with db_manager.get_async_session() as session:
        # Check if equipment requests already exist
        result = await session.execute(select(EquipmentRequest))
        existing_requests = result.scalars().all()
        
        if existing_requests:
            print(f"✅ Found {len(existing_requests)} existing equipment request(s)")
            for req in existing_requests:
                print(f"  - {req.id}: {req.requester_name} requesting {req.equipment_type} ({req.status})")
            return True
        
        # Get some departments and staff for the sample requests
        departments_result = await session.execute(select(Department).limit(3))
        departments = departments_result.scalars().all()
        
        equipment_result = await session.execute(select(MedicalEquipment).limit(4))
        equipment_list = equipment_result.scalars().all()
        
        staff_result = await session.execute(select(StaffMember).limit(3))
        staff_members = staff_result.scalars().all()
        
        print(f"📋 Adding sample equipment requests...")
        print(f"  Found {len(departments)} departments, {len(equipment_list)} equipment items, {len(staff_members)} staff members")
        
        # Create sample equipment requests
        sample_requests = []
        
        # Request 1: High priority urgent request
        sample_requests.append(EquipmentRequest(
            id="req_001",
            requester_name="Dr. Sarah Johnson",
            requester_department_id=departments[0].id if departments else None,
            requester_location="ICU Room 205",
            equipment_type="IV Pump",
            assigned_equipment_id=equipment_list[0].id if equipment_list else None,
            priority="urgent",
            reason="Patient surgery scheduled - urgent need",
            status="pending",
            assigned_porter_id=staff_members[0].id if staff_members else None,
            estimated_delivery_time="15-20 minutes",
            notes="Urgent - Patient surgery scheduled"
        ))
        
        # Request 2: Medium priority assigned request
        sample_requests.append(EquipmentRequest(
            id="req_002",
            requester_name="Nurse Mike Thompson",
            requester_department_id=departments[1].id if len(departments) > 1 else departments[0].id,
            requester_location="Emergency Department",
            equipment_type="Ventilator",
            assigned_equipment_id=equipment_list[1].id if len(equipment_list) > 1 else None,
            priority="medium",
            reason="Equipment needed for patient care",
            status="assigned",
            assigned_porter_id=staff_members[1].id if len(staff_members) > 1 else None,
            estimated_delivery_time="25-30 minutes",
            notes="Standard equipment transfer request"
        ))
        
        # Request 3: Low priority dispatched request
        sample_requests.append(EquipmentRequest(
            id="req_003",
            requester_name="Tech Amy Wilson",
            requester_department_id=departments[2].id if len(departments) > 2 else departments[0].id,
            requester_location="Surgical Ward",
            equipment_type="Monitor",
            assigned_equipment_id=equipment_list[2].id if len(equipment_list) > 2 else None,
            priority="low",
            reason="Routine equipment maintenance check",
            status="dispatched",
            assigned_porter_id=staff_members[2].id if len(staff_members) > 2 else None,
            estimated_delivery_time="45 minutes",
            notes="Routine maintenance and calibration"
        ))
        
        # Request 4: Completed request for history
        sample_requests.append(EquipmentRequest(
            id="req_004",
            requester_name="Dr. Jennifer Lee",
            requester_department_id=departments[0].id if departments else None,
            requester_location="Recovery Room 108",
            equipment_type="Defibrillator",
            assigned_equipment_id=equipment_list[3].id if len(equipment_list) > 3 else None,
            priority="high",
            reason="Patient emergency response equipment",
            status="completed",
            assigned_porter_id=staff_members[0].id if staff_members else None,
            estimated_delivery_time="10 minutes",
            notes="Emergency equipment successfully delivered"
        ))

        # Add all sample requests to the session
        for request in sample_requests:
            session.add(request)
        
        await session.commit()
        print(f"✅ Added {len(sample_requests)} sample equipment requests")
        
        # Verify the requests were added
        result = await session.execute(select(EquipmentRequest))
        all_requests = result.scalars().all()
        print(f"✅ Total equipment requests in database: {len(all_requests)}")
        
        # Display request summary
        for req in all_requests:
            print(f"  - {req.id}: {req.requester_name} requesting {req.equipment_type} ({req.status})")
        
        return True

if __name__ == "__main__":
    print("🏥 Adding Sample Equipment Requests to Hospital Database")
    print("=" * 55)
    
    try:
        success = asyncio.run(add_sample_equipment_requests())
        if success:
            print("\n🎉 Sample equipment requests added successfully!")
        else:
            print("\n💥 Failed to add sample equipment requests!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error adding equipment requests: {e}")
        sys.exit(1)
