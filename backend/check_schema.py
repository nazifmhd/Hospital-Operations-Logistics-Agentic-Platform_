import asyncio
from fixed_database_integration import get_fixed_db_integration
from sqlalchemy import text

async def check_schema():
    db_integration = await get_fixed_db_integration()
    async with db_integration.async_session() as session:
        # Check transfers table structure
        print("=== TRANSFERS TABLE COLUMNS ===")
        result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'transfers' ORDER BY ordinal_position"))
        transfers_columns = [row[0] for row in result.fetchall()]
        for col in transfers_columns:
            print(f"  - {col}")
        
        # Check item_locations table structure  
        print("\n=== ITEM_LOCATIONS TABLE COLUMNS ===")
        result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'item_locations' ORDER BY ordinal_position"))
        item_locations_columns = [row[0] for row in result.fetchall()]
        for col in item_locations_columns:
            print(f"  - {col}")
            
        # Check if transfers table exists and sample data
        print("\n=== TRANSFERS TABLE INFO ===")
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM transfers"))
            count = result.scalar()
            print(f"Transfers table record count: {count}")
            
            if count > 0:
                result = await session.execute(text("SELECT * FROM transfers LIMIT 1"))
                sample = result.fetchone()
                print(f"Sample record keys: {sample._fields if hasattr(sample, '_fields') else 'No fields info'}")
        except Exception as e:
            print(f"Error checking transfers table: {e}")

if __name__ == "__main__":
    asyncio.run(check_schema())
