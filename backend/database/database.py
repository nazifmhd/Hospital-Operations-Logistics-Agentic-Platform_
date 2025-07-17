"""
PostgreSQL Database Setup and Configuration
Hospital Supply Inventory Management System
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import logging

# Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'hospital_supply_db'),
    'username': os.getenv('DB_USER', 'hospital_user'),
    'password': os.getenv('DB_PASSWORD', 'hospital_pass'),
}

# Create database URLs
SYNC_DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# SQLAlchemy setup
Base = declarative_base()

# Async engine and session
async_engine = None
AsyncSessionLocal = None

# Sync engine and session
sync_engine = None
SessionLocal = None

class DatabaseManager:
    """Database manager for hospital supply system"""
    
    def __init__(self):
        self.async_engine = None
        self.sync_engine = None
        self.async_session_maker = None
        self.sync_session_maker = None
        
    async def initialize(self):
        """Initialize both async and sync database connections"""
        try:
            # Initialize async connection
            async_result = await self.initialize_async()
            # Initialize sync connection
            sync_result = self.initialize_sync()
            
            if async_result or sync_result:
                logging.info("✅ Database initialization completed")
                return True
            else:
                logging.error("❌ Database initialization failed")
                return False
        except Exception as e:
            logging.error(f"❌ Database initialization error: {e}")
            return False
        
    async def initialize_async(self):
        """Initialize async database connection"""
        try:
            self.async_engine = create_async_engine(
                ASYNC_DATABASE_URL,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "server_settings": {
                        "application_name": "hospital_supply_system",
                    }
                }
            )
            
            self.async_session_maker = async_sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test connection
            async with self.async_engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                
            logging.info("✅ Async PostgreSQL connection established successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to connect to PostgreSQL (Async): {e}")
            return False
    
    def initialize_sync(self):
        """Initialize sync database connection"""
        try:
            self.sync_engine = create_engine(
                SYNC_DATABASE_URL,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "application_name": "hospital_supply_system_sync",
                }
            )
            
            self.sync_session_maker = sessionmaker(
                bind=self.sync_engine,
                autocommit=False,
                autoflush=False
            )
            
            # Test connection
            with self.sync_engine.begin() as conn:
                conn.execute(text("SELECT 1"))
                
            logging.info("✅ Sync PostgreSQL connection established successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to connect to PostgreSQL (Sync): {e}")
            return False
    
    async def get_async_session(self) -> AsyncSession:
        """Get async database session"""
        if not self.async_session_maker:
            await self.initialize_async()
        return self.async_session_maker()
    
    def get_sync_session(self):
        """Get sync database session"""
        if not self.sync_session_maker:
            self.initialize_sync()
        return self.sync_session_maker()
    
    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logging.info("✅ Database tables created successfully")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to create tables: {e}")
            return False
    
    async def drop_tables(self):
        """Drop all database tables (use with caution)"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logging.info("⚠️ Database tables dropped")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to drop tables: {e}")
            return False
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database health and statistics"""
        try:
            async with self.get_async_session() as session:
                # Check connection
                result = await session.execute(text("SELECT 1 as health_check"))
                health_check = result.scalar()
                
                # Get database size
                db_size_result = await session.execute(
                    text(f"SELECT pg_size_pretty(pg_database_size('{DATABASE_CONFIG['database']}')) as db_size")
                )
                db_size = db_size_result.scalar()
                
                # Get table count
                table_count_result = await session.execute(
                    text("""
                        SELECT COUNT(*) as table_count 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                )
                table_count = table_count_result.scalar()
                
                # Get active connections
                connections_result = await session.execute(
                    text("""
                        SELECT COUNT(*) as active_connections 
                        FROM pg_stat_activity 
                        WHERE datname = :db_name
                    """),
                    {"db_name": DATABASE_CONFIG['database']}
                )
                active_connections = connections_result.scalar()
                
                return {
                    "status": "healthy" if health_check == 1 else "unhealthy",
                    "database_size": db_size,
                    "table_count": table_count,
                    "active_connections": active_connections,
                    "engine_pool_size": self.async_engine.pool.size(),
                    "engine_pool_checked_out": self.async_engine.pool.checkedout(),
                    "timestamp": asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            logging.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        logging.info("🔒 Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency for FastAPI
async def get_async_db() -> AsyncSession:
    """FastAPI dependency for async database session"""
    async with db_manager.get_async_session() as session:
        try:
            yield session
        finally:
            await session.close()

def get_sync_db():
    """FastAPI dependency for sync database session"""
    session = db_manager.get_sync_session()
    try:
        yield session
    finally:
        session.close()

# Database initialization functions
async def init_database():
    """Initialize database connection and create tables"""
    try:
        # Initialize connections
        async_success = await db_manager.initialize_async()
        sync_success = db_manager.initialize_sync()
        
        if async_success and sync_success:
            # Create tables
            await db_manager.create_tables()
            logging.info("🚀 Database initialization completed successfully")
            return True
        else:
            logging.error("❌ Database initialization failed")
            return False
            
    except Exception as e:
        logging.error(f"❌ Database initialization error: {e}")
        return False

async def close_database():
    """Close database connections"""
    await db_manager.close()

# Database utilities
class DatabaseUtilities:
    """Utility functions for database operations"""
    
    @staticmethod
    async def execute_raw_query(query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query and return results"""
        try:
            async with db_manager.get_async_session() as session:
                result = await session.execute(text(query), params or {})
                if result.returns_rows:
                    rows = result.fetchall()
                    return [dict(row._mapping) for row in rows]
                else:
                    await session.commit()
                    return [{"affected_rows": result.rowcount}]
        except Exception as e:
            logging.error(f"Raw query execution failed: {e}")
            raise
    
    @staticmethod
    async def get_table_info(table_name: str) -> Dict[str, Any]:
        """Get information about a specific table"""
        try:
            query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """
            
            async with db_manager.get_async_session() as session:
                result = await session.execute(text(query), {"table_name": table_name})
                columns = [dict(row._mapping) for row in result.fetchall()]
                
                # Get row count
                count_query = f"SELECT COUNT(*) as row_count FROM {table_name}"
                count_result = await session.execute(text(count_query))
                row_count = count_result.scalar()
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "row_count": row_count
                }
                
        except Exception as e:
            logging.error(f"Failed to get table info for {table_name}: {e}")
            raise

# Export main components
__all__ = [
    'Base',
    'db_manager',
    'get_async_db',
    'get_sync_db',
    'init_database',
    'close_database',
    'DatabaseManager',
    'DatabaseUtilities',
    'DATABASE_CONFIG',
    'ASYNC_DATABASE_URL',
    'SYNC_DATABASE_URL'
]
