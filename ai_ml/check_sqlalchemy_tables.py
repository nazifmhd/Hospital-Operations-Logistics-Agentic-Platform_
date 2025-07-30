#!/usr/bin/env python3
"""
Check if SQLAlchemy tables exist and verify the schema matches your models
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import psycopg2
from sqlalchemy import create_engine, text

def check_sqlalchemy_tables():
    """Check if your SQLAlchemy model tables exist"""
    
    print("CHECKING SQLALCHEMY MODEL TABLES")
    print("=" * 50)
    
    try:
        # Direct PostgreSQL connection
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            database='hospital_supply_db',
            user='hospital_user',
            password='hospital_pass'
        )
        cursor = conn.cursor()
        
        # Check for your specific tables from models.py
        expected_tables = [
            'item_locations',
            'inventory_items', 
            'locations',
            'users',
            'suppliers',
            'batches',
            'alerts',
            'transfers',
            'purchase_orders',
            'approval_requests',
            'budgets',
            'audit_logs',
            'notifications',
            'usage_records'
        ]
        
        print(f"🔍 Checking for {len(expected_tables)} expected tables...")
        
        for table_name in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table_name,))
            
            exists = cursor.fetchone()[0]
            if exists:
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"✅ {table_name}: {count} records")
                
                # Show sample data for key tables
                if table_name in ['item_locations', 'inventory_items', 'locations'] and count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                    sample = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name}' 
                        ORDER BY ordinal_position;
                    """)
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    print(f"   📋 Columns: {', '.join(columns)}")
                    for row in sample[:2]:  # Show first 2 rows
                        print(f"   📄 {row}")
            else:
                print(f"❌ {table_name}: NOT FOUND")
        
        # Check the critical item_locations table structure
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'item_locations'
            );
        """)
        
        if cursor.fetchone()[0]:
            print(f"\n🔍 DETAILED CHECK OF item_locations TABLE:")
            
            # Get table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'item_locations' 
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("   Table structure:")
            for col_name, data_type, nullable in columns:
                null_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"   • {col_name}: {data_type} {null_str}")
            
            # Check if it has your data
            cursor.execute("SELECT COUNT(*) FROM item_locations;")
            total_count = cursor.fetchone()[0]
            
            if total_count > 0:
                print(f"\n📊 Found {total_count} records in item_locations")
                
                # Check unique items and locations
                cursor.execute("SELECT COUNT(DISTINCT item_id) FROM item_locations;")
                unique_items = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(DISTINCT location_id) FROM item_locations;")
                unique_locations = cursor.fetchone()[0]
                
                print(f"   📦 Unique items: {unique_items}")
                print(f"   📍 Unique locations: {unique_locations}")
                
                # Show sample data
                cursor.execute("""
                    SELECT item_id, location_id, quantity, minimum_threshold 
                    FROM item_locations 
                    ORDER BY item_id, location_id 
                    LIMIT 5;
                """)
                
                print(f"   Sample data:")
                for item_id, location_id, quantity, min_threshold in cursor.fetchall():
                    print(f"   • {item_id} @ {location_id}: qty={quantity}, min={min_threshold}")
            else:
                print(f"⚠️  item_locations table exists but is EMPTY")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_sqlalchemy_tables()
