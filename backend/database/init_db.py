"""
Database initialization and seeding for Hospital Supply Inventory Management System
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from .database import db_manager
from .models import (
    User, Location, Supplier, InventoryItem, Batch, Alert, Transfer,
    PurchaseOrder, ApprovalRequest, Budget, AuditLog, Notification,
    ItemCategory, AlertLevel, UserRole, QualityStatus, TransferStatus,
    PurchaseOrderStatus, ApprovalStatus
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """Initialize and seed the database with sample data"""
    
    def __init__(self):
        self.db = db_manager
    
    async def initialize_database(self):
        """Create all tables and seed with initial data"""
        try:
            logger.info("Starting database initialization...")
            
            # Create all tables
            await self.db.create_tables()
            logger.info("Database tables created successfully")
            
            # Check if data already exists
            async with await self.db.get_async_session() as session:
                from sqlalchemy import text
                result = await session.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                if user_count > 0:
                    logger.info("Database already contains data, skipping seeding")
                    return
            
            # Seed with sample data
            await self.seed_sample_data()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def seed_sample_data(self):
        """Seed database with comprehensive sample data"""
        logger.info("Starting database seeding...")
        
        async with await self.db.get_async_session() as session:
            # Create locations first
            locations = await self._create_locations(session)
            logger.info(f"Created {len(locations)} locations")
            
            # Create users
            users = await self._create_users(session)
            logger.info(f"Created {len(users)} users")
            
            # Create suppliers
            suppliers = await self._create_suppliers(session)
            logger.info(f"Created {len(suppliers)} suppliers")
            
            # Create inventory items
            items = await self._create_inventory_items(session)
            logger.info(f"Created {len(items)} inventory items")
            
            # Create batches
            batches = await self._create_batches(session, items, locations)
            logger.info(f"Created {len(batches)} batches")
            
            # Create alerts
            alerts = await self._create_alerts(session, items, locations)
            logger.info(f"Created {len(alerts)} alerts")
            
            # Create transfers
            transfers = await self._create_transfers(session, items, locations, users)
            logger.info(f"Created {len(transfers)} transfers")
            
            # Create purchase orders
            pos = await self._create_purchase_orders(session, suppliers, users)
            logger.info(f"Created {len(pos)} purchase orders")
            
            # Create approval requests
            approvals = await self._create_approval_requests(session, users)
            logger.info(f"Created {len(approvals)} approval requests")
            
            # Create budgets
            budgets = await self._create_budgets(session)
            logger.info(f"Created {len(budgets)} budgets")
            
            # Create notifications
            notifications = await self._create_notifications(session, users)
            logger.info(f"Created {len(notifications)} notifications")
            
            await session.commit()
            logger.info("Database seeding completed successfully")
    
    async def _create_locations(self, session) -> List[Location]:
        """Create sample locations"""
        locations_data = [
            {
                "id": "LOC_MAIN_WAREHOUSE",
                "name": "Main Warehouse",
                "type": "warehouse",
                "description": "Primary storage facility for hospital supplies",
                "address": "123 Hospital Drive, Medical Center",
                "capacity": 10000.0,
                "manager_id": None,  # Will be set after users are created
                "storage_conditions": {"temperature": "20-25°C", "humidity": "45-60%"},
                "security_level": "high",
                "is_active": True
            },
            {
                "id": "LOC_EMERGENCY_ROOM",
                "name": "Emergency Room",
                "type": "department",
                "description": "Emergency department storage",
                "address": "Emergency Wing, Floor 1",
                "capacity": 500.0,
                "storage_conditions": {"temperature": "18-22°C", "humidity": "40-60%"},
                "security_level": "medium",
                "is_active": True
            },
            {
                "id": "LOC_OR_CENTRAL",
                "name": "Operating Room Central",
                "type": "department",
                "description": "Central OR supply storage",
                "address": "Surgical Wing, Floor 3",
                "capacity": 800.0,
                "storage_conditions": {"temperature": "20-24°C", "humidity": "45-55%", "sterile": True},
                "security_level": "high",
                "is_active": True
            },
            {
                "id": "LOC_ICU_STORAGE",
                "name": "ICU Storage",
                "type": "department",
                "description": "Intensive Care Unit supply storage",
                "address": "ICU Wing, Floor 4",
                "capacity": 300.0,
                "storage_conditions": {"temperature": "20-23°C", "humidity": "40-55%"},
                "security_level": "high",
                "is_active": True
            },
            {
                "id": "LOC_PHARMACY",
                "name": "Pharmacy Storage",
                "type": "pharmacy",
                "description": "Pharmaceutical storage facility",
                "address": "Pharmacy Wing, Floor 2",
                "capacity": 1200.0,
                "storage_conditions": {"temperature": "15-25°C", "humidity": "45-65%", "controlled": True},
                "security_level": "maximum",
                "is_active": True
            }
        ]
        
        locations = []
        for loc_data in locations_data:
            location = Location(**loc_data)
            session.add(location)
            locations.append(location)
        
        await session.flush()
        return locations
    
    async def _create_users(self, session) -> List[User]:
        """Create sample users"""
        users_data = [
            {
                "id": "USER_ADMIN",
                "username": "admin",
                "email": "admin@hospital.com",
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
                "department": "IT",
                "phone": "+1-555-0001",
                "is_active": True
            },
            {
                "id": "USER_INVENTORY_MGR",
                "username": "inv_manager",
                "email": "inventory@hospital.com",
                "full_name": "Sarah Johnson",
                "role": UserRole.INVENTORY_MANAGER,
                "department": "Supply Chain",
                "phone": "+1-555-0002",
                "is_active": True
            },
            {
                "id": "USER_WAREHOUSE_STAFF",
                "username": "warehouse_clerk",
                "email": "warehouse@hospital.com",
                "full_name": "Mike Rodriguez",
                "role": UserRole.WAREHOUSE_STAFF,
                "department": "Warehouse",
                "phone": "+1-555-0003",
                "is_active": True
            },
            {
                "id": "USER_NURSE_SUPERVISOR",
                "username": "nurse_super",
                "email": "nursing@hospital.com",
                "full_name": "Dr. Emily Chen",
                "role": UserRole.DEPARTMENT_HEAD,
                "department": "Nursing",
                "phone": "+1-555-0004",
                "is_active": True
            },
            {
                "id": "USER_PHARMACIST",
                "username": "pharmacist",
                "email": "pharmacy@hospital.com",
                "full_name": "Robert Kim",
                "role": UserRole.DEPARTMENT_HEAD,
                "department": "Pharmacy",
                "phone": "+1-555-0005",
                "is_active": True
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            session.add(user)
            users.append(user)
        
        await session.flush()
        return users
    
    async def _create_suppliers(self, session) -> List[Supplier]:
        """Create sample suppliers"""
        suppliers_data = [
            {
                "id": "SUP_MEDTECH",
                "name": "MedTech Supplies Inc.",
                "contact_person": "James Wilson",
                "email": "orders@medtech.com",
                "phone": "+1-800-555-0101",
                "address": "456 Industrial Blvd, Supply City, SC 12345",
                "specialty": "Medical Equipment",
                "rating": 4.8,
                "payment_terms": "Net 30",
                "delivery_time": 3,
                "is_active": True
            },
            {
                "id": "SUP_PHARMAPLUS",
                "name": "PharmaCorp Plus",
                "contact_person": "Dr. Maria Santos",
                "email": "procurement@pharmacorp.com",
                "phone": "+1-800-555-0102",
                "address": "789 Pharma Drive, Medicine City, MC 54321",
                "specialty": "Pharmaceuticals",
                "rating": 4.9,
                "payment_terms": "Net 15",
                "delivery_time": 2,
                "is_active": True
            },
            {
                "id": "SUP_SURGICAL_PRO",
                "name": "Surgical Professionals Ltd.",
                "contact_person": "Dr. John Davis",
                "email": "sales@surgicalpro.com",
                "phone": "+1-800-555-0103",
                "address": "321 Surgery Lane, OR City, OR 98765",
                "specialty": "Surgical Instruments",
                "rating": 4.7,
                "payment_terms": "Net 45",
                "delivery_time": 5,
                "is_active": True
            }
        ]
        
        suppliers = []
        for sup_data in suppliers_data:
            supplier = Supplier(**sup_data)
            session.add(supplier)
            suppliers.append(supplier)
        
        await session.flush()
        return suppliers
    
    async def _create_inventory_items(self, session) -> List[InventoryItem]:
        """Create sample inventory items"""
        items_data = [
            {
                "id": "ITEM_SYRINGE_10ML",
                "name": "Disposable Syringe 10ml",
                "sku": "SYR-10ML-001",
                "category": ItemCategory.CONSUMABLES,
                "description": "Sterile disposable syringe with luer lock, 10ml capacity",
                "unit": "piece",
                "unit_cost": Decimal("2.50"),
                "minimum_level": 100,
                "maximum_level": 1000,
                "reorder_point": 200,
                "primary_supplier": "MedTech Supplies Inc.",
                "secondary_suppliers": ["Surgical Professionals Ltd."],
                "storage_requirements": {"sterile": True, "temperature": "room"},
                "is_active": True
            },
            {
                "id": "ITEM_GAUZE_PADS",
                "name": "Sterile Gauze Pads 4x4",
                "sku": "GAU-4X4-002",
                "category": ItemCategory.CONSUMABLES,
                "description": "Sterile gauze pads, 4 inch x 4 inch, absorbent",
                "unit": "pack",
                "unit_cost": Decimal("8.75"),
                "minimum_level": 50,
                "maximum_level": 500,
                "reorder_point": 100,
                "primary_supplier": "MedTech Supplies Inc.",
                "storage_requirements": {"sterile": True, "dry": True},
                "is_active": True
            },
            {
                "id": "ITEM_IBUPROFEN_200MG",
                "name": "Ibuprofen 200mg Tablets",
                "sku": "IBU-200-003",
                "category": ItemCategory.MEDICATION,
                "description": "Ibuprofen tablets, 200mg, pain relief medication",
                "unit": "bottle",
                "unit_cost": Decimal("15.50"),
                "minimum_level": 20,
                "maximum_level": 200,
                "reorder_point": 40,
                "primary_supplier": "PharmaCorp Plus",
                "storage_requirements": {"controlled": True, "temperature": "room", "secure": True},
                "is_active": True
            },
            {
                "id": "ITEM_SURGICAL_MASK",
                "name": "Surgical Face Mask",
                "sku": "MASK-SUR-004",
                "category": ItemCategory.PPE,
                "description": "Disposable surgical face mask, 3-layer protection",
                "unit": "box",
                "unit_cost": Decimal("25.00"),
                "minimum_level": 30,
                "maximum_level": 300,
                "reorder_point": 60,
                "primary_supplier": "MedTech Supplies Inc.",
                "storage_requirements": {"dry": True, "room_temperature": True},
                "is_active": True
            },
            {
                "id": "ITEM_BLOOD_PRESSURE_CUFF",
                "name": "Blood Pressure Cuff - Adult",
                "sku": "BP-CUFF-005",
                "category": ItemCategory.EQUIPMENT,
                "description": "Reusable blood pressure cuff for adult patients",
                "unit": "piece",
                "unit_cost": Decimal("45.00"),
                "minimum_level": 10,
                "maximum_level": 50,
                "reorder_point": 15,
                "primary_supplier": "Surgical Professionals Ltd.",
                "storage_requirements": {"clean": True, "room_temperature": True},
                "is_active": True
            }
        ]
        
        items = []
        for item_data in items_data:
            item = InventoryItem(**item_data)
            session.add(item)
            items.append(item)
        
        await session.flush()
        return items
    
    async def _create_batches(self, session, items: List[InventoryItem], locations: List[Location]) -> List[Batch]:
        """Create sample batches"""
        batches = []
        
        # Create multiple batches for each item
        for item in items:
            for i in range(2, 4):  # 2-3 batches per item
                batch_data = {
                    "id": f"BATCH_{item.sku}_{i:03d}",
                    "batch_number": f"{item.sku}-B{i:03d}",
                    "item_id": item.id,
                    "quantity": item.maximum_level // (i + 1),  # Varying quantities
                    "expiry_date": datetime.now() + timedelta(days=90 * i),  # Varying expiry dates
                    "quality_status": QualityStatus.APPROVED,
                    "supplier_batch_id": f"SUP-{item.sku}-{i:03d}",
                    "received_date": datetime.now() - timedelta(days=i * 10),
                    "received_by": "USER_WAREHOUSE_STAFF",
                    "location_id": locations[i % len(locations)].id,
                    "is_active": True
                }
                
                batch = Batch(**batch_data)
                session.add(batch)
                batches.append(batch)
        
        await session.flush()
        return batches
    
    async def _create_alerts(self, session, items: List[InventoryItem], locations: List[Location]) -> List[Alert]:
        """Create sample alerts"""
        alerts_data = [
            {
                "id": "ALERT_LOW_STOCK_001",
                "type": "low_stock",
                "level": AlertLevel.WARNING,
                "message": "Low stock level detected for Disposable Syringe 10ml",
                "item_id": "ITEM_SYRINGE_10ML",
                "location": "Main Warehouse",
                "threshold_value": 200.0,
                "current_value": 150.0,
                "is_resolved": False
            },
            {
                "id": "ALERT_EXPIRY_002",
                "type": "expiry_warning",
                "level": AlertLevel.CRITICAL,
                "message": "Batch expiring within 30 days: Ibuprofen 200mg",
                "item_id": "ITEM_IBUPROFEN_200MG",
                "location": "Pharmacy Storage",
                "threshold_value": 30.0,
                "current_value": 15.0,
                "is_resolved": False
            },
            {
                "id": "ALERT_QUALITY_003",
                "type": "quality_issue",
                "level": AlertLevel.HIGH,
                "message": "Quality inspection required for incoming batch",
                "item_id": "ITEM_GAUZE_PADS",
                "location": "Main Warehouse",
                "is_resolved": False
            }
        ]
        
        alerts = []
        for alert_data in alerts_data:
            alert = Alert(**alert_data)
            session.add(alert)
            alerts.append(alert)
        
        await session.flush()
        return alerts
    
    async def _create_transfers(self, session, items: List[InventoryItem], 
                              locations: List[Location], users: List[User]) -> List[Transfer]:
        """Create sample transfers"""
        transfers_data = [
            {
                "id": "TRANS_001",
                "item_id": "ITEM_SURGICAL_MASK",
                "from_location_id": "LOC_MAIN_WAREHOUSE",
                "to_location_id": "LOC_EMERGENCY_ROOM",
                "quantity": 10,
                "status": TransferStatus.COMPLETED,
                "requested_by": "USER_NURSE_SUPERVISOR",
                "requested_at": datetime.now() - timedelta(days=2),
                "approved_by": "USER_INVENTORY_MGR",
                "approved_at": datetime.now() - timedelta(days=1),
                "completed_at": datetime.now() - timedelta(hours=6),
                "reason": "Emergency room supply replenishment",
                "priority": "high"
            },
            {
                "id": "TRANS_002",
                "item_id": "ITEM_GAUZE_PADS",
                "from_location_id": "LOC_MAIN_WAREHOUSE",
                "to_location_id": "LOC_OR_CENTRAL",
                "quantity": 25,
                "status": TransferStatus.PENDING,
                "requested_by": "USER_NURSE_SUPERVISOR",
                "requested_at": datetime.now() - timedelta(hours=3),
                "reason": "Scheduled OR supply replenishment",
                "priority": "medium"
            }
        ]
        
        transfers = []
        for trans_data in transfers_data:
            transfer = Transfer(**trans_data)
            session.add(transfer)
            transfers.append(transfer)
        
        await session.flush()
        return transfers
    
    async def _create_purchase_orders(self, session, suppliers: List[Supplier], users: List[User]) -> List[PurchaseOrder]:
        """Create sample purchase orders"""
        pos_data = [
            {
                "id": "PO_001",
                "po_number": "PO202412001",
                "supplier_id": "SUP_MEDTECH",
                "items": [
                    {"item_id": "ITEM_SYRINGE_10ML", "quantity": 500, "unit_cost": 2.50},
                    {"item_id": "ITEM_SURGICAL_MASK", "quantity": 100, "unit_cost": 25.00}
                ],
                "total_amount": Decimal("3750.00"),
                "status": PurchaseOrderStatus.APPROVED,
                "created_by": "USER_INVENTORY_MGR",
                "expected_delivery": datetime.now() + timedelta(days=5),
                "notes": "Urgent order for emergency supplies"
            },
            {
                "id": "PO_002",
                "po_number": "PO202412002",
                "supplier_id": "SUP_PHARMAPLUS",
                "items": [
                    {"item_id": "ITEM_IBUPROFEN_200MG", "quantity": 50, "unit_cost": 15.50}
                ],
                "total_amount": Decimal("775.00"),
                "status": PurchaseOrderStatus.PENDING,
                "created_by": "USER_PHARMACIST",
                "expected_delivery": datetime.now() + timedelta(days=3),
                "notes": "Regular pharmaceutical restock"
            }
        ]
        
        pos = []
        for po_data in pos_data:
            po = PurchaseOrder(**po_data)
            session.add(po)
            pos.append(po)
        
        await session.flush()
        return pos
    
    async def _create_approval_requests(self, session, users: List[User]) -> List[ApprovalRequest]:
        """Create sample approval requests"""
        approvals_data = [
            {
                "id": "APPR_001",
                "request_type": "purchase_order",
                "request_data": {
                    "item_id": "ITEM_BLOOD_PRESSURE_CUFF",
                    "quantity": 20,
                    "supplier": "Surgical Professionals Ltd.",
                    "total_cost": 900.00
                },
                "requester_id": "USER_NURSE_SUPERVISOR",
                "status": ApprovalStatus.PENDING,
                "emergency": True,
                "justification": "Emergency replacement for damaged equipment",
                "estimated_cost": Decimal("900.00")
            },
            {
                "id": "APPR_002",
                "request_type": "emergency_purchase",
                "request_data": {
                    "item_id": "ITEM_SURGICAL_MASK",
                    "quantity": 200,
                    "reason": "COVID surge preparation"
                },
                "requester_id": "USER_INVENTORY_MGR",
                "status": ApprovalStatus.APPROVED,
                "emergency": True,
                "justification": "Increased patient volume requires additional PPE",
                "estimated_cost": Decimal("5000.00"),
                "approved_by": ["USER_ADMIN"]
            }
        ]
        
        approvals = []
        for approval_data in approvals_data:
            approval = ApprovalRequest(**approval_data)
            session.add(approval)
            approvals.append(approval)
        
        await session.flush()
        return approvals
    
    async def _create_budgets(self, session) -> List[Budget]:
        """Create sample budgets"""
        budgets_data = [
            {
                "id": "BUDGET_MEDICAL_2024",
                "department": "Medical Supplies",
                "category": "CONSUMABLES",
                "allocated_amount": Decimal("250000.00"),
                "spent_amount": Decimal("125000.00"),
                "fiscal_year": 2024,
                "quarter": 4,
                "is_active": True
            },
            {
                "id": "BUDGET_PHARMACY_2024",
                "department": "Pharmacy",
                "category": "MEDICATION",
                "allocated_amount": Decimal("500000.00"),
                "spent_amount": Decimal("275000.00"),
                "fiscal_year": 2024,
                "quarter": 4,
                "is_active": True
            },
            {
                "id": "BUDGET_EQUIPMENT_2024",
                "department": "Equipment",
                "category": "EQUIPMENT",
                "allocated_amount": Decimal("100000.00"),
                "spent_amount": Decimal("45000.00"),
                "fiscal_year": 2024,
                "quarter": 4,
                "is_active": True
            }
        ]
        
        budgets = []
        for budget_data in budgets_data:
            budget = Budget(**budget_data)
            session.add(budget)
            budgets.append(budget)
        
        await session.flush()
        return budgets
    
    async def _create_notifications(self, session, users: List[User]) -> List[Notification]:
        """Create sample notifications"""
        notifications_data = [
            {
                "id": "NOTIF_001",
                "user_id": "USER_INVENTORY_MGR",
                "title": "Low Stock Alert",
                "message": "Multiple items are below minimum stock levels",
                "type": "alert",
                "priority": "high",
                "is_read": False
            },
            {
                "id": "NOTIF_002",
                "user_id": "USER_PHARMACIST",
                "title": "Batch Expiry Warning",
                "message": "Ibuprofen batch expires in 15 days",
                "type": "expiry",
                "priority": "medium",
                "is_read": False
            },
            {
                "id": "NOTIF_003",
                "user_id": "USER_NURSE_SUPERVISOR",
                "title": "Transfer Approved",
                "message": "Your surgical mask transfer request has been approved",
                "type": "approval",
                "priority": "low",
                "is_read": True,
                "read_at": datetime.now() - timedelta(hours=2)
            }
        ]
        
        notifications = []
        for notif_data in notifications_data:
            notification = Notification(**notif_data)
            session.add(notification)
            notifications.append(notification)
        
        await session.flush()
        return notifications

# Create global initializer instance
db_initializer = DatabaseInitializer()

# Convenience function to initialize database
async def init_database():
    """Initialize the database with tables and sample data"""
    await db_initializer.initialize_database()

if __name__ == "__main__":
    asyncio.run(init_database())
