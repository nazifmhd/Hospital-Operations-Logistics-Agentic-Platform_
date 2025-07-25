"""Check purchase_orders table structure"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_purchase_orders_table():
    # Use the same config as the application
    DATABASE_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'multi_agent_hospital'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password'),
    }
    DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Get column information
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'purchase_orders'
            ORDER BY ordinal_position
        """)
        
        print("📋 purchase_orders table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
        
        # Check sample data
        sample = await conn.fetch("SELECT * FROM purchase_orders LIMIT 3")
        print(f"\n📊 Sample data ({len(sample)} rows):")
        for row in sample:
            print(f"  {dict(row)}")
            
        # Check if suppliers table has data
        suppliers = await conn.fetch("SELECT * FROM suppliers LIMIT 3")
        print(f"\n📊 Suppliers sample data ({len(suppliers)} rows):")
        for row in suppliers:
            print(f"  {dict(row)}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_purchase_orders_table())
