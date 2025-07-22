"""
Clean Data Models for Hospital Supply Chain Platform
Essential data structures extracted from legacy supply_agent.py for LangGraph integration
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


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
    certificates: List[str]
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expiry_date
    
    @property
    def days_until_expiry(self) -> int:
        return (self.expiry_date - datetime.now()).days


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
        return self.current_quantity <= self.minimum_threshold


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
    """Represents a supply item in the inventory"""
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
    abc_classification: str
    criticality_level: str
    storage_requirements: str
    regulatory_info: Dict[str, Any]
    supplier_id: str
    alternative_suppliers: List[str]
    last_updated: datetime
    created_by: str
    locations: Dict[str, LocationStock]
    batches: List[InventoryBatch]
    usage_history: List[Dict[str, Any]]
    daily_consumption: int = 10
    
    @property
    def total_quantity(self) -> int:
        return sum(location.current_quantity for location in self.locations.values())
    
    @property
    def is_low_stock(self) -> bool:
        return self.total_quantity <= self.reorder_point
    
    def get_location_stock(self, location_id: str) -> Optional[LocationStock]:
        return self.locations.get(location_id)


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
        return "*" in self.permissions or permission in self.permissions


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
    def is_overdue(self) -> bool:
        if self.resolved:
            return False
        hours_since_created = (datetime.now() - self.created_at).total_seconds() / 3600
        return hours_since_created > 24
    
    @property
    def urgency_score(self) -> int:
        score = {"low": 1, "medium": 2, "high": 3, "critical": 4}[self.level.value]
        if self.is_overdue:
            score += 2
        return min(score, 5)


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
    def overall_rating(self) -> float:
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
    po_id: str
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
    def total_items(self) -> int:
        return len(self.items)


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
    def remaining_budget(self) -> float:
        return self.allocated_budget - self.spent_amount - self.committed_amount
    
    @property
    def utilization_rate(self) -> float:
        return (self.spent_amount + self.committed_amount) / self.allocated_budget if self.allocated_budget > 0 else 0


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
        return (self.expiry_date - datetime.now()).days
