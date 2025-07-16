"""
Advanced Workflow Automation Engine
Handles approval processes, purchase order generation, and supplier integration
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import asyncio


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"


class PurchaseOrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT_TO_SUPPLIER = "sent_to_supplier"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SupplierStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class ApprovalRequest:
    id: str
    request_type: str  # 'purchase_order', 'inventory_transfer', 'budget_request'
    requester_id: str
    item_details: Dict[str, Any]
    amount: float
    justification: str
    created_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    current_approver: Optional[str] = None
    approval_chain: List[str] = field(default_factory=list)
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    comments: List[Dict[str, Any]] = field(default_factory=list)
    deadline: Optional[datetime] = None


@dataclass
class PurchaseOrder:
    id: str
    po_number: str
    requester_id: str
    supplier_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    created_at: datetime
    status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT
    approval_request_id: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    notes: str = ""
    attachments: List[str] = field(default_factory=list)


@dataclass
class Supplier:
    id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    tax_id: str
    status: SupplierStatus = SupplierStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_sync: Optional[datetime] = None
    catalog: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    payment_terms: str = "Net 30"
    lead_time_days: int = 7


class WorkflowEngine:
    def __init__(self):
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.approval_rules = self._setup_approval_rules()
        self.notification_handlers = []
        
    def _setup_approval_rules(self) -> Dict[str, Dict]:
        """Setup approval rules based on amount and type"""
        return {
            "purchase_order": {
                "0-1000": ["department_manager"],
                "1000-5000": ["department_manager", "finance_manager"],
                "5000-10000": ["department_manager", "finance_manager", "director"],
                "10000+": ["department_manager", "finance_manager", "director", "ceo"]
            },
            "inventory_transfer": {
                "any": ["department_manager"]
            },
            "budget_request": {
                "0-2000": ["department_manager"],
                "2000+": ["department_manager", "finance_manager", "director"]
            }
        }

    async def submit_approval_request(self, request_type: str, requester_id: str, 
                                    item_details: Dict, amount: float, justification: str) -> ApprovalRequest:
        """Submit a new approval request"""
        request_id = f"AR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Determine approval chain based on rules
        approval_chain = self._get_approval_chain(request_type, amount)
        
        # Set deadline (72 hours for urgent, 7 days for normal)
        deadline = datetime.now() + timedelta(hours=72 if amount > 5000 else 168)
        
        request = ApprovalRequest(
            id=request_id,
            request_type=request_type,
            requester_id=requester_id,
            item_details=item_details,
            amount=amount,
            justification=justification,
            created_at=datetime.now(),
            approval_chain=approval_chain,
            current_approver=approval_chain[0] if approval_chain else None,
            deadline=deadline
        )
        
        self.approval_requests[request_id] = request
        
        # Trigger notification to first approver
        await self._notify_approver(request)
        
        return request

    async def process_approval(self, request_id: str, approver_id: str, 
                             action: str, comments: str = "") -> ApprovalRequest:
        """Process an approval decision"""
        if request_id not in self.approval_requests:
            raise ValueError(f"Approval request {request_id} not found")
        
        request = self.approval_requests[request_id]
        
        if request.current_approver != approver_id:
            raise ValueError(f"User {approver_id} is not authorized to approve this request")
        
        # Record the approval/rejection
        approval_record = {
            "approver_id": approver_id,
            "action": action,
            "comments": comments,
            "timestamp": datetime.now().isoformat()
        }
        request.approvals.append(approval_record)
        
        if action == "approve":
            # Move to next approver in chain
            current_index = request.approval_chain.index(approver_id)
            if current_index + 1 < len(request.approval_chain):
                request.current_approver = request.approval_chain[current_index + 1]
                await self._notify_approver(request)
            else:
                # All approvals completed
                request.status = ApprovalStatus.APPROVED
                request.current_approver = None
                await self._handle_final_approval(request)
        
        elif action == "reject":
            request.status = ApprovalStatus.REJECTED
            request.current_approver = None
            await self._notify_rejection(request)
        
        return request

    async def create_purchase_order(self, approval_request_id: str, supplier_id: str) -> PurchaseOrder:
        """Create a purchase order from an approved request"""
        if approval_request_id not in self.approval_requests:
            raise ValueError(f"Approval request {approval_request_id} not found")
        
        request = self.approval_requests[approval_request_id]
        if request.status != ApprovalStatus.APPROVED:
            raise ValueError("Cannot create PO from non-approved request")
        
        po_number = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
        po_id = f"PO-{str(uuid.uuid4())[:8].upper()}"
        
        # Convert approval request to PO items
        items = []
        if isinstance(request.item_details, dict):
            if "items" in request.item_details:
                items = request.item_details["items"]
            else:
                items = [request.item_details]
        
        purchase_order = PurchaseOrder(
            id=po_id,
            po_number=po_number,
            requester_id=request.requester_id,
            supplier_id=supplier_id,
            items=items,
            total_amount=request.amount,
            created_at=datetime.now(),
            status=PurchaseOrderStatus.APPROVED,
            approval_request_id=approval_request_id,
            expected_delivery_date=datetime.now() + timedelta(days=self._get_supplier_lead_time(supplier_id))
        )
        
        self.purchase_orders[po_id] = purchase_order
        
        # Auto-send to supplier if configured
        await self._send_po_to_supplier(purchase_order)
        
        return purchase_order

    async def update_po_status(self, po_id: str, new_status: PurchaseOrderStatus, 
                             notes: str = "") -> PurchaseOrder:
        """Update purchase order status"""
        if po_id not in self.purchase_orders:
            raise ValueError(f"Purchase order {po_id} not found")
        
        po = self.purchase_orders[po_id]
        po.status = new_status
        if notes:
            po.notes = f"{po.notes}\n{datetime.now().isoformat()}: {notes}"
        
        if new_status == PurchaseOrderStatus.DELIVERED:
            po.actual_delivery_date = datetime.now()
        
        return po

    async def add_supplier(self, name: str, contact_person: str, email: str, 
                         phone: str, address: str, tax_id: str) -> Supplier:
        """Add a new supplier"""
        supplier_id = f"SUP-{str(uuid.uuid4())[:8].upper()}"
        
        supplier = Supplier(
            id=supplier_id,
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address,
            tax_id=tax_id,
            created_at=datetime.now()
        )
        
        self.suppliers[supplier_id] = supplier
        return supplier

    async def sync_supplier_catalog(self, supplier_id: str, catalog_data: List[Dict]) -> Supplier:
        """Sync supplier catalog data"""
        if supplier_id not in self.suppliers:
            raise ValueError(f"Supplier {supplier_id} not found")
        
        supplier = self.suppliers[supplier_id]
        supplier.catalog = catalog_data
        supplier.last_sync = datetime.now()
        
        return supplier

    def _get_approval_chain(self, request_type: str, amount: float) -> List[str]:
        """Determine approval chain based on type and amount"""
        rules = self.approval_rules.get(request_type, {})
        
        if request_type == "purchase_order":
            if amount <= 1000:
                return rules.get("0-1000", [])
            elif amount <= 5000:
                return rules.get("1000-5000", [])
            elif amount <= 10000:
                return rules.get("5000-10000", [])
            else:
                return rules.get("10000+", [])
        
        elif request_type == "budget_request":
            if amount <= 2000:
                return rules.get("0-2000", [])
            else:
                return rules.get("2000+", [])
        
        else:
            return rules.get("any", ["department_manager"])

    def _get_supplier_lead_time(self, supplier_id: str) -> int:
        """Get supplier lead time in days"""
        if supplier_id in self.suppliers:
            return self.suppliers[supplier_id].lead_time_days
        return 7  # Default

    async def _notify_approver(self, request: ApprovalRequest):
        """Send notification to current approver"""
        # In a real system, this would send email/SMS
        print(f"Notification: Approval request {request.id} sent to {request.current_approver}")

    async def _handle_final_approval(self, request: ApprovalRequest):
        """Handle final approval completion"""
        print(f"Approval request {request.id} fully approved")

    async def _notify_rejection(self, request: ApprovalRequest):
        """Handle rejection notification"""
        print(f"Approval request {request.id} rejected")

    async def _send_po_to_supplier(self, po: PurchaseOrder):
        """Send PO to supplier"""
        po.status = PurchaseOrderStatus.SENT_TO_SUPPLIER
        print(f"Purchase order {po.po_number} sent to supplier {po.supplier_id}")

    # Analytics and reporting methods
    def get_approval_metrics(self) -> Dict[str, Any]:
        """Get approval process metrics"""
        total_requests = len(self.approval_requests)
        approved = sum(1 for r in self.approval_requests.values() if r.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for r in self.approval_requests.values() if r.status == ApprovalStatus.REJECTED)
        pending = sum(1 for r in self.approval_requests.values() if r.status == ApprovalStatus.PENDING)
        
        return {
            "total_requests": total_requests,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": approved / total_requests if total_requests > 0 else 0,
            "avg_processing_time_hours": 24  # Placeholder
        }

    def get_po_metrics(self) -> Dict[str, Any]:
        """Get purchase order metrics"""
        total_pos = len(self.purchase_orders)
        completed = sum(1 for po in self.purchase_orders.values() if po.status == PurchaseOrderStatus.COMPLETED)
        
        return {
            "total_pos": total_pos,
            "completed": completed,
            "completion_rate": completed / total_pos if total_pos > 0 else 0,
            "total_value": sum(po.total_amount for po in self.purchase_orders.values())
        }

    def get_supplier_metrics(self) -> Dict[str, Any]:
        """Get supplier metrics"""
        active_suppliers = sum(1 for s in self.suppliers.values() if s.status == SupplierStatus.ACTIVE)
        
        return {
            "total_suppliers": len(self.suppliers),
            "active_suppliers": active_suppliers,
            "avg_lead_time": sum(s.lead_time_days for s in self.suppliers.values()) / len(self.suppliers) if self.suppliers else 0
        }


# Initialize the workflow engine
workflow_engine = WorkflowEngine()
