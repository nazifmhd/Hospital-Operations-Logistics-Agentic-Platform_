import asyncio
import sys
sys.path.append('.')

async def check_database_tables():
    try:
        from backend.database.config import DatabaseManager
        db = DatabaseManager()
        async with db.get_async_session() as session:
            from sqlalchemy import text
            
            # Check what tables exist
            result = await session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print('Available tables:')
            for table in tables:
                print(f'  - {table}')
            
            # Check structure of relevant tables
            relevant_tables = ['supply_items', 'suppliers', 'purchase_orders', 'reorders', 'supply_requests']
            
            for table in relevant_tables:
                if table in tables:
                    print(f'\n{table} table structure:')
                    result = await session.execute(text(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """))
                    for row in result.fetchall():
                        print(f'  - {row[0]} ({row[1]}) {"NULL" if row[2] == "YES" else "NOT NULL"}')
                    
                    # Show sample data
                    result = await session.execute(text(f'SELECT * FROM {table} LIMIT 3'))
                    rows = result.fetchall()
                    if rows:
                        print(f'  Sample data: {len(rows)} rows')
                        columns = result.keys()
                        for i, row in enumerate(rows):
                            print(f'    Row {i+1}: {dict(zip(columns, row))}')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(check_database_tables())
