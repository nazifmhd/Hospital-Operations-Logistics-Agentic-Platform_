"""
LEGACY FILE - NO LONGER IN USE

Supply Inventory Agent for Hospital Operations Platform
❌ THIS FILE CONTAINS LEGACY CODE AND EXTENSIVE MOCK DATA ❌

⚠️  IMPORTANT: This file is now DEPRECATED
✅  Use the LangGraph-based agent system instead:
    - langgraph_supply_agent.py (main LangGraph implementation)
    - enhanced_supply_agent.py (LangGraph wrapper)
    - data_models.py (clean data structures only)

🗑️  This file is kept only for historical reference and should NOT be imported
    All data models have been extracted to data_models.py
    All functionality has been migrated to LangGraph-based agents

This agent autonomously monitors, manages, and optimizes hospital supply inventory
including medical supplies, pharmaceuticals, and equipment consumables.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from typing import Union
import sys
import os

# Add AI/ML modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_ml'))

# AI/ML imports with better error handling
try:
    # Check if AI/ML modules exist before importing
    ai_ml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ai_ml')
    if os.path.exists(ai_ml_path):
        sys.path.append(ai_ml_path)
        
        try:
            from predictive_analytics import (
                AdvancedPredictiveAnalytics, 
                predictive_analytics, 
                initialize_ai_engine,
                ForecastResult,
                AnomalyDetection,
                OptimizationResult
            )
        except:
            # Create fallback classes
            class AdvancedPredictiveAnalytics: pass
            class ForecastResult: pass 
            class AnomalyDetection: pass
            class OptimizationResult: pass
            predictive_analytics = None
            initialize_ai_engine = None
            
        try:
            from demand_forecasting import (
                AdvancedDemandForecasting,
                demand_forecasting,
                DemandForecast
            )
        except:
            class AdvancedDemandForecasting: pass
            class DemandForecast: pass
            demand_forecasting = None
            
        try:
            from intelligent_optimization import (
                IntelligentOptimizer,
                intelligent_optimizer,
                OptimizationSolution,
                OptimizationObjective
            )
        except:
            class IntelligentOptimizer: pass
            class OptimizationSolution: pass
            class OptimizationObjective:
                MINIMIZE_COST = "minimize_cost"
                BALANCE_ALL = "balance_all"
            intelligent_optimizer = None
            
        AI_ML_AVAILABLE = False  # Set to False for now until modules are created
        print("✅ AI/ML fallback classes loaded")
    else:
        # Create all fallback classes
        class AdvancedPredictiveAnalytics: pass
        class ForecastResult: pass 
        class AnomalyDetection: pass
        class OptimizationResult: pass
        class AdvancedDemandForecasting: pass
        class DemandForecast: pass
        class IntelligentOptimizer: pass
        class OptimizationSolution: pass
        class OptimizationObjective:
            MINIMIZE_COST = "minimize_cost"
            BALANCE_ALL = "balance_all"
        
        predictive_analytics = None
        initialize_ai_engine = None
        demand_forecasting = None
        intelligent_optimizer = None
        AI_ML_AVAILABLE = False
        print("✅ AI/ML fallback classes created (no AI/ML directory)")
        
except ImportError as e:
    print(f"⚠️ AI/ML modules not available: {e}")
    AI_ML_AVAILABLE = False

class SupplyCategory(Enum):
    MEDICAL_SUPPLIES = "medical_supplies"
    PHARMACEUTICALS = "pharmaceuticals"
    CONSUMABLES = "consumables"
    PPE = "personal_protective_equipment"
    SURGICAL = "surgical_supplies"
    LABORATORY = "laboratory"
    RADIOLOGY = "radiology"
    EMERGENCY = "emergency"

class AlertLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRole(Enum):
    INVENTORY_MANAGER = "inventory_manager"
    DEPARTMENT_HEAD = "department_head"
    PHARMACIST = "pharmacist"
    NURSE = "nurse"
    PROCUREMENT_OFFICER = "procurement_officer"
    WAREHOUSE_STAFF = "warehouse_staff"
    ADMIN = "admin"

class PurchaseOrderStatus(Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT_TO_SUPPLIER = "sent_to_supplier"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PARTIALLY_DELIVERED = "partially_delivered"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class QualityStatus(Enum):
    APPROVED = "approved"
    QUARANTINE = "quarantine"
    REJECTED = "rejected"
    PENDING_INSPECTION = "pending_inspection"
    RECALLED = "recalled"

class TransferStatus(Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class InventoryBatch:
    """Represents a batch/lot of inventory items"""
    batch_id: str
    lot_number: str
    manufacture_date: datetime
    expiry_date: datetime
    quantity: int
    supplier_id: str
    quality_status: QualityStatus
    received_date: datetime
    cost_per_unit: float
    storage_conditions: str
    certificates: List[str]  # Quality certificates, compliance docs
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() >= self.expiry_date
    
    @property
    def days_until_expiry(self) -> int:
        delta = self.expiry_date - datetime.now()
        return max(0, delta.days)

@dataclass
class LocationStock:
    """Represents stock at a specific location"""
    location_id: str
    location_name: str
    current_quantity: int
    reserved_quantity: int
    minimum_threshold: int
    maximum_capacity: int
    
    @property
    def available_quantity(self) -> int:
        return self.current_quantity - self.reserved_quantity
    
    @property
    def is_low_stock(self) -> bool:
        return self.available_quantity <= self.minimum_threshold

@dataclass
@dataclass
class TransferRequest:
    """Represents an inventory transfer between locations"""
    transfer_id: str
    item_id: str
    from_location: str
    to_location: str
    quantity: int
    requested_by: str
    requested_date: datetime
    status: TransferStatus
    priority: str
    reason: str
    approved_by: Optional[str] = None
    completed_date: Optional[datetime] = None

@dataclass
class SupplyItem:
    """Represents a supply item in the inventory with multi-location and batch support"""
    id: str
    name: str
    description: str
    category: SupplyCategory
    sku: str
    manufacturer: str
    model_number: Optional[str]
    unit_of_measure: str
    unit_cost: float
    reorder_point: int
    reorder_quantity: int
    abc_classification: str  # A, B, C classification for inventory management
    criticality_level: str  # Critical, High, Medium, Low
    storage_requirements: str
    regulatory_info: Dict[str, Any]
    supplier_id: str
    alternative_suppliers: List[str]
    last_updated: datetime
    created_by: str
    
    # Multi-location inventory
    locations: Dict[str, LocationStock]
    
    # Batch tracking
    batches: List[InventoryBatch]
    
    # Usage tracking
    usage_history: List[Dict[str, Any]]

    # Daily consumption for demand forecasting
    daily_consumption: int = 10
    
    @property
    def current_quantity(self) -> int:
        """Total quantity across all locations (alias for total_quantity)"""
        return self.total_quantity
    
    @property
    def total_quantity(self) -> int:
        return sum(location.current_quantity for location in self.locations.values())
    
    @property
    def total_available_quantity(self) -> int:
        return sum(location.available_quantity for location in self.locations.values())
    
    @property
    def total_reserved_quantity(self) -> int:
        return sum(location.reserved_quantity for location in self.locations.values())
    
    @property
    def is_low_stock(self) -> bool:
        return any(location.is_low_stock for location in self.locations.values())
    
    @property
    def is_critical_low_stock(self) -> bool:
        total_available = self.total_available_quantity
        total_reorder_point = sum(location.minimum_threshold for location in self.locations.values())
        return total_available <= (total_reorder_point * 0.5)
    
    @property
    def is_expired_stock_present(self) -> bool:
        return any(batch.is_expired for batch in self.batches)
    
    @property
    def expiring_soon_batches(self) -> List[InventoryBatch]:
        return [batch for batch in self.batches if batch.days_until_expiry <= 30 and not batch.is_expired]
    
    @property
    def expired_batches(self) -> List[InventoryBatch]:
        return [batch for batch in self.batches if batch.is_expired]
    
    @property
    def total_value(self) -> float:
        return sum(batch.quantity * batch.cost_per_unit for batch in self.batches)
    
    @property
    def average_cost_per_unit(self) -> float:
        total_qty = sum(batch.quantity for batch in self.batches)
        if total_qty == 0:
            return self.unit_cost
        return self.total_value / total_qty
    
    @property
    def minimum_threshold(self) -> int:
        """Total minimum threshold across all locations"""
        return sum(location.minimum_threshold for location in self.locations.values())
    
    @property
    def maximum_capacity(self) -> int:
        """Total maximum capacity across all locations"""
        return sum(location.maximum_capacity for location in self.locations.values())
    
    @property
    def needs_reorder(self) -> bool:
        """Check if the item needs reorder based on all locations"""
        return any(location.available_quantity <= location.minimum_threshold for location in self.locations.values())
    
    def get_location_stock(self, location_id: str) -> Optional[LocationStock]:
        return self.locations.get(location_id)
    
    def get_available_quantity_at_location(self, location_id: str) -> int:
        location = self.locations.get(location_id)
        return location.available_quantity if location else 0
    
    def has_sufficient_stock_at_location(self, location_id: str, required_quantity: int) -> bool:
        return self.get_available_quantity_at_location(location_id) >= required_quantity

@dataclass
class User:
    """Represents a system user with role-based permissions"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    department: str
    permissions: List[str]
    is_active: bool
    created_date: datetime
    last_login: Optional[datetime]
    
    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions or self.role == UserRole.ADMIN

