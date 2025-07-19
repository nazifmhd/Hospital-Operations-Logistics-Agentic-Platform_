"""
Database initialization for Hospital Supply Inventory Management System
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal

from .database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Initialize the database - create tables only, no sample data"""
    
    def __init__(self):
        self.db = db_manager
    
    async def initialize_database(self):
        """Create all tables - no seeding, use real data only"""
        try:
            logger.info("Starting database initialization...")
            
            # Create all tables
            await self.db.create_tables()
            logger.info("Database tables created successfully")
            
            # Check if data already exists
            async with await self.db.get_async_session() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                if user_count > 0:
                    logger.info(f"Database contains {user_count} users - using existing data")
                else:
                    logger.info("Database is empty - ready for real data input")
            
            logger.info("Database initialization completed - no sample data inserted")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

# Create global initializer instance
db_initializer = DatabaseInitializer()

# Convenience function to initialize database
async def init_database():
    """Initialize the database with tables only - no sample data"""
    await db_initializer.initialize_database()

if __name__ == "__main__":
    asyncio.run(init_database())
