"""
Ultra-Simple Database Setup - Hospital Supply System
Direct SQL approach without complex models
"""

import asyncio
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def setup_database():
    """Setup database with direct SQL"""
    
    # Database URL
    db_url = f"postgresql+asyncpg://postgres:1234@localhost:5432/hospital_supply_db"
    
    engine = create_async_engine(db_url, echo=False)
    
    try:
        logger.info("🔌 Testing database connection...")
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        logger.info("🏗️ Creating database tables...")
        async with engine.begin() as conn:
            # Drop and recreate tables for clean setup
            await conn.execute(text("DROP TABLE IF EXISTS budgets CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS transfers CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS alerts CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS inventory_items CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS suppliers CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS locations CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            
            # Create tables
            tables_sql = [
                """
                CREATE TABLE users (
                    user_id VARCHAR(50) PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255),
                    role VARCHAR(50) NOT NULL,
                    department VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    password_hash VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                
                """
                CREATE TABLE locations (
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
                
                """
                CREATE TABLE suppliers (
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
                
                """
                CREATE TABLE inventory_items (
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                
                """
                CREATE TABLE alerts (
                    alert_id VARCHAR(50) PRIMARY KEY,
                    alert_type VARCHAR(100) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    message TEXT,
                    item_id VARCHAR(50),
                    location_id VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolved_at TIMESTAMP
                )
                """,
                
                """
                CREATE TABLE transfers (
                    transfer_id VARCHAR(50) PRIMARY KEY,
                    item_id VARCHAR(50),
                    from_location_id VARCHAR(50),
                    to_location_id VARCHAR(50),
                    quantity INTEGER NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    requested_by VARCHAR(50),
                    requested_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
                """,
                
                """
                CREATE TABLE budgets (
                    budget_id VARCHAR(50) PRIMARY KEY,
                    department VARCHAR(100),
                    total_budget DECIMAL(15,2),
                    allocated_budget DECIMAL(15,2),
                    spent_amount DECIMAL(15,2),
                    remaining_budget DECIMAL(15,2),
                    fiscal_year INTEGER,
                    created_by VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]
            
            for sql in tables_sql:
                await conn.execute(text(sql))
            
            logger.info("✅ Tables created successfully")
            
        logger.info("🌱 Inserting sample data...")
        async with engine.begin() as conn:
            sample_data = [
                """
                INSERT INTO users VALUES 
                ('admin001', 'admin', 'admin@hospital.com', 'System Administrator', 'admin', 'IT', TRUE, 'hash123', CURRENT_TIMESTAMP),
                ('nurse001', 'nurse1', 'nurse1@hospital.com', 'Sarah Johnson', 'staff', 'ICU', TRUE, 'hash123', CURRENT_TIMESTAMP),
                ('manager001', 'manager1', 'manager1@hospital.com', 'Dr. Michael Chen', 'manager', 'Emergency', TRUE, 'hash123', CURRENT_TIMESTAMP)
                """,
                
                """
                INSERT INTO locations VALUES 
                ('ICU-01', 'Intensive Care Unit', 'department', 100, 0, 'Main ICU ward', TRUE, CURRENT_TIMESTAMP),
                ('ER-01', 'Emergency Room', 'department', 200, 0, 'Emergency department', TRUE, CURRENT_TIMESTAMP),
                ('WAREHOUSE', 'Main Warehouse', 'storage', 10000, 0, 'Central supply warehouse', TRUE, CURRENT_TIMESTAMP)
                """,
                
                """
                INSERT INTO suppliers VALUES 
                ('SUP-001', 'MedSupply Inc.', 'John Smith', 'orders@medsupply.com', '+1-555-0123', '123 Medical Drive, Health City, HC 12345', 'Net 30', TRUE, 4.5, CURRENT_TIMESTAMP),
                ('SUP-002', 'Healthcare Solutions LLC', 'Emma Wilson', 'sales@healthcaresolutions.com', '+1-555-0456', '456 Supply Lane, Med Town, MT 67890', 'Net 15', TRUE, 4.2, CURRENT_TIMESTAMP)
                """,
                
                """
                INSERT INTO inventory_items VALUES 
                ('ITEM-001', 'Surgical Gloves (Box of 100)', 'PPE', 'box', 85, 50, 200, 75, 25.00, 'WAREHOUSE', 'SUP-001', CURRENT_TIMESTAMP + INTERVAL '365 days', TRUE, 'Latex-free surgical gloves', CURRENT_TIMESTAMP),
                ('ITEM-002', 'Paracetamol 500mg (Box)', 'Medication', 'box', 120, 100, 500, 150, 12.50, 'WAREHOUSE', 'SUP-002', CURRENT_TIMESTAMP + INTERVAL '730 days', TRUE, 'Pain relief medication', CURRENT_TIMESTAMP),
                ('ITEM-003', 'Sterile Gauze Pads', 'Medical Supplies', 'pack', 300, 200, 1000, 250, 8.75, 'WAREHOUSE', 'SUP-001', CURRENT_TIMESTAMP + INTERVAL '1095 days', TRUE, 'Sterile wound dressing pads', CURRENT_TIMESTAMP)
                """,
                
                """
                INSERT INTO budgets VALUES 
                ('BUDGET-2025', 'Hospital', 1000000.00, 750000.00, 250000.00, 500000.00, 2025, 'admin001', TRUE, CURRENT_TIMESTAMP)
                """
            ]
            
            for sql in sample_data:
                await conn.execute(text(sql))
            
            logger.info("✅ Sample data inserted successfully")
        
        logger.info("✅ Verifying setup...")
        async with engine.begin() as conn:
            for table in ['users', 'inventory_items', 'locations', 'suppliers']:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                logger.info(f"✅ {table}: {count} records")
        
        logger.info("🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(setup_database())
    
    if success:
        print("\n" + "="*60)
        print("🎉 DATABASE SETUP COMPLETE!")
        print("✅ PostgreSQL is ready for your Hospital Supply System")
        print("🚀 Now restart your API server to use database mode:")
        print("   python api/professional_main_smart.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ DATABASE SETUP FAILED!")
        print("="*60)
