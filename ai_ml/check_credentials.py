#!/usr/bin/env python3
"""
Check with different user credentials - maybe permissions issue
"""

import psycopg2

def check_with_different_credentials():
    """Try different database users to access your tables"""
    
    print("CHECKING WITH DIFFERENT CREDENTIALS")
    print("=" * 50)
    
    # Try different user combinations
    credential_sets = [
        {'user': 'hospital_user', 'password': 'hospital_pass', 'name': 'Hospital User'},
        {'user': 'postgres', 'password': 'hospital_pass', 'name': 'Postgres with hospital pass'},
        {'user': 'postgres', 'password': 'postgres', 'name': 'Default postgres'},
        {'user': 'postgres', 'password': '', 'name': 'Postgres no password'},
    ]
    
    for creds in credential_sets:
        print(f"\n🔑 Trying {creds['name']}...")
        
        try:
            conn = psycopg2.connect(
                host='localhost',
                port='5432',
                database='hospital_supply_db',
                user=creds['user'],
                password=creds['password']
            )
            cursor = conn.cursor()
            
            print(f"✅ Connected as {creds['user']}!")
            
            # Check current user and permissions
            cursor.execute("SELECT current_user, session_user;")
            current_user, session_user = cursor.fetchone()
            print(f"   👤 Current user: {current_user}, Session user: {session_user}")
            
            # List tables this user can see
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            if tables:
                print(f"   📋 Can see {len(tables)} tables:")
                for (table_name,) in tables:
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                        count = cursor.fetchone()[0]
                        print(f"      ✅ {table_name}: {count} rows")
                        
                        # If this table has data, it might be your inventory
                        if count > 0:
                            cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 1;')
                            sample = cursor.fetchone()
                            if sample:
                                # Show first few values
                                sample_str = str(sample)[:100] + "..." if len(str(sample)) > 100 else str(sample)
                                print(f"         📄 Sample: {sample_str}")
                                
                    except Exception as e:
                        print(f"      ❌ {table_name}: {e}")
            else:
                print(f"   ❌ No tables visible to this user")
            
            # Try to list actual PostgreSQL objects this user owns/can access
            cursor.execute("""
                SELECT c.relname, c.relkind, c.relowner::regrole
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public'
                AND c.relkind = 'r'
                AND has_table_privilege(c.oid, 'SELECT');
            """)
            
            accessible_tables = cursor.fetchall()
            if accessible_tables:
                print(f"   🔓 Tables this user can access:")
                for table_name, table_type, owner in accessible_tables:
                    print(f"      • {table_name} (owner: {owner})")
            
            cursor.close()
            conn.close()
            
            if tables:  # If we found tables with this user, we're done
                break
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    # Also try connecting to see what PostgreSQL thinks about the database
    print(f"\n🔍 Checking database metadata...")
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='postgres',  # Connect to postgres db to check hospital_supply_db
            user='postgres',
            password='postgres'
        )
        cursor = conn.cursor()
        
        # Check if hospital_supply_db exists and its owner
        cursor.execute("""
            SELECT datname, datdba::regrole as owner, pg_size_pretty(pg_database_size(datname))
            FROM pg_database 
            WHERE datname = 'hospital_supply_db';
        """)
        
        db_info = cursor.fetchone()
        if db_info:
            db_name, owner, size = db_info
            print(f"   📊 Database: {db_name}, Owner: {owner}, Size: {size}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Could not check database metadata: {e}")

if __name__ == "__main__":
    check_with_different_credentials()
