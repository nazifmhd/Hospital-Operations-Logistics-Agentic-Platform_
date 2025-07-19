"""
Enhanced Supply Inventory Agent with Automated Reordering and Inter-facility Transfers

This intelligent agent automatically:
1. Monitors stock levels across all departments
2. Triggers reorders when hitting reorder points
3. Initiates inter-facility transfers when below minimum stock
4. Logs all activities for notifications and dashboard
5. Manages department-wise inventory operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    REORDER = "reorder"
    INTER_TRANSFER = "inter_transfer"
    STOCK_DECREASE = "stock_decrease"
    ALERT_CREATED = "alert_created"
    TRANSFER_COMPLETED = "transfer_completed"

class ActionPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DepartmentInventory:
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
    """Enhanced Supply Inventory Agent with automated processes"""
    
    def __init__(self, db_integration):
        self.db = db_integration
        self.active_actions: Dict[str, AutomatedAction] = {}
        self.department_inventories: Dict[str, List[DepartmentInventory]] = {}
        self.activity_log: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize the agent and load department inventories"""
        try:
            logger.info("🤖 Initializing Enhanced Supply Inventory Agent...")
            await self.load_department_inventories()
            await self.start_monitoring()
            logger.info("✅ Enhanced Supply Inventory Agent initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise

    async def load_department_inventories(self):
        """Load inventory data for all departments from real database tables"""
        try:
            logger.info("📊 Loading department inventories from real database...")
            
            # Try to get real database data from item_locations table
            try:
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
                
                # Execute query using direct database connection
                import asyncpg
                
                # Database connection details (same as update_database.py)
                DB_CONFIG = {
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'hospital_supply_db',
                    'user': 'postgres',
                    'password': '1234'
                }
                
                try:
                    conn = await asyncpg.connect(**DB_CONFIG)
                    result = await conn.fetch(query)
                    result = [dict(row) for row in result]
                    await conn.close()
                    logger.info(f"📦 Database query executed successfully, found {len(result)} records")
                except Exception as db_error:
                    logger.warning(f"⚠️ Database connection failed: {db_error}")
                    result = []
                
                if result:
                    logger.info(f"📦 Found {len(result)} item-location records from database")
                    
                    # Group by location_id (department)
                    self.department_inventories = {}
                    
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
                        
                        if location_id not in self.department_inventories:
                            self.department_inventories[location_id] = []
                        
                        self.department_inventories[location_id].append(dept_inv)
                    
                    logger.info(f"📋 Loaded inventories for {len(self.department_inventories)} departments from real database")
                    
                    # Log department summary
                    for dept_id, items in self.department_inventories.items():
                        critical_items = sum(1 for item in items if item.current_stock <= item.minimum_stock)
                        logger.info(f"   🏥 {dept_id}: {len(items)} items ({critical_items} critical)")
                    
                    return
                else:
                    logger.warning("⚠️ No data returned from database query")
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not load from real database: {e}")
            
            # Fallback to mock data that matches your real data structure
            logger.info("📋 Creating mock department data based on real database structure...")
            await self._create_real_data_mock()
            
        except Exception as e:
            logger.error(f"❌ Failed to load department inventories: {e}")
            # Create fallback data even if everything fails
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
        """Create mock data that matches your real database structure"""
        logger.info("📋 Creating mock data based on real item_locations structure...")
        
        # Use data structure matching your real database
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
            
            if location_id not in self.department_inventories:
                self.department_inventories[location_id] = []
            
            self.department_inventories[location_id].append(dept_inv)
        
        logger.info(f"📋 Created mock data for {len(self.department_inventories)} departments with automation test scenarios")
        
        # Log critical items for automation testing
        for dept_id, items in self.department_inventories.items():
            critical_items = [item for item in items if item.current_stock <= item.minimum_stock]
            if critical_items:
                logger.info(f"   🚨 {dept_id}: {len(critical_items)} items below minimum stock")
        
        # Add to activity log
        self.activity_log.append({
            "timestamp": datetime.now().isoformat(),
            "action_type": "system_initialization",
            "description": f"Loaded inventory data for {len(self.department_inventories)} departments",
            "priority": "medium",
            "details": {"departments": list(self.department_inventories.keys())}
        })

    async def _execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute database query through integration"""
        try:
            if hasattr(self.db, 'engine'):
                # SQLAlchemy approach
                from sqlalchemy import text
                async with self.db.engine.begin() as conn:
                    result = await conn.execute(text(query), params or {})
                    return [dict(row._mapping) for row in result.fetchall()]
            else:
                # Fallback approach
                return []
        except Exception as e:
            logger.error(f"❌ Query execution failed: {e}")
            return []

    async def _create_mock_department_data(self):
        """Simple fallback mock data if real data mock fails"""
        logger.info("📋 Creating simple fallback mock data...")
        
        # Just use the real data mock method
        await self._create_real_data_mock()

    async def start_monitoring(self):
        """Start the automated monitoring process"""
        logger.info("🔍 Starting automated inventory monitoring...")
        
        # Run initial analysis
        await self.analyze_all_departments()
        
        # Schedule periodic monitoring (every 5 minutes)
        # In production, this would be a background task
        logger.info("✅ Automated monitoring started")

    async def analyze_all_departments(self):
        """Analyze inventory across all departments and trigger actions with global optimization"""
        logger.info("🔍 Analyzing inventory across all departments with global optimization...")
        
        # Step 1: Create a comprehensive item-by-item analysis
        item_global_analysis = await self.create_global_item_analysis()
        
        # Step 2: Process inter-transfers first for all items that can be solved internally
        inter_transfer_actions = []
        items_solved_internally = set()
        
        for item_id, analysis in item_global_analysis.items():
            if analysis['can_solve_internally']:
                # Create transfers for this item
                transfers = await self.create_optimal_transfers_for_item(item_id, analysis)
                inter_transfer_actions.extend(transfers)
                items_solved_internally.add(item_id)
        
        # Step 3: Execute all inter-transfer actions
        for action in inter_transfer_actions:
            await self.execute_automated_action(action)
        
        # Step 4: Only create reorders for items that CANNOT be solved internally
        reorder_actions = 0
        for item_id, analysis in item_global_analysis.items():
            if not analysis['can_solve_internally'] and analysis['needs_external_reorder']:
                # Create reorders only for departments that truly need them
                for dept_data in analysis['departments_needing_reorder']:
                    # Calculate quantity needed (minimum stock * 2 for safety)
                    quantity_needed = max(dept_data['minimum_stock'] * 2, dept_data['shortage'] + 20)
                    
                    reorder_action = AutomatedAction(
                        action_id=f"REORDER-{uuid.uuid4().hex[:8]}",
                        action_type=ActionType.REORDER,
                        priority=ActionPriority.HIGH,
                        source_department=dept_data['department_id'],
                        target_department=None,
                        item_id=item_id,
                        item_name=dept_data['item_name'],
                        quantity=quantity_needed,
                        reason=f"External reorder required - total system shortage: {analysis['total_shortage']} units",
                        status="pending",
                        created_at=datetime.now(),
                        completed_at=None,
                        details={
                            "current_stock": dept_data['current_stock'],
                            "minimum_stock": dept_data['minimum_stock'],
                            "supplier_action": "automatic_purchase_order",
                            "inter_transfer_attempted": True,
                            "inter_transfer_available": False,
                            "total_system_shortage": analysis['total_shortage']
                        }
                    )
                    await self.execute_automated_action(reorder_action)
                    reorder_actions += 1
        
        total_actions = len(inter_transfer_actions) + reorder_actions
        logger.info(f"📊 Global Analysis complete: {len(inter_transfer_actions)} inter-transfers, {reorder_actions} reorders ({total_actions} total)")
        logger.info(f"✅ Items solved internally: {len(items_solved_internally)}")
        
        return total_actions

    async def create_global_item_analysis(self) -> Dict[str, Dict]:
        """Create a comprehensive analysis of each item across all departments"""
        analysis = {}
        
        # Group all inventory by item_id
        items_by_id = {}
        for dept_id, inventories in self.department_inventories.items():
            for inventory in inventories:
                if inventory.item_id not in items_by_id:
                    items_by_id[inventory.item_id] = []
                items_by_id[inventory.item_id].append(inventory)
        
        # Analyze each item
        for item_id, inventories in items_by_id.items():
            total_stock = sum(inv.current_stock for inv in inventories)
            total_minimum = sum(inv.minimum_stock for inv in inventories)
            
            # Find locations with excess and shortage
            excess_locations = []
            shortage_locations = []
            
            for inv in inventories:
                excess = inv.current_stock - inv.minimum_stock
                if excess > 5:  # Has meaningful excess
                    excess_locations.append({
                        'department_id': inv.department_id,
                        'department_name': inv.department_name,
                        'excess': excess,
                        'available_for_transfer': excess - 2  # Keep small buffer
                    })
                elif inv.current_stock <= inv.minimum_stock:
                    shortage_locations.append({
                        'department_id': inv.department_id,
                        'department_name': inv.department_name,
                        'item_name': inv.item_name,
                        'current_stock': inv.current_stock,
                        'minimum_stock': inv.minimum_stock,
                        'shortage': inv.minimum_stock - inv.current_stock
                    })
            
            # Calculate if item can be solved internally
            total_excess = sum(loc['available_for_transfer'] for loc in excess_locations)
            total_shortage = sum(loc['shortage'] for loc in shortage_locations)
            
            analysis[item_id] = {
                'total_stock': total_stock,
                'total_minimum': total_minimum,
                'excess_locations': excess_locations,
                'shortage_locations': shortage_locations,
                'total_excess': total_excess,
                'total_shortage': total_shortage,
                'can_solve_internally': total_excess >= total_shortage,
                'needs_external_reorder': total_shortage > 0 and total_excess < total_shortage,
                'departments_needing_reorder': shortage_locations if total_excess < total_shortage else []
            }
        
        return analysis
    
    async def create_optimal_transfers_for_item(self, item_id: str, analysis: Dict) -> List[AutomatedAction]:
        """Create optimal inter-transfer actions for a specific item"""
        transfers = []
        
        if not analysis['can_solve_internally']:
            return transfers
        
        # Sort excess locations by available amount (most first)
        excess_locations = sorted(analysis['excess_locations'], 
                                key=lambda x: x['available_for_transfer'], reverse=True)
        
        # Process each shortage location
        for shortage in analysis['shortage_locations']:
            remaining_need = shortage['shortage']
            
            # Find sources to fulfill this shortage
            for excess in excess_locations:
                if remaining_need <= 0:
                    break
                
                if excess['available_for_transfer'] > 0:
                    # Calculate transfer amount
                    transfer_amount = min(remaining_need, excess['available_for_transfer'])
                    
                    # Create transfer action
                    transfer = AutomatedAction(
                        action_id=f"TRANSFER-{uuid.uuid4().hex[:8]}",
                        action_type=ActionType.INTER_TRANSFER,
                        priority=ActionPriority.HIGH,
                        source_department=excess['department_id'],
                        target_department=shortage['department_id'],
                        item_id=item_id,
                        item_name=shortage['item_name'],
                        quantity=transfer_amount,
                        reason=f"Global optimization: {excess['department_name']} → {shortage['department_name']}",
                        status="pending",
                        created_at=datetime.now(),
                        completed_at=None,
                        details={
                            "optimization_type": "global_item_balancing",
                            "source_excess": excess['excess'],
                            "target_shortage": shortage['shortage'],
                            "transfer_amount": transfer_amount
                        }
                    )
                    transfers.append(transfer)
                    
                    # Update remaining amounts
                    remaining_need -= transfer_amount
                    excess['available_for_transfer'] -= transfer_amount
        
        return transfers

    async def determine_required_action(self, inventory: DepartmentInventory) -> Optional[AutomatedAction]:
        """Determine what automated action is needed for inventory item"""
        
        # PRIORITY 1: Check if we're below minimum stock - try inter-transfer first
        if inventory.current_stock <= inventory.minimum_stock:
            # Find department with excess stock for inter-transfer
            source_dept = await self.find_department_with_excess_stock(
                inventory.item_id, 
                5,  # Just need some excess, not huge amounts
                exclude_dept=inventory.department_id
            )
            
            if source_dept:
                # Calculate how much we need to get above minimum
                shortage = inventory.minimum_stock - inventory.current_stock + 5  # Small buffer
                transfer_quantity = min(shortage, source_dept["available_excess"])
                
                return AutomatedAction(
                    action_id=f"TRANSFER-{uuid.uuid4().hex[:8]}",
                    action_type=ActionType.INTER_TRANSFER,
                    priority=ActionPriority.HIGH,
                    source_department=source_dept["department_id"],
                    target_department=inventory.department_id,
                    item_id=inventory.item_id,
                    item_name=inventory.item_name,
                    quantity=transfer_quantity,
                    reason=f"Critical stock level ({inventory.current_stock} ≤ {inventory.minimum_stock}) - inter-transfer from {source_dept['department_name']}",
                    status="pending",
                    created_at=datetime.now(),
                    completed_at=None,
                    details={
                        "current_stock": inventory.current_stock,
                        "minimum_stock": inventory.minimum_stock,
                        "source_department_name": source_dept["department_name"],
                        "transfer_type": "emergency_inter_facility",
                        "shortage": shortage,
                        "available_excess": source_dept["available_excess"]
                    }
                )
        
        # PRIORITY 2: Check if we're at reorder point but above minimum - try inter-transfer first
        elif inventory.current_stock <= inventory.reorder_point:
            # Find department with excess stock for inter-transfer
            source_dept = await self.find_department_with_excess_stock(
                inventory.item_id, 
                5,  # Just need some excess
                exclude_dept=inventory.department_id
            )
            
            if source_dept:
                # Calculate how much we need to get above reorder point
                shortage = inventory.reorder_point - inventory.current_stock + 5  # Small buffer
                transfer_quantity = min(shortage, source_dept["available_excess"])
                
                return AutomatedAction(
                    action_id=f"TRANSFER-{uuid.uuid4().hex[:8]}",
                    action_type=ActionType.INTER_TRANSFER,
                    priority=ActionPriority.MEDIUM,
                    source_department=source_dept["department_id"],
                    target_department=inventory.department_id,
                    item_id=inventory.item_id,
                    item_name=inventory.item_name,
                    quantity=transfer_quantity,
                    reason=f"Stock at reorder point ({inventory.current_stock} ≤ {inventory.reorder_point}) - inter-transfer from {source_dept['department_name']}",
                    status="pending",
                    created_at=datetime.now(),
                    completed_at=None,
                    details={
                        "current_stock": inventory.current_stock,
                        "reorder_point": inventory.reorder_point,
                        "source_department_name": source_dept["department_name"],
                        "transfer_type": "preventive_inter_facility",
                        "shortage": shortage,
                        "available_excess": source_dept["available_excess"]
                    }
                )
        
        return None

    async def find_department_with_excess_stock(self, item_id: str, required_quantity: int, exclude_dept: str) -> Optional[Dict]:
        """Find a department that has excess stock for transfer"""
        
        for dept_id, inventories in self.department_inventories.items():
            if dept_id == exclude_dept:
                continue
                
            for inventory in inventories:
                if inventory.item_id == item_id:
                    # Check if this department has enough excess
                    excess = inventory.current_stock - inventory.minimum_stock
                    if excess >= required_quantity:
                        return {
                            "department_id": dept_id,
                            "department_name": inventory.department_name,
                            "available_excess": excess,
                            "current_stock": inventory.current_stock
                        }
        
        return None

    async def execute_automated_action(self, action: AutomatedAction):
        """Execute the automated action"""
        logger.info(f"🤖 Executing automated action: {action.action_type.value} for {action.item_name}")
        
        try:
            self.active_actions[action.action_id] = action
            
            if action.action_type == ActionType.REORDER:
                await self._execute_reorder(action)
            elif action.action_type == ActionType.INTER_TRANSFER:
                await self._execute_inter_transfer(action)
            
            # Log activity
            await self._log_activity(action)
            
            # Create notification
            await self._create_action_notification(action)
            
            logger.info(f"✅ Automated action {action.action_id} executed successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to execute action {action.action_id}: {e}")
            action.status = "failed"

    async def _execute_reorder(self, action: AutomatedAction):
        """Execute automatic reorder from supplier"""
        logger.info(f"📦 Executing automatic reorder: {action.quantity} units of {action.item_name}")
        
        # Create purchase order automatically
        purchase_order = {
            "po_id": f"PO-{uuid.uuid4().hex[:8]}",
            "item_id": action.item_id,
            "quantity": action.quantity,
            "department": action.source_department,
            "priority": action.priority.value,
            "auto_generated": True,
            "created_at": datetime.now(),
            "status": "pending_supplier_confirmation"
        }
        
        # In production, this would interface with supplier systems
        action.details["purchase_order"] = purchase_order
        action.status = "supplier_ordered"
        
        logger.info(f"📋 Purchase order {purchase_order['po_id']} created for {action.item_name}")

    async def _execute_inter_transfer(self, action: AutomatedAction):
        """Execute automatic inter-facility transfer"""
        logger.info(f"🔄 Executing inter-facility transfer: {action.quantity} units of {action.item_name}")
        logger.info(f"   From: {action.details.get('source_department_name')} → To: {action.target_department}")
        
        # Create transfer record
        transfer_record = {
            "transfer_id": f"TRF-{uuid.uuid4().hex[:8]}",
            "from_location": action.source_department,
            "to_location": action.target_department,
            "item_id": action.item_id,
            "quantity": action.quantity,
            "priority": action.priority.value,
            "auto_generated": True,
            "created_at": datetime.now(),
            "status": "in_progress"
        }
        
        # Update stock levels in both memory and database
        await self._update_stock_levels(action)
        await self._update_database_stock_levels(action)
        
        action.details["transfer_record"] = transfer_record
        action.status = "completed"
        action.completed_at = datetime.now()
        
        logger.info(f"✅ Transfer {transfer_record['transfer_id']} completed successfully")

    async def _update_database_stock_levels(self, action: AutomatedAction):
        """Update stock levels in database after transfer"""
        import asyncpg
        
        # Database connection details
        DB_CONFIG = {
            'host': 'localhost',
            'port': 5432,
            'database': 'hospital_supply_db',
            'user': 'postgres',
            'password': '1234'
        }
        
        try:
            conn = await asyncpg.connect(**DB_CONFIG)
            
            # Update source location (decrease stock)
            await conn.execute("""
                UPDATE item_locations 
                SET quantity = quantity - $1, last_updated = NOW()
                WHERE item_id = $2 AND location_id = $3
            """, action.quantity, action.item_id, action.source_department)
            
            # Update target location (increase stock)
            await conn.execute("""
                UPDATE item_locations 
                SET quantity = quantity + $1, last_updated = NOW()
                WHERE item_id = $2 AND location_id = $3
            """, action.quantity, action.item_id, action.target_department)
            
            await conn.close()
            logger.info(f"✅ Database updated: {action.item_name} transferred from {action.source_department} to {action.target_department}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update database stock levels: {e}")

    async def _update_stock_levels(self, action: AutomatedAction):
        """Update stock levels after transfer"""
        
        # Update source department (decrease)
        for inventory in self.department_inventories.get(action.source_department, []):
            if inventory.item_id == action.item_id:
                inventory.current_stock -= action.quantity
                logger.info(f"📉 {action.source_department}: {inventory.item_name} stock decreased by {action.quantity}")
                break
        
        # Update target department (increase)
        for inventory in self.department_inventories.get(action.target_department, []):
            if inventory.item_id == action.item_id:
                inventory.current_stock += action.quantity
                logger.info(f"📈 {action.target_department}: {inventory.item_name} stock increased by {action.quantity}")
                break

    async def _log_activity(self, action: AutomatedAction):
        """Log activity for dashboard and notifications"""
        
        activity = {
            "activity_id": f"ACT-{uuid.uuid4().hex[:8]}",
            "type": "automated_supply_action",
            "action_type": action.action_type.value,
            "timestamp": datetime.now().isoformat(),
            "department": action.source_department,
            "target_department": action.target_department,  # Add target department for transfers
            "item_name": action.item_name,
            "quantity": action.quantity,
            "reason": action.reason,
            "status": action.status,
            "priority": action.priority.value,
            "details": action.details
        }
        
        self.activity_log.append(activity)
        logger.info(f"📝 Activity logged: {action.action_type.value} for {action.item_name}")

    async def _create_action_notification(self, action: AutomatedAction):
        """Create notification for the automated action"""
        
        if action.action_type == ActionType.REORDER:
            message = f"🤖 Auto-Reorder: {action.quantity} units of {action.item_name} ordered for {action.source_department}"
            alert_type = "auto_reorder"
        elif action.action_type == ActionType.INTER_TRANSFER:
            source_name = action.details.get('source_department_name', action.source_department)
            message = f"🔄 Auto-Transfer: {action.quantity} units of {action.item_name} transferred from {source_name} to {action.target_department}"
            alert_type = "auto_transfer"
        else:
            message = f"🤖 Automated action: {action.action_type.value} for {action.item_name}"
            alert_type = "automated_action"
        
        # Create alert through database integration
        try:
            if hasattr(self.db, 'create_alert_from_inventory'):
                alert_data = {
                    "id": action.action_id,
                    "item_id": action.item_id,
                    "name": action.item_name,
                    "current_stock": 0,  # Will be updated by the alert system
                    "minimum_stock": 0
                }
                
                alert_id = await self.db.create_alert_from_inventory(
                    alert_data, 
                    alert_type=alert_type
                )
                
                if alert_id:
                    logger.info(f"🔔 Notification created: {alert_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to create notification: {e}")

    async def decrease_stock(self, department_id: str, item_id: str, quantity: int, reason: str = "consumption"):
        """Decrease stock for a specific department and item, updating both database tables"""
        logger.info(f"📉 Decreasing stock: {quantity} units of {item_id} in {department_id}")
        
        # Find the inventory item
        for inventory in self.department_inventories.get(department_id, []):
            if inventory.item_id == item_id:
                old_stock = inventory.current_stock
                new_stock = max(0, inventory.current_stock - quantity)
                actual_decrease = old_stock - new_stock
                
                # Update in-memory stock
                inventory.current_stock = new_stock
                inventory.last_updated = datetime.now()
                
                # Update database tables
                await self._update_database_stock(department_id, item_id, new_stock, actual_decrease)
                
                # Log the decrease
                decrease_action = AutomatedAction(
                    action_id=f"DECREASE-{uuid.uuid4().hex[:8]}",
                    action_type=ActionType.STOCK_DECREASE,
                    priority=ActionPriority.LOW,
                    source_department=department_id,
                    target_department=None,
                    item_id=item_id,
                    item_name=inventory.item_name,
                    quantity=actual_decrease,
                    reason=reason,
                    status="completed",
                    created_at=datetime.now(),
                    completed_at=datetime.now(),
                    details={
                        "old_stock": old_stock,
                        "new_stock": new_stock,
                        "actual_decrease": actual_decrease
                    }
                )
                
                await self._log_activity(decrease_action)
                
                # Check if this triggers any automated actions
                action_needed = await self.determine_required_action(inventory)
                if action_needed:
                    await self.execute_automated_action(action_needed)
                
                logger.info(f"✅ Stock decreased successfully. Old: {old_stock} → New: {new_stock}")
                return new_stock
        
        logger.warning(f"⚠️ Item {item_id} not found in department {department_id}")
        return None

    async def _update_database_stock(self, department_id: str, item_id: str, new_stock: int, decrease_amount: int):
        """Update stock levels in both item_locations and inventory_items tables"""
        try:
            # Database connection details (same as above)
            import asyncpg
            
            DB_CONFIG = {
                'host': 'localhost',
                'port': 5432,
                'database': 'hospital_supply_db',
                'user': 'postgres',
                'password': '1234'
            }
            
            # Update item_locations table (department-specific stock)
            update_item_locations_query = """
            UPDATE item_locations 
            SET quantity = $1, last_updated = CURRENT_TIMESTAMP 
            WHERE item_id = $2 AND location_id = $3
            """
            
            # For inventory_items table, we need to calculate total stock across all locations
            # and update the current_stock field
            calculate_total_query = """
            SELECT COALESCE(SUM(quantity), 0) as total_stock 
            FROM item_locations 
            WHERE item_id = $1
            """
            
            update_inventory_items_query = """
            UPDATE inventory_items 
            SET current_stock = $1, updated_at = CURRENT_TIMESTAMP 
            WHERE item_id = $2
            """
            
            # Execute database updates with direct connection
            try:
                conn = await asyncpg.connect(**DB_CONFIG)
                
                # Update item_locations
                await conn.execute(update_item_locations_query, new_stock, item_id, department_id)
                
                # Calculate new total stock
                total_result = await conn.fetchrow(calculate_total_query, item_id)
                total_stock = total_result['total_stock'] if total_result else new_stock
                
                # Update inventory_items
                await conn.execute(update_inventory_items_query, total_stock, item_id)
                
                await conn.close()
                
                logger.info(f"📊 Database updated: {item_id} in {department_id} = {new_stock}, total = {total_stock}")
                
            except Exception as db_error:
                logger.warning(f"⚠️ Database update failed: {db_error}")
                
        except Exception as e:
            logger.error(f"❌ Database stock update failed: {e}")

    async def get_department_inventory(self, department_id: str) -> List[Dict]:
        """Get current inventory for a specific department"""
        inventories = self.department_inventories.get(department_id, [])
        
        return [{
            "item_id": inv.item_id,
            "item_name": inv.item_name,
            "current_stock": inv.current_stock,
            "minimum_stock": inv.minimum_stock,
            "reorder_point": inv.reorder_point,
            "maximum_capacity": inv.maximum_capacity,
            "last_updated": inv.last_updated.isoformat(),
            "status": self._get_stock_status(inv)
        } for inv in inventories]

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

    async def get_recent_activities(self, limit: int = 10) -> List[Dict]:
        """Get recent automated activities for dashboard"""
        # Get a diverse set of activities by action type
        all_activities = sorted(
            self.activity_log, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        # Try to get a mix of different action types
        if len(all_activities) > limit:
            # Get activities by type to ensure diversity
            reorder_activities = [a for a in all_activities if a.get("action_type") == "reorder"]
            transfer_activities = [a for a in all_activities if a.get("action_type") == "inter_transfer"]
            other_activities = [a for a in all_activities if a.get("action_type") not in ["reorder", "inter_transfer"]]
            
            # Take a balanced mix
            selected_activities = []
            selected_activities.extend(reorder_activities[:4])  # 4 reorders
            selected_activities.extend(transfer_activities[:4])  # 4 transfers
            selected_activities.extend(other_activities[:2])   # 2 others
            
            # Fill remaining slots with newest activities
            remaining_slots = limit - len(selected_activities)
            if remaining_slots > 0:
                remaining_activities = [a for a in all_activities if a not in selected_activities]
                selected_activities.extend(remaining_activities[:remaining_slots])
            
            return sorted(selected_activities, key=lambda x: x["timestamp"], reverse=True)[:limit]
        else:
            return all_activities[:limit]

    async def get_active_actions(self) -> List[Dict]:
        """Get currently active automated actions"""
        return [
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "item_name": action.item_name,
                "status": action.status,
                "created_at": action.created_at.isoformat(),
                "priority": action.priority.value,
                "details": action.details
            }
            for action in self.active_actions.values()
            if action.status in ["pending", "in_progress", "supplier_ordered"]
        ]

# Global instance
enhanced_supply_agent = None

async def get_enhanced_supply_agent(db_integration):
    """Get or create the enhanced supply agent instance"""
    global enhanced_supply_agent
    
    if enhanced_supply_agent is None:
        enhanced_supply_agent = EnhancedSupplyInventoryAgent(db_integration)
        await enhanced_supply_agent.initialize()
    
    return enhanced_supply_agent

# Test function
async def test_enhanced_agent():
    """Test the enhanced supply agent"""
    print("🧪 Testing Enhanced Supply Inventory Agent...")
    
    # Mock database integration
    class MockDB:
        async def create_alert_from_inventory(self, item, alert_type="automated_action"):
            return f"ALERT-{uuid.uuid4().hex[:8]}"
    
    db = MockDB()
    agent = EnhancedSupplyInventoryAgent(db)
    await agent.initialize()
    
    # Test stock decrease
    print("\n📉 Testing stock decrease...")
    new_stock = await agent.decrease_stock("ICU-001", "ITEM-001", 10, "patient consumption")
    print(f"New stock level: {new_stock}")
    
    # Test getting department inventory
    print("\n📊 Getting ICU inventory...")
    icu_inventory = await agent.get_department_inventory("ICU-001")
    for item in icu_inventory:
        print(f"  - {item['item_name']}: {item['current_stock']} ({item['status']})")
    
    # Test getting recent activities
    print("\n📋 Recent activities:")
    activities = await agent.get_recent_activities(5)
    for activity in activities:
        print(f"  - {activity['action_type']}: {activity['item_name']} ({activity['status']})")

if __name__ == "__main__":
    asyncio.run(test_enhanced_agent())
