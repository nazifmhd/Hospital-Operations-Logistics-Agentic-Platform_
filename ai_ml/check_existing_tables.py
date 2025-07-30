#!/usr/bin/env python3
"""
Check your existing database tables more thoroughly
"""

import psycopg2
import asyncio

async def check_existing_tables():
    """Check your existing database tables and data"""
    
    print("DETAILED CHECK OF YOUR EXISTING DATABASE")
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
        
        # Get ALL tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"\n📋 ALL TABLES IN DATABASE:")
        for table in tables:
            print(f"   • {table[0]}")
            
            # Check row count for each table
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
                count = cursor.fetchone()[0]
                print(f"     → {count} records")
                
                # If it's an inventory-related table, show sample data
                if any(keyword in table[0].lower() for keyword in ['item', 'inventory', 'location']):
                    cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3;")
                    sample = cursor.fetchall()
                    if sample:
                        print(f"     → Sample data:")
                        for row in sample:
                            print(f"       {row}")
                    
            except Exception as e:
                print(f"     → Error checking table: {e}")
        
        # Specifically check for your data format
        print(f"\n🔍 LOOKING FOR YOUR 31-ITEM DATA...")
        
        # Check if item_locations exists (this should have your data)
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'item_locations'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("✅ Found 'item_locations' table")
            
            # Check your specific data
            cursor.execute("SELECT COUNT(*) FROM item_locations;")
            total_records = cursor.fetchone()[0]
            print(f"   📊 Total records: {total_records}")
            
            cursor.execute("SELECT COUNT(DISTINCT item_id) FROM item_locations;")
            unique_items = cursor.fetchone()[0]
            print(f"   📦 Unique items: {unique_items}")
            
            cursor.execute("SELECT COUNT(DISTINCT location_id) FROM item_locations;")
            unique_locations = cursor.fetchone()[0]
            print(f"   📍 Unique locations: {unique_locations}")
            
            # Show your actual data
            print(f"\n📋 YOUR ACTUAL DATA (first 10 records):")
            cursor.execute("""
                SELECT item_id, location_id, quantity, minimum_threshold, last_updated 
                FROM item_locations 
                ORDER BY item_id, location_id 
                LIMIT 10;
            """)
            
            for row in cursor.fetchall():
                item_id, location_id, quantity, min_threshold, last_updated = row
                print(f"   {item_id} @ {location_id}: {quantity} units (min: {min_threshold})")
                
            # Check specific items from your CSV
            print(f"\n🔍 CHECKING SPECIFIC ITEMS FROM YOUR DATA:")
            test_items = ['ITEM-001', 'ITEM-030', 'IV_BAGS_1000ML']
            
            for item_id in test_items:
                cursor.execute("""
                    SELECT location_id, quantity FROM item_locations 
                    WHERE item_id = %s ORDER BY location_id;
                """, (item_id,))
                
                locations = cursor.fetchall()
                if locations:
                    location_list = [f"{loc}({qty})" for loc, qty in locations]
                    print(f"   {item_id}: {', '.join(location_list)}")
                else:
                    print(f"   {item_id}: ❌ NOT FOUND")
        else:
            print("❌ 'item_locations' table not found")
            
        # Check if inventory_items exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'inventory_items'
            );
        """)
        
        if cursor.fetchone()[0]:
            print(f"\n✅ Found 'inventory_items' table")
            cursor.execute("SELECT COUNT(*) FROM inventory_items;")
            items_count = cursor.fetchone()[0]
            print(f"   📦 Total items: {items_count}")
            
            if items_count > 0:
                cursor.execute("SELECT item_id, name FROM inventory_items ORDER BY item_id LIMIT 5;")
                items = cursor.fetchall()
                print(f"   Sample items:")
                for item_id, name in items:
                    print(f"   • {item_id}: {name}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    asyncio.run(check_existing_tables())
