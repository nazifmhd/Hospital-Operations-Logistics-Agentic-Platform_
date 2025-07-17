"""
Environment-based Database Setup for Hospital Supply System
Uses .env file configuration for database connection
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Database imports
from database.models import Base, User, InventoryItem, Location, Supplier, Budget
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    host = os.getenv('DATABASE_HOST', 'localhost')
    port = os.getenv('DATABASE_PORT', '5432')
    database = os.getenv('DATABASE_NAME', 'hospital_supply_db')
    username = os.getenv('DATABASE_USER', 'postgres')
    password = os.getenv('DATABASE_PASSWORD', '')
    
    if not password:
        print("❌ Please set DATABASE_PASSWORD in your .env file")
        print("📝 Edit backend/.env and replace 'YOUR_POSTGRES_PASSWORD' with your actual PostgreSQL password")
        return None
    
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

class EnvDatabaseSetup:
    def __init__(self):
        self.db_url = get_database_url()
        if not self.db_url:
            raise ValueError("Database URL not configured")
        
        self.engine = create_async_engine(self.db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def test_connection(self):
        """Test database connection"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.engine.begin() as conn:
                # Create all tables (don't drop existing ones)
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Database tables created successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False

    async def seed_sample_data(self):
        """Seed database with sample data"""
        try:
            async with self.async_session() as session:
                # Check if data already exists
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                if result.scalar() > 0:
                    logger.info("✅ Database already contains data")
                    return True

                logger.info("📊 Seeding database with sample data...")

                # Sample users
                users = [
                    User(
                        user_id="admin001",
                        username="admin",
                        email="admin@hospital.com",
                        full_name="System Administrator",
                        role="admin",
                        department="IT",
                        is_active=True,
                        password_hash="$2b$12$hashed_password"
                    ),
                    User(
                        user_id="nurse001",
                        username="nurse1",
                        email="nurse1@hospital.com",
                        full_name="Sarah Johnson",
                        role="nurse",
                        department="ICU",
                        is_active=True,
                        password_hash="$2b$12$hashed_password"
                    )
                ]

                # Sample locations
                locations = [
                    Location(
                        location_id="ICU-01",
                        name="Intensive Care Unit",
                        location_type="department",
                        capacity=100,
                        current_utilization=0
                    ),
                    Location(
                        location_id="WAREHOUSE",
                        name="Main Warehouse",
                        location_type="storage",
                        capacity=10000,
                        current_utilization=0
                    )
                ]

                # Sample suppliers
                suppliers = [
                    Supplier(
                        supplier_id="SUP-001",
                        name="MedSupply Inc.",
                        contact_person="John Smith",
                        email="orders@medsupply.com",
                        phone="+1-555-0123",
                        address="123 Medical Drive, Health City, HC 12345",
                        is_active=True,
                        performance_rating=4.5
                    )
                ]

                # Sample inventory items
                inventory_items = [
                    InventoryItem(
                        item_id="ITEM-001",
                        name="Surgical Gloves (Box of 100)",
                        category="PPE",
                        unit_of_measure="box",
                        current_stock=85,
                        minimum_stock=50,
                        maximum_stock=200,
                        reorder_point=75,
                        unit_cost=Decimal("25.00"),
                        location_id="WAREHOUSE",
                        supplier_id="SUP-001",
                        is_active=True
                    ),
                    InventoryItem(
                        item_id="ITEM-002",
                        name="Paracetamol 500mg (Box)",
                        category="Medication",
                        unit_of_measure="box",
                        current_stock=120,
                        minimum_stock=100,
                        maximum_stock=500,
                        reorder_point=150,
                        unit_cost=Decimal("12.50"),
                        location_id="WAREHOUSE",
                        supplier_id="SUP-001",
                        is_active=True
                    )
                ]

                # Sample budget
                budget = Budget(
                    budget_id="BUDGET-2025",
                    department="Hospital",
                    total_budget=Decimal("1000000.00"),
                    allocated_budget=Decimal("750000.00"),
                    spent_amount=Decimal("250000.00"),
                    remaining_budget=Decimal("500000.00"),
                    fiscal_year=2025,
                    created_by="admin001",
                    is_active=True
                )

                # Add all data
                for user in users:
                    session.add(user)
                for location in locations:
                    session.add(location)
                for supplier in suppliers:
                    session.add(supplier)
                for item in inventory_items:
                    session.add(item)
                session.add(budget)

                await session.commit()
                logger.info("✅ Sample data seeded successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to seed data: {e}")
            return False

    async def verify_setup(self):
        """Verify database setup"""
        try:
            async with self.async_session() as session:
                tables = ['users', 'inventory_items', 'locations', 'suppliers']
                for table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"✅ {table}: {count} records")
                return True
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False

    async def close(self):
        await self.engine.dispose()

async def main():
    """Main setup function"""
    print("🏥 Hospital Supply System - Database Setup")
    print("=" * 50)
    
    try:
        # Check environment
        if not os.path.exists('.env'):
            logger.error("❌ .env file not found")
            return False
        
        db_setup = EnvDatabaseSetup()
        
        # Test connection
        logger.info("🔌 Testing database connection...")
        if not await db_setup.test_connection():
            return False
        
        # Create tables
        logger.info("🏗️ Creating database tables...")
        if not await db_setup.create_tables():
            return False
        
        # Seed data
        logger.info("🌱 Setting up sample data...")
        if not await db_setup.seed_sample_data():
            return False
        
        # Verify
        logger.info("✅ Verifying setup...")
        if not await db_setup.verify_setup():
            return False
        
        await db_setup.close()
        return True
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    
    if success:
        print("\n" + "="*60)
        print("🎉 DATABASE SETUP COMPLETE!")
        print("✅ PostgreSQL is ready for your Hospital Supply System")
        print("🚀 Restart your API server to use database mode")
        print("   python api/professional_main_smart.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ DATABASE SETUP FAILED!")
        print("📝 Please:")
        print("   1. Check your PostgreSQL password in .env file")
        print("   2. Ensure PostgreSQL is running")
        print("   3. Verify database 'hospital_supply_db' exists")
        print("="*60)
