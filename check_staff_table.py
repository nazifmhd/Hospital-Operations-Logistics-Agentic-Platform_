"""Check staff_members table structure"""
import asyncio
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'multi_agent_system'))

async def check_staff_table():
    try:
        from database.config import db_manager
        
        # Initialize the database manager
        db_manager.initialize_async_engine()
        
        async with db_manager.get_async_session() as session:
            from sqlalchemy import text
            
            # Check if staff_members table exists
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'staff_members'
            """))
            
            if result.fetchone():
                print("✅ staff_members table exists")
                
                # Get column information
                columns = await session.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = 'staff_members'
                    ORDER BY ordinal_position
                """))
                
                column_list = [col.column_name for col in columns.fetchall()]
                print(f"   Columns: {column_list}")
                
                # Check if 'department' and 'status' columns exist
                if 'department' not in column_list:
                    print("❌ 'department' column missing")
                if 'status' not in column_list:
                    print("❌ 'status' column missing")
                    
            else:
                print("❌ staff_members table does not exist")
                
                # Check if there's a similar table like 'staff'
                similar_tables = await session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name LIKE '%staff%'
                """))
                
                for table in similar_tables.fetchall():
                    print(f"Found similar table: {table.table_name}")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_staff_table())
