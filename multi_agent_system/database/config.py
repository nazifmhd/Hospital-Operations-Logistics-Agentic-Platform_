"""
Database Configuration for Multi-Agent Hospital Operations System
Enhanced database setup with connection pooling and optimization
"""

import os
import logging
from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import asyncio

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'multi_agent_hospital'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

# Connection strings
SYNC_DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

class DatabaseManager:
    """Enhanced database manager for multi-agent system"""
    
    def __init__(self):
        self.sync_engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialized = False
    
    def initialize_sync_engine(self):
        """Initialize synchronous database engine"""
        self.sync_engine = create_engine(
            SYNC_DATABASE_URL,
            poolclass=pool.QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.sync_engine
        )
        logger.info("✅ Sync database engine initialized")
    
    def initialize_async_engine(self):
        """Initialize asynchronous database engine"""
        self.async_engine = create_async_engine(
            ASYNC_DATABASE_URL,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("✅ Async database engine initialized")
    
    def initialize(self):
        """Initialize both sync and async engines"""
        if not self._initialized:
            self.initialize_sync_engine()
            self.initialize_async_engine()
            self._initialized = True
            logger.info("✅ Database manager fully initialized")
    
    def get_sync_session(self):
        """Get synchronous database session"""
        if not self.SessionLocal:
            self.initialize_sync_engine()
        return self.SessionLocal()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get asynchronous database session with context manager"""
        if not self.AsyncSessionLocal:
            self.initialize_async_engine()
        
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all database tables"""
        from .models import Base
        
        if not self.async_engine:
            self.initialize_async_engine()
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables"""
        from .models import Base
        
        if not self.async_engine:
            self.initialize_async_engine()
        
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        logger.info("✅ Database tables dropped successfully")
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.get_async_session() as session:
                result = await session.execute(text("SELECT 1"))
                return result.scalar() == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    async def is_healthy(self) -> bool:
        """Alias for health_check for compatibility"""
        return await self.health_check()
    
    async def close(self):
        """Close database connections"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.sync_engine:
            self.sync_engine.dispose()
        logger.info("✅ Database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Dependency functions for FastAPI
def get_sync_db():
    """Dependency for synchronous database sessions"""
    db = db_manager.get_sync_session()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for asynchronous database sessions"""
    async with db_manager.get_async_session() as session:
        yield session

# Utility functions
async def init_database():
    """Initialize database with tables"""
    logger.info("🔄 Initializing database...")
    db_manager.initialize()
    await db_manager.create_tables()
    logger.info("✅ Database initialization complete")

async def reset_database():
    """Reset database (drop and recreate tables)"""
    logger.warning("⚠️ Resetting database - all data will be lost!")
    db_manager.initialize()
    await db_manager.drop_tables()
    await db_manager.create_tables()
    logger.info("✅ Database reset complete")

# Connection verification
def verify_connection():
    """Verify database connection on startup"""
    try:
        db_manager.initialize()
        with db_manager.get_sync_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
