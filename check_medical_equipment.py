"""Check medical_equipment table structure"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_medical_equipment_table():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hospital_db")
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Check if table exists
        result = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'medical_equipment'
        """)
        
        if result:
            print("✅ medical_equipment table exists")
            
            # Get column information
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'medical_equipment'
                ORDER BY ordinal_position
            """)
            
            print("\n📋 medical_equipment table columns:")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Check sample data
            sample = await conn.fetch("SELECT * FROM medical_equipment LIMIT 3")
            print(f"\n📊 Sample data ({len(sample)} rows):")
            for row in sample:
                print(f"  {dict(row)}")
                
        else:
            print("❌ medical_equipment table does not exist")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_medical_equipment_table())
