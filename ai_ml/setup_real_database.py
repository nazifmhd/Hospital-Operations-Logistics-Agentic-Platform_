#!/usr/bin/env python3
"""
Create the proper database tables and import your 31-item data
"""

import psycopg2
import asyncio

async def setup_real_database():
    """Create tables and import your actual 31-item data"""
    
    print("SETTING UP YOUR REAL DATABASE WITH 31 ITEMS")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL database")
        
        # Create the necessary tables
        print("\n📋 Creating database tables...")
        
        # Create inventory_items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                item_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                unit VARCHAR(50),
                unit_cost DECIMAL(10, 2) DEFAULT 0.00,
                supplier_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create locations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                location_type VARCHAR(100),
                capacity INTEGER,
                current_utilization INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create item_locations table (your main data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_locations (
                item_id VARCHAR(50),
                location_id VARCHAR(50),
                quantity INTEGER NOT NULL DEFAULT 0,
                reserved_quantity INTEGER DEFAULT 0,
                minimum_threshold INTEGER DEFAULT 0,
                maximum_capacity INTEGER DEFAULT 100,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (item_id, location_id),
                FOREIGN KEY (item_id) REFERENCES inventory_items(item_id),
                FOREIGN KEY (location_id) REFERENCES locations(location_id)
            );
        """)
        
        print("✅ Tables created successfully")
        
        # Insert your 12 locations
        print("\n📍 Inserting your 12 hospital locations...")
        locations = [
            ('ICU-01', 'Intensive Care Unit 1'),
            ('ICU-02', 'Intensive Care Unit 2'),
            ('ER-01', 'Emergency Room 1'),
            ('SURGERY-01', 'Surgery Department 1'),
            ('SURGERY-02', 'Surgery Department 2'),
            ('CARDIOLOGY', 'Cardiology Department'),
            ('PHARMACY', 'Pharmacy'),
            ('LAB-01', 'Clinical Laboratory 1'),
            ('WAREHOUSE', 'Central Warehouse'),
            ('MATERNITY', 'Maternity Ward'),
            ('PEDIATRICS', 'Pediatrics Department'),
            ('ONCOLOGY', 'Oncology Department')
        ]
        
        for location_id, name in locations:
            cursor.execute("""
                INSERT INTO locations (location_id, name, location_type)
                VALUES (%s, %s, 'Department')
                ON CONFLICT (location_id) DO NOTHING;
            """, (location_id, name))
        
        # Insert your 31 items with proper names
        print("\n📦 Inserting your 31 inventory items...")
        items = [
            ('ITEM-001', 'Surgical Gloves (Box of 100)', 'PPE'),
            ('ITEM-002', 'Digital Thermometers', 'Equipment'),
            ('ITEM-003', 'Disposable Syringes 10ml (100 pack)', 'Medical Supplies'),
            ('ITEM-004', 'Blood Pressure Cuffs', 'Equipment'),
            ('ITEM-005', 'Disposable Gowns (Pack of 20)', 'PPE'),
            ('ITEM-006', 'Surgical Masks (Box of 50)', 'PPE'),
            ('ITEM-007', 'Hand Sanitizer 500ml', 'Cleaning'),
            ('ITEM-008', 'Sterile Gauze Pads 4x4 (200 pack)', 'Medical Supplies'),
            ('ITEM-009', 'Blood Collection Tubes (100 pack)', 'Medical Supplies'),
            ('ITEM-010', 'Pulse Oximeters', 'Equipment'),
            ('ITEM-011', 'Surgical Sutures 3-0 (Box of 12)', 'Medical Supplies'),
            ('ITEM-012', 'EKG Electrodes (Pack of 50)', 'Medical Supplies'),
            ('ITEM-013', 'Paracetamol 500mg (Box of 100)', 'Medication'),
            ('ITEM-014', 'Aspirin 100mg (Bottle of 100)', 'Medication'),
            ('ITEM-015', 'Antibiotics - Amoxicillin 500mg', 'Medication'),
            ('ITEM-016', 'Insulin Pens (Box of 5)', 'Medication'),
            ('ITEM-017', 'Morphine 10mg/ml (10ml vial)', 'Medication'),
            ('ITEM-018', 'Epinephrine Auto-Injector', 'Medication'),
            ('ITEM-019', 'N95 Respirator Masks (20 pack)', 'PPE'),
            ('ITEM-020', 'Defibrillator Pads (Pack of 2)', 'Equipment'),
            ('ITEM-021', 'Face Shields (Pack of 10)', 'PPE'),
            ('ITEM-022', 'Urinary Catheters (Pack of 10)', 'Medical Supplies'),
            ('ITEM-023', 'Disinfectant Wipes (Pack of 100)', 'Cleaning'),
            ('ITEM-024', 'Hospital-Grade Disinfectant 1L', 'Cleaning'),
            ('ITEM-025', 'IV Bags (1000ml)', 'Medical Supplies'),
            ('ITEM-026', 'Oxygen Masks (Adult)', 'Respiratory'),
            ('ITEM-027', 'Pediatric IV Sets', 'Pediatric'),
            ('ITEM-028', 'Dialysis Tubing Sets', 'Specialty'),
            ('ITEM-029', 'Chemotherapy Drug Vials', 'Oncology'),
            ('ITEM-030', 'Birthing Kit Supplies', 'Maternity'),
            ('IV_BAGS_1000ML', 'IV Bags (1000ml)', 'Medical Supplies')
        ]
        
        for item_id, name, category in items:
            cursor.execute("""
                INSERT INTO inventory_items (item_id, name, category, unit, unit_cost)
                VALUES (%s, %s, %s, 'unit', 10.00)
                ON CONFLICT (item_id) DO NOTHING;
            """, (item_id, name, category))
        
        print("✅ Items inserted successfully")
        
        # Commit the changes
        conn.commit()
        print("\n🎉 DATABASE SETUP COMPLETE!")
        print("📝 Next step: Import your actual quantity data from the CSV you provided")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")

if __name__ == "__main__":
    asyncio.run(setup_real_database())