@dataclass
class SupplyAlert:
    """Enhanced alert system with user assignment and priority"""
    id: str
    item_id: str
    alert_type: str
    level: AlertLevel
    message: str
    description: str
    created_at: datetime
    created_by: str
    assigned_to: Optional[str]
    department: str
    location: Optional[str]
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    escalation_level: int = 0
    requires_approval: bool = False
    
    @property
    def age_hours(self) -> float:
        return (datetime.now() - self.created_at).total_seconds() / 3600
    
    @property
    def is_overdue(self) -> bool:
        # Define SLA based on alert level
        sla_hours = {
            AlertLevel.CRITICAL: 1,
            AlertLevel.HIGH: 4,
            AlertLevel.MEDIUM: 24,
            AlertLevel.LOW: 72
        }
        return self.age_hours > sla_hours.get(self.level, 24)

@dataclass
class AuditLog:
    """Comprehensive audit trail for all inventory operations"""
    log_id: str
    timestamp: datetime
    user_id: str
    action: str
    item_id: Optional[str]
    location: Optional[str]
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]

@dataclass
@dataclass
class Supplier:
    """Enhanced supplier management with performance tracking"""
    supplier_id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    tax_id: str
    payment_terms: str
    lead_time_days: int
    minimum_order_value: float
    reliability_score: float
    quality_rating: float
    delivery_performance: float
    price_competitiveness: float
    certifications: List[str]
    preferred_categories: List[SupplyCategory]
    contract_start_date: datetime
    contract_end_date: datetime
    is_active: bool
    
    @property
    def overall_score(self) -> float:
        return (self.reliability_score + self.quality_rating + 
                self.delivery_performance + self.price_competitiveness) / 4

@dataclass
class PurchaseOrderItem:
    """Individual item in a purchase order"""
    item_id: str
    item_name: str
    sku: str
    quantity: int
    unit_price: float
    total_price: float
    specification: str
    delivery_location: str
    urgency_level: str

@dataclass
class PurchaseOrder:
    """Comprehensive purchase order management"""
    # Required fields (no defaults)
    po_id: str
    
    # Optional fields with defaults
    po_number: str = ""
    supplier_id: str = ""
    created_by: str = ""
    delivery_address: str = ""
    notes: str = ""
    total_amount: float = 0.0
    currency: str = "USD"
    payment_terms: str = "NET30"
    status: PurchaseOrderStatus = PurchaseOrderStatus.PENDING_APPROVAL
    created_date: datetime = field(default_factory=datetime.now)
    required_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=3))
    items: List[PurchaseOrderItem] = field(default_factory=list)
    approval_workflow: List[Dict[str, Any]] = field(default_factory=list)
    delivery_tracking: Dict[str, Any] = field(default_factory=dict)
    invoice_details: Optional[Dict[str, Any]] = None
    
    @property
    def is_overdue(self) -> bool:
        return datetime.now() > self.required_date and self.status not in [
            PurchaseOrderStatus.DELIVERED, PurchaseOrderStatus.CANCELLED
        ]
    
    @property
    def days_until_required(self) -> int:
        delta = self.required_date - datetime.now()
        return delta.days

@dataclass
class Budget:
    """Department budget management"""
    budget_id: str
    department: str
    fiscal_year: str
    total_budget: float
    allocated_budget: float
    spent_amount: float
    committed_amount: float
    category_allocations: Dict[str, float]
    
    @property
    def available_budget(self) -> float:
        return self.allocated_budget - self.spent_amount - self.committed_amount
    
    @property
    def utilization_percentage(self) -> float:
        if self.allocated_budget == 0:
            return 0
        return (self.spent_amount / self.allocated_budget) * 100

@dataclass
class ComplianceRecord:
    """Regulatory compliance tracking"""
    record_id: str
    item_id: str
    regulation_type: str
    compliance_status: str
    certification_number: str
    issued_date: datetime
    expiry_date: datetime
    issuing_authority: str
    documents: List[str]
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expiry_date
    
    @property
    def days_until_expiry(self) -> int:
        delta = self.expiry_date - datetime.now()
        return max(0, delta.days)

