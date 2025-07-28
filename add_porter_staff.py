#!/usr/bin/env python3
"""
Add Porter Staff Members to Database
Adds porter/transport staff to the staff_members table for testing equipment dispatch functionality.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system.database.config import get_async_session
from multi_agent_system.database.models import StaffMember
from sqlalchemy import select

async def add_porter_staff():
    """Add porter staff members to the database"""
    print("🔧 Initializing database connection...")
    
    async with get_async_session() as session:
        # Check if porters already exist
        result = await session.execute(
            select(StaffMember).where(StaffMember.role.ilike('%porter%'))
        )
        existing_porters = result.scalars().all()
        
        if existing_porters:
            print(f"✅ Found {len(existing_porters)} existing porter(s) in database")
            for porter in existing_porters:
                print(f"   - {porter.name} ({porter.role})")
            return
        
        print("📋 Adding porter staff members...")
        
        # Add porter staff members
        porter_staff = [
            StaffMember(
                name="John Smith",
                role="Porter",
                department="Transportation",
                shift="Day",
                contact_info="ext. 1234",
                is_available=True
            ),
            StaffMember(
                name="Maria Rodriguez",
                role="Transport Porter",
                department="Transportation", 
                shift="Evening",
                contact_info="ext. 1235",
                is_available=True
            ),
            StaffMember(
                name="David Chen",
                role="Medical Porter",
                department="Emergency",
                shift="Night",
                contact_info="ext. 1236", 
                is_available=True
            ),
            StaffMember(
                name="Sarah Johnson",
                role="Equipment Transport",
                department="Central Supply",
                shift="Day",
                contact_info="ext. 1237",
                is_available=False
            )
        ]
        
        # Add all porter staff
        session.add_all(porter_staff)
        await session.commit()
        
        print(f"✅ Added {len(porter_staff)} porter staff members:")
        for staff in porter_staff:
            status = "Available" if staff.is_available else "Busy"
            print(f"   - {staff.name} ({staff.role}) - {status}")
        
        # Verify porter count
        result = await session.execute(
            select(StaffMember).where(
                StaffMember.role.ilike('%porter%') | 
                StaffMember.role.ilike('%transport%')
            )
        )
        total_porters = len(result.scalars().all())
        print(f"✅ Verified: {total_porters} porter/transport staff in database")

if __name__ == "__main__":
    print("🏥 Adding Porter Staff to Hospital Database")
    print("=" * 50)
    
    try:
        asyncio.run(add_porter_staff())
        print("\n🎉 Porter staff setup completed successfully!")
    except Exception as e:
        print(f"\n❌ Error adding porter staff: {e}")
        sys.exit(1)
