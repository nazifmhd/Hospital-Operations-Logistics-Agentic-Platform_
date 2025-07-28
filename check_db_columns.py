import asyncio
import sys
sys.path.append('.')
from backend.database.config import DatabaseManager

async def check_columns():
    db = DatabaseManager()
    async with db.get_async_session() as session:
        from sqlalchemy import text
        result = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'supply_items' ORDER BY ordinal_position"))
        columns = [row[0] for row in result.fetchall()]
        print('Columns in supply_items table:')
        for col in columns:
            print(f'  - {col}')
        
        # Also show a sample row
        result = await session.execute(text('SELECT * FROM supply_items LIMIT 1'))
        row = result.fetchone()
        if row:
            print('\nSample row:')
            for i, col in enumerate(columns):
                print(f'  {col}: {row[i] if i < len(row) else "N/A"}')

asyncio.run(check_columns())
