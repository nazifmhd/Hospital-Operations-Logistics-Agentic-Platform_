#!/usr/bin/env python3
"""
Check all locations in the hospital database
"""

import psycopg2

def check_database_locations():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        
        # First check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print('Available tables:')
        print('=' * 30)
        for table in tables:
            print(f'- {table[0]}')
        
        # Try different possible table names for inventory
        possible_tables = ['inventory', 'inventory_items', 'items', 'stock', 'supply_inventory']
        
        for table_name in possible_tables:
            try:
                cursor.execute(f"SELECT DISTINCT location_name FROM {table_name} ORDER BY location_name;")
                locations = cursor.fetchall()
                
                print(f'\nLocations found in {table_name} table:')
                print('=' * 50)
                for i, (location,) in enumerate(locations, 1):
                    print(f'{i:2d}. {location}')
                
                print(f'\nTotal locations: {len(locations)}')
                break
                
            except Exception as e:
                print(f'Table {table_name} not found or error: {e}')
                continue
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'Database connection error: {e}')

if __name__ == "__main__":
    check_database_locations()
