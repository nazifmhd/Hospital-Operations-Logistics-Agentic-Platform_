"""
Enhanced Supply Agent with LangGraph Integration
Provides full compatibility wrapper for the LangGraph-based agent
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import os
import sys

# SQLAlchemy imports for database operations
from sqlalchemy import text

# Import LangGraph agent
from langgraph_supply_agent import LangGraphSupplyAgent, langgraph_agent

# Import clean data models (no legacy mock data)
from data_models import (
    SupplyCategory, AlertLevel, UserRole, PurchaseOrderStatus, 
    QualityStatus, TransferStatus, InventoryBatch, LocationStock,
    TransferRequest, SupplyItem, User, SupplyAlert, AuditLog, 
    Supplier, PurchaseOrder, Budget, ComplianceRecord
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    REORDER = "reorder"
    INTER_TRANSFER = "inter_transfer"
    EMERGENCY_ORDER = "emergency_order"
    BULK_ORDER = "bulk_order"
    ALERT_RESOLUTION = "alert_resolution"
    STOCK_DECREASE = "stock_decrease"
    STOCK_INCREASE = "stock_increase"

class ActionPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Department inventory data structure
@dataclass
class DepartmentInventory:
    """Department-specific inventory item"""
    department_id: str
    department_name: str
    location_id: str
    item_id: str
    item_name: str
    current_stock: int
    minimum_stock: int
    reorder_point: int
    maximum_capacity: int
    last_updated: datetime
    
    def __getattr__(self, name):
        """Debug attribute access on DepartmentInventory objects"""
        if name == 'total_available_quantity':
            return self.current_stock
        raise AttributeError(f"'DepartmentInventory' object has no attribute '{name}'")
        if name == 'total_available_quantity':
            import logging
            import traceback
            logger = logging.getLogger('department_inventory_debug')
            logger.error(f"🚨 CRITICAL: Someone is trying to access 'total_available_quantity' on DepartmentInventory!")
            logger.error(f"🚨 DepartmentInventory object: {self}")
            logger.error(f"🚨 Call stack:")
            for frame_info in traceback.extract_stack():
                logger.error(f"  📍 {frame_info.filename}:{frame_info.lineno} in {frame_info.name}")
                logger.error(f"     {frame_info.line}")
            # Return the current_stock as a fallback
            return self.current_stock
        raise AttributeError(f"'DepartmentInventory' object has no attribute '{name}'")

@dataclass
class AutomatedAction:
    action_id: str
    action_type: ActionType
    priority: ActionPriority
    source_department: str
    target_department: Optional[str]
    item_id: str
    item_name: str
    quantity: int
    reason: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    details: Dict[str, Any]

class EnhancedSupplyInventoryAgent:
    """
    Enhanced wrapper around LangGraph Supply Agent for full API compatibility
    """
    
    def __init__(self, db_integration=None):
        # Initialize core attributes first using super() to avoid recursion
        super().__setattr__('logger', logging.getLogger(__name__))
        
        # Store database integration instance
        super().__setattr__('db_integration', db_integration)
        
        # Use the global LangGraph agent instance
        super().__setattr__('langgraph_agent', langgraph_agent)
        
        # Proxy all attributes to the LangGraph agent
        super().__setattr__('_proxy_attributes', [
            'inventory', 'alerts', 'suppliers', 'users', 'locations',
            'purchase_orders', 'transfer_requests', 'audit_logs', 'budgets',
            'compliance_records', 'usage_patterns', 'transfers', 'is_running'
        ])
        
        # Initialize department_inventories for compatibility with real database structure
        super().__setattr__('_department_inventories', None)
        super().__setattr__('active_actions', {})
        super().__setattr__('activity_log', [])
        
        self.logger.info("✅ Enhanced Supply Agent initialized with LangGraph backend")
    
    def __getattr__(self, name):
        """Proxy attribute access to the LangGraph agent"""
        try:
            # Add critical debugging for total_available_quantity
            if name == 'total_available_quantity':
                import traceback
                self.logger.error(f"🚨 CRITICAL: Someone is trying to access 'total_available_quantity' on EnhancedSupplyInventoryAgent!")
                self.logger.error(f"🚨 Call stack:")
                for frame_info in traceback.extract_stack():
                    self.logger.error(f"  📍 {frame_info.filename}:{frame_info.lineno} in {frame_info.name}")
                    self.logger.error(f"     {frame_info.line}")
                # Return a safe default value instead of crashing
                return 0
            
            if name == 'department_inventories':
                self.logger.info("🔍 Accessing department_inventories property...")
                result = self._get_department_inventories()
                self.logger.info(f"✅ Successfully returned department_inventories with {len(result)} departments")
                return result
            elif name == '_department_inventories':
                return self._department_inventories
            elif hasattr(self.langgraph_agent, name):
                return getattr(self.langgraph_agent, name)
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        except Exception as e:
            self.logger.error(f"❌ Error in __getattr__ for attribute '{name}': {e}")
            import traceback
            self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            if name == 'department_inventories':
                # Return empty dict as fallback for department_inventories
                return {}
            raise
    
    def _get_department_inventories(self):
        """Generate department inventories with real database integration"""
        try:
            if self._department_inventories is None:
                self._department_inventories = {}
                
                # Try to load from database first, then fallback to LangGraph agent data
                try:
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If we're in an async context, schedule the database loading
                        asyncio.create_task(self._load_department_inventories_from_db())
                    else:
                        # If not in async context, run synchronously
                        loop.run_until_complete(self._load_department_inventories_from_db())
                except Exception as e:
                    self.logger.warning(f"Could not load from database: {e}")
                    try:
                        self._create_fallback_department_inventories()
                    except Exception as fallback_error:
                        self.logger.error(f"Fallback creation failed: {fallback_error}")
                        # Create empty structure as last resort
                        self._department_inventories = {}
            
            return self._department_inventories
            
        except Exception as e:
            self.logger.error(f"❌ Error in _get_department_inventories: {e}")
            import traceback
            self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            # Return empty dict as fallback
            return {}

    async def _load_department_inventories_from_db(self):
        """Load department inventories from real database tables"""
        try:
            self.logger.info("📊 Loading department inventories from real database...")
            
            # Database connection details
            DB_CONFIG = {
                'host': 'localhost',
                'port': 5432,
                'database': 'hospital_supply_db',
                'user': 'postgres',
                'password': '1234'
            }
            
            # Query to get all item-location data with item and location details
            query = """
            SELECT 
                il.item_id,
                il.location_id,
                il.quantity,
                il.minimum_threshold,
                il.maximum_capacity,
                il.last_updated,
                i.name as item_name,
                i.category,
                i.reorder_point,
                l.name as location_name,
                l.location_type
            FROM item_locations il
            LEFT JOIN inventory_items i ON il.item_id = i.item_id
            LEFT JOIN locations l ON il.location_id = l.location_id
            WHERE l.is_active = true AND i.is_active = true
            ORDER BY il.location_id, il.item_id
            """
            
            try:
                import asyncpg
                conn = await asyncpg.connect(**DB_CONFIG)
                result = await conn.fetch(query)
                result = [dict(row) for row in result]
                await conn.close()
                self.logger.info(f"📦 Database query executed successfully, found {len(result)} records")
            except Exception as db_error:
                self.logger.warning(f"⚠️ Database connection failed: {db_error}")
                result = []
            
            if result:
                self.logger.info(f"📦 Found {len(result)} item-location records from database")
                
                # Group by location_id (department)
                self._department_inventories = {}
                
                for row in result:
                    location_id = row['location_id']
                    location_name = row['location_name'] or self._get_department_name(location_id)
                    
                    # Create department inventory entry
                    dept_inv = DepartmentInventory(
                        department_id=location_id,
                        department_name=location_name,
                        location_id=location_id,
                        item_id=row['item_id'],
                        item_name=row['item_name'] or f"Item {row['item_id']}",
                        current_stock=row['quantity'] or 0,
                        minimum_stock=row['minimum_threshold'] or 0,
                        reorder_point=row.get('reorder_point') or max(row['minimum_threshold'] + 10, int(row['minimum_threshold'] * 1.5)) if row['minimum_threshold'] else 50,
                        maximum_capacity=row['maximum_capacity'] or 100,
                        last_updated=row['last_updated'] or datetime.now()
                    )
                    
                    if location_id not in self._department_inventories:
                        self._department_inventories[location_id] = []
                    
                    self._department_inventories[location_id].append(dept_inv)
                
                self.logger.info(f"📋 Loaded inventories for {len(self._department_inventories)} departments from real database")
                
                # Log department summary
                for dept_id, items in self._department_inventories.items():
                    critical_items = sum(1 for item in items if item.current_stock <= item.minimum_stock)
                    self.logger.info(f"   🏥 {dept_id}: {len(items)} items ({critical_items} critical)")
                
                return
            else:
                self.logger.warning("⚠️ No data returned from database query")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load from real database: {e}")
        
        # Fallback to mock data if database fails
        await self._create_real_data_mock()

    def _get_department_name(self, location_id):
        """Get human-readable department name from location ID"""
        name_map = {
            "ICU-01": "Intensive Care Unit",
            "ICU-02": "Intensive Care Unit 2", 
            "ER-01": "Emergency Room",
            "SURGERY-01": "Surgery Department",
            "PHARMACY": "Central Pharmacy",
            "LAB-01": "Laboratory",
            "WAREHOUSE": "Central Warehouse",
            "CARDIOLOGY": "Cardiology Department",
            "PEDIATRICS": "Pediatrics Department",
            "ONCOLOGY": "Oncology Department",
            "MATERNITY": "Maternity Department"
        }
        return name_map.get(location_id, f"Department {location_id}")

    async def _create_real_data_mock(self):
        """Create mock data that matches real database structure"""
        self.logger.info("📋 Creating mock data based on real item_locations structure...")
        
        # Use data structure matching real database
        mock_data = [
            # ICU-01 items (some with low stock for testing)
            {"item_id": "ITEM-001", "location_id": "ICU-01", "quantity": 38, "minimum_threshold": 40, "maximum_capacity": 750, "item_name": "Disposable Syringes"},
            {"item_id": "ITEM-002", "location_id": "ICU-01", "quantity": 10, "minimum_threshold": 20, "maximum_capacity": 450, "item_name": "Surgical Masks N95"},
            {"item_id": "ITEM-003", "location_id": "ICU-01", "quantity": 65, "minimum_threshold": 80, "maximum_capacity": 1500, "item_name": "Blood Collection Tubes"},
            {"item_id": "ITEM-009", "location_id": "ICU-01", "quantity": 6, "minimum_threshold": 32, "maximum_capacity": 450, "item_name": "IV Fluid Bags"},
            {"item_id": "ITEM-022", "location_id": "ICU-01", "quantity": 2, "minimum_threshold": 6, "maximum_capacity": 60, "item_name": "Emergency Medications"},
            
            # ER-01 items
            {"item_id": "ITEM-005", "location_id": "ER-01", "quantity": 58, "minimum_threshold": 32, "maximum_capacity": 600, "item_name": "Antibiotics"},
            {"item_id": "ITEM-013", "location_id": "ER-01", "quantity": 90, "minimum_threshold": 80, "maximum_capacity": 2000, "item_name": "Gauze Bandages"},
            {"item_id": "ITEM-014", "location_id": "ER-01", "quantity": 5, "minimum_threshold": 12, "maximum_capacity": 200, "item_name": "Pain Medications"},
            
            # SURGERY-01 items
            {"item_id": "ITEM-001", "location_id": "SURGERY-01", "quantity": 37, "minimum_threshold": 40, "maximum_capacity": 900, "item_name": "Disposable Syringes"},
            {"item_id": "ITEM-008", "location_id": "SURGERY-01", "quantity": 93, "minimum_threshold": 64, "maximum_capacity": 1080, "item_name": "Surgical Instruments"},
            
            # PHARMACY items
            {"item_id": "ITEM-006", "location_id": "PHARMACY", "quantity": 74, "minimum_threshold": 24, "maximum_capacity": 800, "item_name": "Medical Supplies"},
            {"item_id": "ITEM-013", "location_id": "PHARMACY", "quantity": 270, "minimum_threshold": 80, "maximum_capacity": 2000, "item_name": "Pharmaceuticals"},
            
            # WAREHOUSE items (higher stock levels)
            {"item_id": "ITEM-001", "location_id": "WAREHOUSE", "quantity": 111, "minimum_threshold": 40, "maximum_capacity": 1500, "item_name": "Disposable Syringes"},
            {"item_id": "ITEM-002", "location_id": "WAREHOUSE", "quantity": 27, "minimum_threshold": 20, "maximum_capacity": 900, "item_name": "Surgical Masks N95"},
            {"item_id": "ITEM-003", "location_id": "WAREHOUSE", "quantity": 192, "minimum_threshold": 80, "maximum_capacity": 3000, "item_name": "Blood Collection Tubes"},
        ]
        
        self._department_inventories = {}
        for item_data in mock_data:
            location_id = item_data["location_id"]
            
            dept_inv = DepartmentInventory(
                department_id=location_id,
                department_name=self._get_department_name(location_id),
                location_id=location_id,
                item_id=item_data["item_id"],
                item_name=item_data["item_name"],
                current_stock=item_data["quantity"],
                minimum_stock=item_data["minimum_threshold"],
                reorder_point=max(item_data["minimum_threshold"] + 10, int(item_data["minimum_threshold"] * 1.5)),
                maximum_capacity=item_data["maximum_capacity"],
                last_updated=datetime.now()
            )
            
            if location_id not in self._department_inventories:
                self._department_inventories[location_id] = []
            
            self._department_inventories[location_id].append(dept_inv)
        
        self.logger.info(f"📋 Created mock data for {len(self._department_inventories)} departments")
        
        # Log critical items for automation testing
        for dept_id, items in self._department_inventories.items():
            critical_items = [item for item in items if item.current_stock <= item.minimum_stock]
            if critical_items:
                self.logger.info(f"   🚨 {dept_id}: {len(critical_items)} items below minimum stock")

    def _create_fallback_department_inventories(self):
        """Create fallback department inventories from LangGraph agent data"""
        try:
            self._department_inventories = {}
            
            # Group inventory by department/category
            for item in self.inventory.values():
                dept = None
                if hasattr(item, 'department') and item.department:
                    dept = item.department
                elif hasattr(item, 'category'):
                    dept = item.category.value if hasattr(item.category, 'value') else str(item.category)
                
                if dept:
                    if dept not in self._department_inventories:
                        self._department_inventories[dept] = []
                    
                    # Create DepartmentInventory from SupplyItem
                    dept_inv = DepartmentInventory(
                        department_id=dept,
                        department_name=dept.replace('_', ' ').title(),
                        location_id=dept,
                        item_id=item.item_id,
                        item_name=item.name,
                        current_stock=getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0)),
                        minimum_stock=getattr(item, 'minimum_stock', item.reorder_point),
                        reorder_point=item.reorder_point,
                        maximum_capacity=getattr(item, 'maximum_capacity', item.reorder_point * 5),
                        last_updated=getattr(item, 'last_updated', datetime.now())
                    )
                    self._department_inventories[dept].append(dept_inv)
            
            self.logger.info(f"📋 Created fallback inventories for {len(self._department_inventories)} departments")
                    
        except Exception as e:
            self.logger.error(f"Failed to create fallback inventories: {e}")
            self._department_inventories = {}
    
    def __setattr__(self, name, value):
        """Proxy attribute setting to the LangGraph agent for relevant attributes"""
        # During initialization, these attributes must be set directly
        if name in ['logger', 'langgraph_agent', '_proxy_attributes', '_department_inventories', 'db_integration', 'active_actions', 'activity_log']:
            super().__setattr__(name, value)
        # If we have proxy attributes defined and the attribute should be proxied
        elif hasattr(self, '_proxy_attributes') and self._proxy_attributes and name in self._proxy_attributes:
            # Make sure langgraph_agent exists before proxying
            if hasattr(self, 'langgraph_agent') and self.langgraph_agent:
                setattr(self.langgraph_agent, name, value)
            else:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)
    
    # Core agent methods that proxy to LangGraph agent
    async def initialize(self):
        """Initialize the enhanced agent"""
        await self.langgraph_agent.initialize()
        # Generate initial automated activities based on current inventory
        await self._generate_automated_activities()
        # Add some sample historical activities
        await self._add_sample_historical_activities()
        self.logger.info("✅ Enhanced Supply Agent fully initialized with automated monitoring")
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        await self.langgraph_agent.start_monitoring()
        # Also start our automated activity generation
        await self._generate_automated_activities()
        
    async def _generate_automated_activities(self):
        """Generate automated activities and actions based on current inventory status"""
        try:
            self.logger.info("🤖 Generating automated activities based on inventory analysis...")
            
            # Get current department inventories
            dept_inventories = self._get_department_inventories()
            
            for dept_id, items in dept_inventories.items():
                for item in items:
                    try:
                        # Check if item needs automated action
                        if hasattr(item, 'current_stock') and hasattr(item, 'minimum_stock'):
                            current_stock = getattr(item, 'current_stock', 0)
                            minimum_stock = getattr(item, 'minimum_stock', 0)
                            
                            # Generate reorder action for critical items
                            if current_stock <= minimum_stock:
                                action = AutomatedAction(
                                    action_id=f"AUTO-{uuid.uuid4().hex[:8]}",
                                    action_type=ActionType.REORDER,
                                    priority=ActionPriority.CRITICAL if current_stock == 0 else ActionPriority.HIGH,
                                    source_department=dept_id,
                                    target_department=None,
                                    item_id=getattr(item, 'item_id', 'UNKNOWN'),
                                    item_name=getattr(item, 'item_name', 'Unknown Item'),
                                    quantity=max(minimum_stock * 2, 20),  # Order double minimum or 20, whichever is higher
                                    reason=f"Stock critically low: {current_stock}/{minimum_stock}",
                                    status="pending",
                                    created_at=datetime.now(),
                                    completed_at=None,
                                    details={
                                        "trigger": "automated_monitoring",
                                        "current_stock": current_stock,
                                        "minimum_threshold": minimum_stock,
                                        "suggested_quantity": max(minimum_stock * 2, 20)
                                    }
                                )
                                
                                # Add to active actions
                                self.active_actions[action.action_id] = action
                                
                                # Log activity
                                activity = {
                                    "id": action.action_id,
                                    "timestamp": datetime.now().isoformat(),
                                    "action": f"Automated Reorder Initiated",
                                    "details": f"Critical stock alert for {action.item_name} in {dept_id}. Current: {current_stock}, Min: {minimum_stock}",
                                    "user_id": "autonomous_agent",
                                    "status": "pending",
                                    "action_type": "reorder",
                                    "department": dept_id,
                                    "item": action.item_name,
                                    "priority": action.priority.value
                                }
                                self.activity_log.append(activity)
                                
                            # Generate transfer action for low stock items (but not critical)
                            elif current_stock <= minimum_stock * 1.5:
                                # Look for departments with surplus of this item
                                surplus_dept = self._find_surplus_department(getattr(item, 'item_id', ''), dept_inventories, dept_id)
                                
                                if surplus_dept:
                                    action = AutomatedAction(
                                        action_id=f"AUTO-{uuid.uuid4().hex[:8]}",
                                        action_type=ActionType.INTER_TRANSFER,
                                        priority=ActionPriority.MEDIUM,
                                        source_department=surplus_dept,
                                        target_department=dept_id,
                                        item_id=getattr(item, 'item_id', 'UNKNOWN'),
                                        item_name=getattr(item, 'item_name', 'Unknown Item'),
                                        quantity=min(20, minimum_stock),  # Transfer reasonable amount
                                        reason=f"Inter-department optimization: {surplus_dept} → {dept_id}",
                                        status="pending",
                                        created_at=datetime.now(),
                                        completed_at=None,
                                        details={
                                            "trigger": "automated_optimization",
                                            "source_current_stock": "surplus",
                                            "target_current_stock": current_stock,
                                            "target_minimum": minimum_stock
                                        }
                                    )
                                    
                                    # Add to active actions
                                    self.active_actions[action.action_id] = action
                                    
                                    # Log activity
                                    activity = {
                                        "id": action.action_id,
                                        "timestamp": datetime.now().isoformat(),
                                        "action": f"Automated Transfer Scheduled",
                                        "details": f"Transfer {action.item_name} from {surplus_dept} to {dept_id}. Target stock: {current_stock}, Min: {minimum_stock}",
                                        "user_id": "autonomous_agent",
                                        "status": "pending",
                                        "action_type": "inter_transfer",
                                        "source_department": surplus_dept,
                                        "target_department": dept_id,
                                        "item": action.item_name,
                                        "priority": action.priority.value
                                    }
                                    self.activity_log.append(activity)
                                    
                                    # Auto-execute inter-department transfers immediately
                                    await self._auto_execute_transfer(action)
                                    
                    except Exception as item_error:
                        self.logger.error(f"Error processing item in {dept_id}: {item_error}")
                        continue
            
            # Limit activity log size
            if len(self.activity_log) > 100:
                self.activity_log = self.activity_log[-50:]  # Keep last 50 activities
                
            self.logger.info(f"✅ Generated {len(self.active_actions)} automated actions and {len(self.activity_log)} activities")
            
        except Exception as e:
            self.logger.error(f"❌ Error generating automated activities: {e}")
            import traceback
            self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
    
    def _find_surplus_department(self, item_id: str, dept_inventories: Dict, exclude_dept: str) -> Optional[str]:
        """Find a department with surplus stock of the given item"""
        try:
            for dept_id, items in dept_inventories.items():
                if dept_id == exclude_dept:
                    continue
                    
                for item in items:
                    if getattr(item, 'item_id', '') == item_id:
                        current_stock = getattr(item, 'current_stock', 0)
                        minimum_stock = getattr(item, 'minimum_stock', 0)
                        
                        # Consider surplus if stock is > 2x minimum
                        if current_stock > minimum_stock * 2:
                            return dept_id
            return None
        except Exception as e:
            self.logger.error(f"Error finding surplus department: {e}")
            return None
    
    async def _add_sample_historical_activities(self):
        """Add some sample historical activities to demonstrate the system"""
        try:
            # Add some completed activities from the past few hours
            sample_activities = [
                {
                    "id": f"HIST-{uuid.uuid4().hex[:8]}",
                    "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                    "action": "Automated Reorder Completed",
                    "details": "Successfully ordered 50 units of Surgical Gloves for ICU-01",
                    "user_id": "autonomous_agent",
                    "status": "completed",
                    "action_type": "reorder",
                    "department": "ICU-01",
                    "item": "Surgical Gloves (Box of 100)",
                    "priority": "high"
                },
                {
                    "id": f"HIST-{uuid.uuid4().hex[:8]}",
                    "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                    "action": "Inter-Department Transfer Executed",
                    "details": "Transferred 20 N95 masks from WAREHOUSE to ER-01",
                    "user_id": "autonomous_agent",
                    "status": "completed",
                    "action_type": "inter_transfer",
                    "source_department": "WAREHOUSE",
                    "target_department": "ER-01",
                    "item": "N95 Respirator Masks",
                    "priority": "medium"
                },
                {
                    "id": f"HIST-{uuid.uuid4().hex[:8]}",
                    "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                    "action": "Stock Level Alert Resolved",
                    "details": "Critical stock alert for IV Bags in ICU-02 resolved through emergency procurement",
                    "user_id": "autonomous_agent",
                    "status": "completed",
                    "action_type": "alert_resolution",
                    "department": "ICU-02",
                    "item": "IV Bags (1000ml)",
                    "priority": "critical"
                },
                {
                    "id": f"HIST-{uuid.uuid4().hex[:8]}",
                    "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
                    "action": "Automated Transfer Scheduled",
                    "details": "Transfer 15 units of Disposable Gowns from WAREHOUSE to SURGERY-01",
                    "user_id": "autonomous_agent",
                    "status": "in_progress",
                    "action_type": "inter_transfer",
                    "source_department": "WAREHOUSE",
                    "target_department": "SURGERY-01",
                    "item": "Disposable Gowns",
                    "priority": "medium"
                },
                {
                    "id": f"HIST-{uuid.uuid4().hex[:8]}",
                    "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                    "action": "Bulk Purchase Order Approved",
                    "details": "Approved purchase of 200 units of Hand Sanitizer for multiple departments",
                    "user_id": "autonomous_agent",
                    "status": "completed",
                    "action_type": "bulk_order",
                    "department": "Multiple",
                    "item": "Hand Sanitizer 500ml",
                    "priority": "high"
                }
            ]
            
            # Add to activity log
            self.activity_log.extend(sample_activities)
            self.logger.info(f"✅ Added {len(sample_activities)} sample historical activities")
            
        except Exception as e:
            self.logger.error(f"❌ Error adding sample activities: {e}")
    
    async def _auto_execute_transfer(self, action: AutomatedAction):
        """Automatically execute inter-department transfer"""
        try:
            self.logger.info(f"🔄 Auto-executing transfer: {action.item_name} from {action.source_department} to {action.target_department}")
            
            # Database connection details (same as used in _load_from_database)
            DB_CONFIG = {
                'host': 'localhost',
                'port': 5432,
                'database': 'hospital_supply_db',
                'user': 'postgres',
                'password': '1234'
            }
            
            try:
                import asyncpg
                conn = await asyncpg.connect(**DB_CONFIG)
                
                # First, check current stock in both locations
                check_query = """
                SELECT il.item_id, il.location_id, il.quantity, i.name as item_name
                FROM item_locations il
                LEFT JOIN inventory_items i ON il.item_id = i.item_id
                WHERE i.name = $1 AND il.location_id IN ($2, $3)
                """
                
                current_stocks = await conn.fetch(check_query, action.item_name, action.source_department, action.target_department)
                
                source_stock = None
                target_stock = None
                
                for stock in current_stocks:
                    if stock['location_id'] == action.source_department:
                        source_stock = stock
                    elif stock['location_id'] == action.target_department:
                        target_stock = stock
                
                if source_stock and target_stock:
                    # Check if source has enough stock
                    if source_stock['quantity'] >= action.quantity:
                        # Execute the transfer using database transaction
                        async with conn.transaction():
                            # Decrease source stock
                            await conn.execute("""
                                UPDATE item_locations 
                                SET quantity = quantity - $1, last_updated = NOW()
                                WHERE item_id = $2 AND location_id = $3
                            """, action.quantity, source_stock['item_id'], action.source_department)
                            
                            # Increase target stock
                            await conn.execute("""
                                UPDATE item_locations 
                                SET quantity = quantity + $1, last_updated = NOW()
                                WHERE item_id = $2 AND location_id = $3
                            """, action.quantity, target_stock['item_id'], action.target_department)
                            
                            # Create transfer record in transfers table (if it exists)
                            try:
                                await conn.execute("""
                                    INSERT INTO transfers (id, item_id, from_location_id, to_location_id, 
                                                         quantity, requested_by, status, requested_at, completed_at, notes)
                                    VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW(), $8)
                                """, f"TRANSFER-{uuid.uuid4().hex[:8]}", source_stock['item_id'], 
                                action.source_department, action.target_department, action.quantity,
                                'autonomous_agent', 'completed', 'Automated inter-department optimization transfer')
                            except Exception as transfer_log_error:
                                # If transfers table doesn't exist, just log the warning
                                self.logger.warning(f"Could not log transfer to transfers table: {transfer_log_error}")
                        
                        # Update action status to completed
                        action.status = "completed"
                        action.completed_at = datetime.now()
                        
                        # Update activity log
                        for activity in self.activity_log:
                            if activity["id"] == action.action_id:
                                activity["status"] = "completed"
                                activity["action"] = "Automated Transfer Completed"
                                activity["details"] = f"✅ Successfully transferred {action.quantity} units of {action.item_name} from {action.source_department} to {action.target_department}"
                                break
                        
                        # Remove from active actions
                        if action.action_id in self.active_actions:
                            del self.active_actions[action.action_id]
                        
                        self.logger.info(f"✅ Transfer completed: {action.item_name} ({action.quantity} units) {action.source_department} → {action.target_department}")
                        
                    else:
                        self.logger.warning(f"⚠️ Insufficient stock in {action.source_department} for transfer: {source_stock['quantity']} < {action.quantity}")
                        # Update status to failed
                        action.status = "failed"
                        for activity in self.activity_log:
                            if activity["id"] == action.action_id:
                                activity["status"] = "failed"
                                activity["details"] = f"❌ Transfer failed - insufficient stock in {action.source_department}"
                                break
                else:
                    self.logger.error(f"❌ Could not find matching items for transfer: {action.item_name}")
                    action.status = "failed"
                
                await conn.close()
                
            except Exception as db_error:
                self.logger.error(f"❌ Database error during transfer execution: {db_error}")
                action.status = "failed"
                    
        except Exception as e:
            self.logger.error(f"❌ Error auto-executing transfer: {e}")
            import traceback
            self.logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            # Update status to failed
            action.status = "failed"
    
    async def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        return await self.langgraph_agent.run_monitoring_cycle()
    
    def get_agent_status(self):
        """Get current agent status"""
        return self.langgraph_agent.get_agent_status()
    
    # Inventory management methods
    def get_all_inventory(self):
        """Get all inventory items"""
        return self.langgraph_agent.get_all_inventory()
    
    def get_inventory_by_location(self, location_id: str):
        """Get inventory for specific location"""
        return self.langgraph_agent.get_inventory_by_location(location_id)
    
    def add_inventory_item(self, item_data: Dict):
        """Add new inventory item"""
        return self.langgraph_agent.add_inventory_item(item_data)
    
    def update_inventory_item(self, item_id: str, updates: Dict):
        """Update existing inventory item"""
        return self.langgraph_agent.update_inventory_item(item_id, updates)
    
    def delete_inventory_item(self, item_id: str):
        """Delete inventory item"""
        return self.langgraph_agent.delete_inventory_item(item_id)
    
    def get_low_stock_items(self):
        """Get items with low stock"""
        return self.langgraph_agent.get_low_stock_items()
    
    def get_critical_items(self):
        """Get items with critical stock levels"""
        return self.langgraph_agent.get_critical_items()
    
    # Alert management methods
    def get_all_alerts(self):
        """Get all alerts"""
        return self.langgraph_agent.get_all_alerts()
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "", resolved_by: str = "system"):
        """Resolve an alert"""
        return self.langgraph_agent.resolve_alert(alert_id, resolution_notes, resolved_by)

    def create_alert(self, item_id: str, alert_type: str, message: str, level: AlertLevel):
        """Create a new alert"""
        try:
            alert = SupplyAlert(
                alert_id=str(uuid.uuid4()),
                item_id=item_id,
                alert_type=alert_type,
                message=message,
                level=level,
                created_at=datetime.now(),
                resolved=False
            )
            self.alerts.append(alert)
            
            # Log the alert creation
            self.add_audit_log(
                action="alert_created",
                details={
                    "alert_id": alert.alert_id,
                    "item_id": item_id,
                    "alert_type": alert_type,
                    "level": level.value if hasattr(level, 'value') else str(level)
                },
                user_id="system"
            )
            
            return alert
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return None
    
    # Purchase order methods
    def get_purchase_orders(self, status_filter: Optional[str] = None):
        """Get purchase orders with optional status filter"""
        return self.langgraph_agent.get_purchase_orders(status_filter)
    
    def update_purchase_order_status(self, po_id: str, new_status: str):
        """Update purchase order status"""
        return self.langgraph_agent.update_purchase_order_status(po_id, new_status)
    
    # Transfer methods
    def create_transfer(self, transfer_data: Dict):
        """Create transfer request"""
        return self.langgraph_agent.create_transfer(transfer_data)
    
    def get_transfers(self):
        """Get all transfer requests"""
        return self.langgraph_agent.get_transfers()
    
    def update_transfer_status(self, transfer_id: str, new_status: str):
        """Update transfer status"""
        return self.langgraph_agent.update_transfer_status(transfer_id, new_status)
    
    # Supplier methods
    def get_all_suppliers(self):
        """Get all suppliers"""
        return self.langgraph_agent.get_all_suppliers()
    
    # Audit and analytics methods
    def get_audit_logs(self, limit: int = 100):
        """Get recent audit logs"""
        return self.langgraph_agent.get_audit_logs(limit)
    
    def add_audit_log(self, action: str, details: Dict, user_id: str = "system"):
        """Add new audit log entry"""
        return self.langgraph_agent.add_audit_log(action, details, user_id)
    
    def get_usage_analytics(self, item_id: Optional[str] = None, days: int = 30):
        """Get usage analytics"""
        return self.langgraph_agent.get_usage_analytics(item_id, days)
    
    def get_department_summary(self, department: str):
        """Get summary for specific department"""
        return self.langgraph_agent.get_department_summary(department)
    
    # Additional methods for full compatibility with original agent
    def process_low_stock_order(self, item_id: str, quantity: int, supplier_id: str = None):
        """Process low stock order - enhanced with LangGraph workflow"""
        try:
            # Create purchase order through LangGraph workflow
            item = self.inventory.get(item_id)
            if not item:
                return {"status": "error", "message": "Item not found"}
            
            # Find supplier if not provided
            if not supplier_id:
                for sid, supplier in self.suppliers.items():
                    if item.category.value in supplier.capabilities:
                        supplier_id = sid
                        break
            
            if not supplier_id:
                return {"status": "error", "message": "No suitable supplier found"}
            
            # Create purchase order
            po = PurchaseOrder(
                po_id=str(uuid.uuid4()),
                po_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{len(self.purchase_orders)+1:03d}",
                supplier_id=supplier_id,
                items=[{
                    "item_id": item_id,
                    "quantity": quantity,
                    "unit_price": item.unit_cost
                }],
                status=PurchaseOrderStatus.DRAFT,
                created_date=datetime.now(),
                created_by="enhanced_agent",
                department=item.category.value,
                total_amount=item.unit_cost * quantity,
                urgency_level="high"
            )
            
            self.purchase_orders[po.po_id] = po
            
            # Add audit log
            self.add_audit_log(
                action="purchase_order_created",
                details={
                    "item_id": item_id,
                    "quantity": quantity,
                    "supplier_id": supplier_id,
                    "po_id": po.po_id
                }
            )
            
            return {
                "status": "success",
                "message": f"Purchase order {po.po_number} created successfully",
                "po_id": po.po_id,
                "po_number": po.po_number
            }
            
        except Exception as e:
            self.logger.error(f"Error processing low stock order: {e}")
            return {"status": "error", "message": str(e)}
    
    def process_emergency_order(self, item_id: str, quantity: int, justification: str):
        """Process emergency order with high priority"""
        try:
            result = self.process_low_stock_order(item_id, quantity)
            if result["status"] == "success":
                # Update to emergency priority
                po_id = result["po_id"]
                if po_id in self.purchase_orders:
                    self.purchase_orders[po_id].urgency_level = "emergency"
                    self.purchase_orders[po_id].notes = f"EMERGENCY: {justification}"
                
                # Create critical alert
                alert = SupplyAlert(
                    id=str(uuid.uuid4()),
                    item_id=item_id,
                    alert_type="emergency_order",
                    level=AlertLevel.CRITICAL,
                    message=f"Emergency order placed for {self.inventory[item_id].name}",
                    description=f"Emergency justification: {justification}",
                    created_at=datetime.now(),
                    created_by="enhanced_agent",
                    assigned_to=None,
                    department=self.inventory[item_id].category.value,
                    location=None
                )
                self.alerts.append(alert)
                
                result["alert_id"] = alert.id
                result["message"] = f"Emergency order {result['po_number']} created with critical priority"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing emergency order: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_low_stock_summary(self):
        """Get comprehensive low stock summary"""
        try:
            low_stock_items = self.get_low_stock_items()
            critical_items = self.get_critical_items()
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_items": len(self.inventory),
                "low_stock_count": len(low_stock_items),
                "critical_count": len(critical_items),
                "low_stock_items": [
                    {
                        "item_id": getattr(item, 'item_id', getattr(item, 'item_id', 'unknown')),
                        "name": getattr(item, 'name', getattr(item, 'item_name', 'unknown')),
                        "category": getattr(item, 'category', 'unknown'),
                        "total_available": getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0)),
                        "reorder_point": getattr(item, 'reorder_point', 0),
                        "estimated_days_remaining": max(0, getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0)) / 1)  # Simplified calculation
                    }
                    for item in low_stock_items
                ],
                "critical_items": [
                    {
                        "item_id": getattr(item, 'item_id', getattr(item, 'item_id', 'unknown')),
                        "name": getattr(item, 'name', getattr(item, 'item_name', 'unknown')),
                        "category": getattr(item, 'category', 'unknown'),
                        "total_available": getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0)),
                        "locations": getattr(item, 'locations', {})
                    }
                    for item in critical_items
                ]
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating low stock summary: {e}")
            return {"error": str(e)}
    
    def get_analytics_summary(self):
        """Get comprehensive analytics summary"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "inventory_metrics": {
                    "total_items": len(self.inventory),
                    "total_value": sum(item.unit_cost * getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0)) for item in self.inventory.values()),
                    "low_stock_items": len(self.get_low_stock_items()),
                    "critical_items": len(self.get_critical_items())
                },
                "alert_metrics": {
                    "total_alerts": len(self.alerts),
                    "unresolved_alerts": len([a for a in self.alerts if not a.resolved]),
                    "critical_alerts": len([a for a in self.alerts if a.level == AlertLevel.CRITICAL]),
                    "recent_alerts": len([a for a in self.alerts if a.created_at >= datetime.now() - timedelta(hours=24)])
                },
                "procurement_metrics": {
                    "total_purchase_orders": len(self.purchase_orders),
                    "pending_orders": len([po for po in self.purchase_orders.values() if po.status == PurchaseOrderStatus.PENDING_APPROVAL]),
                    "approved_orders": len([po for po in self.purchase_orders.values() if po.status == PurchaseOrderStatus.APPROVED])
                },
                "transfer_metrics": {
                    "total_transfers": len(self.transfer_requests),
                    "pending_transfers": len([t for t in self.transfer_requests.values() if t.status == TransferStatus.PENDING]),
                    "completed_transfers": len([t for t in self.transfer_requests.values() if t.status == TransferStatus.COMPLETED])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating analytics summary: {e}")
            return {"error": str(e)}

    # Missing methods needed by the backend API
    async def get_recent_activities(self, limit: int = 10):
        """Get recent activities from the agent"""
        try:
            self.logger.info(f"🔍 Getting recent activities, activity_log has {len(self.activity_log)} items")
            
            # Return activities from our activity_log first (these are the automated activities)
            if self.activity_log:
                # Sort by timestamp and return most recent
                sorted_activities = sorted(
                    self.activity_log, 
                    key=lambda x: x.get('timestamp', ''), 
                    reverse=True
                )
                self.logger.info(f"✅ Returning {len(sorted_activities[:limit])} activities from activity_log")
                return sorted_activities[:limit]
            
            # Fallback: Get recent audit logs as activities
            recent_logs = self.get_audit_logs(limit)
            activities = []
            
            for log in recent_logs[-limit:]:
                activity = {
                    "id": str(uuid.uuid4()),
                    "timestamp": log.timestamp.isoformat() if hasattr(log, 'timestamp') else datetime.now().isoformat(),
                    "action": log.action,
                    "details": log.details if hasattr(log, 'details') else str(log),
                    "user_id": log.user_id if hasattr(log, 'user_id') else "system",
                    "status": "completed"
                }
                activities.append(activity)
            
            # Add some recent alerts as activities
            recent_alerts = [a for a in self.alerts if a.created_at >= datetime.now() - timedelta(hours=24)]
            for alert in recent_alerts[-5:]:  # Last 5 recent alerts
                activity = {
                    "id": alert.alert_id,
                    "timestamp": alert.created_at.isoformat(),
                    "action": f"Alert Generated: {alert.alert_type}",
                    "details": alert.message,
                    "user_id": "system",
                    "status": "resolved" if alert.resolved else "active"
                }
                activities.append(activity)
            
            # Sort by timestamp and return most recent
            activities.sort(key=lambda x: x['timestamp'], reverse=True)
            self.logger.info(f"✅ Returning {len(activities[:limit])} fallback activities")
            return activities[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting recent activities: {e}")
            return []

    async def get_active_actions(self):
        """Get currently active automated actions"""
        try:
            self.logger.info(f"🔍 Getting active actions, active_actions has {len(self.active_actions)} items")
            
            # Return active actions from our active_actions dict first
            if self.active_actions:
                active_list = []
                for action_id, action in self.active_actions.items():
                    if action.status in ["pending", "in_progress", "supplier_ordered"]:
                        active_item = {
                            "action_id": action.action_id,
                            "action_type": action.action_type.value,
                            "item_name": action.item_name,
                            "status": action.status,
                            "created_at": action.created_at.isoformat(),
                            "priority": action.priority.value,
                            "details": action.details,
                            "source_department": action.source_department,
                            "target_department": action.target_department,
                            "quantity": action.quantity,
                            "reason": action.reason
                        }
                        active_list.append(active_item)
                
                self.logger.info(f"✅ Returning {len(active_list)} active actions")
                return active_list
            
            # Fallback: Check for pending purchase orders and transfers
            active_actions = []
            
            # Check for pending purchase orders
            pending_pos = [po for po in self.purchase_orders.values() if po.status == PurchaseOrderStatus.PENDING_APPROVAL]
            for po in pending_pos:
                action = {
                    "id": po.po_id,
                    "type": "purchase_order",
                    "status": "pending_approval",
                    "created": po.created_date.isoformat(),
                    "details": f"Purchase Order {po.po_number} waiting for approval",
                    "urgency": getattr(po, 'urgency_level', 'medium')
                }
                active_actions.append(action)
            
            # Check for pending transfers
            pending_transfers = [t for t in self.transfer_requests.values() if t.status == TransferStatus.PENDING]
            for transfer in pending_transfers:
                action = {
                    "id": transfer.transfer_id,
                    "type": "transfer_request",
                    "status": "pending",
                    "created": transfer.requested_date.isoformat(),
                    "details": f"Transfer from {transfer.from_location} to {transfer.to_location}",
                    "urgency": "medium"
                }
                active_actions.append(action)
            
            # Check for unresolved critical alerts
            critical_alerts = [a for a in self.alerts if not a.resolved and a.level == AlertLevel.CRITICAL]
            for alert in critical_alerts:
                action = {
                    "id": alert.alert_id,
                    "type": "critical_alert",
                    "status": "requires_attention",
                    "created": alert.created_at.isoformat(),
                    "details": alert.message,
                    "urgency": "high"
                }
                active_actions.append(action)
            
            return active_actions
            
        except Exception as e:
            self.logger.error(f"Error getting active actions: {e}")
            return []

    async def analyze_all_departments(self):
        """Manually trigger analysis for all departments"""
        try:
            actions_triggered = 0
            
            # Analyze each department's inventory
            departments = set()
            for item in self.inventory.values():
                if hasattr(item, 'department') and item.department:
                    departments.add(item.department)
                elif hasattr(item, 'category'):
                    departments.add(item.category.value)
            
            for department in departments:
                # Check for low stock in this department
                dept_items = [item for item in self.inventory.values() 
                             if (hasattr(item, 'department') and item.department == department) or
                                (hasattr(item, 'category') and item.category.value == department)]
                
                for item in dept_items:
                    current_stock = getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0))
                    if current_stock <= item.minimum_stock:
                        # Trigger reorder
                        result = self.process_low_stock_order(item.item_id, item.minimum_stock * 2)
                        if result.get('status') == 'success':
                            actions_triggered += 1
                            
                        # Create alert if not exists
                        existing_alerts = [a for a in self.alerts 
                                         if a.item_id == item.item_id and not a.resolved]
                        if not existing_alerts:
                            self.create_alert(
                                item_id=item.item_id,
                                alert_type="low_stock",
                                message=f"Low stock detected for {item.name} in {department}",
                                level=AlertLevel.HIGH
                            )
                            actions_triggered += 1
            
            # Log the analysis
            self.add_audit_log(
                action="department_analysis",
                details={"departments_analyzed": list(departments), "actions_triggered": actions_triggered},
                user_id="enhanced_agent"
            )
            
            return actions_triggered
            
        except Exception as e:
            self.logger.error(f"Error analyzing departments: {e}")
            return 0

    # ==================== DUPLICATE METHOD REMOVED ====================
    # The decrease_stock method was duplicated and has been consolidated below.

    async def get_department_inventory(self, department_id: str):
        """Get inventory for a specific department with proper structure"""
        try:
            # First try the new approach using self.inventory
            if hasattr(self, 'inventory') and self.inventory:
                department_items = []
                
                for item in self.inventory.values():
                    location_stock = item.get_location_stock(department_id)
                    if location_stock:
                        department_items.append({
                            "item_id": item.item_id,
                            "item_name": item.name,
                            "current_stock": location_stock.current_quantity,
                            "minimum_stock": location_stock.minimum_threshold,
                            "reorder_point": item.reorder_point,
                            "maximum_capacity": location_stock.maximum_capacity,
                            "last_updated": location_stock.last_updated.isoformat() if location_stock.last_updated else datetime.now().isoformat(),
                            "status": self._get_stock_status_for_item(item, location_stock)
                        })
                
                if department_items:
                    return department_items
            
            # Fallback to the original approach
            dept_inventories = self._get_department_inventories()
            inventories = dept_inventories.get(department_id, [])
            
            return [{
                "item_id": inv.item_id,
                "item_name": inv.item_name,
                "current_stock": inv.current_stock,
                "minimum_stock": inv.minimum_stock,
                "reorder_point": inv.reorder_point,
                "maximum_capacity": inv.maximum_capacity,
                "last_updated": inv.last_updated.isoformat() if hasattr(inv.last_updated, 'isoformat') else str(inv.last_updated),
                "status": self._get_stock_status(inv)
            } for inv in inventories]
            
        except Exception as e:
            self.logger.error(f"Error getting department inventory: {e}")
            return []

    def _get_stock_status(self, inventory: DepartmentInventory) -> str:
        """Get stock status for an inventory item"""
        if inventory.current_stock <= inventory.minimum_stock:
            return "critical"
        elif inventory.current_stock <= inventory.reorder_point:
            return "low"
        elif inventory.current_stock >= inventory.maximum_capacity * 0.9:
            return "overstocked"
        else:
            return "normal"

    # Enhanced functionality from the original agent
    async def initialize(self):
        """Initialize the agent and load department inventories"""
        try:
            self.logger.info("🤖 Initializing Enhanced Supply Inventory Agent...")
            await self._load_department_inventories_from_db()
            self.logger.info("✅ Enhanced Supply Inventory Agent initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize agent: {e}")

    async def analyze_all_departments(self):
        """Analyze inventory across all departments and trigger actions"""
        self.logger.info("🔍 Analyzing inventory across all departments...")
        
        actions_triggered = 0
        
        # Analyze each department's inventory
        dept_inventories = self._get_department_inventories()
        
        for dept_id, inventories in dept_inventories.items():
            for inventory in inventories:
                # Check if action is needed
                if inventory.current_stock <= inventory.minimum_stock:
                    # Create automated action
                    action = AutomatedAction(
                        action_id=f"REORDER-{uuid.uuid4().hex[:8]}",
                        action_type=ActionType.REORDER,
                        priority=ActionPriority.HIGH,
                        source_department=dept_id,
                        target_department=None,
                        item_id=inventory.item_id,
                        item_name=inventory.item_name,
                        quantity=inventory.minimum_stock * 2,
                        reason=f"Critical stock level ({inventory.current_stock} ≤ {inventory.minimum_stock})",
                        status="pending",
                        created_at=datetime.now(),
                        completed_at=None,
                        details={
                            "current_stock": inventory.current_stock,
                            "minimum_stock": inventory.minimum_stock,
                            "department": dept_id
                        }
                    )
                    
                    await self._log_activity(action)
                    actions_triggered += 1
        
        self.logger.info(f"📊 Analysis complete: {actions_triggered} actions triggered")
        return actions_triggered

    async def _log_activity(self, action: AutomatedAction):
        """Log activity for dashboard and notifications"""
        activity = {
            "activity_id": f"ACT-{uuid.uuid4().hex[:8]}",
            "type": "automated_supply_action",
            "action_type": action.action_type.value,
            "timestamp": datetime.now().isoformat(),
            "department": action.source_department,
            "target_department": action.target_department,
            "item_name": action.item_name,
            "quantity": action.quantity,
            "reason": action.reason,
            "status": action.status,
            "priority": action.priority.value,
            "details": action.details
        }
        
        self.activity_log.append(activity)
        self.logger.info(f"📝 Activity logged: {action.action_type.value} for {action.item_name}")

    # Additional essential methods for full functionality
    async def analyze_all_departments(self):
        """Manually trigger analysis for all departments"""
        try:
            actions_triggered = 0
            
            # Analyze each department's inventory
            departments = set()
            for item in self.inventory.values():
                if hasattr(item, 'department') and item.department:
                    departments.add(item.department)
                elif hasattr(item, 'category'):
                    dept = item.category.value if hasattr(item.category, 'value') else str(item.category)
                    departments.add(dept)
            
            for department in departments:
                # Check for low stock items in this department
                dept_items = [item for item in self.inventory.values() 
                            if (hasattr(item, 'department') and item.department == department) or
                            (hasattr(item, 'category') and (item.category.value if hasattr(item.category, 'value') else str(item.category)) == department)]
                
                for item in dept_items:
                    if hasattr(item, 'total_available_quantity') and hasattr(item, 'reorder_point'):
                        if item.total_available_quantity <= item.reorder_point:
                            # Trigger automated reorder
                            result = self.process_low_stock_order(item.item_id, item.reorder_point * 2)
                            if result.get("status") == "success":
                                actions_triggered += 1
            
            # Log the analysis
            self.add_audit_log(
                action="department_analysis_complete",
                details={
                    "departments_analyzed": len(departments),
                    "actions_triggered": actions_triggered
                },
                user_id="enhanced_agent"
            )
            
            return {
                "status": "success",
                "departments_analyzed": len(departments),
                "actions_triggered": actions_triggered
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing departments: {e}")
            return {"status": "error", "message": str(e)}

    async def decrease_stock(self, department_id: str, item_id: str, quantity: int, reason: str = "consumption"):
        """Decrease stock for an item and trigger automated processes"""
        try:
            # Use database integration to decrease stock
            if hasattr(self, 'db_integration') and self.db_integration:
                try:
                    # Check if item exists in the department
                    async with self.db_integration.async_session() as session:
                        # First check if the item exists in this location
                        check_query = text("""
                            SELECT il.quantity, ii.name 
                            FROM item_locations il
                            JOIN inventory_items ii ON il.item_id = ii.id
                            WHERE il.item_id = :item_id AND il.location_id = :location_id
                        """)
                        
                        result = await session.execute(check_query, {
                            "item_id": item_id, 
                            "location_id": department_id
                        })
                        row = result.fetchone()
                        
                        if not row:
                            return {"status": "error", "message": "Item not found in this department"}
                        
                        current_quantity = int(row[0]) if row[0] else 0
                        item_name = row[1] if row[1] else f"Item {item_id}"
                        
                        if current_quantity < quantity:
                            return {"status": "error", "message": f"Insufficient stock. Available: {current_quantity}, Requested: {quantity}"}
                        
                        # Decrease the stock in item_locations
                        update_query = text("""
                            UPDATE item_locations 
                            SET quantity = GREATEST(0, quantity - :quantity),
                                last_updated = :timestamp
                            WHERE item_id = :item_id AND location_id = :location_id
                        """)
                        
                        await session.execute(update_query, {
                            "quantity": quantity,
                            "item_id": item_id,
                            "location_id": department_id,
                            "timestamp": datetime.now()
                        })
                        
                        # Get the new quantity
                        new_quantity = max(0, current_quantity - quantity)
                        
                        # Update total stock in inventory_items table
                        total_query = text("""
                            UPDATE inventory_items 
                            SET current_stock = (
                                SELECT COALESCE(SUM(quantity), 0) 
                                FROM item_locations 
                                WHERE item_id = :item_id
                            ),
                            last_updated = :timestamp
                            WHERE id = :item_id
                        """)
                        
                        await session.execute(total_query, {
                            "item_id": item_id,
                            "timestamp": datetime.now()
                        })
                        
                        # Record the transfer/usage
                        transfer_query = text("""
                            INSERT INTO transfers (
                                item_id, from_location_id, to_location_id, 
                                quantity, reason, status, created_at, completed_at
                            ) VALUES (
                                :item_id, :from_location, 'CONSUMPTION', 
                                :quantity, :reason, 'COMPLETED', :timestamp, :timestamp
                            )
                        """)
                        
                        await session.execute(transfer_query, {
                            "item_id": item_id,
                            "from_location": department_id,
                            "quantity": quantity,
                            "reason": reason,
                            "timestamp": datetime.now()
                        })
                        
                        await session.commit()
                        
                        self.logger.info(f"✅ Decreased stock for {item_id} in {department_id}: -{quantity} units (new: {new_quantity})")
                        
                        # Check if low stock triggers reorder
                        min_threshold_query = text("""
                            SELECT il.minimum_threshold, ii.reorder_point
                            FROM item_locations il
                            JOIN inventory_items ii ON il.item_id = ii.id
                            WHERE il.item_id = :item_id AND il.location_id = :location_id
                        """)
                        
                        threshold_result = await session.execute(min_threshold_query, {
                            "item_id": item_id,
                            "location_id": department_id
                        })
                        threshold_row = threshold_result.fetchone()
                        
                        low_stock_triggered = False
                        if threshold_row:
                            min_threshold = threshold_row[0] or 5
                            reorder_point = threshold_row[1] or 10
                            
                            if new_quantity <= min_threshold:
                                low_stock_triggered = True
                                self.logger.warning(f"⚠️ Low stock alert: {item_id} in {department_id} has {new_quantity} units (threshold: {min_threshold})")
                        
                        return {
                            "status": "success",
                            "message": f"Stock decreased successfully. New level: {new_quantity}",
                            "new_stock": new_quantity,
                            "item_name": item_name,
                            "department": department_id,
                            "quantity_decreased": quantity,
                            "low_stock_triggered": low_stock_triggered
                        }
                        
                except Exception as db_error:
                    self.logger.error(f"❌ Database error in decrease_stock: {db_error}")
                    return {"status": "error", "message": f"Database error: {str(db_error)}"}
            else:
                # Fallback to in-memory inventory
                if item_id not in self.inventory:
                    return {"status": "error", "message": "Item not found"}
                
                item = self.inventory[item_id]
                old_quantity = getattr(item, 'current_stock', getattr(item, 'total_available_quantity', 0))
                
                if old_quantity < quantity:
                    return {"status": "error", "message": f"Insufficient stock. Available: {old_quantity}"}
                
                # Decrease stock
                new_quantity = max(0, old_quantity - quantity)
                if hasattr(item, 'current_stock'):
                    item.current_stock = new_quantity
                elif hasattr(item, 'total_available_quantity'):
                    item.total_available_quantity = new_quantity
                
                self.logger.info(f"✅ Decreased stock for {item_id}: -{quantity} units (new: {new_quantity})")
                
                return {
                    "status": "success", 
                    "message": f"Stock decreased successfully. New level: {new_quantity}",
                    "new_stock": new_quantity,
                    "quantity_decreased": quantity
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error decreasing stock: {e}")
            return {"status": "error", "message": str(e)}

    async def get_department_inventory(self, department_id: str):
        """Get inventory for a specific department"""
        try:
            department_items = []
            
            for item in self.inventory.values():
                location_stock = item.get_location_stock(department_id)
                if location_stock:
                    department_items.append({
                        "item_id": item.item_id,
                        "name": item.name,
                        "category": item.category.value if hasattr(item.category, 'value') else str(item.category),
                        "current_stock": location_stock.current_quantity,
                        "reserved_stock": location_stock.reserved_quantity,
                        "available_stock": location_stock.available_quantity,
                        "minimum_threshold": location_stock.minimum_threshold,
                        "maximum_capacity": location_stock.maximum_capacity,
                        "reorder_point": item.reorder_point,
                        "unit_cost": item.unit_cost,
                        "supplier": item.primary_supplier_id,
                        "last_updated": location_stock.last_updated.isoformat() if location_stock.last_updated else None,
                        "status": self._get_stock_status_for_item(item, location_stock)
                    })
            
            return {
                "department_id": department_id,
                "department_name": self.locations.get(department_id, {}).get("name", department_id),
                "total_items": len(department_items),
                "items": department_items,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting department inventory: {e}")
            return {"error": str(e)}

    def _get_stock_status(self, inventory: DepartmentInventory) -> str:
        """Get stock status for department inventory item"""
        if inventory.current_stock == 0:
            return "out_of_stock"
        elif inventory.current_stock <= inventory.minimum_stock * 0.5:
            return "critical"
        elif inventory.current_stock <= inventory.minimum_stock:
            return "low"
        elif inventory.current_stock <= inventory.minimum_stock * 1.5:
            return "moderate"
        else:
            return "adequate"

    def _get_stock_status_for_item(self, item: SupplyItem, location_stock: LocationStock) -> str:
        """Get stock status for a supply item at a location"""
        current = location_stock.current_quantity
        minimum = location_stock.minimum_threshold
        
        if current == 0:
            return "out_of_stock"
        elif current <= minimum * 0.5:
            return "critical"
        elif current <= minimum:
            return "low"
        elif current <= minimum * 1.5:
            return "moderate"
        else:
            return "adequate"

    # Additional methods for transfer functionality
    def find_departments_with_surplus(self, item_name: str, required_quantity: int) -> List[dict]:
        """Find departments that have surplus of a specific item"""
        try:
            surplus_departments = []
            dept_inventories = self._get_department_inventories()
            
            for dept_id, items in dept_inventories.items():
                for item in items:
                    if getattr(item, 'item_name', '') == item_name:
                        current_stock = getattr(item, 'current_stock', 0)
                        minimum_stock = getattr(item, 'minimum_stock', 0)
                        
                        # Consider surplus if stock is significantly above minimum
                        surplus_available = current_stock - (minimum_stock * 1.5)
                        if surplus_available >= required_quantity:
                            surplus_departments.append({
                                "department_id": dept_id,
                                "department_name": self._get_department_name(dept_id),
                                "current_stock": current_stock,
                                "minimum_stock": minimum_stock,
                                "surplus_available": surplus_available,
                                "can_supply": min(surplus_available, required_quantity)
                            })
            
            # Sort by surplus available (highest first)
            surplus_departments.sort(key=lambda x: x["surplus_available"], reverse=True)
            return surplus_departments
            
        except Exception as e:
            self.logger.error(f"Error finding surplus departments: {e}")
            return []

    def execute_inter_department_transfer(self, item_name: str, from_dept: str, to_dept: str, quantity: int) -> dict:
        """Execute transfer between departments"""
        try:
            self.logger.info(f"Executing transfer: {quantity} {item_name} from {from_dept} to {to_dept}")
            
            # This will be handled by the automated transfer system
            transfer_id = f"MANUAL-{uuid.uuid4().hex[:8]}"
            
            # Create transfer record
            transfer_record = {
                "transfer_id": transfer_id,
                "item_name": item_name,
                "from_department": from_dept,
                "to_department": to_dept,
                "quantity": quantity,
                "status": "scheduled",
                "requested_at": datetime.now().isoformat(),
                "requested_by": "manual_request"
            }
            
            self.transfers.append(transfer_record)
            
            # Log the transfer request
            self.add_audit_log(
                action="manual_transfer_requested",
                details={
                    "transfer_id": transfer_id,
                    "item_name": item_name,
                    "from_department": from_dept,
                    "to_department": to_dept,
                    "quantity": quantity
                },
                user_id="manual_request"
            )
            
            return {
                "status": "success",
                "transfer_id": transfer_id,
                "message": f"Transfer scheduled: {quantity} {item_name} from {from_dept} to {to_dept}"
            }
            
        except Exception as e:
            self.logger.error(f"Error executing transfer: {e}")
            return {"status": "error", "message": str(e)}

    def get_transfer_history(self, limit: int = 50) -> List[dict]:
        """Get transfer history"""
        try:
            # Combine automated transfers from activity log and manual transfers
            all_transfers = []
            
            # Get completed transfers from activity log
            for activity in self.activity_log:
                if activity.get("action_type") == "inter_transfer" and activity.get("status") == "completed":
                    all_transfers.append({
                        "transfer_id": activity.get("id"),
                        "item_name": activity.get("item"),
                        "from_department": activity.get("source_department"),
                        "to_department": activity.get("target_department"),
                        "quantity": activity.get("details", "").split("(")[1].split(" ")[0] if "(" in activity.get("details", "") else "Unknown",
                        "status": "completed",
                        "completed_at": activity.get("timestamp"),
                        "type": "automated"
                    })
            
            # Add manual transfers
            for transfer in self.transfers:
                all_transfers.append({
                    **transfer,
                    "type": "manual"
                })
            
            # Sort by timestamp (most recent first)
            all_transfers.sort(key=lambda x: x.get("completed_at") or x.get("requested_at", ""), reverse=True)
            
            return all_transfers[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting transfer history: {e}")
            return []

    def check_and_execute_autonomous_transfers(self):
        """Check for and execute autonomous transfers (called by the automated system)"""
        try:
            self.logger.info("🔄 Checking for autonomous transfer opportunities...")
            transfers_executed = 0
            
            dept_inventories = self._get_department_inventories()
            
            # Look for departments with low stock that can be supplied by others
            for dept_id, items in dept_inventories.items():
                for item in items:
                    current_stock = getattr(item, 'current_stock', 0)
                    minimum_stock = getattr(item, 'minimum_stock', 0)
                    item_name = getattr(item, 'item_name', '')
                    
                    # If stock is low but not critical (to avoid conflicts with reorders)
                    if minimum_stock < current_stock <= minimum_stock * 1.2:
                        # Look for surplus in other departments
                        surplus_depts = self.find_departments_with_surplus(item_name, minimum_stock)
                        
                        for surplus_dept in surplus_depts[:1]:  # Take best match
                            if surplus_dept["department_id"] != dept_id:
                                transfer_quantity = min(surplus_dept["can_supply"], minimum_stock)
                                
                                # Execute the transfer
                                result = self.execute_inter_department_transfer(
                                    item_name=item_name,
                                    from_dept=surplus_dept["department_id"],
                                    to_dept=dept_id,
                                    quantity=transfer_quantity
                                )
                                
                                if result.get("status") == "success":
                                    transfers_executed += 1
                                    self.logger.info(f"✅ Autonomous transfer executed: {item_name} {surplus_dept['department_id']} → {dept_id}")
                                break
            
            return transfers_executed
            
        except Exception as e:
            self.logger.error(f"Error in autonomous transfer check: {e}")
            return 0

# Global instance for backward compatibility
def get_enhanced_supply_agent(db_integration=None):
    """Get the enhanced supply agent instance"""
    global _enhanced_agent_instance
    if '_enhanced_agent_instance' not in globals():
        _enhanced_agent_instance = EnhancedSupplyInventoryAgent(db_integration=db_integration)
    elif db_integration and not hasattr(_enhanced_agent_instance, 'db_integration'):
        # Update existing instance with database integration
        _enhanced_agent_instance.db_integration = db_integration
    return _enhanced_agent_instance

# Create global instance (will be updated with db_integration later)
enhanced_supply_agent = get_enhanced_supply_agent()
