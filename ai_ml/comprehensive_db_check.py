#!/usr/bin/env python3
"""
Thorough check of your database - all schemas, all connection methods
"""

import psycopg2
import psycopg2.extras

def comprehensive_database_check():
    """Check your database thoroughly for all tables and data"""
    
    print("COMPREHENSIVE DATABASE CHECK")
    print("=" * 60)
    
    # Try different connection methods
    connection_configs = [
        {
            'name': 'Standard Config',
            'params': {
                'host': 'localhost',
                'port': '5432',
                'database': 'hospital_supply_db',
                'user': 'hospital_user',
                'password': 'hospital_pass'
            }
        },
        {
            'name': 'Alternative Config',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'hospital_supply_db',
                'user': 'postgres',
                'password': 'hospital_pass'
            }
        },
        {
            'name': 'Default PostgreSQL',
            'params': {
                'host': 'localhost',
                'port': 5432,
                'database': 'postgres',
                'user': 'postgres',
                'password': 'postgres'
            }
        }
    ]
    
    for config in connection_configs:
        print(f"\n🔍 TRYING {config['name']}...")
        try:
            conn = psycopg2.connect(**config['params'])
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            print(f"✅ Connected successfully!")
            
            # List all databases
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            databases = [row['datname'] for row in cursor.fetchall()]
            print(f"📊 Available databases: {databases}")
            
            # List all schemas in current database
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast');")
            schemas = [row['schema_name'] for row in cursor.fetchall()]
            print(f"📁 Available schemas: {schemas}")
            
            # List ALL tables in ALL schemas
            cursor.execute("""
                SELECT table_schema, table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY table_schema, table_name;
            """)
            all_tables = cursor.fetchall()
            
            if all_tables:
                print(f"\n📋 Found {len(all_tables)} tables:")
                for table in all_tables:
                    schema = table['table_schema']
                    name = table['table_name']
                    table_type = table['table_type']
                    
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{schema}"."{name}";')
                        count = cursor.fetchone()[0]
                        print(f"   ✅ {schema}.{name} ({table_type}): {count} rows")
                        
                        # If this looks like your inventory table, show sample data
                        if any(keyword in name.lower() for keyword in ['item', 'inventory', 'location', 'supply']):
                            cursor.execute(f'SELECT * FROM "{schema}"."{name}" LIMIT 2;')
                            sample = cursor.fetchall()
                            if sample:
                                print(f"      📄 Sample: {dict(sample[0])}")
                                
                    except Exception as e:
                        print(f"   ❌ {schema}.{name}: Error reading - {e}")
            else:
                print("❌ No tables found")
            
            cursor.close()
            conn.close()
            break  # If successful, don't try other configs
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
    
    # Also check if tables exist with different names
    print(f"\n🔍 SEARCHING FOR INVENTORY-RELATED TABLES...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        
        # Search for tables with inventory-related keywords
        keywords = ['item', 'inventory', 'supply', 'stock', 'location', 'hospital', 'medical']
        
        for keyword in keywords:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND LOWER(table_name) LIKE %s;
            """, (f'%{keyword}%',))
            
            matching_tables = cursor.fetchall()
            if matching_tables:
                print(f"📦 Tables matching '{keyword}': {[t[0] for t in matching_tables]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Search failed: {e}")

if __name__ == "__main__":
    comprehensive_database_check()
