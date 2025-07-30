#!/usr/bin/env python3
"""
Simple but thorough check of hospital_supply_db database
"""

import psycopg2

def simple_hospital_supply_check():
    """Simple check of hospital_supply_db database"""
    
    print("CHECKING hospital_supply_db DATABASE")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='postgres',
            password='1234'
        )
        cursor = conn.cursor()
        
        print("✅ Connected to hospital_supply_db!")
        
        # Get database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size('hospital_supply_db'));")
        db_size = cursor.fetchone()[0]
        print(f"📊 Database size: {db_size}")
        
        # List all tables in public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n📋 Found {len(tables)} tables:")
            for (table_name,) in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {table_name}: {count} rows")
                    
                    # If table has data, show some details
                    if count > 0:
                        # Get column names
                        cursor.execute(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = '{table_name}' 
                            ORDER BY ordinal_position;
                        """)
                        columns = [col[0] for col in cursor.fetchall()]
                        print(f"      📋 Columns: {', '.join(columns[:6])}...")  # First 6 columns
                        
                        # Show 2 sample rows
                        cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 2;')
                        sample_rows = cursor.fetchall()
                        print(f"      📄 Sample data:")
                        for i, row in enumerate(sample_rows, 1):
                            # Show first few values
                            values = [str(v)[:30] + '...' if len(str(v)) > 30 else str(v) for v in row[:4]]
                            print(f"         {i}. {values}")
                        
                        # Check if this might be your inventory data
                        if any(keyword in table_name.lower() for keyword in ['item', 'inventory', 'location', 'supply']):
                            print(f"      🎯 This looks like inventory data!")
                            
                            # Try to count unique items and locations
                            if 'item' in columns and 'location' in columns:
                                try:
                                    cursor.execute(f'SELECT COUNT(DISTINCT item) FROM "{table_name}";')
                                    unique_items = cursor.fetchone()[0]
                                    cursor.execute(f'SELECT COUNT(DISTINCT location) FROM "{table_name}";')
                                    unique_locations = cursor.fetchone()[0]
                                    print(f"      📦 Unique items: {unique_items}")
                                    print(f"      📍 Unique locations: {unique_locations}")
                                except:
                                    pass
                        
                        print()  # Empty line for readability
                        
                except Exception as e:
                    print(f"   ❌ {table_name}: Error - {e}")
        else:
            print("❌ No tables found in public schema")
            
            # Check if tables might be in a different schema
            cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY table_schema, table_name;
            """)
            
            all_tables = cursor.fetchall()
            if all_tables:
                print(f"\n🔍 Found tables in other schemas:")
                for schema, table in all_tables:
                    cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}";')
                    count = cursor.fetchone()[0]
                    print(f"   ✅ {schema}.{table}: {count} rows")
        
        # Check for any PostgreSQL objects that might not show up in information_schema
        print(f"\n🔍 Checking PostgreSQL system catalog...")
        cursor.execute("""
            SELECT n.nspname as schema, c.relname as name, c.relkind as type
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            AND c.relkind IN ('r', 'v', 'm')
            ORDER BY n.nspname, c.relname;
        """)
        
        pg_objects = cursor.fetchall()
        if pg_objects:
            print(f"📦 Objects in PostgreSQL catalog:")
            for schema, name, obj_type in pg_objects:
                type_name = {'r': 'table', 'v': 'view', 'm': 'materialized view'}[obj_type]
                cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{name}";')
                count = cursor.fetchone()[0]
                print(f"   • {schema}.{name} ({type_name}): {count} rows")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    simple_hospital_supply_check()
