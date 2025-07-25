#!/usr/bin/env python3
"""
Database Migration Script: Add floor field to Bed table
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from database.config import db_manager
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_add_floor_field():
    """Add floor field to Bed table if it doesn't exist"""
    try:
        # Initialize database connection
        db_manager.initialize()
        
        logger.info("🔄 Starting database migration: Add floor field to Bed table")
        
        async with db_manager.get_async_session() as session:
            # Check if floor column exists
            check_column_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='beds' AND column_name='floor';
            """)
            
            result = await session.execute(check_column_query)
            column_exists = result.fetchone()
            
            if column_exists:
                logger.info("✅ Floor column already exists in Bed table")
                return
            
            # Add floor column to beds table
            logger.info("➕ Adding floor column to beds table...")
            add_column_query = text("""
                ALTER TABLE beds 
                ADD COLUMN floor VARCHAR(10) DEFAULT '1';
            """)
            
            await session.execute(add_column_query)
            await session.commit()
            
            logger.info("✅ Successfully added floor column to beds table")
            
            # Update existing records with default floor value if needed
            update_query = text("""
                UPDATE beds 
                SET floor = '1' 
                WHERE floor IS NULL;
            """)
            
            result = await session.execute(update_query)
            await session.commit()
            
            rows_updated = result.rowcount
            logger.info(f"✅ Updated {rows_updated} existing bed records with default floor value")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await db_manager.close()

async def main():
    """Main migration execution"""
    try:
        await migrate_add_floor_field()
        logger.info("🎉 Migration completed successfully!")
    except Exception as e:
        logger.error(f"💥 Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
