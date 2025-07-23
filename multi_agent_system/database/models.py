"""
Enhanced Database Models for Multi-Agent Hospital Operations System
Comprehensive models for Bed Management, Equipment Tracking, Staff Allocation, and Supply Inventory
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Enum, DECIMAL, BigInteger, Index, UniqueConstraint,
    CheckConstraint, Table, Time
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base
from sqlalchemy.sql import func
from datetime import datetime, time
from typing import Optional, List, Dict, Any
import enum

Base = declarative_base()

# Enhanced Enums for Multi-Agent System
class BedStatus(enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"
    MAINTENANCE = "maintenance"
    BLOCKED = "blocked"
    RESERVED = "reserved"

class BedType(enum.Enum):
    STANDARD = "standard"
    ICU = "icu"
    TELEMETRY = "telemetry"
    ISOLATION = "isolation"
    BARIATRIC = "bariatric"
    PEDIATRIC = "pediatric"
    MATERNITY = "maternity"

class PatientAcuity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EquipmentStatus(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    BROKEN = "broken"
    CLEANING = "cleaning"
    CALIBRATION = "calibration"

class EquipmentType(enum.Enum):
    VENTILATOR = "ventilator"
    IV_PUMP = "iv_pump"
    MONITOR = "monitor"
    DEFIBRILLATOR = "defibrillator"
    WHEELCHAIR = "wheelchair"
    TRANSPORT_BED = "transport_bed"
    DIALYSIS = "dialysis"
    ULTRASOUND = "ultrasound"

class StaffRole(enum.Enum):
    NURSE = "nurse"
    DOCTOR = "doctor"
    TECHNICIAN = "technician"
    THERAPIST = "therapist"
    ADMIN = "admin"
    SUPPORT = "support"

class ShiftType(enum.Enum):
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"
    WEEKEND = "weekend"

class StaffStatus(enum.Enum):
    AVAILABLE = "available"
    ON_DUTY = "on_duty"
    BREAK = "break"
    UNAVAILABLE = "unavailable"
    OFF_DUTY = "off_duty"

class AlertLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SupplyCategory(enum.Enum):
    MEDICAL_SUPPLIES = "medical_supplies"
    PHARMACEUTICALS = "pharmaceuticals"
    SURGICAL_INSTRUMENTS = "surgical_instruments"
    PERSONAL_PROTECTIVE_EQUIPMENT = "ppe"
    LABORATORY_SUPPLIES = "laboratory_supplies"
    NUTRITION_SUPPLIES = "nutrition_supplies"
    CLEANING_SUPPLIES = "cleaning_supplies"
    OFFICE_SUPPLIES = "office_supplies"

class SupplyStatus(enum.Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    ORDERED = "ordered"
    RECEIVED = "received"
    EXPIRED = "expired"
    RECALLED = "recalled"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# Association Tables
bed_equipment_association = Table(
    'bed_equipment_associations',
    Base.metadata,
    Column('bed_id', String, ForeignKey('beds.id'), primary_key=True),
    Column('equipment_id', String, ForeignKey('medical_equipment.id'), primary_key=True),
    Column('assigned_at', DateTime, default=func.now())
)

staff_equipment_association = Table(
    'staff_equipment_associations',
    Base.metadata,
    Column('staff_id', String, ForeignKey('staff_members.id'), primary_key=True),
    Column('equipment_id', String, ForeignKey('medical_equipment.id'), primary_key=True),
    Column('assigned_at', DateTime, default=func.now()),
    Column('expected_return', DateTime)
)

# Core Models for Multi-Agent System

class Department(Base):
    """Hospital departments and units"""
    __tablename__ = 'departments'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    floor = Column(Integer)
    building = Column(String(50))
    manager_id = Column(String(50), ForeignKey('staff_members.id'))
    capacity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    specialties = Column(JSON)  # List of medical specialties
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    beds = relationship("Bed", back_populates="department")
    manager = relationship("StaffMember", foreign_keys=[manager_id])
    equipment = relationship("MedicalEquipment", back_populates="department")

class Bed(Base):
    """Hospital beds with enhanced tracking"""
    __tablename__ = 'beds'
    
    id = Column(String(50), primary_key=True)
    number = Column(String(20), nullable=False)
    department_id = Column(String(50), ForeignKey('departments.id'), nullable=False)
    room_number = Column(String(20))
    bed_type = Column(Enum(BedType), nullable=False)
    status = Column(Enum(BedStatus), default=BedStatus.AVAILABLE)
    is_isolation_capable = Column(Boolean, default=False)
    is_bariatric = Column(Boolean, default=False)
    has_telemetry = Column(Boolean, default=False)
    current_patient_id = Column(String(50), ForeignKey('patients.id'), nullable=True)
    last_cleaned = Column(DateTime)
    last_maintenance = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="beds")
    current_patient = relationship("Patient", back_populates="current_bed")
    bed_assignments = relationship("BedAssignment", back_populates="bed")
    equipment = relationship("MedicalEquipment", secondary=bed_equipment_association, back_populates="beds")

class Patient(Base):
    """Patient information for bed and resource allocation"""
    __tablename__ = 'patients'
    
    id = Column(String(50), primary_key=True)
    mrn = Column(String(20), unique=True, nullable=False)  # Medical Record Number
    name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime)
    gender = Column(String(10))
    acuity_level = Column(Enum(PatientAcuity), default=PatientAcuity.LOW)
    admission_date = Column(DateTime, default=func.now())
    discharge_date = Column(DateTime, nullable=True)
    primary_diagnosis = Column(String(200))
    isolation_required = Column(Boolean, default=False)
    isolation_type = Column(String(50))  # contact, droplet, airborne
    allergies = Column(JSON)
    special_needs = Column(JSON)
    emergency_contact = Column(JSON)
    insurance_info = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    current_bed = relationship("Bed", back_populates="current_patient")
    bed_assignments = relationship("BedAssignment", back_populates="patient")
    care_assignments = relationship("CareAssignment", back_populates="patient")

class BedAssignment(Base):
    """Track bed assignment history"""
    __tablename__ = 'bed_assignments'
    
    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=False)
    bed_id = Column(String(50), ForeignKey('beds.id'), nullable=False)
    assigned_by = Column(String(50), ForeignKey('staff_members.id'))
    assigned_at = Column(DateTime, default=func.now())
    discharged_at = Column(DateTime, nullable=True)
    reason = Column(String(200))
    notes = Column(Text)
    
    # Relationships
    patient = relationship("Patient", back_populates="bed_assignments")
    bed = relationship("Bed", back_populates="bed_assignments")
    assigned_by_staff = relationship("StaffMember", foreign_keys=[assigned_by])

class MedicalEquipment(Base):
    """Medical equipment tracking"""
    __tablename__ = 'medical_equipment'
    
    id = Column(String(50), primary_key=True)
    asset_tag = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    equipment_type = Column(Enum(EquipmentType), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.AVAILABLE)
    location_type = Column(String(20))  # "department", "bed", "storage"
    current_location_id = Column(String(50))  # Could be department_id, bed_id, etc.
    department_id = Column(String(50), ForeignKey('departments.id'))
    purchase_date = Column(DateTime)
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    maintenance_interval_days = Column(Integer, default=365)
    warranty_expiry = Column(DateTime)
    is_portable = Column(Boolean, default=True)
    requires_certification = Column(Boolean, default=False)
    cost = Column(DECIMAL(10, 2))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", back_populates="equipment")
    beds = relationship("Bed", secondary=bed_equipment_association, back_populates="equipment")
    staff_assignments = relationship("StaffMember", secondary=staff_equipment_association, back_populates="assigned_equipment")
    maintenance_records = relationship("EquipmentMaintenance", back_populates="equipment")

class EquipmentMaintenance(Base):
    """Equipment maintenance tracking"""
    __tablename__ = 'equipment_maintenance'
    
    id = Column(String(50), primary_key=True)
    equipment_id = Column(String(50), ForeignKey('medical_equipment.id'), nullable=False)
    maintenance_type = Column(String(50))  # preventive, corrective, calibration
    scheduled_date = Column(DateTime)
    completed_date = Column(DateTime)
    performed_by = Column(String(50), ForeignKey('staff_members.id'))
    vendor = Column(String(100))
    cost = Column(DECIMAL(10, 2))
    description = Column(Text)
    parts_used = Column(JSON)
    next_maintenance = Column(DateTime)
    status = Column(String(20), default="scheduled")
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    equipment = relationship("MedicalEquipment", back_populates="maintenance_records")
    technician = relationship("StaffMember", foreign_keys=[performed_by])

class StaffMember(Base):
    """Staff member information and tracking"""
    __tablename__ = 'staff_members'
    
    id = Column(String(50), primary_key=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    role = Column(Enum(StaffRole), nullable=False)
    department_id = Column(String(50), ForeignKey('departments.id'))
    specialties = Column(JSON)  # List of specialties/certifications
    skill_level = Column(Integer, default=1)  # 1-5 scale
    certifications = Column(JSON)
    license_number = Column(String(50))
    license_expiry = Column(DateTime)
    hire_date = Column(DateTime)
    status = Column(Enum(StaffStatus), default=StaffStatus.OFF_DUTY)
    current_shift_id = Column(String(50), ForeignKey('staff_shifts.id'), nullable=True)
    max_patients = Column(Integer, default=6)  # Maximum patient load
    phone = Column(String(20))
    emergency_contact = Column(JSON)
    preferences = Column(JSON)  # Shift preferences, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department", foreign_keys=[department_id])
    current_shift = relationship("StaffShift", foreign_keys=[current_shift_id], overlaps="current_staff")
    care_assignments = relationship("CareAssignment", back_populates="staff_member")
    assigned_equipment = relationship("MedicalEquipment", secondary=staff_equipment_association, back_populates="staff_assignments")

class StaffShift(Base):
    """Staff shift scheduling"""
    __tablename__ = 'staff_shifts'
    
    id = Column(String(50), primary_key=True)
    date = Column(DateTime, nullable=False)
    shift_type = Column(Enum(ShiftType), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    department_id = Column(String(50), ForeignKey('departments.id'))
    required_staff_count = Column(Integer, default=1)
    current_staff_count = Column(Integer, default=0)
    is_critical_shift = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department")
    current_staff = relationship("StaffMember", foreign_keys="StaffMember.current_shift_id")

class CareAssignment(Base):
    """Patient care assignments to staff"""
    __tablename__ = 'care_assignments'
    
    id = Column(String(50), primary_key=True)
    patient_id = Column(String(50), ForeignKey('patients.id'), nullable=False)
    staff_id = Column(String(50), ForeignKey('staff_members.id'), nullable=False)
    assigned_at = Column(DateTime, default=func.now())
    assignment_end = Column(DateTime, nullable=True)
    is_primary = Column(Boolean, default=False)  # Primary vs secondary nurse
    care_level = Column(String(20))  # total, partial, monitoring
    notes = Column(Text)
    
    # Relationships
    patient = relationship("Patient", back_populates="care_assignments")
    staff_member = relationship("StaffMember", back_populates="care_assignments")

class MultiAgentAlert(Base):
    """Enhanced alerts for multi-agent coordination"""
    __tablename__ = 'multi_agent_alerts'
    
    id = Column(String(50), primary_key=True)
    agent_type = Column(String(50), nullable=False)  # bed, equipment, staff, supply
    alert_type = Column(String(50), nullable=False)
    level = Column(Enum(AlertLevel), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    entity_id = Column(String(50))  # bed_id, equipment_id, staff_id, etc.
    entity_type = Column(String(50))
    department_id = Column(String(50), ForeignKey('departments.id'))
    assigned_to = Column(String(50), ForeignKey('staff_members.id'))
    requires_immediate_action = Column(Boolean, default=False)
    escalation_level = Column(Integer, default=0)
    auto_resolve = Column(Boolean, default=False)
    resolution_deadline = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String(50), ForeignKey('staff_members.id'))
    resolved_at = Column(DateTime)
    resolution_notes = Column(Text)
    alert_metadata = Column(JSON)  # Additional alert-specific data
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    department = relationship("Department")
    assigned_staff = relationship("StaffMember", foreign_keys=[assigned_to])
    resolved_by_staff = relationship("StaffMember", foreign_keys=[resolved_by])

class AgentActivity(Base):
    """Track all agent activities for monitoring and optimization"""
    __tablename__ = 'agent_activities'
    
    id = Column(String(50), primary_key=True)
    agent_type = Column(String(50), nullable=False)
    activity_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    entity_id = Column(String(50))
    entity_type = Column(String(50))
    decision_data = Column(JSON)  # The data used to make the decision
    outcome = Column(String(50))  # success, failure, pending
    performance_metrics = Column(JSON)  # Time taken, resources used, etc.
    timestamp = Column(DateTime, default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_agent_activities_agent_type', 'agent_type'),
        Index('idx_agent_activities_timestamp', 'timestamp'),
        Index('idx_agent_activities_entity', 'entity_type', 'entity_id'),
    )

class SupplyItem(Base):
    """Hospital supply inventory items"""
    __tablename__ = 'supply_items'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(Enum(SupplyCategory), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
    manufacturer = Column(String(100))
    model_number = Column(String(50))
    unit_of_measure = Column(String(20), default="each")  # each, box, case, liter, etc.
    unit_cost = Column(DECIMAL(10, 2))
    reorder_point = Column(Integer, default=10)
    max_stock_level = Column(Integer, default=100)
    expiration_required = Column(Boolean, default=False)
    controlled_substance = Column(Boolean, default=False)
    hazardous = Column(Boolean, default=False)
    storage_requirements = Column(JSON)  # temperature, humidity, special conditions
    specifications = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    inventory_locations = relationship("InventoryLocation", back_populates="supply_item")
    purchase_orders = relationship("PurchaseOrderItem", back_populates="supply_item")
    usage_records = relationship("SupplyUsageRecord", back_populates="supply_item")

class InventoryLocation(Base):
    """Inventory storage locations and stock levels"""
    __tablename__ = 'inventory_locations'
    
    id = Column(String(50), primary_key=True)
    supply_item_id = Column(String(50), ForeignKey('supply_items.id'), nullable=False)
    location_name = Column(String(100), nullable=False)  # Main Pharmacy, ICU Supply Room, etc.
    department_id = Column(String(50), ForeignKey('departments.id'))
    current_quantity = Column(Integer, default=0)
    reserved_quantity = Column(Integer, default=0)  # Reserved for scheduled procedures
    available_quantity = Column(Integer, default=0)  # current - reserved
    lot_number = Column(String(50))
    expiration_date = Column(DateTime)
    received_date = Column(DateTime)
    status = Column(Enum(SupplyStatus), default=SupplyStatus.IN_STOCK)
    last_counted = Column(DateTime)
    storage_location = Column(String(100))  # Specific shelf, room, etc.
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supply_item = relationship("SupplyItem", back_populates="inventory_locations")
    department = relationship("Department")

class Supplier(Base):
    """Supplier/vendor information"""
    __tablename__ = 'suppliers'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    contact_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(JSON)  # Street, city, state, zip, country
    payment_terms = Column(String(50))  # Net 30, Net 15, etc.
    lead_time_days = Column(Integer, default=7)
    minimum_order_value = Column(DECIMAL(10, 2))
    preferred_supplier = Column(Boolean, default=False)
    quality_rating = Column(Float, default=5.0)  # 1-5 scale
    delivery_rating = Column(Float, default=5.0)  # 1-5 scale
    price_rating = Column(Float, default=5.0)  # 1-5 scale
    certifications = Column(JSON)  # ISO, FDA, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    supplier_items = relationship("SupplierItem", back_populates="supplier")

class SupplierItem(Base):
    """Supplier-specific item information and pricing"""
    __tablename__ = 'supplier_items'
    
    id = Column(String(50), primary_key=True)
    supplier_id = Column(String(50), ForeignKey('suppliers.id'), nullable=False)
    supply_item_id = Column(String(50), ForeignKey('supply_items.id'), nullable=False)
    supplier_sku = Column(String(50))
    supplier_name = Column(String(200))  # Supplier's name for the item
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    minimum_order_quantity = Column(Integer, default=1)
    pack_size = Column(Integer, default=1)  # Items per pack/case
    lead_time_days = Column(Integer, default=7)
    is_preferred = Column(Boolean, default=False)
    contract_price = Column(DECIMAL(10, 2))
    contract_expiry = Column(DateTime)
    last_price_update = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="supplier_items")
    supply_item = relationship("SupplyItem")

class PurchaseOrder(Base):
    """Purchase orders for supply procurement"""
    __tablename__ = 'purchase_orders'
    
    id = Column(String(50), primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(String(50), ForeignKey('suppliers.id'), nullable=False)
    requested_by = Column(String(50), ForeignKey('staff_members.id'))
    approved_by = Column(String(50), ForeignKey('staff_members.id'))
    department_id = Column(String(50), ForeignKey('departments.id'))
    order_date = Column(DateTime, default=func.now())
    expected_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    priority = Column(String(20), default="normal")  # normal, urgent, emergency
    total_amount = Column(DECIMAL(12, 2), default=0)
    tax_amount = Column(DECIMAL(10, 2), default=0)
    shipping_cost = Column(DECIMAL(10, 2), default=0)
    discount_amount = Column(DECIMAL(10, 2), default=0)
    payment_terms = Column(String(50))
    delivery_address = Column(JSON)
    special_instructions = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    requested_by_staff = relationship("StaffMember", foreign_keys=[requested_by])
    approved_by_staff = relationship("StaffMember", foreign_keys=[approved_by])
    department = relationship("Department")
    order_items = relationship("PurchaseOrderItem", back_populates="purchase_order")

class PurchaseOrderItem(Base):
    """Individual items in purchase orders"""
    __tablename__ = 'purchase_order_items'
    
    id = Column(String(50), primary_key=True)
    purchase_order_id = Column(String(50), ForeignKey('purchase_orders.id'), nullable=False)
    supply_item_id = Column(String(50), ForeignKey('supply_items.id'), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    quantity_received = Column(Integer, default=0)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    line_total = Column(DECIMAL(10, 2), nullable=False)
    expected_delivery = Column(DateTime)
    actual_delivery = Column(DateTime)
    lot_number = Column(String(50))
    expiration_date = Column(DateTime)
    received_by = Column(String(50), ForeignKey('staff_members.id'))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="order_items")
    supply_item = relationship("SupplyItem", back_populates="purchase_orders")
    received_by_staff = relationship("StaffMember", foreign_keys=[received_by])

class SupplyUsageRecord(Base):
    """Track supply usage for consumption analysis"""
    __tablename__ = 'supply_usage_records'
    
    id = Column(String(50), primary_key=True)
    supply_item_id = Column(String(50), ForeignKey('supply_items.id'), nullable=False)
    department_id = Column(String(50), ForeignKey('departments.id'))
    used_by = Column(String(50), ForeignKey('staff_members.id'))
    patient_id = Column(String(50), ForeignKey('patients.id'))
    quantity_used = Column(Integer, nullable=False)
    usage_date = Column(DateTime, default=func.now())
    usage_type = Column(String(50))  # patient_care, maintenance, waste, expired
    procedure_code = Column(String(20))  # Associated medical procedure
    cost_center = Column(String(50))
    lot_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    supply_item = relationship("SupplyItem", back_populates="usage_records")
    department = relationship("Department")
    used_by_staff = relationship("StaffMember", foreign_keys=[used_by])
    patient = relationship("Patient")

class SupplyAlert(Base):
    """Automated alerts for supply management"""
    __tablename__ = 'supply_alerts'
    
    id = Column(String(50), primary_key=True)
    supply_item_id = Column(String(50), ForeignKey('supply_items.id'))
    inventory_location_id = Column(String(50), ForeignKey('inventory_locations.id'))
    alert_type = Column(String(50), nullable=False)  # low_stock, expired, recall, etc.
    severity = Column(Enum(AlertLevel), default=AlertLevel.MEDIUM)
    message = Column(Text, nullable=False)
    threshold_value = Column(Integer)  # The threshold that triggered the alert
    current_value = Column(Integer)    # Current quantity or days until expiry
    auto_resolved = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String(50), ForeignKey('staff_members.id'))
    resolved_at = Column(DateTime)
    resolution_action = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    supply_item = relationship("SupplyItem")
    inventory_location = relationship("InventoryLocation")
    resolved_by_staff = relationship("StaffMember", foreign_keys=[resolved_by])

# Add indexes for performance optimization
Index('idx_beds_status_department', Bed.status, Bed.department_id)
Index('idx_equipment_status_type', MedicalEquipment.status, MedicalEquipment.equipment_type)
Index('idx_staff_status_department', StaffMember.status, StaffMember.department_id)
Index('idx_patients_acuity_active', Patient.acuity_level, Patient.is_active)
