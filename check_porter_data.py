#!/usr/bin/env python3
"""
Check Porter Data in Database
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_agent_system.database.config import db_manager
from multi_agent_system.database.models import StaffMember
from sqlalchemy import select, text

async def check_porter_data():
    """Check porter data in the database"""
    print("🔧 Checking porter data in database...")
    db_manager.initialize_async_engine()
    
    async with db_manager.get_async_session() as session:
        # Check all staff members
        result = await session.execute(select(StaffMember))
        all_staff = result.scalars().all()
        
        print(f"📋 Found {len(all_staff)} staff members:")
        for staff in all_staff:
            print(f"  - {staff.name}: role={staff.role}, status={staff.status}, specialties={staff.specialties}")
        
        # Check with raw SQL
        result = await session.execute(text("""
            SELECT id, name, role, status, specialties 
            FROM staff_members 
            ORDER BY name
        """))
        
        print(f"\n📋 Raw SQL results:")
        for row in result:
            print(f"  - {row.name}: role={row.role}, status={row.status}, specialties={row.specialties}")

if __name__ == "__main__":
    asyncio.run(check_porter_data())
