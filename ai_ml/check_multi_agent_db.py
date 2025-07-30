#!/usr/bin/env python3
"""
Check the multi_agent_hospital database - this might have your data!
"""

import psycopg2
import psycopg2.extras

def check_multi_agent_hospital_db():
    """Check the multi_agent_hospital database for your inventory data"""
    
    print("CHECKING multi_agent_hospital DATABASE")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='multi_agent_hospital',  # Changed to multi_agent_hospital
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("✅ Connected to multi_agent_hospital database!")
        
        # List all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        all_tables = [row['table_name'] for row in cursor.fetchall()]
        
        if all_tables:
            print(f"\n📋 Found {len(all_tables)} tables:")
            for table_name in all_tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table_name}: {count} rows")
                    
                    # Show sample data for inventory-related tables
                    if any(keyword in table_name.lower() for keyword in ['item', 'inventory', 'location', 'supply', 'stock']):
                        print(f"      🔍 Checking {table_name} structure...")
                        
                        # Get column names
                        cursor.execute(f"""
                            SELECT column_name, data_type 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}'
                            ORDER BY ordinal_position;
                        """)
                        columns = cursor.fetchall()
                        col_names = [col['column_name'] for col in columns]
                        print(f"      📋 Columns: {', '.join(col_names)}")
                        
                        # Show sample data
                        if count > 0:
                            cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 3;')
                            sample_rows = cursor.fetchall()
                            print(f"      📄 Sample data:")
                            for i, row in enumerate(sample_rows, 1):
                                row_dict = dict(row)
                                # Show first few columns to avoid clutter
                                display_cols = list(row_dict.items())[:5]
                                print(f"         {i}. {dict(display_cols)}")
                        
                        print()  # Empty line for readability
                        
                except Exception as e:
                    print(f"   ❌ {table_name}: Error - {e}")
        else:
            print("❌ No tables found in multi_agent_hospital database")
        
        # Specifically look for your 31-item inventory data
        print(f"\n🔍 SEARCHING FOR YOUR 31-ITEM INVENTORY DATA...")
        
        # Look for tables that might contain item locations
        potential_tables = ['item_locations', 'inventory_items', 'locations', 'inventory', 'items', 'supplies']
        
        for table_name in potential_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            if cursor.fetchone()[0]:
                print(f"✅ Found {table_name} table!")
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   📊 Total records: {count}")
                
                if count > 0:
                    # Check for your specific items
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
                    sample = cursor.fetchall()
                    print(f"   📄 Sample records:")
                    for row in sample:
                        print(f"      {dict(row)}")
                
                # Check if this has your 31 items across 12 locations
                if 'item' in table_name.lower():
                    try:
                        if 'location' in table_name.lower():
                            cursor.execute(f"SELECT COUNT(DISTINCT item_id) FROM {table_name};")
                            unique_items = cursor.fetchone()[0]
                            cursor.execute(f"SELECT COUNT(DISTINCT location_id) FROM {table_name};")
                            unique_locations = cursor.fetchone()[0]
                            print(f"   📦 Unique items: {unique_items}")
                            print(f"   📍 Unique locations: {unique_locations}")
                        else:
                            cursor.execute(f"SELECT COUNT(DISTINCT id) FROM {table_name};")
                            unique_items = cursor.fetchone()[0]
                            print(f"   📦 Unique items: {unique_items}")
                    except Exception as e:
                        print(f"   ⚠️ Could not count unique items: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error accessing multi_agent_hospital database: {e}")

if __name__ == "__main__":
    check_multi_agent_hospital_db()
