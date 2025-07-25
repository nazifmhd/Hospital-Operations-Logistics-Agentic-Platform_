#!/usr/bin/env python3
"""
Check database tables and their structure
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import db_manager
from sqlalchemy import text

async def check_database_structure():
    db_manager.initialize()
    async with db_manager.get_async_session() as session:
        # Check what tables exist
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))
        tables = result.fetchall()
        print('Available tables:')
        for table in tables:
            print(f'  - {table.table_name}')
            
        # Check specific tables that the API needs
        needed_tables = ['medical_equipment', 'purchase_orders', 'tasks', 'staff_members']
        missing_tables = []
        
        existing_table_names = [t.table_name for t in tables]
        for table in needed_tables:
            if table in existing_table_names:
                print(f'✅ {table} table exists')
            else:
                print(f'❌ {table} table missing')
                missing_tables.append(table)
        
        if missing_tables:
            print(f'\n⚠️  Missing tables: {missing_tables}')
        else:
            print(f'\n✅ All required tables exist')
            
    await db_manager.close()

if __name__ == "__main__":
    asyncio.run(check_database_structure())
