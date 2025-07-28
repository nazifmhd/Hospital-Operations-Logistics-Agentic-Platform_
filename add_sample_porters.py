#!/usr/bin/env python3
"""
Add Sample Porter Staff to Database
Creates porter staff members for testing the Equipment Request & Dispatch functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system.database.config import db_manager
from multi_agent_system.database.models import StaffMember, Department, StaffRole, StaffStatus
from sqlalchemy import select

async def add_sample_porters():
    """Add sample porter staff to the database"""
    print("🔧 Initializing database connection...")
    db_manager.initialize_async_engine()
    
    async with db_manager.get_async_session() as session:
        # Check if support staff (porters) already exist
        result = await session.execute(
            select(StaffMember).where(StaffMember.role == StaffRole.SUPPORT)
        )
        existing_porters = result.scalars().all()
        
        if existing_porters:
            print(f"✅ Found {len(existing_porters)} existing porter(s)")
            for porter in existing_porters:
                print(f"  - {porter.name} ({porter.status})")
            return True
        
        # Get a department for the porters
        departments_result = await session.execute(select(Department).limit(1))
        departments = departments_result.scalars().all()
        
        print(f"👥 Adding sample porter staff...")
        
        # Create sample porters
        sample_porters = []
        
        # Porter 1: Available
        sample_porters.append(StaffMember(
            id="porter_001",
            employee_id="EMP-PORT-001",
            name="John Porter",
            email="john.porter@hospital.com",
            role=StaffRole.SUPPORT,  # Use SUPPORT role for porters
            department_id=departments[0].id if departments else None,
            specialties=["Equipment Transport", "Patient Transport"],
            status=StaffStatus.AVAILABLE,
            phone="555-0101",
            hire_date=datetime(2023, 1, 15)
        ))
        
        # Porter 2: On duty but busy
        sample_porters.append(StaffMember(
            id="porter_002",
            employee_id="EMP-PORT-002",
            name="Mike Transporter",
            email="mike.transporter@hospital.com",
            role=StaffRole.SUPPORT,
            department_id=departments[0].id if departments else None,
            specialties=["Heavy Equipment Transport", "Emergency Response"],
            status=StaffStatus.ON_DUTY,
            phone="555-0102",
            hire_date=datetime(2023, 3, 10)
        ))
        
        # Porter 3: Available
        sample_porters.append(StaffMember(
            id="porter_003",
            employee_id="EMP-PORT-003",
            name="Sarah Orderly",
            email="sarah.orderly@hospital.com",
            role=StaffRole.SUPPORT,
            department_id=departments[0].id if departments else None,
            specialties=["Patient Transport", "Equipment Setup"],
            status=StaffStatus.AVAILABLE,
            phone="555-0103",
            hire_date=datetime(2023, 5, 20)
        ))

        # Add all sample porters to the session
        for porter in sample_porters:
            session.add(porter)
        
        await session.commit()
        print(f"✅ Added {len(sample_porters)} sample porter staff members")
        
        # Verify the porters were added
        result = await session.execute(
            select(StaffMember).where(StaffMember.role == StaffRole.SUPPORT)
        )
        all_porters = result.scalars().all()
        print(f"✅ Total porter/support staff in database: {len(all_porters)}")
        
        # Display porter summary
        for porter in all_porters:
            print(f"  - {porter.name} ({porter.employee_id}) - Status: {porter.status}")
        
        return True

if __name__ == "__main__":
    print("🏥 Adding Sample Porter Staff to Hospital Database")
    print("=" * 50)
    
    try:
        success = asyncio.run(add_sample_porters())
        if success:
            print("\n🎉 Sample porter staff added successfully!")
        else:
            print("\n💥 Failed to add sample porter staff!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error adding porter staff: {e}")
        sys.exit(1)
