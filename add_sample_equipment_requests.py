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
            return
        
        print("📋 Adding sample equipment requests...")
        
        # Get some departments
        dept_result = await session.execute(select(Department).limit(3))
        departments = dept_result.scalars().all()
        
        # Get some equipment
        equip_result = await session.execute(select(MedicalEquipment).limit(5))
        equipment_list = equip_result.scalars().all()
        
        # Get some staff members
        staff_result = await session.execute(select(StaffMember).limit(3))
        staff_members = staff_result.scalars().all()
        
        if not departments or not equipment_list or not staff_members:
            print("⚠️ Missing required data (departments, equipment, or staff). Creating basic requests...")
            
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
        
        # Request 2: Medium priority maintenance request
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
        
        # Request 3: Low priority routine transfer
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
            requested_by_staff_id=staff_members[2].id if len(staff_members) > 2 else None,
            request_type="Transfer",
            priority="Low", 
            status="Pending",
            requested_at=datetime.now() - timedelta(minutes=30),
            required_by=datetime.now() + timedelta(hours=12),
            pickup_location="Recovery Room 108",
            delivery_location="Medical Storage",
            special_instructions="End of shift cleanup",
            quantity=1
        ))
        
        # Request 4: Completed request for history
        sample_requests.append(EquipmentRequest(
            equipment_id=equipment_list[3].id if len(equipment_list) > 3 else None,
            requesting_department_id=departments[0].id if departments else None,
            requested_by_staff_id=staff_members[0].id if staff_members else None,
            request_type="Transfer",
            priority="Medium",
            status="Completed",
            requested_at=datetime.now() - timedelta(hours=3),
            required_by=datetime.now() - timedelta(hours=1),
            pickup_location="Radiology",
            delivery_location="Cardiology",
            special_instructions="Patient scan completed",
            quantity=1,
            completed_at=datetime.now() - timedelta(minutes=45)
        ))
        
        # Add all requests
        session.add_all(sample_requests)
        await session.commit()
        
        print(f"✅ Added {len(sample_requests)} sample equipment requests:")
        for req in sample_requests:
            print(f"   - {req.request_type} ({req.priority} priority) - {req.status}")
        
        # Verify request count
        result = await session.execute(select(EquipmentRequest))
        total_requests = len(result.scalars().all())
        print(f"✅ Verified: {total_requests} equipment requests in database")

if __name__ == "__main__":
    print("🏥 Adding Sample Equipment Requests to Hospital Database")
    print("=" * 55)
    
    try:
        asyncio.run(add_sample_equipment_requests())
        print("\n🎉 Sample equipment requests setup completed successfully!")
    except Exception as e:
        print(f"\n❌ Error adding equipment requests: {e}")
        sys.exit(1)
