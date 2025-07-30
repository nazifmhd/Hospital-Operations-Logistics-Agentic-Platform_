#!/usr/bin/env python3
"""
Thorough check of hospital_supply_db database - your actual database
"""

import psycopg2
import psycopg2.extras

def thorough_hospital_supply_check():
    """Thoroughly check hospital_supply_db for all tables and data"""
    
    print("THOROUGH CHECK OF hospital_supply_db DATABASE")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("✅ Connected to hospital_supply_db!")
        
        # Check database size and info
        cursor.execute("SELECT pg_size_pretty(pg_database_size('hospital_supply_db'));")
        db_size = cursor.fetchone()[0]
        print(f"📊 Database size: {db_size}")
        
        # List ALL schemas (including system ones to be thorough)
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            ORDER BY schema_name;
        """)
        all_schemas = [row['schema_name'] for row in cursor.fetchall()]
        print(f"📁 All schemas: {all_schemas}")
        
        # Check each schema for tables
        for schema in all_schemas:
            if schema in ['information_schema', 'pg_catalog', 'pg_toast']:
                continue
                
            print(f"\n🔍 Checking schema: {schema}")
            
            cursor.execute("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name;
            """, (schema,))
            
            schema_tables = cursor.fetchall()
            
            if schema_tables:
                print(f"   Found {len(schema_tables)} tables in {schema}:")
                for table in schema_tables:
                    table_name = table['table_name']
                    table_type = table['table_type']
                    
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{table_name}";')
                        count = cursor.fetchone()[0]
                        print(f"   ✅ {table_name} ({table_type}): {count} rows")
                        
                        # If it has data, show structure and sample
                        if count > 0:
                            # Get columns
                            cursor.execute(f"""
                                SELECT column_name, data_type, is_nullable
                                FROM information_schema.columns 
                                WHERE table_schema = '{schema}' AND table_name = '{table_name}'
                                ORDER BY ordinal_position;
                            """)
                            columns = cursor.fetchall()
                            col_info = [f"{col['column_name']}({col['data_type']})" for col in columns]
                            print(f"      📋 Columns: {', '.join(col_info[:5])}...")  # Show first 5 columns
                            
                            # Show sample data
                            cursor.execute(f'SELECT * FROM "{schema}"."{table_name}" LIMIT 2;')
                            sample = cursor.fetchall()
                            print(f"      📄 Sample data:")
                            for i, row in enumerate(sample, 1):
                                # Convert to dict and show first few fields
                                row_dict = dict(row)
                                display_items = list(row_dict.items())[:4]  # First 4 fields
                                print(f"         {i}. {dict(display_items)}")
                        
                    except Exception as e:
                        print(f"   ❌ {table_name}: Error accessing - {e}")
            else:
                print(f"   No tables found in {schema}")
        
        # Look for any relations/views/sequences
        print(f"\n🔍 Checking for other database objects...")
        
        # Check for views
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public';
        """)
        views = cursor.fetchall()
        if views:
            print(f"📋 Views: {[v['table_name'] for v in views]}")
        
        # Check for sequences
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public';
        """)
        sequences = cursor.fetchall()
        if sequences:
            print(f"🔢 Sequences: {[s['sequence_name'] for s in sequences]}")
        
        # Check for materialized views
        cursor.execute("""
            SELECT schemaname, matviewname 
            FROM pg_matviews 
            WHERE schemaname = 'public';
        """)
        matviews = cursor.fetchall()
        if matviews:
            print(f"📊 Materialized Views: {[m['matviewname'] for m in matviews]}")
        
        # Raw query to see what PostgreSQL thinks exists
        print(f"\n🔍 Raw PostgreSQL catalog check...")
        cursor.execute("""
            SELECT relname, relkind 
            FROM pg_class 
            WHERE relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            AND relkind IN ('r', 'v', 'm')  -- tables, views, materialized views
            ORDER BY relname;
        """)
        
        pg_objects = cursor.fetchall()
        if pg_objects:
            print(f"📦 PostgreSQL catalog objects:")
            for obj in pg_objects:
                rel_type = {'r': 'table', 'v': 'view', 'm': 'matview'}[obj['relkind']]
                print(f"   • {obj['relname']} ({rel_type})")
        else:
            print("❌ No objects found in PostgreSQL catalog")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    thorough_hospital_supply_check()
