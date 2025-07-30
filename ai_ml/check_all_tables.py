#!/usr/bin/env python3
"""
Check if tables exist with different names or in different schemas
"""

import psycopg2

def check_all_possible_tables():
    """Check for any existing tables that might contain your inventory data"""
    
    print("COMPREHENSIVE TABLE SEARCH")
    print("=" * 50)
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        
        # Check all schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');
        """)
        schemas = cursor.fetchall()
        print(f"Available schemas: {[s[0] for s in schemas]}")
        
        # Check all tables in all schemas
        cursor.execute("""
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY table_schema, table_name;
        """)
        all_tables = cursor.fetchall()
        
        if all_tables:
            print(f"\nFound {len(all_tables)} tables:")
            for schema, table, table_type in all_tables:
                print(f"  {schema}.{table} ({table_type})")
        else:
            print("❌ NO TABLES FOUND IN ANY SCHEMA")
            
        # Check if database has any data at all
        cursor.execute("SELECT datname FROM pg_database WHERE datname = 'hospital_supply_db';")
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"✅ Database 'hospital_supply_db' exists")
            
            # Check database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size('hospital_supply_db'));
            """)
            size = cursor.fetchone()[0]
            print(f"📊 Database size: {size}")
        else:
            print("❌ Database doesn't exist")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_all_possible_tables()
