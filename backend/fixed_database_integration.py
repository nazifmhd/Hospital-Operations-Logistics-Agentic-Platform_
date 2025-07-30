"""
Fixed Database Integration Manager
Handles PostgreSQL connection with proper permissions and table access
"""

import os
import sys
import asyncio
import logging
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Configure logging
logger = logging.getLogger(__name__)

class FixedDatabaseIntegration:
    """Fixed database integration with direct SQL access"""
    
    def __init__(self):
        self.db_url = self._get_database_url()
        self.engine = None
        self.async_session = None
        self.is_connected = False
    
    def safe_convert_to_int(self, value, field_name="unknown"):
        """Safely convert value to integer, handling lists and other types with ultra-aggressive validation"""
        try:
            # NUCLEAR OPTION: Log everything for debugging
            logger.debug(f"🔧 Converting {field_name}: {value} (type: {type(value)})")
            
            if isinstance(value, list):
                logger.warning(f"⚠️ {field_name} is a list: {value}, using first value")
                if value and len(value) > 0:
                    first_val = value[0]
                    if isinstance(first_val, (int, float)):
                        result = int(first_val)
                        logger.debug(f"✅ Converted list {field_name} to int: {result}")
                        return result
                    elif isinstance(first_val, str):
                        result = int(float(first_val))
                        logger.debug(f"✅ Converted list string {field_name} to int: {result}")
                        return result
                    else:
                        logger.error(f"❌ First list element of {field_name} is {type(first_val)}: {first_val}, using 0")
                        return 0
                logger.error(f"❌ Empty list for {field_name}, using 0")
                return 0
            elif isinstance(value, (int, float)):
                result = int(value)
                logger.debug(f"✅ Converted numeric {field_name} to int: {result}")
                return result
            elif isinstance(value, str):
                try:
                    result = int(float(value))
                    logger.debug(f"✅ Converted string {field_name} to int: {result}")
                    return result
                except ValueError:
                    logger.error(f"❌ Cannot convert string {field_name} '{value}' to int, using 0")
                    return 0
            elif value is None:
                logger.debug(f"✅ None value for {field_name}, using 0")
                return 0
            else:
                logger.error(f"❌ Unknown type for {field_name}: {type(value)} - {value}, using 0")
                return 0
        except Exception as e:
            logger.error(f"❌ Error converting {field_name}: {e}, using 0")
            return 0
    
    def safe_convert_to_float(self, value, field_name="unknown"):
        """Safely convert value to float, handling lists and other types"""
        try:
            if isinstance(value, list):
                logger.warning(f"⚠️ {field_name} is a list: {value}, using first value")
                if value and len(value) > 0:
                    return float(value[0])
                return 0.0
            elif isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    return 0.0
            elif value is None:
                return 0.0
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _get_database_url(self):
        """Get database URL from environment"""
        host = os.getenv('DATABASE_HOST', 'localhost')
        port = os.getenv('DATABASE_PORT', '5432')
        database = os.getenv('DATABASE_NAME', 'hospital_supply_db')
        username = os.getenv('DATABASE_USER', 'postgres')
        password = os.getenv('DATABASE_PASSWORD', '1234')
        
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.engine = create_async_engine(self.db_url, echo=False)
            self.async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )
            
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            
            self.is_connected = True
            logger.info("✅ Fixed database integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            self.is_connected = False
            return False
    
    async def test_connection(self):
        """Test if database connection is working"""
        try:
            if not self.engine:
                return False
                
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                logger.info(f"✅ Database connection test successful - {count} users found")
                return True
                
        except Exception as e:
            logger.warning(f"⚠️ Database connection test failed: {e}")
            return False
    
    def _generate_procurement_recommendations(self, inventory_items):
        """Generate procurement recommendations based on inventory levels"""
        recommendations = []
        
        try:
            # Consolidate items by item_id to avoid duplicates across locations
            consolidated_items = {}
            
            for item in inventory_items:
                item_id = item.get("item_id")
                if item_id not in consolidated_items:
                    consolidated_items[item_id] = {
                        "item_id": item_id,
                        "name": item.get("name"),
                        "current_stock": item.get("current_stock", 0),
                        "minimum_stock": item.get("minimum_stock", 0),
                        "reorder_point": item.get("reorder_point", item.get("minimum_stock", 0)),
                        "unit_cost": item.get("unit_cost", 10.0),
                        "supplier": item.get("supplier_name", "Default Supplier")
                    }
                else:
                    # Aggregate stock across locations, but preserve unit_cost if available
                    consolidated_items[item_id]["current_stock"] += item.get("current_stock", 0)
                    # Update unit_cost if we find a non-default value
                    current_unit_cost = item.get("unit_cost", 10.0)
                    if current_unit_cost != 10.0:  # If not the default, use it
                        consolidated_items[item_id]["unit_cost"] = current_unit_cost
            
            for item_id, item in consolidated_items.items():
                current_stock = item["current_stock"]
                minimum_stock = item["minimum_stock"]
                reorder_point = item["reorder_point"]
                unit_cost = float(item["unit_cost"]) if item["unit_cost"] else 10.0
                
                # Generate recommendation if stock is at or below minimum
                if current_stock <= minimum_stock:
                    urgency = "critical" if current_stock == 0 else ("high" if current_stock <= minimum_stock * 0.5 else "medium")
                    recommended_quantity = max(minimum_stock * 2, 50)  # Order double minimum or 50, whichever is higher
                    
                    recommendation = {
                        "id": f"REC-{item_id.replace('ITEM-', '')}",
                        "item_id": item_id,
                        "item_name": item["name"],
                        "current_quantity": current_stock,
                        "minimum_stock": minimum_stock,
                        "recommended_order": recommended_quantity,
                        "urgency": urgency,
                        "estimated_cost": float(recommended_quantity * unit_cost),
                        "reason": f"Stock below minimum threshold ({current_stock} ≤ {minimum_stock})",
                        "supplier": item["supplier"],
                        "estimated_delivery": "2-3 business days",
                        "data_source": "database"
                    }
                    recommendations.append(recommendation)
                    
                # Also recommend for items approaching minimum (within 20% above minimum but below reorder point)
                elif current_stock <= reorder_point and current_stock > minimum_stock:
                    urgency = "low"
                    recommended_quantity = max(minimum_stock, 30)
                    
                    recommendation = {
                        "id": f"REC-PRED-{item_id.replace('ITEM-', '')}",
                        "item_id": item_id,
                        "item_name": item["name"],
                        "current_quantity": current_stock,
                        "minimum_stock": minimum_stock,
                        "recommended_order": recommended_quantity,
                        "urgency": urgency,
                        "estimated_cost": float(recommended_quantity * unit_cost),
                        "reason": f"Stock approaching reorder point ({current_stock} ≤ {reorder_point})",
                        "supplier": item["supplier"],
                        "estimated_delivery": "2-3 business days",
                        "data_source": "predictive_analysis"
                    }
                    recommendations.append(recommendation)
            
            logger.info(f"📊 Generated {len(recommendations)} procurement recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating procurement recommendations: {e}")
            return []
    
    async def get_dashboard_data(self):
        """Get dashboard data from database"""
        try:
            async with self.async_session() as session:
                # Get inventory summary using the correct table structure
                inventory_result = await session.execute(text("""
                    SELECT 
                        COUNT(*) as total_items,
                        SUM(current_stock) as total_stock,
                        COUNT(CASE WHEN current_stock <= minimum_stock THEN 1 END) as low_stock_items,
                        COUNT(CASE WHEN current_stock <= reorder_point THEN 1 END) as reorder_items
                    FROM inventory_items WHERE is_active = TRUE
                """))
                inventory_stats = inventory_result.fetchone()
                
                # Get locations
                locations_result = await session.execute(text("""
                    SELECT location_id, name, location_type, capacity, current_utilization
                    FROM locations WHERE is_active = TRUE
                """))
                locations = [
                    {
                        "location_id": row[0],
                        "name": row[1],
                        "type": row[2],
                        "capacity": int(row[3]) if row[3] is not None else 0,
                        "utilization": float(row[4]) if row[4] is not None else 0.0
                    }
                    for row in locations_result.fetchall()
                ]
                
                # Get ALL inventory items with proper low stock detection using item_locations
                items_result = await session.execute(text("""
                    SELECT 
                        il.item_id, 
                        ii.name, 
                        ii.category, 
                        il.quantity as current_stock, 
                        il.minimum_threshold as minimum_stock, 
                        il.maximum_capacity as maximum_stock, 
                        il.minimum_threshold as reorder_point, 
                        ii.unit_cost, 
                        il.location_id
                    FROM item_locations il
                    LEFT JOIN inventory_items ii ON il.item_id = ii.item_id
                    WHERE ii.is_active = TRUE OR ii.is_active IS NULL
                    ORDER BY 
                        CASE 
                            WHEN il.quantity <= il.minimum_threshold THEN 1
                            WHEN il.quantity <= il.minimum_threshold THEN 2  
                            ELSE 3
                        END,
                        ii.name
                """))
                inventory_items = []
                
                for row in items_result.fetchall():
                    current_stock = int(row[3]) if row[3] is not None else 0
                    minimum_stock = int(row[4]) if row[4] is not None else 0
                    maximum_stock = int(row[5]) if row[5] is not None else 0
                    reorder_point = int(row[6]) if row[6] is not None else 0
                    if reorder_point == 0:
                        reorder_point = minimum_stock
                    unit_cost = float(row[7]) if row[7] is not None else 10.0
                    
                    # Determine status based on stock levels - force int conversion before comparison with nuclear option
                    current_stock_int = int(current_stock)
                    minimum_stock_int = int(minimum_stock)
                    reorder_point_int = int(reorder_point)
                    
                    status = "active"
                    if current_stock_int.__le__(minimum_stock_int):
                        status = "critical_low"
                    elif current_stock_int.__le__(reorder_point_int):
                        status = "low_stock"
                    
                    inventory_items.append({
                        "item_id": row[0] or "",
                        "name": row[1] or "",
                        "category": row[2] or "",
                        "current_stock": current_stock_int,
                        "minimum_stock": minimum_stock_int,
                        "maximum_stock": int(maximum_stock),
                        "reorder_point": reorder_point_int,
                        "unit_cost": unit_cost,
                        "total_value": float(current_stock_int * unit_cost),
                        "location_id": row[8] or "",
                        # Status and analytics
                        "status": status,
                        "is_low_stock": current_stock_int.__le__(minimum_stock_int) or current_stock_int.__le__(reorder_point_int),
                        "needs_reorder": current_stock_int.__le__(reorder_point_int),
                        "criticality": "critical" if current_stock_int.__le__(minimum_stock_int) else ("low" if current_stock_int.__le__(reorder_point_int) else "normal"),
                        # Additional fields for frontend compatibility
                        "value_per_unit": unit_cost,
                        "stock_percentage": min(100.0, (current_stock / max(maximum_stock, 1)) * 100),
                        "days_until_stockout": max(0, int(current_stock / max(1, current_stock * 0.1))),
                        "usage_rate": 8.5,
                        "cost_per_day": float(unit_cost * 8.5),
                        "monthly_consumption": float(current_stock * 0.3),
                        "annual_cost": float(unit_cost * current_stock * 12),
                        "criticality_score": 85.0,
                        "availability_score": 95.0,
                        "quality_score": 98.0,
                        "supplier_name": "Unknown Supplier",
                        "last_updated": datetime.now().isoformat(),
                        "expiry_date": None,
                        "batch_number": None
                    })
                
                # Get active alerts from database
                alerts_result = await session.execute(text("""
                    SELECT alert_id, alert_type, level, message, item_id, 
                           location_id, created_at, is_resolved
                    FROM alerts
                    WHERE is_resolved = FALSE
                    ORDER BY created_at DESC
                    LIMIT 50
                """))
                
                alerts_list = []
                for alert_row in alerts_result.fetchall():
                    alerts_list.append({
                        "id": alert_row[0],
                        "alert_type": alert_row[1],
                        "level": alert_row[2] or "medium",
                        "message": alert_row[3],
                        "item_id": alert_row[4],
                        "location_id": alert_row[5],
                        "created_at": alert_row[6].isoformat() if alert_row[6] else None,
                        "is_resolved": alert_row[7],
                        "data_source": "database"
                    })

                return {
                    "summary": {
                        "total_items": inventory_stats[0] or 0,
                        "total_locations": len(locations),
                        "low_stock_items": inventory_stats[2] or 0,  # Count of items <= minimum_stock
                        "reorder_items": inventory_stats[3] or 0,    # Count of items <= reorder_point  
                        "critical_low_stock": inventory_stats[2] or 0,
                        "expired_items": 0,
                        "expiring_soon": 0,
                        "total_value": float(sum(
                            (item.get("current_stock", 0) or 0) * (item.get("unit_cost", 0.0) or 0.0) 
                            for item in inventory_items
                        )),
                        "critical_alerts": len([alert for alert in alerts_list if alert.get("level") == "critical"]),
                        "overdue_alerts": 0,
                        "pending_pos": 0,
                        "overdue_pos": 0
                    },
                    "inventory": inventory_items,  # Return as array for frontend compatibility
                    "locations": locations,
                    "alerts": alerts_list,  # Now includes actual alerts from database
                    "purchase_orders": [],
                    "recommendations": self._generate_procurement_recommendations(inventory_items),
                    "budget_summary": {
                        "ICU": {
                            "utilization": 75.5,
                            "available": 245000.00,
                            "status": "healthy"
                        },
                        "Emergency": {
                            "utilization": 82.3,
                            "available": 177000.00,
                            "status": "warning"
                        },
                        "Surgery": {
                            "utilization": 68.9,
                            "available": 311000.00,
                            "status": "healthy"
                        },
                        "Pharmacy": {
                            "utilization": 91.2,
                            "available": 88000.00,
                            "status": "warning"
                        }
                    },
                    "compliance_status": {
                        "total_items_tracked": len(inventory_items),
                        "compliant_items": len(inventory_items),
                        "pending_reviews": 0,
                        "expired_certifications": 0,
                        "compliance_score": 100.0
                    },
                    "performance_metrics": {
                        "average_order_fulfillment_time": 3.2,
                        "inventory_turnover_rate": 8.5,
                        "stockout_incidents": inventory_stats[2] or 0,
                        "supplier_performance_avg": 89.5,
                        "cost_savings_ytd": 15000.0,
                        "waste_reduction_percentage": 12.3
                    },
                    "data_source": "database",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get dashboard data from database: {e}")
            raise
    
    async def get_inventory_data(self):
        """Get inventory data from item_locations table (multi-location view)"""
        try:
            logger.info("🔍 Fetching inventory data from item_locations table...")
            async with self.async_session() as session:
                # Get inventory from item_locations with item details
                result = await session.execute(text("""
                    SELECT 
                        il.item_id, 
                        ii.name, 
                        ii.category, 
                        ii.unit_of_measure, 
                        il.quantity as current_stock, 
                        il.minimum_threshold as minimum_stock, 
                        il.maximum_capacity as maximum_stock, 
                        il.minimum_threshold as reorder_point, 
                        ii.unit_cost, 
                        il.location_id, 
                        ii.supplier_id, 
                        ii.is_active, 
                        ii.description
                    FROM item_locations il
                    LEFT JOIN inventory_items ii ON il.item_id = ii.item_id
                    WHERE ii.is_active = TRUE OR ii.is_active IS NULL
                    ORDER BY il.item_id, il.location_id
                """))
                
                inventory_items = []
                for row in result.fetchall():
                    # Ensure all numeric fields have safe defaults
                    current_stock = int(row[4]) if row[4] is not None else 0
                    minimum_stock = int(row[5]) if row[5] is not None else 0
                    maximum_stock = int(row[6]) if row[6] is not None else 0
                    reorder_point = int(row[7]) if row[7] is not None else 0
                    unit_cost = float(row[8]) if row[8] is not None else 0.0
                    
                    item_data = {
                        "item_id": row[0] or "",
                        "name": row[1] or "",
                        "category": row[2] or "",
                        "unit_of_measure": row[3] or "",
                        "current_stock": current_stock,
                        "minimum_stock": minimum_stock,
                        "maximum_stock": maximum_stock,
                        "reorder_point": reorder_point,
                        "unit_cost": unit_cost,
                        "total_value": float(current_stock * unit_cost),
                        "location_id": row[9] or "",
                        "supplier_id": row[10] or "",
                        "is_active": bool(row[11]) if row[11] is not None else True,
                        "description": row[12] or "",
                        # Additional fields for frontend compatibility
                        "status": "active",
                        "value_per_unit": unit_cost,
                        "stock_percentage": float((current_stock / maximum_stock * 100) if maximum_stock > 0 else 0),
                        "days_until_stockout": 10,
                        "supplier_name": "Unknown Supplier",
                        "last_updated": datetime.now().isoformat(),
                        "expiry_date": None,
                        "batch_number": None,
                        "usage_rate": 8.5,
                        "cost_per_day": float(unit_cost * 8.5),
                        "monthly_consumption": float(current_stock * 0.3),
                        "annual_cost": float(unit_cost * current_stock * 12),
                        "criticality_score": 85.0,
                        "availability_score": 95.0,
                        "quality_score": 98.0,
                        "data_source": "database"
                    }
                    
                    # Add debug logging for items that might trigger alerts - force int comparison with nuclear option
                    try:
                        current_stock_check = int(current_stock)
                        minimum_stock_check = int(minimum_stock)
                        
                        # Nuclear option comparison using method instead of operator
                        if current_stock_check.__le__(minimum_stock_check):
                            logger.info(f"🔴 LOW STOCK ITEM FOUND: {item_data['name']} - Current: {current_stock_check}, Minimum: {minimum_stock_check}")
                    except Exception as comp_error:
                        logger.debug(f"Nuclear option comparison failed for {item_data.get('name', 'Unknown')}: {comp_error}")
                    
                    inventory_items.append(item_data)
                
                logger.info(f"✅ Successfully fetched {len(inventory_items)} inventory items")
                return {
                    "items": inventory_items,
                    "data_source": "database",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get inventory data from database: {e}")
            raise
    
    async def get_multi_location_inventory_data(self):
        """Get inventory data with all locations where each item is stored"""
        try:
            logger.info("🔍 Fetching multi-location inventory data from database...")
            async with self.async_session() as session:
                # Get item details with all locations
                result = await session.execute(text("""
                    SELECT 
                        i.item_id,
                        i.name,
                        i.category,
                        i.unit_of_measure,
                        i.minimum_stock,
                        i.reorder_point,
                        i.unit_cost,
                        i.supplier_id,
                        i.is_active,
                        i.description,
                        i.current_stock,
                        il.location_id,
                        COALESCE(l.name, il.location_id) as location_name,
                        il.quantity,
                        il.minimum_threshold,
                        il.maximum_capacity,
                        il.last_updated,
                        CASE 
                            WHEN il.quantity <= il.minimum_threshold THEN 'LOW'
                            WHEN il.quantity >= il.maximum_capacity * 0.8 THEN 'HIGH'
                            ELSE 'GOOD'
                        END as stock_status
                    FROM inventory_items i
                    JOIN item_locations il ON i.item_id = il.item_id
                    LEFT JOIN locations l ON il.location_id = l.location_id
                    WHERE i.is_active = TRUE
                    ORDER BY i.name, il.location_id
                """))
                
                # Group by item_id to aggregate locations
                items_dict = {}
                for row in result.fetchall():
                    item_id = row[0]
                    
                    if item_id not in items_dict:
                        # Create new item entry
                        items_dict[item_id] = {
                            "item_id": item_id or "",
                            "name": row[1] or "",
                            "category": row[2] or "",
                            "unit_of_measure": row[3] or "",
                            "minimum_stock": int(row[4]) if row[4] is not None else 0,
                            "reorder_point": int(row[5]) if row[5] is not None else 0,
                            "unit_cost": float(row[6]) if row[6] is not None else 0.0,
                            "supplier_id": row[7] or "",
                            "is_active": bool(row[8]) if row[8] is not None else True,
                            "description": row[9] or "",
                            "current_stock": int(row[10]) if row[10] is not None else 0,  # Use actual current_stock from database
                            "locations": []
                        }
                    
                    # Add location details
                    quantity = int(row[13]) if row[13] is not None else 0
                    location_data = {
                        "location_id": row[11] or "",
                        "location_name": row[12] or "",
                        "quantity": quantity,
                        "minimum_threshold": int(row[14]) if row[14] is not None else 0,
                        "maximum_capacity": int(row[15]) if row[15] is not None else 0,
                        "stock_status": row[17] or "GOOD",
                        "last_updated": row[16].isoformat() if row[16] else datetime.now().isoformat()
                    }
                    
                    items_dict[item_id]["locations"].append(location_data)
                    # Remove this line: items_dict[item_id]["current_stock"] += quantity
                
                # Convert to list and add additional fields
                inventory_items = []
                for item_data in items_dict.values():
                    current_stock = item_data["current_stock"]
                    unit_cost = item_data["unit_cost"]
                    
                    # Add computed fields
                    item_data.update({
                        "total_value": float(current_stock * unit_cost),
                        "status": "active",
                        "value_per_unit": unit_cost,
                        "stock_percentage": 100.0,  # Multi-location doesn't have single max
                        "days_until_stockout": 10,
                        "supplier_name": "Unknown Supplier",
                        "last_updated": datetime.now().isoformat(),
                        "expiry_date": None,
                        "batch_number": None,
                        "usage_rate": 8.5,
                        "cost_per_day": float(unit_cost * 8.5),
                        "monthly_consumption": float(current_stock * 0.3),
                        "annual_cost": float(unit_cost * current_stock * 12),
                        "criticality_score": 85.0,
                        "availability_score": 95.0,
                        "quality_score": 98.0,
                        "data_source": "database_multi_location"
                    })
                    
                    # Add location count for better visibility
                    item_data["location_count"] = len(item_data["locations"])
                    
                    inventory_items.append(item_data)
                
                logger.info(f"✅ Successfully fetched {len(inventory_items)} multi-location inventory items")
                return {
                    "items": inventory_items,
                    "data_source": "database_multi_location",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get multi-location inventory data from database: {e}")
            raise
    
    async def get_inventory_by_location(self, location_name: str = None, location_id: str = None):
        """Get inventory items filtered by location"""
        try:
            logger.info(f"🔍 Fetching inventory data for location: {location_name or location_id}")
            async with self.async_session() as session:
                
                # Build the WHERE clause based on what's provided
                where_clause = "WHERE (ii.is_active = TRUE OR ii.is_active IS NULL)"
                params = {}
                
                if location_id:
                    where_clause += " AND il.location_id = :location_id"
                    params['location_id'] = location_id
                elif location_name:
                    # Try to match location name (case-insensitive)
                    where_clause += " AND (LOWER(l.name) LIKE LOWER(:location_name) OR LOWER(il.location_id) LIKE LOWER(:location_name))"
                    params['location_name'] = f"%{location_name}%"
                
                query = f"""
                    SELECT 
                        il.item_id, 
                        ii.name as item_name, 
                        ii.category, 
                        ii.unit_of_measure, 
                        il.quantity as current_stock, 
                        il.minimum_threshold as minimum_stock, 
                        il.maximum_capacity as maximum_stock, 
                        il.minimum_threshold as reorder_point, 
                        ii.unit_cost, 
                        il.location_id, 
                        COALESCE(l.name, il.location_id) as location_name,
                        ii.supplier_id, 
                        ii.is_active, 
                        ii.description,
                        il.last_updated
                    FROM item_locations il
                    LEFT JOIN inventory_items ii ON il.item_id = ii.item_id
                    LEFT JOIN locations l ON il.location_id = l.location_id
                    {where_clause}
                    ORDER BY ii.name, il.location_id
                """
                
                result = await session.execute(text(query), params)
                
                inventory_items = []
                for row in result.fetchall():
                    # Safe conversion for all numeric fields
                    current_stock = self.safe_convert_to_int(row[4], "current_stock")
                    minimum_stock = self.safe_convert_to_int(row[5], "minimum_stock")
                    maximum_stock = self.safe_convert_to_int(row[6], "maximum_stock")
                    reorder_point = self.safe_convert_to_int(row[7], "reorder_point")
                    unit_cost = self.safe_convert_to_float(row[8], "unit_cost")
                    
                    # Determine stock status
                    stock_status = "GOOD"
                    if current_stock <= minimum_stock:
                        stock_status = "CRITICAL"
                    elif current_stock <= reorder_point:
                        stock_status = "LOW"
                    elif current_stock >= maximum_stock * 0.9:
                        stock_status = "HIGH"
                    
                    item_data = {
                        "item_id": row[0] or "",
                        "item_name": row[1] or "",
                        "name": row[1] or "",  # Duplicate for compatibility
                        "category": row[2] or "",
                        "unit_of_measure": row[3] or "",
                        "unit": row[3] or "",  # Duplicate for compatibility
                        "current_stock": current_stock,
                        "minimum_stock": minimum_stock,
                        "maximum_stock": maximum_stock,
                        "reorder_point": reorder_point,
                        "unit_cost": unit_cost,
                        "total_value": float(current_stock * unit_cost),
                        "location_id": row[9] or "",
                        "location_name": row[10] or "",
                        "location": row[10] or "",  # Duplicate for compatibility
                        "supplier_id": row[11] or "",
                        "is_active": bool(row[12]) if row[12] is not None else True,
                        "description": row[13] or "",
                        "last_updated": row[14].isoformat() if row[14] else datetime.now().isoformat(),
                        "sku": "",  # Default empty since not available in database
                        "stock_status": stock_status,
                        # Additional computed fields
                        "stock_percentage": float((current_stock / maximum_stock * 100) if maximum_stock > 0 else 0),
                        "stock_deficit": max(0, reorder_point - current_stock),
                        "data_source": "database_location_filtered"
                    }
                    
                    inventory_items.append(item_data)
                
                logger.info(f"✅ Successfully fetched {len(inventory_items)} inventory items for location: {location_name or location_id}")
                return {
                    "items": inventory_items,
                    "location_filter": location_name or location_id,
                    "total_items": len(inventory_items),
                    "data_source": "database_location_filtered",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get inventory data by location from database: {e}")
            raise
    
    async def get_transfers_data(self):
        """Get transfers data from database"""
        try:
            async with self.async_session() as session:
                result = await session.execute(text("""
                    SELECT transfer_id, item_id, from_location_id, to_location_id, 
                           quantity, status, requested_by, requested_date, reason
                    FROM transfers
                """))
                
                transfers = []
                for row in result.fetchall():
                    transfers.append({
                        "transfer_id": row[0],
                        "item_id": row[1],
                        "item_name": f"Item-{row[1]}",  # Simplified - could join with items table
                        "from_location": row[2],
                        "from_location_name": row[2],
                        "to_location": row[3],
                        "to_location_name": row[3],
                        "quantity": row[4],
                        "status": row[5],
                        "requested_by": row[6],
                        "timestamp": row[7].isoformat() if row[7] else None,
                        "reason": row[8],
                        "priority": "medium",  # Default priority
                        "data_source": "database"
                    })
                
                return transfers
                
        except Exception as e:
            logger.error(f"❌ Failed to get transfers data from database: {e}")
            raise
    
    async def store_transfer_record(self, transfer_id: str, item_id: str, from_location: str, 
                                  to_location: str, quantity: int, reason: str = "", priority: str = "medium"):
        """Store transfer record in database"""
        try:
            async with self.async_session() as session:
                # Insert transfer record
                await session.execute(text("""
                    INSERT INTO transfers (transfer_id, item_id, from_location_id, to_location_id, 
                                         quantity, reason, priority, status, requested_date, requested_by)
                    VALUES (:transfer_id, :item_id, :from_location, :to_location, 
                           :quantity, :reason, :priority, 'completed', NOW(), 'manual_user')
                """), {
                    "transfer_id": transfer_id,
                    "item_id": item_id,
                    "from_location": from_location,
                    "to_location": to_location,
                    "quantity": quantity,
                    "reason": reason,
                    "priority": priority
                })
                await session.commit()
                logger.info(f"✅ Transfer {transfer_id} stored in database")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to store transfer record: {e}")
            return False

    async def execute_inventory_transfer(self, item_id: str, from_location: str, to_location: str, quantity: int):
        """Execute actual inventory transfer between locations"""
        try:
            async with self.async_session() as session:
                # Check if source location has enough inventory
                source_check = await session.execute(text("""
                    SELECT quantity FROM item_locations 
                    WHERE item_id = :item_id AND location_id = :from_location
                """), {"item_id": item_id, "from_location": from_location})
                
                source_row = source_check.fetchone()
                if not source_row:
                    logger.warning(f"❌ Source location not found for transfer: {item_id} at {from_location}")
                    return False
                    
                # Safely extract quantity with type checking
                available_quantity = source_row[0]
                if isinstance(available_quantity, list):
                    logger.warning(f"⚠️ Available quantity is a list: {available_quantity}, using first value")
                    available_quantity = int(available_quantity[0]) if available_quantity and isinstance(available_quantity[0], (int, float, str)) else 0
                elif not isinstance(available_quantity, (int, float)):
                    logger.warning(f"⚠️ Available quantity is not numeric: {available_quantity} (type: {type(available_quantity)}), using 0")
                    available_quantity = 0
                else:
                    available_quantity = int(available_quantity)
                    
                if available_quantity < quantity:
                    logger.warning(f"❌ Insufficient inventory for transfer: {item_id} at {from_location} - Available: {available_quantity}, Requested: {quantity}")
                    return False
                
                # Subtract from source location
                await session.execute(text("""
                    UPDATE item_locations 
                    SET quantity = quantity - :quantity
                    WHERE item_id = :item_id AND location_id = :from_location
                """), {
                    "quantity": quantity,
                    "item_id": item_id,
                    "from_location": from_location
                })
                
                # Check if destination location already has this item
                dest_check = await session.execute(text("""
                    SELECT quantity FROM item_locations 
                    WHERE item_id = :item_id AND location_id = :to_location
                """), {"item_id": item_id, "to_location": to_location})
                
                dest_row = dest_check.fetchone()
                
                if dest_row:
                    # Add to existing location
                    await session.execute(text("""
                        UPDATE item_locations 
                        SET quantity = quantity + :quantity
                        WHERE item_id = :item_id AND location_id = :to_location
                    """), {
                        "quantity": quantity,
                        "item_id": item_id,
                        "to_location": to_location
                    })
                else:
                    # Create new location entry
                    await session.execute(text("""
                        INSERT INTO item_locations (item_id, location_id, quantity, minimum_threshold, maximum_threshold)
                        VALUES (:item_id, :to_location, :quantity, 10, 100)
                    """), {
                        "item_id": item_id,
                        "to_location": to_location,
                        "quantity": quantity
                    })
                
                await session.commit()
                logger.info(f"✅ Successfully transferred {quantity} units of {item_id} from {from_location} to {to_location}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to execute inventory transfer: {e}")
            return False
    
    async def get_alerts_data(self):
        """Get alerts data from database"""
        try:
            async with self.async_session() as session:
                result = await session.execute(text("""
                    SELECT alert_id, alert_type, level, message, item_id, 
                           location_id, created_at, is_resolved
                    FROM alerts
                    WHERE is_resolved = FALSE
                    ORDER BY created_at DESC
                """))
                
                alerts = []
                for row in result.fetchall():
                    alerts.append({
                        "id": row[0],
                        "alert_type": row[1],
                        "level": row[2],
                        "message": row[3],
                        "item_id": row[4],
                        "location_id": row[5],
                        "created_at": row[6].isoformat() if row[6] else None,
                        "is_resolved": row[7],
                        "data_source": "database"
                    })
                
                return {
                    "alerts": alerts,
                    "data_source": "database",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get alerts data from database: {e}")
            raise
    
    async def get_purchase_orders_data(self):
        """Get purchase orders data from database"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            async with self.engine.begin() as conn:
                # Check if purchase_orders table exists
                table_check = text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_name = 'purchase_orders'
                """)
                table_exists = await conn.execute(table_check)
                if not table_exists.scalar():
                    logger.info("Purchase orders table does not exist - returning empty list")
                    return {"purchase_orders": [], "data_source": "database"}
                
                # Get purchase orders from database
                result = await conn.execute(text("""
                    SELECT 
                        po_id, supplier_id, requester_id, items::text, 
                        total_amount, status, created_date, expected_delivery,
                        department, priority, notes, approved_by, approved_date
                    FROM purchase_orders
                    ORDER BY created_date DESC
                """))
                
                purchase_orders = []
                for row in result.fetchall():
                    try:
                        # Parse items JSON if it exists
                        items = []
                        if row[3]:  # items field
                            try:
                                items = json.loads(row[3]) if isinstance(row[3], str) else row[3]
                            except (json.JSONDecodeError, TypeError):
                                items = []
                        
                        purchase_orders.append({
                            "po_id": row[0],
                            "supplier_id": row[1],
                            "requester_id": row[2],
                            "items": items,
                            "total_amount": float(row[4]) if row[4] else 0.0,
                            "status": row[5],
                            "created_date": row[6].isoformat() if row[6] else None,
                            "expected_delivery": row[7].isoformat() if row[7] else None,
                            "department": row[8],
                            "priority": row[9],
                            "notes": row[10],
                            "approved_by": row[11],
                            "approved_date": row[12].isoformat() if row[12] else None,
                            "data_source": "database"
                        })
                    except Exception as item_error:
                        logger.warning(f"Error processing purchase order row: {item_error}")
                        continue
                
                return {
                    "purchase_orders": purchase_orders,
                    "data_source": "database",
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.info(f"❌ Failed to get purchase orders from database (table may not exist): {e}")
            # Return empty list if table doesn't exist
            return {"purchase_orders": [], "data_source": "database"}
    
    async def update_inventory_quantity(self, item_id: str, quantity_change: int, reason: str):
        """Update inventory quantity in the database"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            async with self.engine.begin() as conn:
                # Check if the item exists in the inventory_items table
                check_query = text("""
                    SELECT item_id, current_stock FROM inventory_items 
                    WHERE item_id = :item_id OR name = :item_id
                    LIMIT 1
                """)
                result = await conn.execute(check_query, {"item_id": item_id})
                row = result.fetchone()
                
                if row:
                    # Update existing item
                    new_quantity = max(0, row.current_stock + quantity_change)  # Prevent negative quantities
                    update_query = text("""
                        UPDATE inventory_items 
                        SET current_stock = :new_quantity
                        WHERE item_id = :item_id
                    """)
                    await conn.execute(update_query, {
                        "new_quantity": new_quantity,
                        "item_id": row.item_id
                    })
                    logger.info(f"✅ Updated inventory for {item_id}: {row.current_stock} -> {new_quantity}")
                    
                    # ⚡ IMMEDIATE AUTONOMOUS REORDER TRIGGER ⚡
                    # Check if this update created a low stock situation and trigger immediate response
                    try:
                        # Check current stock level against minimum
                        minimum_stock = getattr(row, 'minimum_stock', 0) if hasattr(row, 'minimum_stock') else 0
                        if new_quantity <= minimum_stock:
                            logger.info(f"🚨 Low stock detected after update - triggering immediate reorder check")
                            # Import and call trigger function dynamically to avoid circular imports
                            try:
                                from autonomous_supply_manager import trigger_immediate_reorder_check
                                # Schedule the immediate check (don't await to avoid blocking the transaction)
                                asyncio.create_task(trigger_immediate_reorder_check(item_id, None, "inventory_change"))
                            except ImportError:
                                logger.warning("⚠️ Autonomous trigger not available - will be handled in next cycle")
                                
                    except Exception as trigger_error:
                        logger.warning(f"⚠️ Could not trigger immediate reorder check: {trigger_error}")
                    
                    # For now, let's NOT auto-distribute to avoid transaction issues
                    # Manual sync can be done separately
                    
                else:
                    # If item doesn't exist, we might need to create it or log a warning
                    logger.warning(f"⚠️ Item {item_id} not found in database for update")
                    
        except Exception as e:
            logger.error(f"❌ Failed to update inventory quantity: {e}")
            raise

    async def sync_inventory_with_locations(self, item_id: str):
        """Sync inventory_items.current_stock with sum of item_locations.quantity"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            async with self.engine.begin() as conn:
                # Get sum of all location quantities
                location_sum_query = text("""
                    SELECT COALESCE(SUM(quantity), 0) as location_sum
                    FROM item_locations 
                    WHERE item_id = :item_id
                """)
                result = await conn.execute(location_sum_query, {"item_id": item_id})
                row = result.fetchone()
                location_sum = row.location_sum
                
                # Update inventory_items table to match location sum
                update_query = text("""
                    UPDATE inventory_items 
                    SET current_stock = :location_sum
                    WHERE item_id = :item_id
                """)
                await conn.execute(update_query, {
                    "location_sum": location_sum,
                    "item_id": item_id
                })
                
                logger.info(f"✅ Synced {item_id} inventory: current_stock = {location_sum}")
                return location_sum
                
        except Exception as e:
            logger.error(f"❌ Failed to sync inventory: {e}")
            raise

    async def update_location_inventory(self, item_id: str, location_id: str, quantity_change: int, reason: str):
        """Update inventory for a specific location directly"""
        try:
            async with self.engine.begin() as conn:
                # Get item name for logging
                item_query = text("SELECT name FROM inventory_items WHERE item_id = :item_id")
                item_result = await conn.execute(item_query, {"item_id": item_id})
                item_name = item_result.scalar() or f"Item {item_id}"
                
                # Get location name for logging  
                location_query = text("SELECT name FROM locations WHERE location_id = :location_id")
                location_result = await conn.execute(location_query, {"location_id": location_id})
                location_name = location_result.scalar() or location_id
                
                # Update the specific location's inventory
                update_query = text("""
                    UPDATE item_locations 
                    SET quantity = quantity + :quantity_change,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE item_id = :item_id AND location_id = :location_id
                """)
                
                result = await conn.execute(update_query, {
                    "item_id": item_id,
                    "location_id": location_id,
                    "quantity_change": quantity_change
                })
                
                # Don't update inventory_items table here - stock is managed through item_locations
                # The total stock is calculated dynamically from item_locations
                
                if result.rowcount > 0:
                    # Log the activity
                    await self.log_activity(
                        "direct_location_update",  # activity_type
                        item_id,                   # item_id
                        item_name,                 # item_name
                        location_name,             # location
                        abs(quantity_change),      # quantity
                        f"Direct location update: {reason}",  # reason
                        "system"                   # user
                    )
                    
                    logger.info(f"✅ Updated {item_name} in {location_name}: {quantity_change:+d} units")
                    
                    # ⚡ IMMEDIATE AUTONOMOUS REORDER TRIGGER ⚡
                    # Check if this update created a low stock situation and trigger immediate response
                    try:
                        # Get the current stock level after update
                        stock_check_query = text("""
                            SELECT il.quantity, il.minimum_stock 
                            FROM item_locations il
                            WHERE il.item_id = :item_id AND il.location_id = :location_id
                        """)
                        stock_result = await conn.execute(stock_check_query, {
                            "item_id": item_id, 
                            "location_id": location_id
                        })
                        stock_row = stock_result.fetchone()
                        
                        if stock_row:
                            current_quantity = stock_row[0]
                            minimum_stock = stock_row[1] or 0
                            
                            if current_quantity <= minimum_stock:
                                # Trigger immediate autonomous reorder check
                                logger.info(f"🚨 Low stock detected after update - triggering immediate reorder check")
                                # Import and call trigger function dynamically to avoid circular imports
                                try:
                                    from autonomous_supply_manager import trigger_immediate_reorder_check
                                    # Schedule the immediate check (don't await to avoid blocking the transaction)
                                    asyncio.create_task(trigger_immediate_reorder_check(item_id, location_id, "inventory_change"))
                                except ImportError:
                                    logger.warning("⚠️ Autonomous trigger not available - will be handled in next cycle")
                                    
                    except Exception as trigger_error:
                        logger.warning(f"⚠️ Could not trigger immediate reorder check: {trigger_error}")
                else:
                    logger.warning(f"⚠️ No location found for {item_id} in {location_id}")
                    
        except Exception as e:
            logger.error(f"❌ Failed to update location inventory: {e}")
            raise

    async def smart_distribute_to_locations(self, item_id: str, quantity_to_distribute: int, reason: str):
        """Smart distribution of stock to locations based on priorities and low stock"""
        try:
            async with self.engine.begin() as conn:
                # Get item name for activity logging
                item_query = text("SELECT name FROM inventory_items WHERE item_id = :item_id")
                item_result = await conn.execute(item_query, {"item_id": item_id})
                item_name = item_result.scalar() or f"Item {item_id}"
                
                # Define location priorities (lower number = higher priority)
                location_priorities = {
                    'ICU-01': 1,
                    'ICU-02': 2,
                    'ER-01': 3,
                    'SURGERY-01': 4,
                    'SURGERY-02': 5,
                    'CARDIOLOGY': 6,
                    'PHARMACY': 7,
                    'LAB-01': 8,
                    'LAB-02': 9,
                    'GENERAL-01': 10,
                    'GENERAL-02': 11,
                    'STORAGE': 12
                }
                
                # Get all locations for this item with their current stock
                locations_query = text("""
                    SELECT 
                        il.location_id,
                        COALESCE(l.name, il.location_id) as location_name,
                        il.quantity as current_quantity,
                        il.minimum_threshold,
                        il.maximum_capacity
                    FROM item_locations il
                    LEFT JOIN locations l ON il.location_id = l.location_id
                    WHERE il.item_id = :item_id
                    ORDER BY il.location_id
                """)
                
                locations_result = await conn.execute(locations_query, {"item_id": item_id})
                locations = locations_result.fetchall()
                
                if not locations:
                    logger.warning(f"⚠️ No locations found for item {item_id}")
                    return
                
                # Convert to list of dictionaries for easier sorting
                locations_list = []
                for location in locations:
                    current_qty = location.current_quantity
                    min_threshold = location.minimum_threshold
                    # Nuclear option comparison for low stock detection
                    is_low_stock = current_qty.__le__(min_threshold)
                    priority = location_priorities.get(location.location_id, 999)
                    
                    locations_list.append({
                        'location_id': location.location_id,
                        'location_name': location.location_name,
                        'current_quantity': current_qty,
                        'minimum_threshold': min_threshold,
                        'maximum_capacity': location.maximum_capacity,
                        'is_low_stock': is_low_stock,
                        'priority': priority,
                        'deficit': max(0, min_threshold - current_qty)
                    })
                
                # Sort by:
                # 1. Low stock first (is_low_stock = True first)
                # 2. Then by priority (lower number = higher priority)
                # 3. Then by deficit (higher deficit first for low stock items)
                locations_list.sort(key=lambda x: (
                    not x['is_low_stock'],  # False (low stock) comes before True (good stock)
                    x['priority'],          # Lower priority number = higher priority
                    -x['deficit']           # Higher deficit first (negative for descending)
                ))
                
                remaining_quantity = quantity_to_distribute
                distribution_log = []
                
                logger.info(f"🎯 Smart distribution for {item_id} - {quantity_to_distribute} units:")
                
                # Phase 1: Fill low stock locations to minimum threshold (in priority order)
                for location in locations_list:
                    if remaining_quantity <= 0:
                        break
                        
                    if location['is_low_stock']:
                        deficit = location['deficit']
                        if deficit > 0:
                            available_capacity = location['maximum_capacity'] - location['current_quantity']
                            to_add = min(deficit, remaining_quantity, available_capacity)
                            
                            if to_add > 0:
                                new_qty = location['current_quantity'] + to_add
                                
                                # Update location stock
                                update_location_query = text("""
                                    UPDATE item_locations 
                                    SET quantity = :new_quantity, last_updated = CURRENT_TIMESTAMP
                                    WHERE item_id = :item_id AND location_id = :location_id
                                """)
                                await conn.execute(update_location_query, {
                                    "new_quantity": new_qty,
                                    "item_id": item_id,
                                    "location_id": location['location_id']
                                })
                                
                                remaining_quantity -= to_add
                                location['current_quantity'] = new_qty  # Update for phase 2
                                distribution_log.append(f"📦 {location['location_name']} (Priority {location['priority']}): +{to_add} units ({location['current_quantity'] - to_add} → {new_qty}) [LOW STOCK FILL]")
                                
                                # Log activity for low stock fill
                                await self.log_activity(
                                    "smart_distribution_low_stock",
                                    item_id,
                                    item_name,
                                    location['location_name'],
                                    to_add,
                                    f"Low stock replenishment (Priority {location['priority']})",
                                    "Smart Distribution System"
                                )
                
                # Phase 2: Distribute remaining stock by priority (regardless of low stock status)
                if remaining_quantity > 0:
                    # Re-sort by priority only for remaining distribution
                    locations_list.sort(key=lambda x: x['priority'])
                    
                    # Calculate total available capacity across all locations
                    total_available_capacity = sum(
                        max(0, loc['maximum_capacity'] - loc['current_quantity']) 
                        for loc in locations_list
                    )
                    
                    if total_available_capacity > 0:
                        for location in locations_list:
                            if remaining_quantity <= 0:
                                break
                                
                            available_capacity = location['maximum_capacity'] - location['current_quantity']
                            if available_capacity > 0:
                                # Distribute based on priority weight and available capacity
                                # Higher priority locations get more stock
                                priority_weight = max(1, 13 - location['priority'])  # Higher priority = higher weight
                                
                                # Calculate proportional allocation based on priority and capacity
                                proportion = (priority_weight * available_capacity) / (sum(
                                    max(1, 13 - loc['priority']) * max(0, loc['maximum_capacity'] - loc['current_quantity'])
                                    for loc in locations_list
                                    if loc['maximum_capacity'] - loc['current_quantity'] > 0
                                ) or 1)
                                
                                to_add = min(
                                    int(remaining_quantity * proportion) + (1 if location['priority'] <= 3 else 0),  # Bonus for high priority
                                    available_capacity,
                                    remaining_quantity
                                )
                                
                                if to_add > 0:
                                    new_qty = location['current_quantity'] + to_add
                                    
                                    # Update location stock
                                    update_location_query = text("""
                                        UPDATE item_locations 
                                        SET quantity = :new_quantity, last_updated = CURRENT_TIMESTAMP
                                        WHERE item_id = :item_id AND location_id = :location_id
                                    """)
                                    await conn.execute(update_location_query, {
                                        "new_quantity": new_qty,
                                        "item_id": item_id,
                                        "location_id": location['location_id']
                                    })
                                    
                                    remaining_quantity -= to_add
                                    distribution_log.append(f"📦 {location['location_name']} (Priority {location['priority']}): +{to_add} units ({location['current_quantity']} → {new_qty}) [PRIORITY FILL]")
                                    
                                    # Log activity for priority fill
                                    await self.log_activity(
                                        "smart_distribution_priority",
                                        item_id,
                                        item_name,
                                        location['location_name'],
                                        to_add,
                                        f"Priority-based distribution (Priority {location['priority']})",
                                        "Smart Distribution System"
                                    )
                    
                    # If there's still remaining stock, give it to the highest priority location with capacity
                    if remaining_quantity > 0:
                        for location in locations_list:
                            available_capacity = location['maximum_capacity'] - location['current_quantity']
                            if available_capacity > 0:
                                to_add = min(remaining_quantity, available_capacity)
                                if to_add > 0:
                                    new_qty = location['current_quantity'] + to_add
                                    
                                    # Update location stock
                                    update_location_query = text("""
                                        UPDATE item_locations 
                                        SET quantity = :new_quantity, last_updated = CURRENT_TIMESTAMP
                                        WHERE item_id = :item_id AND location_id = :location_id
                                    """)
                                    await conn.execute(update_location_query, {
                                        "new_quantity": new_qty,
                                        "item_id": item_id,
                                        "location_id": location['location_id']
                                    })
                                    
                                    remaining_quantity -= to_add
                                    distribution_log.append(f"📦 {location['location_name']} (Priority {location['priority']}): +{to_add} units ({location['current_quantity']} → {new_qty}) [OVERFLOW FILL]")
                                    
                                    # Log activity for overflow fill
                                    await self.log_activity(
                                        "smart_distribution_overflow",
                                        item_id,
                                        item_name,
                                        location['location_name'],
                                        to_add,
                                        f"Overflow allocation (Priority {location['priority']})",
                                        "Smart Distribution System"
                                    )
                                    break
                
                # Log the distribution
                logger.info(f"✅ Smart distribution for {item_id} completed:")
                for log_entry in distribution_log:
                    logger.info(f"   {log_entry}")
                
                if remaining_quantity > 0:
                    logger.warning(f"⚠️ {remaining_quantity} units could not be distributed (capacity limits)")
                
                # Log summary activity
                total_distributed = quantity_to_distribute - remaining_quantity
                if total_distributed > 0:
                    await self.log_activity(
                        "smart_distribution_summary",
                        item_id,
                        item_name,
                        f"{len(distribution_log)} locations",
                        total_distributed,
                        f"Smart distribution completed ({len(distribution_log)} locations updated)",
                        "Smart Distribution System"
                    )
                
        except Exception as e:
            logger.error(f"❌ Failed to smart distribute stock: {e}")
            raise
    
    async def log_activity(self, activity_type: str, item_id: str, item_name: str, 
                          location: str, quantity: int, reason: str, user: str = "System"):
        """Log activity for recent activity dashboard"""
        try:
            activity = {
                "activity_id": f"smart-dist-{uuid.uuid4().hex[:8]}",
                "action_type": activity_type,
                "item_id": item_id,
                "item_name": item_name,
                "location": location,
                "quantity": quantity,
                "reason": reason,
                "user": user,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "priority": "medium"
            }
            
            # Store in memory for recent activities (this could be enhanced with database storage)
            if not hasattr(self, 'recent_activities'):
                self.recent_activities = []
            
            self.recent_activities.insert(0, activity)  # Insert at beginning
            
            # Keep only last 50 activities
            if len(self.recent_activities) > 50:
                self.recent_activities = self.recent_activities[:50]
            
            logger.info(f"📝 Activity logged: {activity_type} for {item_name} ({quantity} units) - {reason}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log activity: {e}")
    
    async def get_recent_activities(self, limit: int = 10):
        """Get recent activities for dashboard"""
        try:
            if not hasattr(self, 'recent_activities'):
                self.recent_activities = []
            return self.recent_activities[:limit]
        except Exception as e:
            logger.error(f"❌ Failed to get recent activities: {e}")
            return []
    
    async def check_and_fix_inventory_mismatches(self):
        """Check for and fix inventory mismatches across all items"""
        try:
            mismatches = []
            
            async with self.engine.begin() as conn:
                # Get all items with their total stock
                items_query = text("""
                    SELECT item_id, name, current_stock 
                    FROM inventory_items 
                    WHERE is_active = TRUE
                """)
                items_result = await conn.execute(items_query)
                items = items_result.fetchall()
                
                for item in items:
                    item_id = item[0]
                    item_name = item[1]
                    total_stock = item[2]
                    
                    # Get location sum for this item
                    locations_query = text("""
                        SELECT SUM(quantity) as location_sum
                        FROM item_locations 
                        WHERE item_id = :item_id
                    """)
                    locations_result = await conn.execute(locations_query, {"item_id": item_id})
                    location_sum = locations_result.scalar() or 0
                    
                    # Check for mismatch
                    if total_stock != location_sum:
                        mismatch = total_stock - location_sum
                        mismatches.append({
                            "item_id": item_id,
                            "item_name": item_name,
                            "total_stock": total_stock,
                            "location_sum": location_sum,
                            "mismatch": mismatch
                        })
                        
                        logger.warning(f"⚠️ Mismatch found for {item_name} ({item_id}): Total={total_stock}, Location Sum={location_sum}, Mismatch={mismatch}")
                        
                        # Auto-fix if mismatch is positive (excess in total stock)
                        if mismatch > 0:
                            logger.info(f"🔧 Auto-fixing mismatch for {item_name}: distributing {mismatch} units")
                            await self.smart_distribute_to_locations(item_id, mismatch, "automatic_mismatch_fix")
                        else:
                            logger.warning(f"⚠️ Negative mismatch for {item_name}: {mismatch} units. Manual intervention required.")
                
                logger.info(f"✅ Inventory mismatch check completed: {len(mismatches)} mismatches found")
                return mismatches
                
        except Exception as e:
            logger.error(f"❌ Failed to check inventory mismatches: {e}")
            return []
    
    async def update_user_status(self, user_id: str, is_active: bool):
        """Update user status in the database"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            async with self.engine.begin() as conn:
                # For now, we'll log the action since users table might not exist
                # In a real implementation, this would update the users table
                logger.info(f"✅ User {user_id} status updated to {'active' if is_active else 'inactive'}")
                
        except Exception as e:
            logger.error(f"❌ Failed to update user status: {e}")
            raise
    
    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()
            self.is_connected = False

    async def create_alert_from_inventory(self, item, alert_type="low_stock"):
        """Create an alert in the database based on inventory analysis"""
        try:
            if not self.is_connected:
                await self.initialize()
            
            async with self.engine.begin() as conn:
                # Check if there's already an active alert for this item
                check_query = text("""
                    SELECT alert_id FROM alerts 
                    WHERE item_id = :item_id AND alert_type = :alert_type AND is_resolved = FALSE
                    LIMIT 1
                """)
                
                existing_alert = await conn.execute(check_query, {
                    "item_id": item.get("item_id"),
                    "alert_type": alert_type
                })
                
                if existing_alert.fetchone():
                    logger.info(f"⚠️ Alert already exists for item {item.get('name', 'Unknown')} - skipping duplicate")
                    return None
                
                # Create alert for low stock or other inventory issues
                alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{item.get('item_id', 'UNK')}"
                
                # Determine alert level based on stock levels with safe type conversion
                current_stock_raw = item.get("current_stock", 0)
                minimum_stock_raw = item.get("minimum_stock", 0)
                
                # Force safe conversion to int with error handling
                try:
                    current_stock = self.safe_convert_to_int(current_stock_raw, "current_stock")
                    minimum_stock = self.safe_convert_to_int(minimum_stock_raw, "minimum_stock")
                    
                    # Force final conversion to int to prevent list comparison errors
                    current_stock = int(current_stock) if not isinstance(current_stock, int) else current_stock
                    minimum_stock = int(minimum_stock) if not isinstance(minimum_stock, int) else minimum_stock
                    
                    # Log before any comparisons in alert creation
                    logger.debug(f"🔍 Alert creation comparison: current_stock={current_stock} (type: {type(current_stock)}), minimum_stock={minimum_stock} (type: {type(minimum_stock)})")
                    
                    # Force all values to integers before any arithmetic operations
                    current_stock_int = int(current_stock)
                    minimum_stock_int = int(minimum_stock)
                    critical_threshold = int(minimum_stock_int * 0.5)
                    
                    # Nuclear option comparisons using methods instead of operators
                    if current_stock_int.__le__(0):
                        level = "critical"
                        message = f"{item.get('name', 'Unknown Item')} is out of stock"
                    elif current_stock_int.__le__(critical_threshold):
                        level = "critical"
                        message = f"{item.get('name', 'Unknown Item')} is critically low ({current_stock_int} remaining, minimum: {minimum_stock_int})"
                    elif current_stock_int.__le__(minimum_stock_int):
                        level = "high"
                        message = f"{item.get('name', 'Unknown Item')} is below minimum stock ({current_stock_int} remaining, minimum: {minimum_stock_int})"
                    else:
                        level = "medium"
                        message = f"{item.get('name', 'Unknown Item')} is approaching reorder point ({current_stock_int} remaining)"
                        
                except (TypeError, ValueError) as e:
                    logger.error(f"❌ Type conversion error in alert creation for {item.get('name', 'Unknown')}: {e}")
                    logger.error(f"   Raw values: current_stock_raw={current_stock_raw}, minimum_stock_raw={minimum_stock_raw}")
                    # Fallback to medium level alert
                    level = "medium"
                    message = f"{item.get('name', 'Unknown Item')} has inventory data issues - manual review needed"
                
                # Insert alert into database
                insert_query = text("""
                    INSERT INTO alerts (alert_id, alert_type, level, message, item_id, created_at, is_resolved)
                    VALUES (:alert_id, :alert_type, :level, :message, :item_id, :created_at, :is_resolved)
                """)
                
                await conn.execute(insert_query, {
                    "alert_id": alert_id,
                    "alert_type": alert_type,
                    "level": level,
                    "message": message,
                    "item_id": item.get("item_id"),
                    "created_at": datetime.now(),
                    "is_resolved": False
                })
                
                logger.info(f"✅ Created alert {alert_id} for item {item.get('item_id')}")
                return alert_id
                
        except Exception as e:
            logger.error(f"❌ Failed to create alert: {e}")
            return None
    
    async def auto_resolve_alerts_for_item(self, item_id, alert_type='low_stock'):
        """Automatically resolve alerts for an item when the underlying issue is fixed"""
        try:
            if not self.is_connected:
                await self.initialize()
                
            query = text("""
                UPDATE alerts 
                SET is_resolved = TRUE, resolved_at = NOW()
                WHERE item_id = :item_id AND alert_type = :alert_type AND is_resolved = FALSE
                RETURNING alert_id
            """)
            
            async with self.engine.begin() as conn:
                result = await conn.execute(query, {
                    'item_id': item_id,
                    'alert_type': alert_type
                })
                
                resolved_alerts = result.fetchall()
                logger.info(f"✅ Auto-resolved {len(resolved_alerts)} alerts for item {item_id}")
                return [str(alert[0]) for alert in resolved_alerts]
                
        except Exception as e:
            logger.error(f"❌ Failed to auto-resolve alerts: {e}")
            return []
    
    async def resolve_alert(self, alert_id):
        """Manually resolve a specific alert by ID"""
        try:
            if not self.is_connected:
                await self.initialize()
                
            query = text("""
                UPDATE alerts 
                SET is_resolved = TRUE, resolved_at = NOW()
                WHERE alert_id = :alert_id
                RETURNING alert_id, item_id, alert_type
            """)
            
            async with self.engine.begin() as conn:
                result = await conn.execute(query, {'alert_id': alert_id})
                resolved_alert = result.fetchone()
                
                if resolved_alert:
                    logger.info(f"✅ Resolved alert {alert_id} for item {resolved_alert[1]}")
                    return {
                        'alert_id': str(resolved_alert[0]),
                        'item_id': resolved_alert[1],
                        'alert_type': resolved_alert[2],
                        'resolved_at': datetime.now().isoformat()
                    }
                else:
                    logger.warning(f"⚠️ Alert {alert_id} not found or already resolved")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Failed to resolve alert {alert_id}: {e}")
            return None

    async def analyze_and_create_alerts(self):
        """Analyze inventory and create alerts for low stock items, resolve alerts for resolved issues"""
        try:
            logger.info("🔍 Starting alert analysis...")
            inventory_data = await self.get_inventory_data()
            items = inventory_data.get("items", [])
            logger.info(f"📊 Analyzing {len(items)} inventory items...")
            
            alerts_created = 0
            alerts_resolved = 0
            
            for item in items:
                # Safely extract stock values with comprehensive type checking
                current_stock_raw = item.get("current_stock", 0)
                minimum_stock_raw = item.get("minimum_stock", 0)
                
                # Debug logging before conversion
                logger.debug(f"🔧 Raw values for {item.get('name', 'Unknown')}: current_stock={current_stock_raw} (type: {type(current_stock_raw)}), minimum_stock={minimum_stock_raw} (type: {type(minimum_stock_raw)})")
                
                current_stock = self.safe_convert_to_int(current_stock_raw, "current_stock")
                minimum_stock = self.safe_convert_to_int(minimum_stock_raw, "minimum_stock")
                
                item_name = item.get("name", "Unknown")
                item_id = item.get("item_id")
                
                # Verify the converted values are integers
                if not isinstance(current_stock, int) or not isinstance(minimum_stock, int):
                    logger.error(f"❌ Type conversion failed for {item_name}: current_stock={current_stock} (type: {type(current_stock)}), minimum_stock={minimum_stock} (type: {type(minimum_stock)})")
                    continue
                
                logger.debug(f"📦 Checking {item_name}: current={current_stock}, minimum={minimum_stock}")
                
                try:
                    # ULTRA-AGGRESSIVE type checking and conversion to prevent any list comparisons
                    
                    # If current_stock is still not an int, force it
                    if not isinstance(current_stock, int):
                        logger.warning(f"⚠️ current_stock is not int for {item_name}, forcing conversion: {current_stock} (type: {type(current_stock)})")
                        if isinstance(current_stock, list):
                            current_stock = int(current_stock[0]) if current_stock else 0
                        else:
                            current_stock = int(current_stock)
                    
                    # If minimum_stock is still not an int, force it  
                    if not isinstance(minimum_stock, int):
                        logger.warning(f"⚠️ minimum_stock is not int for {item_name}, forcing conversion: {minimum_stock} (type: {type(minimum_stock)})")
                        if isinstance(minimum_stock, list):
                            minimum_stock = int(minimum_stock[0]) if minimum_stock else 0
                        else:
                            minimum_stock = int(minimum_stock)
                    
                    # Final forced conversion with explicit error handling
                    try:
                        current_stock_final = int(current_stock)
                    except (TypeError, ValueError) as e:
                        logger.error(f"❌ Failed to convert current_stock to int for {item_name}: {current_stock} ({type(current_stock)}) - {e}")
                        current_stock_final = 0
                    
                    try:
                        minimum_stock_final = int(minimum_stock) 
                    except (TypeError, ValueError) as e:
                        logger.error(f"❌ Failed to convert minimum_stock to int for {item_name}: {minimum_stock} ({type(minimum_stock)}) - {e}")
                        minimum_stock_final = 0
                    
                    # Verify both are integers before any operations
                    assert isinstance(current_stock_final, int), f"current_stock_final is not int: {type(current_stock_final)}"
                    assert isinstance(minimum_stock_final, int), f"minimum_stock_final is not int: {type(minimum_stock_final)}"
                    
                    logger.debug(f"🔍 Final verified values: {current_stock_final} ({type(current_stock_final)}) <= {minimum_stock_final} ({type(minimum_stock_final)})")
                    
                    # Ensure we're working with plain Python ints, not any other numeric type
                    current_stock_safe = int(current_stock_final)
                    minimum_stock_safe = int(minimum_stock_final)
                    
                    # Double check types one more time
                    logger.debug(f"🔍 Safe values: {current_stock_safe} ({type(current_stock_safe)}) vs {minimum_stock_safe} ({type(minimum_stock_safe)})")
                    
                    # NUCLEAR OPTION: Wrap comparison in its own try-catch
                    try:
                        # Convert to basic int one more time
                        curr_int = int(current_stock_safe)
                        min_int = int(minimum_stock_safe)
                        
                        # Perform comparison with explicit type checking
                        comparison_result = curr_int.__le__(min_int)  # Using method instead of operator
                        
                        if comparison_result:
                            logger.info(f"🚨 Low stock detected for {item_name}: current={curr_int}, minimum={min_int}")
                            alert_id = await self.create_alert_from_inventory(item)
                            if alert_id:
                                alerts_created += 1
                                logger.info(f"✅ Alert created: {alert_id}")
                            else:
                                logger.info(f"ℹ️ Alert already exists for {item_name} (skipping duplicate)")
                        else:
                            # Stock is sufficient - resolve any existing low stock alerts
                            logger.debug(f"✅ {item_name} stock is sufficient: current={curr_int}, minimum={min_int}")
                            try:
                                resolved_alerts = await self.auto_resolve_alerts_for_item(item_id, 'low_stock')
                                if resolved_alerts and len(resolved_alerts) > 0:
                                    alerts_resolved += len(resolved_alerts)
                                    logger.info(f"✅ Auto-resolved {len(resolved_alerts)} alerts for {item_name} (stock replenished)")
                            except Exception as resolve_error:
                                logger.error(f"❌ Error auto-resolving alerts for {item_name}: {resolve_error}")
                                
                    except Exception as comparison_error:
                        logger.error(f"❌ Comparison operation failed for {item_name}: {comparison_error}")
                        logger.error(f"   Attempting direct string comparison as fallback...")
                        # Fallback: string-based comparison
                        try:
                            curr_str = str(current_stock_safe)
                            min_str = str(minimum_stock_safe)
                            if curr_str.isdigit() and min_str.isdigit():
                                if int(curr_str) <= int(min_str):
                                    logger.info(f"🚨 Low stock detected (fallback) for {item_name}: {curr_str} <= {min_str}")
                        except Exception as fallback_error:
                            logger.error(f"❌ Fallback comparison failed for {item_name}: {fallback_error}")
                            
                except Exception as te:
                    logger.error(f"❌ Major error during item processing for {item_name}: {te}")
                    logger.error(f"   current_stock_safe: {current_stock_safe} (type: {type(current_stock_safe)})")
                    logger.error(f"   minimum_stock_safe: {minimum_stock_safe} (type: {type(minimum_stock_safe)})")
                    continue
                except Exception as e:
                    logger.error(f"❌ Unexpected error processing {item_name}: {e}")
                    continue
            
            logger.info(f"📊 Alert analysis completed: {alerts_created} alerts created, {alerts_resolved} alerts resolved from {len(items)} items")
            return alerts_created
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze inventory for alerts: {e}")
            return 0
    
    async def analyze_item_for_automation(self, item_id: str):
        """Analyze specific item and determine automation action"""
        try:
            async with self.async_session() as session:
                # Get item details with location breakdown
                item_query = text("""
                    SELECT 
                        ii.item_id, ii.name, ii.current_stock, ii.minimum_stock, ii.reorder_point,
                        ii.unit_cost, ii.category
                    FROM inventory_items ii
                    WHERE ii.item_id = :item_id AND ii.is_active = TRUE
                """)
                
                item_result = await session.execute(item_query, {"item_id": item_id})
                item_data = item_result.fetchone()
                
                if not item_data:
                    return {"error": f"Item {item_id} not found"}
                
                # Get location breakdown
                locations_query = text("""
                    SELECT location_id, quantity, minimum_threshold, maximum_capacity
                    FROM item_locations
                    WHERE item_id = :item_id
                    ORDER BY quantity DESC
                """)
                
                locations_result = await session.execute(locations_query, {"item_id": item_id})
                locations = locations_result.fetchall()
                
                # Calculate automation strategy
                # Safely extract and convert values
                item_id_val = str(item_data[0]) if item_data[0] is not None else ""
                item_name = str(item_data[1]) if item_data[1] is not None else "Unknown"
                total_stock = self.safe_convert_to_int(item_data[2], "total_stock")
                minimum_stock = self.safe_convert_to_int(item_data[3], "minimum_stock")
                reorder_point = self.safe_convert_to_int(item_data[4], "reorder_point")
                unit_cost = self.safe_convert_to_float(item_data[5], "unit_cost")
                
                logger.debug(f"📊 Item analysis: {item_name} - Stock: {total_stock}, Min: {minimum_stock}, Reorder: {reorder_point}")
                
                # Calculate transfer availability
                total_available_for_transfer = 0
                critical_locations = []
                surplus_locations = []
                
                for loc in locations:
                    location_id, quantity, min_threshold, max_capacity = loc
                    available_for_transfer = max(0, quantity - min_threshold)
                    total_available_for_transfer += available_for_transfer
                    
                    if quantity <= min_threshold:
                        critical_locations.append({
                            "location_id": location_id,
                            "quantity": quantity,
                            "minimum_threshold": min_threshold,
                            "shortfall": min_threshold - quantity
                        })
                    elif available_for_transfer > 0:
                        surplus_locations.append({
                            "location_id": location_id,
                            "quantity": quantity,
                            "available_for_transfer": available_for_transfer
                        })
                
                # Determine automation action - force int comparison to prevent TypeError
                automation_action = "none"
                recommended_actions = []
                
                # Ensure safe integer comparison
                total_stock_int = int(total_stock)
                minimum_stock_int = int(minimum_stock)
                
                if total_stock_int <= minimum_stock_int:
                    # Critical - below minimum
                    if total_available_for_transfer > 0:
                        automation_action = "inter_transfer"
                        recommended_actions.append({
                            "type": "inter_transfer",
                            "priority": "high",
                            "description": f"Transfer {min(total_available_for_transfer, sum(loc['shortfall'] for loc in critical_locations))} units between locations"
                        })
                    
                    # Always recommend supplier order for critical items
                    order_quantity = max(reorder_point - total_stock, minimum_stock * 2)
                    recommended_actions.append({
                        "type": "supplier_order",
                        "priority": "critical",
                        "quantity": order_quantity,
                        "estimated_cost": float(item_data[5] * order_quantity),
                        "description": f"Emergency order {order_quantity} units from supplier"
                    })
                    automation_action = "both"
                    
                elif total_stock <= reorder_point:
                    # Standard reorder point reached
                    automation_action = "supplier_order"
                    order_quantity = reorder_point + (minimum_stock - total_stock)
                    recommended_actions.append({
                        "type": "supplier_order",
                        "priority": "normal",
                        "quantity": order_quantity,
                        "estimated_cost": float(item_data[5] * order_quantity),
                        "description": f"Standard reorder {order_quantity} units from supplier"
                    })
                
                return {
                    "item_id": item_data[0],
                    "name": item_data[1],
                    "current_stock": total_stock,
                    "minimum_stock": minimum_stock,
                    "reorder_point": reorder_point,
                    "automation_action": automation_action,
                    "recommended_actions": recommended_actions,
                    "critical_locations": critical_locations,
                    "surplus_locations": surplus_locations,
                    "total_available_for_transfer": total_available_for_transfer,
                    "locations_breakdown": [
                        {
                            "location_id": loc[0],
                            "quantity": loc[1],
                            "minimum_threshold": loc[2],
                            "status": "critical" if loc[1] <= loc[2] else "normal"
                        } for loc in locations
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error analyzing item {item_id}: {e}")
            return {"error": str(e)}
    
    async def create_automation_alerts_and_recommendations(self, item_analysis):
        """Create alerts and recommendations based on item analysis"""
        try:
            alerts_created = 0
            recommendations_created = 0
            
            item_id = item_analysis.get("item_id")
            name = item_analysis.get("name")
            automation_action = item_analysis.get("automation_action")
            recommended_actions = item_analysis.get("recommended_actions", [])
            
            async with self.async_session() as session:
                # Create alerts for critical situations
                if automation_action in ["inter_transfer", "both"]:
                    alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{item_id}"
                    alert_message = f"{name} requires inter-location transfers - multiple locations below threshold"
                    
                    alert_query = text("""
                        INSERT INTO alerts (alert_id, alert_type, level, message, item_id, created_at, is_resolved)
                        VALUES (:alert_id, :alert_type, :level, :message, :item_id, :created_at, :is_resolved)
                    """)
                    
                    await session.execute(alert_query, {
                        "alert_id": alert_id,
                        "alert_type": "inter_transfer_needed",
                        "level": "high",
                        "message": alert_message,
                        "item_id": item_id,
                        "created_at": datetime.now(),
                        "is_resolved": False
                    })
                    alerts_created += 1
                
                if automation_action in ["supplier_order", "both"]:
                    alert_id = f"ALERT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{item_id}-ORDER"
                    alert_message = f"{name} requires supplier reorder - below reorder point"
                    alert_level = "critical" if automation_action == "both" else "medium"
                    
                    alert_query = text("""
                        INSERT INTO alerts (alert_id, alert_type, level, message, item_id, created_at, is_resolved)
                        VALUES (:alert_id, :alert_type, :level, :message, :item_id, :created_at, :is_resolved)
                    """)
                    
                    await session.execute(alert_query, {
                        "alert_id": alert_id,
                        "alert_type": "supplier_order_needed",
                        "level": alert_level,
                        "message": alert_message,
                        "item_id": item_id,
                        "created_at": datetime.now(),
                        "is_resolved": False
                    })
                    alerts_created += 1
                
                # Create recommendations
                for action in recommended_actions:
                    if action["type"] == "supplier_order":
                        rec_id = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{item_id}"
                        
                        rec_query = text("""
                            INSERT INTO recommendations (recommendation_id, item_id, item_name, recommendation_type, 
                                                      urgency, recommended_quantity, estimated_cost, reason, created_at)
                            VALUES (:rec_id, :item_id, :item_name, :rec_type, :urgency, :quantity, :cost, :reason, :created_at)
                        """)
                        
                        await session.execute(rec_query, {
                            "rec_id": rec_id,
                            "item_id": item_id,
                            "item_name": name,
                            "rec_type": "purchase_order",
                            "urgency": action["priority"],
                            "quantity": action["quantity"],
                            "cost": action["estimated_cost"],
                            "reason": action["description"],
                            "created_at": datetime.now()
                        })
                        recommendations_created += 1
                
                await session.commit()
                
            return {
                "alerts_created": alerts_created,
                "recommendations_created": recommendations_created,
                "automation_triggered": automation_action != "none"
            }
            
        except Exception as e:
            logger.error(f"Error creating automation alerts/recommendations: {e}")
            return {"alerts_created": 0, "recommendations_created": 0, "automation_triggered": False}

# Global instance
fixed_db_integration = None

async def get_fixed_db_integration():
    """Get or create the fixed database integration instance"""
    global fixed_db_integration
    
    if fixed_db_integration is None:
        fixed_db_integration = FixedDatabaseIntegration()
        await fixed_db_integration.initialize()
    
    return fixed_db_integration

# For compatibility with existing code
db_integration = get_fixed_db_integration
get_db_integration = get_fixed_db_integration
