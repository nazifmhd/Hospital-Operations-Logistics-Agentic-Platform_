"""Check database tables referenced in equipment tracker query"""
import asyncio
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi_agent_system'))

async def check_equipment_tables():
    try:
        from database.config import db_manager
        
        # Initialize the database manager
        db_manager.initialize_async_engine()
        
        async with db_manager.get_async_session() as session:
            from sqlalchemy import text
            
            # Check which tables exist
            tables_to_check = ['medical_equipment', 'departments', 'locations']
            
            for table in tables_to_check:
                result = await session.execute(text(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = '{table}'
                """))
                
                if result.fetchone():
                    print(f"✅ {table} table exists")
                    
                    # Get column information
                    columns = await session.execute(text(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = '{table}'
                        ORDER BY ordinal_position
                    """))
                    
                    print(f"   Columns: {[col.column_name for col in columns.fetchall()]}")
                else:
                    print(f"❌ {table} table does not exist")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_equipment_tables())
