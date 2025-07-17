"""
Simplified Database Setup - Hospital Supply System
Creates tables and basic data without complex relationships
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

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    host = os.getenv('DATABASE_HOST', 'localhost')
    port = os.getenv('DATABASE_PORT', '5432')
    database = os.getenv('DATABASE_NAME', 'hospital_supply_db')
    username = os.getenv('DATABASE_USER', 'postgres')
    password = os.getenv('DATABASE_PASSWORD', '')
    
    if not password or password == 'YOUR_POSTGRES_PASSWORD':
        print("❌ Please set DATABASE_PASSWORD in your .env file")
        print("📝 Edit backend/.env and replace 'YOUR_POSTGRES_PASSWORD' with your actual PostgreSQL password")
        return None
    
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"

class SimpleDatabaseSetup:
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

    async def create_tables_sql(self):
        """Create tables using direct SQL"""
        try:
            async with self.engine.begin() as conn:
                # Create tables with direct SQL to avoid relationship issues
                sql_statements = [
                    # Users table
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        user_id VARCHAR(50) PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        full_name VARCHAR(255),
                        role VARCHAR(50) NOT NULL,
                        department VARCHAR(100),
                        is_active BOOLEAN DEFAULT TRUE,
                        password_hash VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    
                    # Locations table
                    """
                    CREATE TABLE IF NOT EXISTS locations (
                        location_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        location_type VARCHAR(50),
                        capacity INTEGER DEFAULT 0,
                        current_utilization INTEGER DEFAULT 0,
                        description TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    
                    # Suppliers table
                    """
                    CREATE TABLE IF NOT EXISTS suppliers (
                        supplier_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        contact_person VARCHAR(255),
                        email VARCHAR(255),
                        phone VARCHAR(50),
                        address TEXT,
                        payment_terms VARCHAR(100),
                        is_active BOOLEAN DEFAULT TRUE,
                        performance_rating DECIMAL(3,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """,
                    
                    # Inventory Items table
                    """
                    CREATE TABLE IF NOT EXISTS inventory_items (
                        item_id VARCHAR(50) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        category VARCHAR(100),
                        unit_of_measure VARCHAR(50),
                        current_stock INTEGER DEFAULT 0,
                        minimum_stock INTEGER DEFAULT 0,
                        maximum_stock INTEGER DEFAULT 0,
                        reorder_point INTEGER DEFAULT 0,
                        unit_cost DECIMAL(10,2),
                        location_id VARCHAR(50),
                        supplier_id VARCHAR(50),
                        expiry_date TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (location_id) REFERENCES locations(location_id),
                        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
                    )
                    """,
                    
                    # Alerts table
                    """
                    CREATE TABLE IF NOT EXISTS alerts (
                        alert_id VARCHAR(50) PRIMARY KEY,
                        alert_type VARCHAR(100) NOT NULL,
                        level VARCHAR(20) NOT NULL,
                        message TEXT,
                        item_id VARCHAR(50),
                        location_id VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_resolved BOOLEAN DEFAULT FALSE,
                        resolved_at TIMESTAMP,
                        resolved_by VARCHAR(50),
                        FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
                        FOREIGN KEY (location_id) REFERENCES locations(location_id)
                    )
                    """,
                    
                    # Transfers table
                    """
                    CREATE TABLE IF NOT EXISTS transfers (
                        transfer_id VARCHAR(50) PRIMARY KEY,
                        item_id VARCHAR(50),
                        from_location_id VARCHAR(50),
                        to_location_id VARCHAR(50),
                        quantity INTEGER NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        requested_by VARCHAR(50),
                        approved_by VARCHAR(50),
                        requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        approved_date TIMESTAMP,
                        completed_date TIMESTAMP,
                        reason TEXT,
                        notes TEXT,
                        FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
                        FOREIGN KEY (from_location_id) REFERENCES locations(location_id),
                        FOREIGN KEY (to_location_id) REFERENCES locations(location_id),
                        FOREIGN KEY (requested_by) REFERENCES users(user_id),
                        FOREIGN KEY (approved_by) REFERENCES users(user_id)
                    )
                    """,
                    
                    # Purchase Orders table
                    """
                    CREATE TABLE IF NOT EXISTS purchase_orders (
                        po_id VARCHAR(50) PRIMARY KEY,
                        supplier_id VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'pending',
                        total_amount DECIMAL(15,2),
                        created_by VARCHAR(50),
                        approved_by VARCHAR(50),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        approved_date TIMESTAMP,
                        expected_delivery TIMESTAMP,
                        notes TEXT,
                        FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
                        FOREIGN KEY (created_by) REFERENCES users(user_id),
                        FOREIGN KEY (approved_by) REFERENCES users(user_id)
                    )
                    """,
                    
                    # Budget table
                    """
                    CREATE TABLE IF NOT EXISTS budgets (
                        budget_id VARCHAR(50) PRIMARY KEY,
                        department VARCHAR(100),
                        total_budget DECIMAL(15,2),
                        allocated_budget DECIMAL(15,2),
                        spent_amount DECIMAL(15,2),
                        remaining_budget DECIMAL(15,2),
                        fiscal_year INTEGER,
                        created_by VARCHAR(50),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (created_by) REFERENCES users(user_id)
                    )
                    """
                ]
                
                for sql in sql_statements:
                    await conn.execute(text(sql))
                
                logger.info("✅ Database tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False

    async def seed_sample_data(self):
        """Insert sample data"""
        try:
            async with self.engine.begin() as conn:
                # Check if data exists
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                if result.scalar() > 0:
                    logger.info("✅ Database already contains data")
                    return True

                logger.info("📊 Inserting sample data...")
                
                # Insert sample data
                sample_data = [
                    # Users
                    """
                    INSERT INTO users (user_id, username, email, full_name, role, department, is_active, password_hash)
                    VALUES 
                    ('admin001', 'admin', 'admin@hospital.com', 'System Administrator', 'ADMIN', 'IT', TRUE, '$2b$12$hash'),
                    ('nurse001', 'nurse1', 'nurse1@hospital.com', 'Sarah Johnson', 'STAFF', 'ICU', TRUE, '$2b$12$hash'),
                    ('manager001', 'manager1', 'manager1@hospital.com', 'Dr. Michael Chen', 'MANAGER', 'Emergency', TRUE, '$2b$12$hash')
                    """,
                    
                    # Locations
                    """
                    INSERT INTO locations (location_id, name, location_type, capacity, current_utilization, description)
                    VALUES 
                    ('ICU-01', 'Intensive Care Unit', 'department', 100, 0, 'Main ICU ward'),
                    ('ER-01', 'Emergency Room', 'department', 200, 0, 'Emergency department'),
                    ('WAREHOUSE', 'Main Warehouse', 'storage', 10000, 0, 'Central supply warehouse')
                    """,
                    
                    # Suppliers
                    """
                    INSERT INTO suppliers (supplier_id, name, contact_person, email, phone, address, payment_terms, is_active, performance_rating)
                    VALUES 
                    ('SUP-001', 'MedSupply Inc.', 'John Smith', 'orders@medsupply.com', '+1-555-0123', '123 Medical Drive, Health City, HC 12345', 'Net 30', TRUE, 4.5),
                    ('SUP-002', 'Healthcare Solutions LLC', 'Emma Wilson', 'sales@healthcaresolutions.com', '+1-555-0456', '456 Supply Lane, Med Town, MT 67890', 'Net 15', TRUE, 4.2)
                    """,
                    
                    # Inventory Items
                    """
                    INSERT INTO inventory_items (item_id, name, category, unit_of_measure, current_stock, minimum_stock, maximum_stock, reorder_point, unit_cost, location_id, supplier_id, is_active, description)
                    VALUES 
                    ('ITEM-001', 'Surgical Gloves (Box of 100)', 'PPE', 'box', 85, 50, 200, 75, 25.00, 'WAREHOUSE', 'SUP-001', TRUE, 'Latex-free surgical gloves'),
                    ('ITEM-002', 'Paracetamol 500mg (Box)', 'Medication', 'box', 120, 100, 500, 150, 12.50, 'WAREHOUSE', 'SUP-002', TRUE, 'Pain relief medication'),
                    ('ITEM-003', 'Sterile Gauze Pads', 'Medical Supplies', 'pack', 300, 200, 1000, 250, 8.75, 'WAREHOUSE', 'SUP-001', TRUE, 'Sterile wound dressing pads')
                    """,
                    
                    # Budget
                    """
                    INSERT INTO budgets (budget_id, department, total_budget, allocated_budget, spent_amount, remaining_budget, fiscal_year, created_by, is_active)
                    VALUES 
                    ('BUDGET-2025', 'Hospital', 1000000.00, 750000.00, 250000.00, 500000.00, 2025, 'admin001', TRUE)
                    """
                ]
                
                for sql in sample_data:
                    await conn.execute(text(sql))
                
                logger.info("✅ Sample data inserted successfully")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to insert sample data: {e}")
            return False

    async def verify_setup(self):
        """Verify the setup"""
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
    print("🏥 Hospital Supply System - Simple Database Setup")
    print("=" * 55)
    
    try:
        db_setup = SimpleDatabaseSetup()
        
        logger.info("🔌 Testing database connection...")
        if not await db_setup.test_connection():
            return False
        
        logger.info("🏗️ Creating database tables...")
        if not await db_setup.create_tables_sql():
            return False
        
        logger.info("🌱 Setting up sample data...")
        if not await db_setup.seed_sample_data():
            return False
        
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
        print("🚀 Restart your API server to use database mode:")
        print("   python api/professional_main_smart.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ DATABASE SETUP FAILED!")
        print("📝 Please check your .env file and PostgreSQL connection")
        print("="*60)
