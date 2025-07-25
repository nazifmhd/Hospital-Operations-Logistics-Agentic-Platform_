"""Check inventory-related tables"""
import asyncio
from database.config import db_manager

async def check_inventory_tables():
    await db_manager.initialize()
    
    async with db_manager.get_async_session() as session:
        # Check inventory_locations table
        result = await session.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'inventory_locations'
        """)
        
        print("inventory_locations columns:")
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
            
        # Check for any current stock or inventory level data
        result = await session.execute("SELECT * FROM inventory_locations LIMIT 3")
        print("\nSample inventory_locations data:")
        rows = result.fetchall()
        for row in rows:
            print(f"  {dict(zip(result.keys(), row))}")

if __name__ == "__main__":
    asyncio.run(check_inventory_tables())
