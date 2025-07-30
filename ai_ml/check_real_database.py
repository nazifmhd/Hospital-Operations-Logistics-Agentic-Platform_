#!/usr/bin/env python3
"""
Connect to your actual PostgreSQL database and check if your 31 items are there
"""

import psycopg2
import asyncio

async def check_real_database():
    """Check if your real database tables exist and contain your 31 items"""
    
    print("CHECKING YOUR REAL POSTGRESQL DATABASE")
    print("=" * 60)
    
    try:
        # Connect to your actual PostgreSQL database
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        print("✅ Connected to PostgreSQL database")
        
        # Check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📋 EXISTING TABLES:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Check if item_locations table exists (where your data should be)
        table_names = [table[0] for table in tables]
        
        if 'item_locations' in table_names:
            print(f"\n✅ Found 'item_locations' table - checking your data...")
            
            # Count total records
            cursor.execute("SELECT COUNT(*) FROM item_locations;")
            total_records = cursor.fetchone()[0]
            print(f"   📊 Total records: {total_records}")
            
            # Count unique items
            cursor.execute("SELECT COUNT(DISTINCT item_id) FROM item_locations;")
            unique_items = cursor.fetchone()[0]
            print(f"   📦 Unique items: {unique_items}")
            
            # Show sample of your data
            cursor.execute("SELECT item_id, location_id, quantity FROM item_locations ORDER BY item_id LIMIT 10;")
            sample_data = cursor.fetchall()
            
            print(f"\n📋 SAMPLE DATA (first 10 records):")
            for item_id, location_id, quantity in sample_data:
                print(f"   {item_id} in {location_id}: {quantity} units")
                
            if unique_items == 31:
                print(f"\n🎉 PERFECT! Found your 31 unique items in the database!")
                print(f"📝 The issue is that the application isn't connecting to this table properly.")
                
        else:
            print(f"\n❌ 'item_locations' table not found")
            print(f"📝 Need to create the table and import your data")
            
            # Check if there are any inventory-related tables
            inventory_tables = [table for table in table_names if 'inventory' in table[0].lower()]
            if inventory_tables:
                print(f"\n🔍 Found inventory-related tables:")
                for table in inventory_tables:
                    print(f"   • {table}")
        
        # Check for inventory_items table too
        if 'inventory_items' in table_names:
            print(f"\n📦 Checking 'inventory_items' table...")
            cursor.execute("SELECT COUNT(*) FROM inventory_items;")
            items_count = cursor.fetchone()[0]
            print(f"   Total items: {items_count}")
            
            if items_count > 0:
                cursor.execute("SELECT item_id, name FROM inventory_items LIMIT 5;")
                items = cursor.fetchall()
                print(f"   Sample items:")
                for item_id, name in items:
                    print(f"   • {item_id}: {name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print(f"\n💡 Possible solutions:")
        print(f"   1. Ensure PostgreSQL is running")
        print(f"   2. Verify database credentials")
        print(f"   3. Create the database and tables")
        print(f"   4. Import your 31-item data")

if __name__ == "__main__":
    asyncio.run(check_real_database())
