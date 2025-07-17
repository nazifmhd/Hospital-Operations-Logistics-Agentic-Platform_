"""
Data Access Layer for Hospital Supply Inventory Management System
Bridges the API layer with database repositories
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import json

from .repositories import (
    user_repo, inventory_repo, batch_repo, alert_repo, transfer_repo,
    purchase_order_repo, approval_repo, audit_repo, notification_repo,
    location_repo, supplier_repo, budget_repo
)
from .database import db_manager
from .models import (
    ItemCategory, AlertLevel, UserRole, QualityStatus, TransferStatus,
    PurchaseOrderStatus, ApprovalStatus
)

class DataAccessLayer:
    """Main data access layer for all database operations"""
    
    def __init__(self):
        self.db = db_manager
    
    async def get_session(self) -> AsyncSession:
        """Get async database session"""
        return await self.db.get_async_session()
    
    # ==================== INVENTORY OPERATIONS ====================
    
    async def get_inventory_items(self) -> List[Dict[str, Any]]:
        """Get all inventory items with current stock levels"""
        async with await self.get_session() as session:
            items = await inventory_repo.get_all_with_details(session)
            
            inventory_data = []
            for item in items:
                # Calculate total quantity from active batches
                total_quantity = sum(
                    batch.quantity for batch in item.batches 
                    if batch.is_active
                )
                
                # Calculate location quantities
                location_quantities = {}
                for location in item.locations:
                    location_quantities[location.name] = sum(
                        batch.quantity for batch in item.batches
                        if batch.is_active and batch.location_id == location.id
                    )
                
                inventory_data.append({
                    "id": item.id,
                    "name": item.name,
                    "sku": item.sku,
                    "category": item.category.value,
                    "description": item.description,
                    "unit": item.unit,
                    "unit_cost": float(item.unit_cost),
                    "current_quantity": total_quantity,
                    "minimum_level": item.minimum_level,
                    "maximum_level": item.maximum_level,
                    "reorder_point": item.reorder_point,
                    "location_quantities": location_quantities,
                    "supplier_info": {
                        "primary_supplier": item.primary_supplier,
                        "secondary_suppliers": item.secondary_suppliers
                    },
                    "storage_requirements": item.storage_requirements,
                    "status": "In Stock" if total_quantity > item.minimum_level else "Low Stock" if total_quantity > 0 else "Out of Stock",
                    "last_updated": item.updated_at.isoformat() if item.updated_at else item.created_at.isoformat()
                })
            
            return inventory_data
    
    async def get_inventory_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get specific inventory item with batches"""
        async with await self.get_session() as session:
            item = await inventory_repo.get_with_batches(session, item_id)
            if not item:
                return None
            
            # Get active batches
            active_batches = [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "quantity": batch.quantity,
                    "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                    "quality_status": batch.quality_status.value,
                    "supplier_batch_id": batch.supplier_batch_id,
                    "received_date": batch.received_date.isoformat() if batch.received_date else None,
                    "location_id": batch.location_id
                }
                for batch in item.batches if batch.is_active
            ]
            
            total_quantity = sum(batch.quantity for batch in item.batches if batch.is_active)
            
            return {
                "id": item.id,
                "name": item.name,
                "sku": item.sku,
                "category": item.category.value,
                "description": item.description,
                "unit": item.unit,
                "unit_cost": float(item.unit_cost),
                "current_quantity": total_quantity,
                "minimum_level": item.minimum_level,
                "maximum_level": item.maximum_level,
                "reorder_point": item.reorder_point,
                "batches": active_batches,
                "supplier_info": {
                    "primary_supplier": item.primary_supplier,
                    "secondary_suppliers": item.secondary_suppliers
                },
                "storage_requirements": item.storage_requirements,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat() if item.updated_at else None
            }
    
    async def create_inventory_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new inventory item"""
        async with await self.get_session() as session:
            # Generate item ID if not provided
            if "id" not in item_data:
                item_data["id"] = f"ITEM_{item_data.get('sku', 'NEW')}"
            
            # Convert category string to enum
            if "category" in item_data and isinstance(item_data["category"], str):
                item_data["category"] = ItemCategory(item_data["category"])
            
            item = await inventory_repo.create(session, **item_data)
            return await self.get_inventory_item(item.id)
    
    async def update_inventory_item(self, item_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update inventory item"""
        async with await self.get_session() as session:
            # Convert category string to enum if present
            if "category" in update_data and isinstance(update_data["category"], str):
                update_data["category"] = ItemCategory(update_data["category"])
            
            item = await inventory_repo.update(session, item_id, **update_data)
            return await self.get_inventory_item(item.id)
    
    # ==================== BATCH OPERATIONS ====================
    
    async def create_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new batch"""
        async with await self.get_session() as session:
            # Convert datetime strings to datetime objects
            if "expiry_date" in batch_data and isinstance(batch_data["expiry_date"], str):
                batch_data["expiry_date"] = datetime.fromisoformat(batch_data["expiry_date"])
            if "received_date" in batch_data and isinstance(batch_data["received_date"], str):
                batch_data["received_date"] = datetime.fromisoformat(batch_data["received_date"])
            
            # Convert quality status string to enum
            if "quality_status" in batch_data and isinstance(batch_data["quality_status"], str):
                batch_data["quality_status"] = QualityStatus(batch_data["quality_status"])
            
            batch = await batch_repo.create(session, **batch_data)
            
            # Log the batch creation
            await audit_repo.create_log(
                session,
                user_id=batch_data.get("received_by", "SYSTEM"),
                action="BATCH_CREATED",
                item_id=batch.item_id,
                details={"batch_id": batch.id, "quantity": batch.quantity}
            )
            
            return {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "item_id": batch.item_id,
                "quantity": batch.quantity,
                "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                "quality_status": batch.quality_status.value,
                "supplier_batch_id": batch.supplier_batch_id,
                "received_date": batch.received_date.isoformat() if batch.received_date else None,
                "location_id": batch.location_id,
                "is_active": batch.is_active
            }
    
    async def update_batch_status(self, batch_id: str, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update batch status"""
        async with await self.get_session() as session:
            # Convert quality status string to enum if present
            if "quality_status" in status_data and isinstance(status_data["quality_status"], str):
                status_data["quality_status"] = QualityStatus(status_data["quality_status"])
            
            batch = await batch_repo.update(session, batch_id, **status_data)
            
            # Log the status update
            await audit_repo.create_log(
                session,
                user_id=status_data.get("updated_by", "SYSTEM"),
                action="BATCH_STATUS_UPDATED",
                item_id=batch.item_id,
                details={"batch_id": batch_id, "new_status": status_data}
            )
            
            return {
                "id": batch.id,
                "batch_number": batch.batch_number,
                "quality_status": batch.quality_status.value,
                "is_active": batch.is_active,
                "updated_at": batch.updated_at.isoformat() if batch.updated_at else None
            }
    
    async def get_expiring_batches(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get batches expiring within specified days"""
        async with await self.get_session() as session:
            batches = await batch_repo.get_expiring_soon(session, days)
            
            return [
                {
                    "id": batch.id,
                    "batch_number": batch.batch_number,
                    "item_id": batch.item_id,
                    "item_name": batch.item.name if batch.item else "Unknown",
                    "quantity": batch.quantity,
                    "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
                    "days_until_expiry": (batch.expiry_date - datetime.now()).days if batch.expiry_date else None,
                    "quality_status": batch.quality_status.value,
                    "location_id": batch.location_id
                }
                for batch in batches
            ]
    
    # ==================== ALERT OPERATIONS ====================
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all unresolved alerts"""
        async with await self.get_session() as session:
            alerts = await alert_repo.get_unresolved_alerts(session)
            
            return [
                {
                    "id": alert.id,
                    "type": alert.type,
                    "level": alert.level.value,
                    "message": alert.message,
                    "item_id": alert.item_id,
                    "item_name": alert.item.name if alert.item else None,
                    "location": alert.location,
                    "threshold_value": alert.threshold_value,
                    "current_value": alert.current_value,
                    "is_resolved": alert.is_resolved,
                    "created_at": alert.created_at.isoformat(),
                    "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                    "resolved_by": alert.resolved_by
                }
                for alert in alerts
            ]
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new alert"""
        async with await self.get_session() as session:
            # Convert level string to enum
            if "level" in alert_data and isinstance(alert_data["level"], str):
                alert_data["level"] = AlertLevel(alert_data["level"])
            
            alert = await alert_repo.create(session, **alert_data)
            
            return {
                "id": alert.id,
                "type": alert.type,
                "level": alert.level.value,
                "message": alert.message,
                "item_id": alert.item_id,
                "location": alert.location,
                "created_at": alert.created_at.isoformat()
            }
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> Optional[Dict[str, Any]]:
        """Resolve alert"""
        async with await self.get_session() as session:
            alert = await alert_repo.resolve_alert(session, alert_id, resolved_by)
            
            return {
                "id": alert.id,
                "is_resolved": alert.is_resolved,
                "resolved_by": alert.resolved_by,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
    
    # ==================== TRANSFER OPERATIONS ====================
    
    async def get_transfers(self) -> List[Dict[str, Any]]:
        """Get all transfers"""
        async with await self.get_session() as session:
            transfers = await transfer_repo.get_all(session)
            
            transfer_list = []
            for transfer in transfers:
                # Get detailed transfer info
                detailed_transfer = await transfer_repo.get_with_details(session, transfer.id)
                if detailed_transfer:
                    transfer_list.append({
                        "id": detailed_transfer.id,
                        "item_id": detailed_transfer.item_id,
                        "item_name": detailed_transfer.item.name if detailed_transfer.item else "Unknown",
                        "from_location_id": detailed_transfer.from_location_id,
                        "from_location_name": detailed_transfer.from_location.name if detailed_transfer.from_location else "Unknown",
                        "to_location_id": detailed_transfer.to_location_id,
                        "to_location_name": detailed_transfer.to_location.name if detailed_transfer.to_location else "Unknown",
                        "quantity": detailed_transfer.quantity,
                        "status": detailed_transfer.status.value,
                        "requested_by": detailed_transfer.requested_by,
                        "requested_at": detailed_transfer.requested_at.isoformat(),
                        "approved_by": detailed_transfer.approved_by,
                        "approved_at": detailed_transfer.approved_at.isoformat() if detailed_transfer.approved_at else None,
                        "completed_at": detailed_transfer.completed_at.isoformat() if detailed_transfer.completed_at else None,
                        "reason": detailed_transfer.reason,
                        "priority": detailed_transfer.priority
                    })
            
            return transfer_list
    
    async def create_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new transfer request"""
        async with await self.get_session() as session:
            # Convert status string to enum if present
            if "status" in transfer_data and isinstance(transfer_data["status"], str):
                transfer_data["status"] = TransferStatus(transfer_data["status"])
            else:
                transfer_data["status"] = TransferStatus.PENDING
            
            # Set requested_at if not provided
            if "requested_at" not in transfer_data:
                transfer_data["requested_at"] = datetime.now()
            
            transfer = await transfer_repo.create(session, **transfer_data)
            
            # Log the transfer creation
            await audit_repo.create_log(
                session,
                user_id=transfer.requested_by,
                action="TRANSFER_REQUESTED",
                item_id=transfer.item_id,
                details={
                    "transfer_id": transfer.id,
                    "from_location": transfer.from_location_id,
                    "to_location": transfer.to_location_id,
                    "quantity": transfer.quantity
                }
            )
            
            return {
                "id": transfer.id,
                "item_id": transfer.item_id,
                "from_location_id": transfer.from_location_id,
                "to_location_id": transfer.to_location_id,
                "quantity": transfer.quantity,
                "status": transfer.status.value,
                "requested_by": transfer.requested_by,
                "requested_at": transfer.requested_at.isoformat(),
                "reason": transfer.reason,
                "priority": transfer.priority
            }
    
    async def update_transfer_status(self, transfer_id: str, status_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update transfer status"""
        async with await self.get_session() as session:
            # Convert status string to enum
            if "status" in status_data and isinstance(status_data["status"], str):
                status_data["status"] = TransferStatus(status_data["status"])
            
            # Set completion timestamp if status is completed
            if status_data.get("status") == TransferStatus.COMPLETED and "completed_at" not in status_data:
                status_data["completed_at"] = datetime.now()
            
            # Set approval timestamp if status is approved
            if status_data.get("status") == TransferStatus.APPROVED and "approved_at" not in status_data:
                status_data["approved_at"] = datetime.now()
            
            transfer = await transfer_repo.update(session, transfer_id, **status_data)
            
            # Log the status update
            await audit_repo.create_log(
                session,
                user_id=status_data.get("updated_by", "SYSTEM"),
                action="TRANSFER_STATUS_UPDATED",
                item_id=transfer.item_id,
                details={"transfer_id": transfer_id, "new_status": status_data.get("status").value}
            )
            
            return {
                "id": transfer.id,
                "status": transfer.status.value,
                "approved_by": transfer.approved_by,
                "approved_at": transfer.approved_at.isoformat() if transfer.approved_at else None,
                "completed_at": transfer.completed_at.isoformat() if transfer.completed_at else None
            }
    
    # ==================== PURCHASE ORDER OPERATIONS ====================
    
    async def get_purchase_orders(self) -> List[Dict[str, Any]]:
        """Get all purchase orders"""
        async with await self.get_session() as session:
            pos = await purchase_order_repo.get_all(session)
            
            po_list = []
            for po in pos:
                # Get detailed PO info
                detailed_po = await purchase_order_repo.get_with_supplier(session, po.id)
                if detailed_po:
                    po_list.append({
                        "id": detailed_po.id,
                        "po_number": detailed_po.po_number,
                        "supplier_id": detailed_po.supplier_id,
                        "supplier_name": detailed_po.supplier.name if detailed_po.supplier else "Unknown",
                        "items": detailed_po.items,
                        "total_amount": float(detailed_po.total_amount),
                        "status": detailed_po.status.value,
                        "created_by": detailed_po.created_by,
                        "created_at": detailed_po.created_at.isoformat(),
                        "expected_delivery": detailed_po.expected_delivery.isoformat() if detailed_po.expected_delivery else None,
                        "received_at": detailed_po.received_at.isoformat() if detailed_po.received_at else None,
                        "notes": detailed_po.notes
                    })
            
            return po_list
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new purchase order"""
        async with await self.get_session() as session:
            # Generate PO number if not provided
            if "po_number" not in po_data:
                po_data["po_number"] = await purchase_order_repo.generate_po_number(session)
            
            # Convert status string to enum if present
            if "status" in po_data and isinstance(po_data["status"], str):
                po_data["status"] = PurchaseOrderStatus(po_data["status"])
            else:
                po_data["status"] = PurchaseOrderStatus.DRAFT
            
            # Convert datetime strings
            if "expected_delivery" in po_data and isinstance(po_data["expected_delivery"], str):
                po_data["expected_delivery"] = datetime.fromisoformat(po_data["expected_delivery"])
            
            po = await purchase_order_repo.create(session, **po_data)
            
            # Log the PO creation
            await audit_repo.create_log(
                session,
                user_id=po.created_by,
                action="PURCHASE_ORDER_CREATED",
                details={
                    "po_id": po.id,
                    "po_number": po.po_number,
                    "supplier_id": po.supplier_id,
                    "total_amount": float(po.total_amount)
                }
            )
            
            return {
                "id": po.id,
                "po_number": po.po_number,
                "supplier_id": po.supplier_id,
                "items": po.items,
                "total_amount": float(po.total_amount),
                "status": po.status.value,
                "created_by": po.created_by,
                "created_at": po.created_at.isoformat(),
                "expected_delivery": po.expected_delivery.isoformat() if po.expected_delivery else None
            }
    
    # ==================== APPROVAL OPERATIONS ====================
    
    async def get_approval_requests(self) -> List[Dict[str, Any]]:
        """Get all approval requests"""
        async with await self.get_session() as session:
            approvals = await approval_repo.get_pending_approvals(session)
            
            return [
                {
                    "id": approval.id,
                    "request_type": approval.request_type,
                    "request_data": approval.request_data,
                    "requester_id": approval.requester_id,
                    "requester_name": approval.requester.username if approval.requester else "Unknown",
                    "status": approval.status.value,
                    "created_at": approval.created_at.isoformat(),
                    "approved_by": approval.approved_by,
                    "emergency": approval.emergency,
                    "justification": approval.justification,
                    "estimated_cost": float(approval.estimated_cost) if approval.estimated_cost else None
                }
                for approval in approvals
            ]
    
    async def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new approval request"""
        async with await self.get_session() as session:
            # Convert status string to enum if present
            if "status" in approval_data and isinstance(approval_data["status"], str):
                approval_data["status"] = ApprovalStatus(approval_data["status"])
            else:
                approval_data["status"] = ApprovalStatus.PENDING
            
            approval = await approval_repo.create(session, **approval_data)
            
            # Log the approval request creation
            await audit_repo.create_log(
                session,
                user_id=approval.requester_id,
                action="APPROVAL_REQUESTED",
                details={
                    "approval_id": approval.id,
                    "request_type": approval.request_type,
                    "emergency": approval.emergency
                }
            )
            
            return {
                "id": approval.id,
                "request_type": approval.request_type,
                "request_data": approval.request_data,
                "requester_id": approval.requester_id,
                "status": approval.status.value,
                "created_at": approval.created_at.isoformat(),
                "emergency": approval.emergency,
                "justification": approval.justification,
                "estimated_cost": float(approval.estimated_cost) if approval.estimated_cost else None
            }
    
    async def submit_approval_decision(self, approval_id: str, decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit approval decision"""
        async with await self.get_session() as session:
            # Convert status string to enum
            if "status" in decision_data and isinstance(decision_data["status"], str):
                decision_data["status"] = ApprovalStatus(decision_data["status"])
            
            approval = await approval_repo.update(session, approval_id, **decision_data)
            
            # Log the decision
            await audit_repo.create_log(
                session,
                user_id=decision_data.get("decided_by", "SYSTEM"),
                action="APPROVAL_DECISION_MADE",
                details={
                    "approval_id": approval_id,
                    "decision": decision_data.get("status").value,
                    "comments": decision_data.get("comments")
                }
            )
            
            return {
                "id": approval.id,
                "status": approval.status.value,
                "approved_by": approval.approved_by,
                "comments": decision_data.get("comments")
            }
    
    # ==================== LOCATION OPERATIONS ====================
    
    async def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations"""
        async with await self.get_session() as session:
            locations = await location_repo.get_all(session)
            
            return [
                {
                    "id": location.id,
                    "name": location.name,
                    "type": location.type,
                    "description": location.description,
                    "address": location.address,
                    "capacity": location.capacity,
                    "manager_id": location.manager_id,
                    "storage_conditions": location.storage_conditions,
                    "security_level": location.security_level,
                    "is_active": location.is_active,
                    "created_at": location.created_at.isoformat()
                }
                for location in locations if location.is_active
            ]
    
    # ==================== USER OPERATIONS ====================
    
    async def get_users(self) -> List[Dict[str, Any]]:
        """Get all active users"""
        async with await self.get_session() as session:
            users = await user_repo.get_active_users(session)
            
            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "department": user.department,
                    "phone": user.phone,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                }
                for user in users
            ]
    
    # ==================== DASHBOARD DATA ====================
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        async with await self.get_session() as session:
            # Get counts and statistics
            inventory_items = await inventory_repo.get_all(session)
            low_stock_items = await inventory_repo.get_low_stock_items(session)
            unresolved_alerts = await alert_repo.get_unresolved_alerts(session)
            pending_transfers = await transfer_repo.get_pending_transfers(session)
            pending_approvals = await approval_repo.get_pending_approvals(session)
            expiring_batches = await batch_repo.get_expiring_soon(session, days=30)
            
            # Calculate total inventory value
            total_value = sum(
                sum(batch.quantity * item.unit_cost for batch in item.batches if batch.is_active)
                for item in inventory_items if item.is_active
            )
            
            return {
                "inventory_summary": {
                    "total_items": len([item for item in inventory_items if item.is_active]),
                    "low_stock_items": len(low_stock_items),
                    "total_value": float(total_value),
                    "categories": {
                        category.value: len([
                            item for item in inventory_items 
                            if item.category == category and item.is_active
                        ])
                        for category in ItemCategory
                    }
                },
                "alerts_summary": {
                    "total_unresolved": len(unresolved_alerts),
                    "critical_alerts": len([a for a in unresolved_alerts if a.level == AlertLevel.CRITICAL]),
                    "warning_alerts": len([a for a in unresolved_alerts if a.level == AlertLevel.WARNING]),
                    "info_alerts": len([a for a in unresolved_alerts if a.level == AlertLevel.INFO])
                },
                "operations_summary": {
                    "pending_transfers": len(pending_transfers),
                    "pending_approvals": len(pending_approvals),
                    "expiring_batches": len(expiring_batches),
                    "emergency_requests": len([a for a in pending_approvals if a.emergency])
                },
                "recent_activity": {
                    "last_updated": datetime.now().isoformat()
                }
            }

# Create global instance
data_access = DataAccessLayer()
