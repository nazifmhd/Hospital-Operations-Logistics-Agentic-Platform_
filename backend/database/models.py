"""
SQLAlchemy Models for Hospital Supply Inventory Management System
All database tables and relationships
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, DECIMAL, BigInteger, Index, UniqueConstraint,
    CheckConstraint, Table
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
import enum
from .database import Base

# Enums for database fields
class ItemCategory(enum.Enum):
    MEDICAL_SUPPLIES = "medical_supplies"
    PHARMACEUTICALS = "pharmaceuticals" 
    EQUIPMENT = "equipment"
    LABORATORY = "laboratory"
    SURGICAL = "surgical"
    EMERGENCY = "emergency"

class AlertLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class QualityStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    QUARANTINED = "quarantined"

class TransferStatus(enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PurchaseOrderStatus(enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

# Association tables for many-to-many relationships
item_locations = Table(
    'item_locations',
    Base.metadata,
    Column('item_id', String, ForeignKey('inventory_items.id'), primary_key=True),
    Column('location_id', String, ForeignKey('locations.id'), primary_key=True),
    Column('quantity', Integer, default=0),
    Column('reserved_quantity', Integer, default=0),
    Column('minimum_threshold', Integer, default=0),
    Column('maximum_capacity', Integer, default=0),
    Column('last_updated', DateTime, default=func.now(), onupdate=func.now())
)

# Users table
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    department = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    approval_requests = relationship("ApprovalRequest", back_populates="requester")
    transfers_requested = relationship("Transfer", back_populates="requester")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

# Locations table
class Location(Base):
    __tablename__ = 'locations'
    
    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location_type = Column(String(50), nullable=False)  # ICU, ER, PHARMACY, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    capacity_limit = Column(Integer, nullable=True)
    manager_user_id = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    items = relationship("InventoryItem", secondary=item_locations, back_populates="locations")
    transfers_from = relationship("Transfer", foreign_keys="Transfer.from_location_id", back_populates="from_location")
    transfers_to = relationship("Transfer", foreign_keys="Transfer.to_location_id", back_populates="to_location")
    
    def __repr__(self):
        return f"<Location(id='{self.id}', name='{self.name}')>"

# Suppliers table
class Supplier(Base):
    __tablename__ = 'suppliers'
    
    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    lead_time_days = Column(Integer, default=7, nullable=False)
    reliability_score = Column(DECIMAL(3, 2), default=0.0, nullable=False)
    quality_rating = Column(DECIMAL(3, 2), default=0.0, nullable=False)
    delivery_performance = Column(DECIMAL(5, 2), default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    certifications = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    batches = relationship("Batch", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    @property
    def overall_score(self):
        return (self.reliability_score + self.quality_rating + (self.delivery_performance / 100)) / 3
    
    def __repr__(self):
        return f"<Supplier(id='{self.id}', name='{self.name}')>"

# Inventory Items table
class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    
    id = Column(String(20), primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    manufacturer = Column(String(255), nullable=True)
    category = Column(Enum(ItemCategory), nullable=False, index=True)
    unit_cost = Column(DECIMAL(10, 2), nullable=False)
    unit_of_measure = Column(String(20), nullable=False, default='units')
    abc_classification = Column(String(1), nullable=True, index=True)  # A, B, C
    criticality_level = Column(Integer, default=1, nullable=False)  # 1-5 scale
    reorder_point = Column(Integer, default=0, nullable=False)
    economic_order_quantity = Column(Integer, default=0, nullable=False)
    shelf_life_days = Column(Integer, nullable=True)
    storage_requirements = Column(JSON, nullable=True)
    regulatory_info = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    locations = relationship("Location", secondary=item_locations, back_populates="items")
    batches = relationship("Batch", back_populates="item", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="item")
    transfers = relationship("Transfer", back_populates="item")
    audit_logs = relationship("AuditLog", back_populates="item")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('unit_cost >= 0', name='check_unit_cost_positive'),
        CheckConstraint('criticality_level >= 1 AND criticality_level <= 5', name='check_criticality_range'),
        CheckConstraint('reorder_point >= 0', name='check_reorder_point_positive'),
        Index('idx_item_category_active', 'category', 'is_active'),
    )
    
    @property
    def total_quantity(self):
        return sum(batch.quantity for batch in self.batches if batch.is_active)
    
    @property
    def total_value(self):
        return sum(batch.quantity * batch.cost_per_unit for batch in self.batches if batch.is_active)
    
    def __repr__(self):
        return f"<InventoryItem(id='{self.id}', name='{self.name}', category='{self.category.value}')>"

# Batches table
class Batch(Base):
    __tablename__ = 'batches'
    
    id = Column(String(30), primary_key=True)
    item_id = Column(String(20), ForeignKey('inventory_items.id'), nullable=False, index=True)
    supplier_id = Column(String(20), ForeignKey('suppliers.id'), nullable=False)
    lot_number = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost_per_unit = Column(DECIMAL(10, 2), nullable=False)
    manufacture_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    quality_status = Column(Enum(QualityStatus), default=QualityStatus.PENDING, nullable=False)
    storage_location = Column(String(100), nullable=True)
    certificates = Column(JSON, nullable=True)
    received_date = Column(DateTime, default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    item = relationship("InventoryItem", back_populates="batches")
    supplier = relationship("Supplier", back_populates="batches")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_batch_quantity_positive'),
        CheckConstraint('cost_per_unit >= 0', name='check_batch_cost_positive'),
        CheckConstraint('expiry_date IS NULL OR expiry_date > manufacture_date', name='check_expiry_after_manufacture'),
        Index('idx_batch_expiry', 'expiry_date'),
        Index('idx_batch_item_active', 'item_id', 'is_active'),
        UniqueConstraint('item_id', 'lot_number', 'supplier_id', name='uq_batch_lot_supplier'),
    )
    
    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - datetime.now()
            return max(0, delta.days)
        return None
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return datetime.now() > self.expiry_date
        return False
    
    def __repr__(self):
        return f"<Batch(id='{self.id}', lot_number='{self.lot_number}', quantity={self.quantity})>"

# Alerts table
class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(String(30), primary_key=True)
    item_id = Column(String(20), ForeignKey('inventory_items.id'), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    level = Column(Enum(AlertLevel), nullable=False, index=True)
    message = Column(Text, nullable=False)
    location_id = Column(String(20), ForeignKey('locations.id'), nullable=True)
    threshold_value = Column(Integer, nullable=True)
    current_value = Column(Integer, nullable=True)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    assigned_to = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    item = relationship("InventoryItem", back_populates="alerts")
    
    # Constraints
    __table_args__ = (
        Index('idx_alert_unresolved', 'is_resolved', 'level'),
        Index('idx_alert_created', 'created_at'),
    )
    
    @property
    def age_hours(self):
        delta = datetime.now() - self.created_at
        return round(delta.total_seconds() / 3600, 1)
    
    @property
    def is_overdue(self):
        # Consider high/critical alerts overdue after 24/12 hours respectively
        if self.level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            threshold_hours = 12 if self.level == AlertLevel.CRITICAL else 24
            return self.age_hours > threshold_hours
        return False
    
    def __repr__(self):
        return f"<Alert(id='{self.id}', type='{self.alert_type}', level='{self.level.value}')>"

# Transfers table
class Transfer(Base):
    __tablename__ = 'transfers'
    
    id = Column(String(30), primary_key=True)
    item_id = Column(String(20), ForeignKey('inventory_items.id'), nullable=False, index=True)
    from_location_id = Column(String(20), ForeignKey('locations.id'), nullable=False)
    to_location_id = Column(String(20), ForeignKey('locations.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(TransferStatus), default=TransferStatus.PENDING, nullable=False, index=True)
    requested_by = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    approved_by = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    completed_by = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    requested_at = Column(DateTime, default=func.now(), nullable=False)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    item = relationship("InventoryItem", back_populates="transfers")
    from_location = relationship("Location", foreign_keys=[from_location_id], back_populates="transfers_from")
    to_location = relationship("Location", foreign_keys=[to_location_id], back_populates="transfers_to")
    requester = relationship("User", back_populates="transfers_requested")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_transfer_quantity_positive'),
        CheckConstraint('from_location_id != to_location_id', name='check_different_locations'),
        Index('idx_transfer_status_date', 'status', 'requested_at'),
    )
    
    def __repr__(self):
        return f"<Transfer(id='{self.id}', status='{self.status.value}', quantity={self.quantity})>"

# Purchase Orders table
class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    
    id = Column(String(30), primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    supplier_id = Column(String(20), ForeignKey('suppliers.id'), nullable=False)
    status = Column(Enum(PurchaseOrderStatus), default=PurchaseOrderStatus.DRAFT, nullable=False, index=True)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    items = Column(JSON, nullable=False)  # List of items with quantities and prices
    requested_by = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    approved_by = Column(String(50), ForeignKey('users.user_id'), nullable=True)
    department = Column(String(100), nullable=False)
    urgency = Column(String(20), default='medium', nullable=False)
    expected_delivery_date = Column(DateTime, nullable=True)
    actual_delivery_date = Column(DateTime, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_po_amount_positive'),
        Index('idx_po_status_date', 'status', 'created_at'),
    )
    
    def __repr__(self):
        return f"<PurchaseOrder(id='{self.id}', po_number='{self.po_number}', status='{self.status.value}')>"

# Approval Requests table
class ApprovalRequest(Base):
    __tablename__ = 'approval_requests'
    
    id = Column(String(30), primary_key=True)
    request_type = Column(String(50), nullable=False, index=True)
    item_details = Column(JSON, nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    justification = Column(Text, nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    requester_id = Column(String(50), ForeignKey('users.user_id'), nullable=False)
    current_approver = Column(String(50), nullable=True)
    approval_chain = Column(JSON, nullable=True)  # List of required approvers
    approved_by = Column(JSON, nullable=True)  # List of approvers who approved
    rejected_by = Column(String(50), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    emergency = Column(Boolean, default=False, nullable=False)
    related_po_id = Column(String(30), ForeignKey('purchase_orders.id'), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", back_populates="approval_requests")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_approval_amount_positive'),
        Index('idx_approval_status_date', 'status', 'created_at'),
        Index('idx_approval_emergency', 'emergency', 'status'),
    )
    
    def __repr__(self):
        return f"<ApprovalRequest(id='{self.id}', status='{self.status.value}', amount={self.amount})>"

# Budget table
class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(String(30), primary_key=True)
    department = Column(String(100), nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=False)
    total_budget = Column(DECIMAL(15, 2), nullable=False)
    allocated_budget = Column(DECIMAL(15, 2), default=0, nullable=False)
    spent_amount = Column(DECIMAL(15, 2), default=0, nullable=False)
    category_allocations = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_budget >= 0', name='check_total_budget_positive'),
        CheckConstraint('allocated_budget >= 0', name='check_allocated_budget_positive'),
        CheckConstraint('spent_amount >= 0', name='check_spent_amount_positive'),
        CheckConstraint('spent_amount <= allocated_budget', name='check_spent_within_allocated'),
        UniqueConstraint('department', 'fiscal_year', name='uq_budget_dept_year'),
        Index('idx_budget_dept_year', 'department', 'fiscal_year'),
    )
    
    @property
    def available_budget(self):
        return self.allocated_budget - self.spent_amount
    
    @property
    def utilization_percentage(self):
        if self.allocated_budget > 0:
            return (self.spent_amount / self.allocated_budget) * 100
        return 0
    
    def __repr__(self):
        return f"<Budget(department='{self.department}', fiscal_year={self.fiscal_year})>"

# Audit Log table
class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    log_id = Column(String(30), unique=True, nullable=False, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    item_id = Column(String(20), ForeignKey('inventory_items.id'), nullable=True, index=True)
    location = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    item = relationship("InventoryItem", back_populates="audit_logs")
    
    # Constraints
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id='{self.user_id}')>"

# Notifications table
class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(String(30), primary_key=True)
    user_id = Column(String(50), ForeignKey('users.user_id'), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), default='normal', nullable=False)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(String(30), nullable=True)
    action_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        Index('idx_notification_user_unread', 'user_id', 'is_read'),
        Index('idx_notification_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Notification(id='{self.id}', title='{self.title}', is_read={self.is_read})>"
