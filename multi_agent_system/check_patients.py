#!/usr/bin/env python3
"""
Check patients table structure
"""
import asyncio
import sys
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import db_manager
from sqlalchemy import text

async def check_patients_table():
    db_manager.initialize()
    async with db_manager.get_async_session() as session:
        result = await session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'patients'
            ORDER BY ordinal_position;
        """))
        columns = result.fetchall()
        print('Patients table structure:')
        for col in columns:
            print(f'  {col.column_name}: {col.data_type}')
            
        # Test if we can query patients
        result = await session.execute(text("SELECT COUNT(*) as count FROM patients"))
        count = result.scalar()
        print(f'\nTotal patients: {count}')
        
        if count > 0:
            result = await session.execute(text("SELECT * FROM patients LIMIT 1"))
            patient = result.fetchone()
            if patient:
                print(f'Sample patient: {dict(patient._mapping)}')
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(check_patients_table())