class ProfessionalSupplyInventoryAgent:
    """
    Professional-grade autonomous agent for comprehensive hospital supply inventory management
    Features: Multi-location, batch tracking, user management, compliance, analytics
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.inventory: Dict[str, SupplyItem] = {}
        self.alerts: List[SupplyAlert] = []
        self.suppliers: Dict[str, Supplier] = {}
        self.users: Dict[str, User] = {}
        self.locations: Dict[str, Dict] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.transfer_requests: Dict[str, TransferRequest] = {}
        self.audit_logs: List[AuditLog] = []
        self.budgets: Dict[str, Budget] = {}
        self.compliance_records: Dict[str, ComplianceRecord] = {}
        self.usage_patterns: Dict[str, List] = {}
        self.transfers = []  # Track inter-departmental transfers
        self.is_running = False
        
        # Analytics and ML components
        self.demand_forecaster = None
        self.cost_optimizer = None
        self.performance_analyzer = None
        
    async def initialize(self):
        """Initialize the professional-grade agent with comprehensive data"""
        await self._load_locations()
        await self._load_users()
        await self._load_enhanced_inventory()
        await self._load_enhanced_suppliers()
        await self._load_budgets()
        await self._load_sample_transfers()
        await self._initialize_analytics_engine()
        
        # Create realistic alerts for demo
        await self._create_realistic_alerts()
        # Clear alerts and create critical situations for testing
        self.alerts = []  # Clear existing alerts
        await self._create_critical_situations()
        
        self.logger.info("Professional Supply Inventory Agent initialized with realistic alerts")
    
    async def _load_locations(self):
        """Load hospital locations and departments"""
        self.locations = {
            "ICU": {
                "name": "Intensive Care Unit",
                "type": "patient_care",
                "capacity": 50,
                "head": "Dr. Sarah Johnson",
                "contact": "icu@hospital.com"
            },
            "ER": {
                "name": "Emergency Room",
                "type": "emergency",
                "capacity": 100,
                "head": "Dr. Michael Brown",
                "contact": "er@hospital.com"
            },
            "SURGERY": {
                "name": "Operating Theaters",
                "type": "surgical",
                "capacity": 30,
                "head": "Dr. Emily Davis",
                "contact": "surgery@hospital.com"
            },
            "PHARMACY": {
                "name": "Central Pharmacy",
                "type": "pharmacy",
                "capacity": 200,
                "head": "PharmD John Smith",
                "contact": "pharmacy@hospital.com"
            },
            "WAREHOUSE": {
                "name": "Central Warehouse",
                "type": "storage",
                "capacity": 1000,
                "head": "Manager Lisa Wilson",
                "contact": "warehouse@hospital.com"
            },
            "LAB": {
                "name": "Laboratory",
                "type": "diagnostics",
                "capacity": 75,
                "head": "Dr. Robert Taylor",
                "contact": "lab@hospital.com"
            }
        }
    
    async def _load_users(self):
        """Load system users with role-based permissions"""
        self.users = {
            "admin001": User(
                user_id="admin001",
                username="admin",
                email="admin@hospital.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                department="IT",
                permissions=["*"],  # All permissions
                is_active=True,
                created_date=datetime.now(),
                last_login=None
            ),
            "inv001": User(
                user_id="inv001",
                username="inventory_manager",
                email="inventory@hospital.com",
                full_name="Jane Doe",
                role=UserRole.INVENTORY_MANAGER,
                department="Supply Chain",
                permissions=[
                    "inventory.read", "inventory.write", "alerts.manage",
                    "procurement.create", "reports.generate"
                ],
                is_active=True,
                created_date=datetime.now(),
                last_login=None
            ),
            "pharm001": User(
                user_id="pharm001",
                username="pharmacist",
                email="pharmacist@hospital.com",
                full_name="PharmD John Smith",
                role=UserRole.PHARMACIST,
                department="Pharmacy",
                permissions=[
                    "pharmacy.read", "pharmacy.write", "medication.dispense",
                    "compliance.view"
                ],
                is_active=True,
                created_date=datetime.now(),
                last_login=None
            )
        }
        
    async def _load_enhanced_inventory(self):
        """Load enhanced inventory with multi-location and batch tracking"""
        # Sample enhanced inventory items
        sample_items = []
        
        # Surgical Gloves with multi-location and batch tracking
        gloves_locations = {
            "ICU": LocationStock("ICU", "Intensive Care Unit", 15, 2, 10, 50),
            "ER": LocationStock("ER", "Emergency Room", 20, 3, 15, 75),
            "SURGERY": LocationStock("SURGERY", "Operating Theaters", 25, 5, 20, 100),
            "WAREHOUSE": LocationStock("WAREHOUSE", "Central Warehouse", 200, 0, 100, 500)
        }
        
        gloves_batches = [
            InventoryBatch(
                batch_id="GLV-2024-001",
                lot_number="GL240115",
                manufacture_date=datetime(2024, 1, 15),
                expiry_date=datetime(2026, 1, 15),
                quantity=120,
                supplier_id="SUP001",
                quality_status=QualityStatus.APPROVED,
                received_date=datetime(2024, 2, 1),
                cost_per_unit=12.50,
                storage_conditions="Room temperature, dry",
                certificates=["FDA-510K", "CE-Mark"]
            ),
            InventoryBatch(
                batch_id="GLV-2024-002",
                lot_number="GL240220",
                manufacture_date=datetime(2024, 2, 20),
                expiry_date=datetime(2026, 2, 20),
                quantity=140,
                supplier_id="SUP001",
                quality_status=QualityStatus.APPROVED,
                received_date=datetime(2024, 3, 5),
                cost_per_unit=12.75,
                storage_conditions="Room temperature, dry",
                certificates=["FDA-510K", "CE-Mark"]
            )
        ]
        
        surgical_gloves = SupplyItem(
            id="MED001",
            name="Surgical Gloves (Box of 100)",
            description="Sterile latex-free surgical gloves, powder-free",
            category=SupplyCategory.PPE,
            sku="SG-100-LF",
            manufacturer="MedGlove Corp",
            model_number="SG-100",
            unit_of_measure="box",
            unit_cost=12.62,
            reorder_point=50,
            reorder_quantity=200,
            abc_classification="A",
            criticality_level="Critical",
            storage_requirements="Dry, room temperature",
            regulatory_info={"FDA_approved": True, "CE_marked": True},
            supplier_id="SUP001",
            alternative_suppliers=["SUP004", "SUP005"],
            last_updated=datetime.now(),
            created_by="admin001",
            locations=gloves_locations,
            batches=gloves_batches,
            usage_history=[]
        )
        
        # IV Bags with enhanced tracking
        iv_locations = {
            "ICU": LocationStock("ICU", "Intensive Care Unit", 8, 1, 5, 30),
            "ER": LocationStock("ER", "Emergency Room", 12, 2, 8, 40),
            "PHARMACY": LocationStock("PHARMACY", "Central Pharmacy", 30, 0, 25, 150),
            "WAREHOUSE": LocationStock("WAREHOUSE", "Central Warehouse", 150, 0, 75, 200)
        }
        
        iv_batches = [
            InventoryBatch(
                batch_id="IV-2024-001",
                lot_number="IV240310",
                manufacture_date=datetime(2024, 3, 10),
                expiry_date=datetime(2025, 9, 10),
                quantity=200,
                supplier_id="SUP002",
                quality_status=QualityStatus.APPROVED,
                received_date=datetime(2024, 3, 20),
                cost_per_unit=8.75,
                storage_conditions="Room temperature",
                certificates=["USP-NF", "FDA-Approved"]
            )
        ]
        
        iv_bags = SupplyItem(
            id="MED002",
            name="IV Bags (1000ml)",
            description="Sterile 0.9% Sodium Chloride injection",
            category=SupplyCategory.MEDICAL_SUPPLIES,
            sku="IV-1000-NS",
            manufacturer="FluidTech Inc",
            model_number="NS-1000",
            unit_of_measure="bag",
            unit_cost=8.75,
            reorder_point=30,
            reorder_quantity=100,
            abc_classification="A",
            criticality_level="Critical",
            storage_requirements="Room temperature",
            regulatory_info={"FDA_approved": True, "USP_compliant": True},
            supplier_id="SUP002",
            alternative_suppliers=["SUP006"],
            last_updated=datetime.now(),
            created_by="admin001",
            locations=iv_locations,
            batches=iv_batches,
            usage_history=[]
        )
        
        # Store enhanced items - EXPANDED INVENTORY
        enhanced_items = {}
        enhanced_items[surgical_gloves.id] = surgical_gloves
        enhanced_items[iv_bags.id] = iv_bags
        
        # Add more comprehensive inventory items
        additional_items = [
            # Pharmaceuticals
            {
                "id": "MED003", "name": "Paracetamol 500mg (100 tablets)", "category": SupplyCategory.PHARMACEUTICALS,
                "sku": "PAR-500-100", "unit_cost": 8.50, "reorder_point": 20, "reorder_quantity": 100,
                "locations": {"PHARMACY": 45, "ICU": 5, "ER": 8, "WAREHOUSE": 200}
            },
            {
                "id": "MED004", "name": "Morphine 10mg/ml (10ml vial)", "category": SupplyCategory.PHARMACEUTICALS,
                "sku": "MOR-10-10", "unit_cost": 25.75, "reorder_point": 15, "reorder_quantity": 50,
                "locations": {"PHARMACY": 25, "ICU": 10, "ER": 12, "SURGERY": 8}
            },
            
            # PPE and Surgical Supplies
            {
                "id": "MED005", "name": "N95 Respirator Masks (20 pack)", "category": SupplyCategory.PPE,
                "sku": "N95-20PK", "unit_cost": 18.90, "reorder_point": 25, "reorder_quantity": 150,
                "locations": {"ICU": 30, "ER": 40, "SURGERY": 25, "WAREHOUSE": 180}
            },
            {
                "id": "MED006", "name": "Surgical Masks (50 pack)", "category": SupplyCategory.PPE,
                "sku": "SM-50PK", "unit_cost": 12.25, "reorder_point": 30, "reorder_quantity": 200,
                "locations": {"ICU": 25, "ER": 35, "SURGERY": 40, "WAREHOUSE": 250}
            },
            {
                "id": "MED007", "name": "Disposable Syringes 10ml (100 pack)", "category": SupplyCategory.MEDICAL_SUPPLIES,
                "sku": "SYR-10ML-100", "unit_cost": 22.50, "reorder_point": 20, "reorder_quantity": 80,
                "locations": {"ICU": 15, "ER": 25, "PHARMACY": 35, "WAREHOUSE": 120}
            },
            {
                "id": "MED008", "name": "Sterile Gauze Pads 4x4 (200 pack)", "category": SupplyCategory.MEDICAL_SUPPLIES,
                "sku": "GAU-4X4-200", "unit_cost": 15.80, "reorder_point": 25, "reorder_quantity": 100,
                "locations": {"ICU": 20, "ER": 30, "SURGERY": 40, "WAREHOUSE": 150}
            },
            
            # Laboratory Supplies
            {
                "id": "LAB001", "name": "Blood Collection Tubes (100 pack)", "category": SupplyCategory.LABORATORY,
                "sku": "BCT-100PK", "unit_cost": 35.60, "reorder_point": 15, "reorder_quantity": 60,
                "locations": {"LAB": 40, "ER": 10, "ICU": 8, "WAREHOUSE": 80}
            },
            {
                "id": "LAB002", "name": "Urine Collection Cups (50 pack)", "category": SupplyCategory.LABORATORY,
                "sku": "UCC-50PK", "unit_cost": 18.25, "reorder_point": 20, "reorder_quantity": 75,
                "locations": {"LAB": 35, "ER": 15, "WAREHOUSE": 100}
            },
            
            # Emergency Supplies
            {
                "id": "EMG001", "name": "Emergency Crash Cart Medications Kit", "category": SupplyCategory.EMERGENCY,
                "sku": "ECC-MED-KIT", "unit_cost": 285.00, "reorder_point": 3, "reorder_quantity": 10,
                "locations": {"ER": 5, "ICU": 4, "SURGERY": 2, "WAREHOUSE": 12}
            },
            {
                "id": "EMG002", "name": "Defibrillator Pads (Adult)", "category": SupplyCategory.EMERGENCY,
                "sku": "DEF-PAD-ADT", "unit_cost": 45.50, "reorder_point": 10, "reorder_quantity": 40,
                "locations": {"ER": 15, "ICU": 12, "SURGERY": 8, "WAREHOUSE": 50}
            },
            
            # Surgical Supplies
            {
                "id": "SUR001", "name": "Surgical Drapes Sterile (10 pack)", "category": SupplyCategory.SURGICAL,
                "sku": "SD-STER-10", "unit_cost": 65.75, "reorder_point": 12, "reorder_quantity": 50,
                "locations": {"SURGERY": 25, "WAREHOUSE": 75}
            },
            {
                "id": "SUR002", "name": "Suture Kit Assorted (20 pack)", "category": SupplyCategory.SURGICAL,
                "sku": "SUT-AST-20", "unit_cost": 125.90, "reorder_point": 8, "reorder_quantity": 30,
                "locations": {"SURGERY": 18, "ER": 10, "WAREHOUSE": 45}
            },
            
            # Consumables
            {
                "id": "CON001", "name": "Disposable Bed Sheets (50 pack)", "category": SupplyCategory.CONSUMABLES,
                "sku": "BED-SHT-50", "unit_cost": 28.40, "reorder_point": 20, "reorder_quantity": 80,
                "locations": {"ICU": 25, "ER": 20, "SURGERY": 15, "WAREHOUSE": 120}
            },
            {
                "id": "CON002", "name": "Patient Gowns Disposable (25 pack)", "category": SupplyCategory.CONSUMABLES,
                "sku": "PAT-GWN-25", "unit_cost": 32.15, "reorder_point": 15, "reorder_quantity": 60,
                "locations": {"ICU": 20, "ER": 25, "SURGERY": 18, "WAREHOUSE": 90}
            },
            
            # Additional Pharmaceuticals
            {
                "id": "MED009", "name": "Antibiotics - Amoxicillin 500mg (30 caps)", "category": SupplyCategory.PHARMACEUTICALS,
                "sku": "AMX-500-30", "unit_cost": 15.75, "reorder_point": 25, "reorder_quantity": 100,
                "locations": {"PHARMACY": 60, "ICU": 8, "ER": 12, "WAREHOUSE": 150}
            },
            {
                "id": "MED010", "name": "Insulin Pens (5 pack)", "category": SupplyCategory.PHARMACEUTICALS,
                "sku": "INS-PEN-5", "unit_cost": 95.80, "reorder_point": 10, "reorder_quantity": 40,
                "locations": {"PHARMACY": 20, "ICU": 8, "ER": 5, "WAREHOUSE": 60}
            }
        ]
        
        # Create SupplyItem objects for additional items
        for idx, item_data in enumerate(additional_items):
            locations_dict = {}
            for loc_name, quantity in item_data["locations"].items():
                locations_dict[loc_name] = LocationStock(
                    location_id=loc_name,
                    location_name=loc_name,
                    current_quantity=quantity,
                    reserved_quantity=max(1, quantity // 20),  # 5% reserved
                    minimum_threshold=item_data["reorder_point"],
                    maximum_capacity=quantity * 3
                )
            # Create sample batch for each item
            batch = InventoryBatch(
                batch_id=f"{item_data['id']}-2024-001",
                lot_number=f"{item_data['sku']}-240101",
                manufacture_date=datetime(2024, 1, 1),
                expiry_date=datetime(2025, 12, 31),
                quantity=sum(item_data["locations"].values()),
                supplier_id="SUP001",
                quality_status=QualityStatus.APPROVED,
                received_date=datetime(2024, 2, 1),
                cost_per_unit=item_data["unit_cost"],
                storage_conditions="Standard storage",
                certificates=["FDA-Approved"]
            )
            # Assign a unique daily_consumption value for each item using the index
            unique_daily_consumption = 10 + idx * 7
            supply_item = SupplyItem(
                id=item_data["id"],
                name=item_data["name"],
                description=f"Hospital supply item: {item_data['name']}",
                category=item_data["category"],
                sku=item_data["sku"],
                manufacturer="Medical Supplies Corp",
                model_number=item_data["sku"],
                unit_of_measure="pack" if "pack" in item_data["name"] else "unit",
                unit_cost=item_data["unit_cost"],
                reorder_point=item_data["reorder_point"],
                reorder_quantity=item_data["reorder_quantity"],
                abc_classification="A" if item_data["unit_cost"] > 50 else "B" if item_data["unit_cost"] > 20 else "C",
                criticality_level="Critical" if "Emergency" in item_data["name"] or "Morphine" in item_data["name"] else "High" if item_data["unit_cost"] > 50 else "Medium",
                storage_requirements="Standard storage conditions",
                regulatory_info={"FDA_approved": True},
                supplier_id="SUP001",
                alternative_suppliers=["SUP002"],
                last_updated=datetime.now(),
                created_by="admin001",
                locations=locations_dict,
                batches=[batch],
                usage_history=[],
                daily_consumption=unique_daily_consumption
            )
            enhanced_items[item_data["id"]] = supply_item
        
        self.inventory = enhanced_items
    
    async def _load_enhanced_suppliers(self):
        """Load enhanced supplier information with performance tracking"""
        self.suppliers = {
            "SUP001": Supplier(
                supplier_id="SUP001",
                name="MedSupply Corporation",
                contact_person="Sarah Johnson",
                email="orders@medsupply.com",
                phone="+1-555-0123",
                address="123 Medical Plaza, Healthcare City, HC 12345",
                tax_id="TAX123456789",
                payment_terms="Net 30",
                lead_time_days=3,
                minimum_order_value=500.0,
                reliability_score=0.95,
                quality_rating=0.92,
                delivery_performance=0.88,
                price_competitiveness=0.85,
                certifications=["ISO-13485", "FDA-Registered"],
                preferred_categories=[SupplyCategory.PPE, SupplyCategory.SURGICAL],
                contract_start_date=datetime(2024, 1, 1),
                contract_end_date=datetime(2026, 12, 31),
                is_active=True
            ),
            "SUP002": Supplier(
                supplier_id="SUP002",
                name="Healthcare Solutions Inc",
                contact_person="Michael Brown",
                email="procurement@healthsol.com",
                phone="+1-555-0456",
                address="456 Healthcare Blvd, Medical District, MD 67890",
                tax_id="TAX987654321",
                payment_terms="Net 45",
                lead_time_days=5,
                minimum_order_value=1000.0,
                reliability_score=0.88,
                quality_rating=0.90,
                delivery_performance=0.85,
                price_competitiveness=0.88,
                certifications=["ISO-9001", "GMP-Certified"],
                preferred_categories=[SupplyCategory.MEDICAL_SUPPLIES, SupplyCategory.PHARMACEUTICALS],
                contract_start_date=datetime(2024, 1, 1),
                contract_end_date=datetime(2025, 12, 31),
                is_active=True
            )
        }
    
    async def _load_budgets(self):
        """Load department budget information"""
        self.budgets = {
            "ICU": Budget(
                budget_id="BUD-ICU-2025",
                department="ICU",
                fiscal_year="2025",
                total_budget=250000.0,
                allocated_budget=200000.0,
                spent_amount=45000.0,
                committed_amount=15000.0,
                category_allocations={
                    "PPE": 50000.0,
                    "Medical Supplies": 80000.0,
                    "Pharmaceuticals": 70000.0
                }
            ),
            "ER": Budget(
                budget_id="BUD-ER-2025",
                department="ER",
                fiscal_year="2025",
                total_budget=300000.0,
                allocated_budget=250000.0,
                spent_amount=60000.0,
                committed_amount=20000.0,
                category_allocations={
                    "PPE": 60000.0,
                    "Medical Supplies": 100000.0,
                    "Emergency Supplies": 90000.0
                }
            )
        }
    
    async def _initialize_analytics_engine(self):
        """Initialize advanced analytics and ML components"""
        # Initialize demand forecasting
        # Initialize cost optimization
        # Initialize performance analytics
        self.logger.info("Analytics engine initialized")
        
    async def _load_sample_transfers(self):
        """Load sample transfer requests for demonstration"""
        sample_transfers = [
            TransferRequest(
                transfer_id="TR-001",
                item_id="ITEM-001",
                from_location="WAREHOUSE", 
                to_location="ICU",
                quantity=50,
                requested_by="user123",
                requested_date=datetime.now() - timedelta(days=2),
                status=TransferStatus.COMPLETED,
                priority="HIGH",
                reason="Emergency restocking for ICU surge",
                approved_by="manager456",
                completed_date=datetime.now() - timedelta(days=1)
            ),
            TransferRequest(
                transfer_id="TR-002",
                item_id="ITEM-002",
                from_location="ICU",
                to_location="ER", 
                quantity=25,
                requested_by="user789",
                requested_date=datetime.now() - timedelta(hours=6),
                status=TransferStatus.IN_TRANSIT,
                priority="MEDIUM", 
                reason="Routine redistribution",
                approved_by="manager456",
                completed_date=None
            ),
            TransferRequest(
                transfer_id="TR-003",
                item_id="ITEM-003",
                from_location="WAREHOUSE",
                to_location="SURGERY",
                quantity=30,
                requested_by="user456",
                requested_date=datetime.now() - timedelta(hours=2),
                status=TransferStatus.PENDING,
                priority="LOW",
                reason="Scheduled maintenance restocking",
                approved_by=None,
                completed_date=None
            )
        ]
        
        for transfer in sample_transfers:
            self.transfer_requests[transfer.transfer_id] = transfer

    async def transfer_inventory(self, item_id: str, from_location: str, to_location: str, 
                                quantity: int, requested_by: str, reason: str) -> TransferRequest:
        """Transfer inventory between locations with approval workflow"""
        transfer_id = f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        transfer_request = TransferRequest(
            transfer_id=transfer_id,
            item_id=item_id,
            from_location=from_location,
            to_location=to_location,
            quantity=quantity,
            requested_by=requested_by,
            requested_date=datetime.now(),
            status=TransferStatus.PENDING,
            priority="medium",
            reason=reason
        )
        
        # Check if transfer is valid
        item = self.inventory.get(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")
            
        from_stock = item.get_location_stock(from_location)
        if not from_stock or from_stock.available_quantity < quantity:
            raise ValueError(f"Insufficient stock at {from_location}")
        
        # Auto-approve for certain roles or small quantities
        user = self.users.get(requested_by)
        if (user and user.role in [UserRole.INVENTORY_MANAGER, UserRole.ADMIN] 
            and quantity <= 20):
            await self._execute_transfer(transfer_request)
        else:
            # Require approval for large transfers
            transfer_request.status = TransferStatus.PENDING
            
        self.transfer_requests[transfer_id] = transfer_request
        await self._add_audit_log("transfer_requested", requested_by, item_id, 
                                 {"transfer_id": transfer_id, "quantity": quantity})
        
        return transfer_request
    
    async def _execute_transfer(self, transfer_request: TransferRequest):
        """Execute approved transfer"""
        item = self.inventory[transfer_request.item_id]
        
        # Update quantities
        from_location = item.locations[transfer_request.from_location]
        to_location = item.locations[transfer_request.to_location]
        
        from_location.current_quantity -= transfer_request.quantity
        to_location.current_quantity += transfer_request.quantity
        
        transfer_request.status = TransferStatus.COMPLETED
        transfer_request.completed_date = datetime.now()
        
        self.logger.info(f"Transfer completed: {transfer_request.transfer_id}")
    
    async def update_inventory_with_audit(self, item_id: str, location: str, 
                                        quantity_change: int, user_id: str, reason: str):
        """Update inventory with comprehensive audit trail"""
        item = self.inventory.get(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")
            
        location_stock = item.get_location_stock(location)
        if not location_stock:
            raise ValueError(f"Location {location} not found for item {item_id}")
        
        # Record before state
        before_state = {
            "quantity": location_stock.current_quantity,
            "available": location_stock.available_quantity
        }
        
        # Update quantity
        location_stock.current_quantity += quantity_change
        item.last_updated = datetime.now()
        
        # Record after state
        after_state = {
            "quantity": location_stock.current_quantity,
            "available": location_stock.available_quantity
        }
        
        # Add audit log
        await self._add_audit_log("inventory_updated", user_id, item_id, 
                                 {"quantity_change": quantity_change, "reason": reason,
                                  "location": location}, before_state, after_state)
        
        # Check for alerts
        await self._check_inventory_levels()
        
        self.logger.info(f"Inventory updated: {item.name} at {location}, change: {quantity_change}")
    
    async def _add_audit_log(self, action: str, user_id: str, item_id: Optional[str] = None,
                           details: Optional[Dict] = None, before_state: Optional[Dict] = None,
                           after_state: Optional[Dict] = None):
        """Add comprehensive audit log entry"""
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            item_id=item_id,
            location=details.get("location") if details else None,
            details=details or {},
            ip_address="127.0.0.1",  # In real implementation, get from request
            user_agent="System",
            before_state=before_state,
            after_state=after_state
        )
        
        self.audit_logs.append(log_entry)
        
        # Keep only last 10000 logs in memory
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    async def create_purchase_order_professional(self, items: List[Dict], 
                                               created_by: str, department: str,
                                               urgency: str = "normal") -> PurchaseOrder:
        """Create professional purchase order with approval workflow"""
        po_id = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        po_number = f"PO-{datetime.now().year}-{len(self.purchase_orders) + 1:04d}"
        
        # Group items by supplier
        supplier_items = {}
        for item_data in items:
            item = self.inventory.get(item_data["item_id"])
            if item:
                supplier_id = item.supplier_id
                if supplier_id not in supplier_items:
                    supplier_items[supplier_id] = []
                supplier_items[supplier_id].append(item_data)
        
        # Create PO for the main supplier (simplified - in real system, create multiple POs)
        main_supplier = list(supplier_items.keys())[0]
        supplier = self.suppliers[main_supplier]
        
        po_items = []
        total_amount = 0
        
        for item_data in supplier_items[main_supplier]:
            item = self.inventory[item_data["item_id"]]
            quantity = item_data["quantity"]
            unit_price = item.unit_cost
            total_price = quantity * unit_price
            
            po_item = PurchaseOrderItem(
                item_id=item.id,
                item_name=item.name,
                sku=item.sku,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                specification=item.description,
                delivery_location="WAREHOUSE",
                urgency_level=urgency
            )
            po_items.append(po_item)
            total_amount += total_price
        
        # Determine required date based on urgency
        urgency_days = {"urgent": 1, "high": 3, "normal": 7, "low": 14}
        required_date = datetime.now() + timedelta(days=urgency_days.get(urgency, 7))
        
        purchase_order = PurchaseOrder(
            po_id=po_id,
            po_number=po_number,
            supplier_id=main_supplier,
            created_by=created_by,
            created_date=datetime.now(),
            required_date=required_date,
            status=PurchaseOrderStatus.DRAFT,
            total_amount=total_amount,
            currency="USD",
            payment_terms=supplier.payment_terms,
            delivery_address=self.locations["WAREHOUSE"]["name"],
            items=po_items,
            approval_workflow=[],
            delivery_tracking={},
            invoice_details=None,
            notes=f"Auto-generated PO for {department} department"
        )
        
        # Check budget availability
        budget = self.budgets.get(department)
        if budget and budget.available_budget < total_amount:
            purchase_order.status = PurchaseOrderStatus.PENDING_APPROVAL
            purchase_order.notes += " - Requires budget approval"
        
        self.purchase_orders[po_id] = purchase_order
        
        await self._add_audit_log("purchase_order_created", created_by, None,
                                 {"po_id": po_id, "total_amount": total_amount})
        
        return purchase_order
    
    async def get_enhanced_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data with advanced analytics"""
        # Basic inventory summary
        total_items = len(self.inventory)
        total_locations = len(self.locations)
        low_stock_items = 0
        critical_low_stock = 0
        expired_items = 0
        expiring_soon = 0
        total_value = 0
        
        for item in self.inventory.values():
            if item.is_low_stock:
                low_stock_items += 1
            if item.is_critical_low_stock:
                critical_low_stock += 1
            if item.is_expired_stock_present:
                expired_items += 1
            if item.expiring_soon_batches:
                expiring_soon += 1
            total_value += item.total_value
        
        # Alert summary
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        critical_alerts = len([a for a in active_alerts if a.level == AlertLevel.CRITICAL])
        overdue_alerts = len([a for a in active_alerts if a.is_overdue])
        
        # Purchase order summary
        pending_pos = len([po for po in self.purchase_orders.values() 
                          if po.status == PurchaseOrderStatus.PENDING_APPROVAL])
        overdue_pos = len([po for po in self.purchase_orders.values() if po.is_overdue])
        
        # Budget utilization
        budget_summary = {}
        for dept, budget in self.budgets.items():
            budget_summary[dept] = {
                "utilization": budget.utilization_percentage,
                "available": budget.available_budget,
                "status": "healthy" if budget.utilization_percentage < 80 else "warning"
            }
        
        return {
            "summary": {
                "total_items": total_items,
                "total_locations": total_locations,
                "low_stock_items": low_stock_items,
                "critical_low_stock": critical_low_stock,
                "expired_items": expired_items,
                "expiring_soon": expiring_soon,
                "total_value": round(total_value, 2),
                "critical_alerts": critical_alerts,
                "overdue_alerts": overdue_alerts,
                "pending_pos": pending_pos,
                "overdue_pos": overdue_pos
            },
            "inventory": self._get_inventory_summary(),
            "locations": self.locations,
            "alerts": self._get_alerts_summary(),
            "purchase_orders": self._get_po_summary(),
            "recommendations": self._get_procurement_recommendations(),
            "budget_summary": budget_summary,
            "compliance_status": self._get_compliance_summary(),
            "performance_metrics": self._get_performance_metrics()
        }
    
    def _get_inventory_summary(self) -> List[Dict]:
        """Get detailed inventory summary"""
        inventory_list = []
        for item in self.inventory.values():
            item_summary = {
                "id": item.id,
                "name": item.name,
                "sku": item.sku,
                "category": item.category.value,
                "total_quantity": item.total_quantity,
                "total_available": item.total_available_quantity,
                "total_reserved": item.total_reserved_quantity,
                "minimum_threshold": item.minimum_threshold,
                "maximum_capacity": item.maximum_capacity,
                "is_low_stock": item.is_low_stock,
                "is_critical": item.is_critical_low_stock,
                "has_expired": item.is_expired_stock_present,
                "expiring_soon_count": len(item.expiring_soon_batches),
                "total_value": item.total_value,
                "unit_cost": item.unit_cost,
                "daily_consumption": item.daily_consumption,
                "locations": {}
            }
            
            # Add location details
            for loc_id, location_stock in item.locations.items():
                item_summary["locations"][loc_id] = {
                    "current": location_stock.current_quantity,
                    "available": location_stock.available_quantity,
                    "reserved": location_stock.reserved_quantity,
                    "is_low": location_stock.is_low_stock
                }
            
            inventory_list.append(item_summary)
        
        return inventory_list
    
    def _get_alerts_summary(self) -> List[Dict]:
        """Get alerts summary"""
        return [
            {
                "id": alert.id,
                "item_id": alert.item_id,
                "type": alert.alert_type,
                "level": alert.level.value,
                "message": alert.message,
                "department": alert.department,
                "location": alert.location,
                "created_at": alert.created_at.isoformat(),
                "age_hours": alert.age_hours,
                "is_overdue": alert.is_overdue,
                "assigned_to": alert.assigned_to
            }
            for alert in self.alerts if not alert.resolved
        ]
    
    def _get_po_summary(self) -> List[Dict]:
        """Get purchase orders summary"""
        return [
            {
                "po_id": po.po_id,
                "po_number": po.po_number,
                "supplier": self.suppliers[po.supplier_id].name,
                "status": po.status.value,
                "total_amount": po.total_amount,
                "created_date": po.created_date.isoformat(),
                "required_date": po.required_date.isoformat(),
                "is_overdue": po.is_overdue,
                "items_count": len(po.items)
            }
            for po in self.purchase_orders.values()
        ]
    
    def _get_compliance_summary(self) -> Dict:
        """Get compliance status summary"""
        # In a real system, this would check actual compliance records
        return {
            "total_items_tracked": len(self.inventory),
            "compliant_items": len(self.inventory),  # Simplified
            "pending_reviews": 0,
            "expired_certifications": 0,
            "compliance_score": 100  # Simplified
        }
    
    def _get_performance_metrics(self) -> Dict:
        """Get system performance metrics"""
        return {
            "average_order_fulfillment_time": 3.2,
            "inventory_turnover_rate": 8.5,
            "stockout_incidents": 2,
            "supplier_performance_avg": 89.5,
            "cost_savings_ytd": 15000.0,
            "waste_reduction_percentage": 12.3
        }

    def _get_procurement_recommendations(self):
        """Get procurement recommendations (synchronous version for dashboard)"""
        recommendations = []
        
        for item in self.inventory.values():
            if item.is_low_stock:
                supplier = self.suppliers.get(item.supplier_id)
                if supplier:
                    lead_time = supplier.lead_time_days
                    supplier_name = supplier.name
                else:
                    lead_time = 7
                    supplier_name = 'Unknown Supplier'
                
                # Calculate recommended order quantity
                avg_usage = self._get_average_usage(item.id)
                safety_stock = avg_usage * lead_time * 1.5  # 50% safety margin
                order_quantity = max(
                    item.minimum_threshold * 2,
                    safety_stock - item.current_quantity
                )
                
                recommendations.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'current_quantity': item.current_quantity,
                    'recommended_quantity': int(order_quantity),
                    'supplier': supplier_name,
                    'estimated_cost': order_quantity * item.unit_cost,
                    'urgency': 'high' if item.current_quantity < item.minimum_threshold * 0.5 else 'medium',
                    'reason': 'Critical low stock level' if item.current_quantity < item.minimum_threshold * 0.5 else 'Approaching minimum threshold'
                })
        
        return recommendations
    
    async def _load_sample_inventory(self):
        """Load sample inventory data"""
        sample_items = [
            SupplyItem(
                id="MED001",
                name="Surgical Gloves (Box of 100)",
                category=SupplyCategory.PPE,
                current_quantity=45,
                minimum_threshold=50,
                maximum_capacity=500,
                unit_cost=12.50,
                supplier_id="SUP001",
                expiration_date=datetime.now() + timedelta(days=365),
                location="Storage Room A",
                last_updated=datetime.now()
            ),
            SupplyItem(
                id="MED002",
                name="IV Bags (1000ml)",
                category=SupplyCategory.MEDICAL_SUPPLIES,
                current_quantity=25,
                minimum_threshold=30,
                maximum_capacity=200,
                unit_cost=8.75,
                supplier_id="SUP002",
                expiration_date=datetime.now() + timedelta(days=180),
                location="Pharmacy",
                last_updated=datetime.now()
            ),
            SupplyItem(
                id="MED003",
                name="Paracetamol 500mg",
                category=SupplyCategory.PHARMACEUTICALS,
                current_quantity=150,
                minimum_threshold=100,
                maximum_capacity=1000,
                unit_cost=0.15,
                supplier_id="SUP003",
                expiration_date=datetime.now() + timedelta(days=90),
                location="Pharmacy",
                last_updated=datetime.now()
            ),
            SupplyItem(
                id="MED004",
                name="Surgical Masks (Box of 50)",
                category=SupplyCategory.PPE,
                current_quantity=15,
                minimum_threshold=25,
                maximum_capacity=300,
                unit_cost=7.25,
                supplier_id="SUP001",
                expiration_date=None,
                location="Storage Room B",
                last_updated=datetime.now()
            ),
            SupplyItem(
                id="MED005",
                name="Syringes 10ml",
                category=SupplyCategory.CONSUMABLES,
                current_quantity=80,
                minimum_threshold=100,
                maximum_capacity=500,
                unit_cost=0.85,
                supplier_id="SUP002",
                expiration_date=datetime.now() + timedelta(days=730),
                location="Storage Room A",
                last_updated=datetime.now()
            )
        ]
        
        for item in sample_items:
            self.inventory[item.id] = item
    
    async def _load_suppliers(self):
        """Load supplier information"""
        self.suppliers = {
            "SUP001": {
                "name": "MedSupply Corp",
                "contact": "orders@medsupply.com",
                "phone": "+1-555-0123",
                "lead_time_days": 3,
                "reliability_score": 0.95
            },
            "SUP002": {
                "name": "Healthcare Solutions Inc",
                "contact": "procurement@healthsol.com",
                "phone": "+1-555-0456",
                "lead_time_days": 5,
                "reliability_score": 0.88
            },
            "SUP003": {
                "name": "PharmDistribution Ltd",
                "contact": "orders@pharmdist.com",
                "phone": "+1-555-0789",
                "lead_time_days": 2,
                "reliability_score": 0.92
            }
        }
    
    async def start_monitoring(self):
        """Start the continuous monitoring process"""
        self.is_running = True
        self.logger.info("Starting supply inventory monitoring...")
        
        while self.is_running:
            try:
                # Simulate hospital consumption every cycle
                await self._simulate_hospital_consumption()
                
                await self._check_inventory_levels()
                await self._check_expiration_dates()
                await self._analyze_usage_patterns()
                await self._generate_procurement_recommendations()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # Check every 30 seconds for more frequent updates
                
            except Exception as e:
                self.logger.error(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(30)
    
    async def _check_inventory_levels(self):
        """Check for low stock levels and generate alerts"""
        for item in self.inventory.values():
            if item.is_low_stock:
                # Determine alert level based on how low the stock is
                if item.current_quantity <= item.minimum_threshold * 0.25:
                    level = AlertLevel.CRITICAL
                    message_prefix = "CRITICAL LOW STOCK"
                elif item.current_quantity <= item.minimum_threshold * 0.5:
                    level = AlertLevel.HIGH
                    message_prefix = "HIGH PRIORITY"
                elif item.current_quantity <= item.minimum_threshold * 0.75:
                    level = AlertLevel.MEDIUM
                    message_prefix = "MEDIUM PRIORITY"
                else:
                    level = AlertLevel.LOW
                    message_prefix = "LOW STOCK"
                
                alert = SupplyAlert(
                    id=f"ALERT_{item.id}_{datetime.now().timestamp()}",
                    item_id=item.id,
                    alert_type="LOW_STOCK",
                    level=level,
                    message=f"{message_prefix}: {item.name} is running low. Current: {item.current_quantity}, Minimum: {item.minimum_threshold}",
                    description=f"Inventory alert for {item.name}. Current stock level is below minimum threshold.",
                    created_at=datetime.now(),
                    created_by="System",
                    assigned_to="Supply Manager",
                    department="Supply Chain",
                    location="Multiple Locations" if len(item.locations) > 1 else list(item.locations.keys())[0] if item.locations else "General"
                )
                await self._add_alert(alert)
    
    async def _check_expiration_dates(self):
        """Check for items approaching expiration"""
        for item in self.inventory.values():
            # Check expiration dates in batches
            for batch in item.batches:
                if batch.expiry_date:
                    days_until_expiry = (batch.expiry_date - datetime.now()).days
                    if days_until_expiry <= 7:
                        level = AlertLevel.CRITICAL if days_until_expiry <= 3 else AlertLevel.HIGH
                        alert = SupplyAlert(
                            id=f"ALERT_EXP_{item.id}_{batch.batch_number}_{datetime.now().timestamp()}",
                            item_id=item.id,
                            alert_type="EXPIRATION_WARNING",
                            level=level,
                            message=f"{item.name} batch {batch.batch_number} expires in {days_until_expiry} days",
                            description=f"Expiration warning for {item.name} batch {batch.batch_number}. Item will expire soon and should be used or removed.",
                            created_at=datetime.now(),
                            created_by="System",
                            assigned_to="Pharmacy Staff",
                            department="Pharmacy",
                            location="Multiple Locations" if len(item.locations) > 1 else list(item.locations.keys())[0] if item.locations else "General"
                        )
                        await self._add_alert(alert)
    
    async def _analyze_usage_patterns(self):
        """Analyze usage patterns to predict future needs"""
        # Ensure usage_patterns is properly initialized
        if not isinstance(self.usage_patterns, dict):
            self.usage_patterns = {}
        
        # Simulate usage pattern analysis
        for item_id in self.inventory:
            if item_id not in self.usage_patterns:
                self.usage_patterns[item_id] = []
            
            # Ensure it's a list
            if not isinstance(self.usage_patterns[item_id], list):
                self.usage_patterns[item_id] = []
            
            # Simulate daily usage data
            usage = self._simulate_usage(item_id)
            self.usage_patterns[item_id].append({
                'date': datetime.now().date(),
                'usage': usage
            })
            
            # Keep only last 30 days
            if len(self.usage_patterns[item_id]) > 30:
                self.usage_patterns[item_id] = self.usage_patterns[item_id][-30:]
    
    def _simulate_usage(self, item_id: str) -> int:
        """Simulate daily usage for demo purposes"""
        import random
        
        # Different usage patterns based on item type
        base_usage = {
            "MED001": 15,  # Surgical gloves
            "MED002": 8,   # IV bags
            "MED003": 25,  # Paracetamol
            "MED004": 20,  # Surgical masks
            "MED005": 12   # Syringes
        }
        
        base = base_usage.get(item_id, 5)
        return max(0, int(random.normalvariate(base, base * 0.3)))
    
    async def _generate_procurement_recommendations(self):
        """Generate procurement recommendations based on current state"""
        recommendations = []
        
        for item in self.inventory.values():
            if item.is_low_stock:
                supplier = self.suppliers.get(item.supplier_id)
                lead_time = supplier.lead_time_days if supplier else 7
                
                # Calculate recommended order quantity
                avg_usage = self._get_average_usage(item.id)
                safety_stock = avg_usage * lead_time * 1.5  # 50% safety margin
                order_quantity = max(
                    item.minimum_threshold * 2,
                    safety_stock - item.current_quantity
                )
                
                recommendations.append({
                    'item_id': item.id,
                    'item_name': item.name,
                    'current_quantity': item.current_quantity,
                    'recommended_order': int(order_quantity),
                    'supplier': supplier.name if supplier else 'Unknown',
                    'estimated_cost': order_quantity * item.unit_cost,
                    'urgency': 'HIGH' if item.current_quantity < item.minimum_threshold * 0.5 else 'MEDIUM'
                })
        
        return recommendations
    
    def _get_average_usage(self, item_id: str) -> float:
        """Calculate average daily usage for an item"""
        if item_id not in self.usage_patterns or not self.usage_patterns[item_id]:
            return 5.0  # Default assumption
        
        usages = [day['usage'] for day in self.usage_patterns[item_id]]
        return sum(usages) / len(usages)
    
    async def _add_alert(self, alert: SupplyAlert):
        """Add a new alert if it doesn't already exist"""
        # Check if similar alert already exists and is unresolved
        existing_alert = next(
            (a for a in self.alerts 
             if a.item_id == alert.item_id 
             and a.alert_type == alert.alert_type 
             and not a.resolved), 
            None
        )
        
        if not existing_alert:
            self.alerts.append(alert)
            self.logger.warning(f"New alert: {alert.message}")
    
    async def update_inventory(self, item_id: str, quantity_change: int, reason: str = "Manual update", location_id: str = "General"):
        """Update inventory quantity for an item at a specific location"""
        if item_id in self.inventory:
            item = self.inventory[item_id]
            
            # Ensure location exists
            if location_id not in item.locations:
                # Create new location if it doesn't exist
                item.locations[location_id] = LocationStock(
                    location_id=location_id,
                    current_quantity=0,
                    reserved_quantity=0,
                    minimum_threshold=10,
                    maximum_capacity=1000
                )
            
            # Update the specific location's quantity
            item.locations[location_id].current_quantity += quantity_change
            item.last_updated = datetime.now()
            
            self.logger.info(f"Updated {item_id} at {location_id}: {quantity_change:+d} units ({reason})")
            
            # Log usage if it's a consumption
            if quantity_change < 0:
                # Ensure usage_patterns is properly initialized
                if not isinstance(self.usage_patterns, dict):
                    self.usage_patterns = {}
                
                if item_id not in self.usage_patterns:
                    self.usage_patterns[item_id] = []
                
                # Ensure it's a list
                if not isinstance(self.usage_patterns[item_id], list):
                    self.usage_patterns[item_id] = []
                
                self.usage_patterns[item_id].append({
                    'date': datetime.now().date(),
                    'usage': abs(quantity_change)
                })
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        total_items = len(self.inventory)
        low_stock_items = len([item for item in self.inventory.values() if item.is_low_stock])
        expired_items = len([item for item in self.inventory.values() if item.is_expired])
        critical_alerts = len([alert for alert in self.alerts if alert.level == AlertLevel.CRITICAL and not alert.resolved])
        
        # Calculate total inventory value
        total_value = sum(item.current_quantity * item.unit_cost for item in self.inventory.values())
        
        # Get recent alerts
        recent_alerts = sorted(
            [alert for alert in self.alerts if not alert.resolved],
            key=lambda x: x.created_at,
            reverse=True
        )[:10]
        
        # Get procurement recommendations
        recommendations = await self._generate_procurement_recommendations()
        
        return {
            'summary': {
                'total_items': total_items,
                'low_stock_items': low_stock_items,
                'expired_items': expired_items,
                'critical_alerts': critical_alerts,
                'total_value': round(total_value, 2)
            },
            'inventory': [
                {
                    'id': item.id,
                    'name': item.name,
                    'category': item.category.value,
                    'current_quantity': item.current_quantity,
                    'minimum_threshold': item.minimum_threshold,
                    'location': item.location,
                    'is_low_stock': item.is_low_stock,
                    'is_expired': item.is_expired,
                    'days_until_expiry': item.days_until_expiry,
                    'unit_cost': item.unit_cost,
                    'total_value': round(item.current_quantity * item.unit_cost, 2)
                }
                for item in self.inventory.values()
            ],
            'alerts': [
                {
                    'id': alert.id,
                    'item_id': alert.item_id,
                    'alert_type': alert.alert_type,
                    'level': alert.level.value,
                    'message': alert.message,
                    'created_at': alert.created_at.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in recent_alerts
            ],
            'recommendations': recommendations,
            'suppliers': self.suppliers
        }
    
    async def get_suppliers(self) -> Dict[str, Dict]:
        """Get all suppliers information"""
        return self.suppliers
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        self.is_running = False
        self.logger.info("Supply inventory monitoring stopped")
    
    async def _simulate_hospital_consumption(self):
        """Simulate realistic hospital consumption patterns"""
        import random
        
        # Simulate consumption based on hospital activity
        consumption_rates = {
            "MED001": random.randint(1, 3),  # Surgical Gloves - high usage
            "MED002": random.randint(0, 2),  # IV Bags - moderate usage  
            "MED003": random.randint(0, 1),  # Paracetamol - low usage
            "MED004": random.randint(1, 2),  # Surgical Masks - high usage
            "MED005": random.randint(0, 2),  # Syringes - moderate usage
        }
        
        for item_id, consumption in consumption_rates.items():
            if item_id in self.inventory and consumption > 0:
                item = self.inventory[item_id]
                if item.current_quantity > consumption:
                    # Update consumption at the first available location
                    for location_id, location_stock in item.locations.items():
                        if location_stock.current_quantity >= consumption:
                            location_stock.current_quantity -= consumption
                            self.logger.info(f"Consumed {consumption} units of {item.name} at {location_id}. New quantity: {location_stock.current_quantity}")
                            break
                    else:
                        # If no single location has enough, distribute consumption
                        remaining_consumption = consumption
                        for location_id, location_stock in item.locations.items():
                            if remaining_consumption <= 0:
                                break
                            if location_stock.current_quantity > 0:
                                consumed_here = min(location_stock.current_quantity, remaining_consumption)
                                location_stock.current_quantity -= consumed_here
                                remaining_consumption -= consumed_here
                                self.logger.info(f"Consumed {consumed_here} units of {item.name} at {location_id}. New quantity: {location_stock.current_quantity}")
                    
                    # is_low_stock is automatically calculated as a property

    async def _create_realistic_alerts(self):
        """Create realistic alerts by simulating low stock conditions"""
        try:
            # Reduce stock for some items to trigger alerts
            demo_reductions = [
                ("MED001", "ICU", 40),  # Surgical gloves - reduce to very low
                ("MED003", "PHARMACY", 35),  # Paracetamol - reduce to near threshold
                ("LAB001", "LAB", 25),  # Blood collection tubes - reduce significantly
                ("EMG001", "ER", 3),  # Emergency kit - critical level
                ("MED005", "ICU", 20)  # N95 masks - medium alert
            ]
            
            for item_id, location, reduction in demo_reductions:
                if item_id in self.inventory:
                    item = self.inventory[item_id]
                    if location in item.locations:
                        # Only reduce if we have enough stock
                        if item.locations[location].current_quantity > reduction:
                            item.locations[location].current_quantity -= reduction
                            self.logger.info(f"Demo: Reduced {item.name} stock in {location} by {reduction}")
            
            # Force check inventory levels to generate alerts
            await self._check_inventory_levels()
            
        except Exception as e:
            self.logger.error(f"Error creating realistic alerts: {e}")

    async def _create_critical_situations(self):
        """Create critical stock situations to test critical alerts"""
        try:
            # Create critical situations (total stock below 25% of minimum threshold)
            critical_items = [
                ("MED001", 8),   # Surgical gloves to critical level  
                ("MED004", 12),  # Morphine to critical level
                ("LAB001", 10),  # Blood tubes to critical level
                ("EMG001", 2),   # Emergency kit to critical level
            ]
            
            for item_id, target_total in critical_items:
                if item_id in self.inventory:
                    item = self.inventory[item_id]
                    current_total = item.current_quantity
                    critical_threshold = item.minimum_threshold * 0.25
                    
                    if current_total > target_total and target_total < critical_threshold:
                        # Reduce stock proportionally across all locations
                        reduction_needed = current_total - target_total
                        total_current = sum(loc.current_quantity for loc in item.locations.values())
                        
                        for location_id, location_stock in item.locations.items():
                            if total_current > 0:
                                # Calculate proportional reduction for this location
                                location_reduction = int((location_stock.current_quantity / total_current) * reduction_needed)
                                location_stock.current_quantity = max(0, location_stock.current_quantity - location_reduction)
                        
                        self.logger.info(f"Created critical situation: {item.name} total reduced from {current_total} to {item.current_quantity} (threshold: {critical_threshold})")
            
            # Create LOW level alert scenarios (stock between 75% and 100% of minimum threshold)
            low_priority_items = [
                ("MED010", 0.85),  # Insulin pens to 85% of minimum threshold
                ("CON001", 0.90),  # Disposable bed sheets to 90% of minimum threshold
                ("MED009", 0.80),  # Antibiotics to 80% of minimum threshold
            ]
            
            for item_id, threshold_percentage in low_priority_items:
                if item_id in self.inventory:
                    item = self.inventory[item_id]
                    current_total = item.current_quantity
                    target_total = int(item.minimum_threshold * threshold_percentage)
                    
                    if current_total > target_total:
                        # Reduce stock proportionally across all locations
                        reduction_needed = current_total - target_total
                        total_current = sum(loc.current_quantity for loc in item.locations.values())
                        
                        for location_id, location_stock in item.locations.items():
                            if total_current > 0:
                                # Calculate proportional reduction for this location
                                location_reduction = int((location_stock.current_quantity / total_current) * reduction_needed)
                                location_stock.current_quantity = max(0, location_stock.current_quantity - location_reduction)
                        
                        self.logger.info(f"Created low priority scenario: {item.name} total reduced from {current_total} to {item.current_quantity} (target: {target_total}, min threshold: {item.minimum_threshold})")
            
            # Force check inventory levels to generate alerts
            await self._check_inventory_levels()
            
        except Exception as e:
            self.logger.error(f"Error creating critical situations: {e}")

    def find_departments_with_surplus(self, item_name: str, required_quantity: int) -> List[dict]:
        """Find departments that have surplus stock for an item"""
        surplus_departments = []
        
        # Find the item in inventory
        target_item = None
        for item_id, item in self.inventory.items():
            if item.name == item_name:
                target_item = item
                break
        
        if not target_item:
            return surplus_departments
        
        # Check each location for surplus
        for location_id, location_stock in target_item.locations.items():
            current_stock = location_stock.current_quantity
            min_threshold = location_stock.minimum_threshold
            
            # Check if location has surplus (more than 2x minimum threshold)
            if current_stock > (min_threshold * 2) and current_stock >= required_quantity:
                surplus_departments.append({
                    "department": location_id,
                    "available_stock": current_stock,
                    "min_threshold": min_threshold,
                    "surplus": current_stock - min_threshold,
                    "can_transfer": min(required_quantity, current_stock - min_threshold)
                })
        
        # Sort by surplus amount (highest first)
        surplus_departments.sort(key=lambda x: x["surplus"], reverse=True)
        return surplus_departments
    
    def execute_inter_department_transfer(self, item_name: str, from_dept: str, to_dept: str, quantity: int) -> dict:
        """Execute transfer between departments"""
        try:
            # Validate transfer
            if from_dept not in self.inventory or to_dept not in self.inventory:
                return {"success": False, "message": "Invalid department"}
            
            if item_name not in self.inventory[from_dept]:
                return {"success": False, "message": f"Item {item_name} not found in {from_dept}"}
            
            from_stock = self.inventory[from_dept][item_name]["quantity"]
            from_min = self.inventory[from_dept][item_name]["min_threshold"]
            
            # Ensure transfer doesn't put source department below minimum
            if from_stock - quantity < from_min:
                return {"success": False, "message": "Transfer would put source department below minimum threshold"}
            
            # Execute transfer
            self.inventory[from_dept][item_name]["quantity"] -= quantity
            
            # Add to destination (create item if not exists)
            if item_name not in self.inventory[to_dept]:
                self.inventory[to_dept][item_name] = {
                    "quantity": quantity,
                    "min_threshold": self.inventory[from_dept][item_name]["min_threshold"],
                    "unit_cost": self.inventory[from_dept][item_name]["unit_cost"]
                }
            else:
                self.inventory[to_dept][item_name]["quantity"] += quantity
            
            # Log the transfer
            transfer_log = {
                "transfer_id": f"TRF-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                "item_name": item_name,
                "from_department": from_dept,
                "to_department": to_dept,
                "quantity": quantity,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            }
            
            self.transfers.append(transfer_log)
            
            self.logger.info(f"✅ TRANSFER: Moved {quantity} units of {item_name} from {from_dept} to {to_dept}")
            
            return {
                "success": True, 
                "message": "Transfer completed successfully",
                "transfer_id": transfer_log["transfer_id"],
                "details": transfer_log
            }
            
        except Exception as e:
            self.logger.error(f"❌ Transfer failed: {str(e)}")
            return {"success": False, "message": f"Transfer failed: {str(e)}"}
    
    def get_transfer_history(self, limit: int = 50) -> List[dict]:
        """Get recent transfer history"""
        return self.transfers[-limit:] if self.transfers else []
    
    def check_and_execute_autonomous_transfers(self):
        """Check for low stock and attempt inter-departmental transfers"""
        transfers_executed = []
        
        # Check each item in inventory for low stock in any location
        for item_id, item in self.inventory.items():
            for location_id, location_stock in item.locations.items():
                current_stock = location_stock.current_quantity
                min_threshold = location_stock.minimum_threshold
                
                # If stock is below minimum threshold
                if current_stock < min_threshold:
                    required_quantity = min_threshold - current_stock + 10  # Buffer
                    
                    # Find departments with surplus
                    surplus_depts = self.find_departments_with_surplus(item.name, required_quantity)
                    
                    for surplus_dept in surplus_depts:
                        if surplus_dept["department"] == location_id:
                            continue  # Skip same location
                        
                        transfer_qty = min(required_quantity, surplus_dept["can_transfer"])
                        
                        if transfer_qty > 0:
                            result = self.execute_inter_department_transfer(
                                item.name,
                                surplus_dept["department"],
                                location_id,
                                transfer_qty
                            )
                            
                            if result["success"]:
                                transfers_executed.append(result["details"])
                                required_quantity -= transfer_qty
                                
                                # Update current stock after transfer
                                current_stock += transfer_qty
                                
                                if current_stock >= min_threshold:
                                    break  # Sufficient stock achieved
        
        return transfers_executed
