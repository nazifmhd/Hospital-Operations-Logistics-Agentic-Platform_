"""
Direct Database Initialization for Hospital Supply System
Simple and reliable database setup with PostgreSQL
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Database imports
from database.config import DATABASE_URL_ASYNC, DATABASE_CONFIG
from database.models import Base, User, InventoryItem, Location, Supplier, Batch, Alert, Transfer, PurchaseOrder, ApprovalRequest, Budget, AuditLog, Notification
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectDatabaseSetup:
    def __init__(self):
        self.engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create all database tables"""
        try:
            async with self.engine.begin() as conn:
                # Drop all tables first (fresh start)
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("Dropped existing tables")
                
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ All database tables created successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False

    async def seed_data(self):
        """Seed the database with sample data"""
        try:
            async with self.async_session() as session:
                # Check if data already exists
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                if result.scalar() > 0:
                    logger.info("Database already contains data, skipping seeding")
                    return True

                # Create sample users
                users = [
                    User(
                        user_id="admin001",
                        username="admin",
                        email="admin@hospital.com",
                        full_name="System Administrator",
                        role="admin",
                        department="IT",
                        is_active=True,
                        password_hash="hashed_password"
                    ),
                    User(
                        user_id="nurse001",
                        username="nurse1",
                        email="nurse1@hospital.com",
                        full_name="Sarah Johnson",
                        role="nurse",
                        department="ICU",
                        is_active=True,
                        password_hash="hashed_password"
                    ),
                    User(
                        user_id="manager001",
                        username="manager1",
                        email="manager1@hospital.com",
                        full_name="Dr. Michael Chen",
                        role="department_manager",
                        department="Emergency",
                        is_active=True,
                        password_hash="hashed_password"
                    )
                ]
                
                for user in users:
                    session.add(user)

                # Create sample locations
                locations = [
                    Location(
                        location_id="ICU-01",
                        name="Intensive Care Unit",
                        location_type="department",
                        capacity=100,
                        current_utilization=0,
                        description="Main ICU ward"
                    ),
                    Location(
                        location_id="ER-01",
                        name="Emergency Room",
                        location_type="department",
                        capacity=200,
                        current_utilization=0,
                        description="Emergency department"
                    ),
                    Location(
                        location_id="WAREHOUSE",
                        name="Main Warehouse",
                        location_type="storage",
                        capacity=10000,
                        current_utilization=0,
                        description="Central supply warehouse"
                    )
                ]
                
                for location in locations:
                    session.add(location)

                # Create sample suppliers
                suppliers = [
                    Supplier(
                        supplier_id="SUP-001",
                        name="MedSupply Inc.",
                        contact_person="John Smith",
                        email="orders@medsupply.com",
                        phone="+1-555-0123",
                        address="123 Medical Drive, Health City, HC 12345",
                        payment_terms="Net 30",
                        is_active=True,
                        performance_rating=4.5
                    ),
                    Supplier(
                        supplier_id="SUP-002",
                        name="Healthcare Solutions LLC",
                        contact_person="Emma Wilson",
                        email="sales@healthcaresolutions.com",
                        phone="+1-555-0456",
                        address="456 Supply Lane, Med Town, MT 67890",
                        payment_terms="Net 15",
                        is_active=True,
                        performance_rating=4.2
                    )
                ]
                
                for supplier in suppliers:
                    session.add(supplier)

                # Create sample inventory items
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
                        expiry_date=datetime.now() + timedelta(days=365),
                        is_active=True,
                        description="Latex-free surgical gloves"
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
                        supplier_id="SUP-002",
                        expiry_date=datetime.now() + timedelta(days=730),
                        is_active=True,
                        description="Pain relief medication"
                    ),
                    InventoryItem(
                        item_id="ITEM-003",
                        name="Sterile Gauze Pads",
                        category="Medical Supplies",
                        unit_of_measure="pack",
                        current_stock=300,
                        minimum_stock=200,
                        maximum_stock=1000,
                        reorder_point=250,
                        unit_cost=Decimal("8.75"),
                        location_id="WAREHOUSE",
                        supplier_id="SUP-001",
                        expiry_date=datetime.now() + timedelta(days=1095),
                        is_active=True,
                        description="Sterile wound dressing pads"
                    )
                ]
                
                for item in inventory_items:
                    session.add(item)

                # Create sample budget
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
                session.add(budget)

                # Commit all data
                await session.commit()
                logger.info("✅ Database seeded with sample data successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to seed database: {e}")
            return False

    async def verify_setup(self):
        """Verify the database setup"""
        try:
            async with self.async_session() as session:
                # Check tables
                tables = ['users', 'inventory_items', 'locations', 'suppliers']
                for table in tables:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    logger.info(f"✅ {table}: {count} records")
                
                logger.info("✅ Database verification completed successfully")
                return True
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False

    async def close(self):
        """Close database connections"""
        await self.engine.dispose()

async def main():
    """Main database setup function"""
    logger.info("🚀 Starting Direct Database Setup...")
    logger.info(f"Connecting to: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
    
    db_setup = DirectDatabaseSetup()
    
    try:
        # Create tables
        if not await db_setup.create_tables():
            logger.error("Failed to create tables")
            return False
        
        # Seed data
        if not await db_setup.seed_data():
            logger.error("Failed to seed data")
            return False
        
        # Verify setup
        if not await db_setup.verify_setup():
            logger.error("Failed to verify setup")
            return False
        
        logger.info("🎉 Database setup completed successfully!")
        logger.info("✅ Your Hospital Supply System is now connected to PostgreSQL!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False
    finally:
        await db_setup.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n" + "="*60)
        print("🎉 DATABASE SETUP COMPLETE!")
        print("✅ PostgreSQL is ready for your Hospital Supply System")
        print("🚀 You can now restart your API server to use database mode")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ DATABASE SETUP FAILED!")
        print("Please check the error messages above")
        print("="*60)
        sys.exit(1)
