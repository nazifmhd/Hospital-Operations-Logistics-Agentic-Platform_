"""
Database Repository Layer for Hospital Supply Inventory Management System
Handles all database operations with live data synchronization
"""

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, update, delete, func, and_, or_, text, desc, asc
from sqlalchemy.exc import IntegrityError, NoResultFound
from datetime import datetime, timedelta
import logging
import json
import uuid

from .models import (
    User, Location, Supplier, InventoryItem, Batch, Alert, Transfer,
    PurchaseOrder, ApprovalRequest, Budget, AuditLog, Notification,
    ItemCategory, AlertLevel, UserRole, QualityStatus, TransferStatus,
    PurchaseOrderStatus, ApprovalStatus, item_locations
)
from .database import db_manager

class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, model_class):
        self.model = model_class
    
    async def get_by_id(self, session: AsyncSession, id: str):
        """Get record by ID"""
        try:
            result = await session.execute(select(self.model).where(self.model.id == id))
            return result.scalar_one_or_none()
        except Exception as e:
            logging.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise
    
    async def get_all(self, session: AsyncSession, limit: int = 1000, offset: int = 0):
        """Get all records with pagination"""
        try:
            result = await session.execute(
                select(self.model).limit(limit).offset(offset)
            )
            return result.scalars().all()
        except Exception as e:
            logging.error(f"Error getting all {self.model.__name__}: {e}")
            raise
    
    async def create(self, session: AsyncSession, **kwargs):
        """Create new record"""
        try:
            instance = self.model(**kwargs)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance
        except IntegrityError as e:
            await session.rollback()
            logging.error(f"Integrity error creating {self.model.__name__}: {e}")
            raise
        except Exception as e:
            await session.rollback()
            logging.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def update(self, session: AsyncSession, id: str, **kwargs):
        """Update record by ID"""
        try:
            stmt = update(self.model).where(self.model.id == id).values(**kwargs)
            result = await session.execute(stmt)
            await session.commit()
            
            if result.rowcount == 0:
                raise NoResultFound(f"No {self.model.__name__} found with ID {id}")
            
            return await self.get_by_id(session, id)
        except Exception as e:
            await session.rollback()
            logging.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise
    
    async def delete(self, session: AsyncSession, id: str):
        """Delete record by ID"""
        try:
            stmt = delete(self.model).where(self.model.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            await session.rollback()
            logging.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise

class UserRepository(BaseRepository):
    """Repository for User operations"""
    
    def __init__(self):
        super().__init__(User)
    
    async def get_by_username(self, session: AsyncSession, username: str):
        """Get user by username"""
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, session: AsyncSession, email: str):
        """Get user by email"""
        result = await session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_active_users(self, session: AsyncSession):
        """Get all active users"""
        result = await session.execute(select(User).where(User.is_active == True))
        return result.scalars().all()
    
    async def update_last_login(self, session: AsyncSession, user_id: str):
        """Update user's last login timestamp"""
        await self.update(session, user_id, last_login=datetime.now())

class InventoryRepository(BaseRepository):
    """Repository for Inventory operations"""
    
    def __init__(self):
        super().__init__(InventoryItem)
    
    async def get_with_batches(self, session: AsyncSession, item_id: str):
        """Get inventory item with all batches"""
        result = await session.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.batches))
            .where(InventoryItem.id == item_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_details(self, session: AsyncSession):
        """Get all inventory items with batches and locations"""
        result = await session.execute(
            select(InventoryItem)
            .options(
                selectinload(InventoryItem.batches),
                selectinload(InventoryItem.locations)
            )
            .where(InventoryItem.is_active == True)
        )
        return result.scalars().all()
    
    async def get_low_stock_items(self, session: AsyncSession):
        """Get items with low stock levels"""
        # This would need custom logic based on location quantities
        result = await session.execute(
            select(InventoryItem)
            .options(selectinload(InventoryItem.batches))
            .where(InventoryItem.is_active == True)
        )
        items = result.scalars().all()
        
        low_stock_items = []
        for item in items:
            total_quantity = sum(batch.quantity for batch in item.batches if batch.is_active)
            if total_quantity <= item.reorder_point:
                low_stock_items.append(item)
        
        return low_stock_items
    
    async def search_items(self, session: AsyncSession, query: str):
        """Search items by name or SKU"""
        result = await session.execute(
            select(InventoryItem)
            .where(
                or_(
                    InventoryItem.name.ilike(f"%{query}%"),
                    InventoryItem.sku.ilike(f"%{query}%"),
                    InventoryItem.description.ilike(f"%{query}%")
                )
            )
            .where(InventoryItem.is_active == True)
        )
        return result.scalars().all()
    
    async def get_by_category(self, session: AsyncSession, category: ItemCategory):
        """Get items by category"""
        result = await session.execute(
            select(InventoryItem)
            .where(InventoryItem.category == category)
            .where(InventoryItem.is_active == True)
        )
        return result.scalars().all()

class BatchRepository(BaseRepository):
    """Repository for Batch operations"""
    
    def __init__(self):
        super().__init__(Batch)
    
    async def get_by_item(self, session: AsyncSession, item_id: str):
        """Get all batches for an item"""
        result = await session.execute(
            select(Batch)
            .where(Batch.item_id == item_id)
            .where(Batch.is_active == True)
            .order_by(Batch.expiry_date.asc())
        )
        return result.scalars().all()
    
    async def get_expiring_soon(self, session: AsyncSession, days: int = 30):
        """Get batches expiring within specified days"""
        expiry_threshold = datetime.now() + timedelta(days=days)
        result = await session.execute(
            select(Batch)
            .options(selectinload(Batch.item))
            .where(Batch.expiry_date <= expiry_threshold)
            .where(Batch.is_active == True)
            .order_by(Batch.expiry_date.asc())
        )
        return result.scalars().all()
    
    async def get_expired_batches(self, session: AsyncSession):
        """Get all expired batches"""
        result = await session.execute(
            select(Batch)
            .options(selectinload(Batch.item))
            .where(Batch.expiry_date < datetime.now())
            .where(Batch.is_active == True)
        )
        return result.scalars().all()

class AlertRepository(BaseRepository):
    """Repository for Alert operations"""
    
    def __init__(self):
        super().__init__(Alert)
    
    async def get_unresolved_alerts(self, session: AsyncSession):
        """Get all unresolved alerts"""
        result = await session.execute(
            select(Alert)
            .options(selectinload(Alert.item))
            .where(Alert.is_resolved == False)
            .order_by(Alert.level.desc(), Alert.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_level(self, session: AsyncSession, level: AlertLevel):
        """Get alerts by level"""
        result = await session.execute(
            select(Alert)
            .options(selectinload(Alert.item))
            .where(Alert.level == level)
            .where(Alert.is_resolved == False)
            .order_by(Alert.created_at.desc())
        )
        return result.scalars().all()
    
    async def resolve_alert(self, session: AsyncSession, alert_id: str, resolved_by: str):
        """Resolve an alert"""
        return await self.update(
            session, 
            alert_id, 
            is_resolved=True,
            resolved_by=resolved_by,
            resolved_at=datetime.now()
        )

class TransferRepository(BaseRepository):
    """Repository for Transfer operations"""
    
    def __init__(self):
        super().__init__(Transfer)
    
    async def get_with_details(self, session: AsyncSession, transfer_id: str):
        """Get transfer with all related details"""
        result = await session.execute(
            select(Transfer)
            .options(
                selectinload(Transfer.item),
                selectinload(Transfer.from_location),
                selectinload(Transfer.to_location),
                selectinload(Transfer.requester)
            )
            .where(Transfer.id == transfer_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_status(self, session: AsyncSession, status: TransferStatus):
        """Get transfers by status"""
        result = await session.execute(
            select(Transfer)
            .options(
                selectinload(Transfer.item),
                selectinload(Transfer.from_location),
                selectinload(Transfer.to_location)
            )
            .where(Transfer.status == status)
            .order_by(Transfer.requested_at.desc())
        )
        return result.scalars().all()
    
    async def get_pending_transfers(self, session: AsyncSession):
        """Get all pending transfers"""
        return await self.get_by_status(session, TransferStatus.PENDING)

class PurchaseOrderRepository(BaseRepository):
    """Repository for Purchase Order operations"""
    
    def __init__(self):
        super().__init__(PurchaseOrder)
    
    async def get_with_supplier(self, session: AsyncSession, po_id: str):
        """Get purchase order with supplier details"""
        result = await session.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.supplier))
            .where(PurchaseOrder.id == po_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_status(self, session: AsyncSession, status: PurchaseOrderStatus):
        """Get purchase orders by status"""
        result = await session.execute(
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.supplier))
            .where(PurchaseOrder.status == status)
            .order_by(PurchaseOrder.created_at.desc())
        )
        return result.scalars().all()
    
    async def generate_po_number(self, session: AsyncSession) -> str:
        """Generate unique PO number"""
        today = datetime.now()
        prefix = f"PO{today.year}{today.month:02d}"
        
        # Get the latest PO number for this month
        result = await session.execute(
            select(func.max(PurchaseOrder.po_number))
            .where(PurchaseOrder.po_number.like(f"{prefix}%"))
        )
        latest_po = result.scalar()
        
        if latest_po:
            sequence = int(latest_po[-4:]) + 1
        else:
            sequence = 1
        
        return f"{prefix}{sequence:04d}"

class ApprovalRepository(BaseRepository):
    """Repository for Approval Request operations"""
    
    def __init__(self):
        super().__init__(ApprovalRequest)
    
    async def get_pending_approvals(self, session: AsyncSession):
        """Get all pending approval requests"""
        result = await session.execute(
            select(ApprovalRequest)
            .options(selectinload(ApprovalRequest.requester))
            .where(ApprovalRequest.status == ApprovalStatus.PENDING)
            .order_by(ApprovalRequest.emergency.desc(), ApprovalRequest.created_at.asc())
        )
        return result.scalars().all()
    
    async def get_by_requester(self, session: AsyncSession, requester_id: str):
        """Get approval requests by requester"""
        result = await session.execute(
            select(ApprovalRequest)
            .where(ApprovalRequest.requester_id == requester_id)
            .order_by(ApprovalRequest.created_at.desc())
        )
        return result.scalars().all()
    
    async def approve_request(self, session: AsyncSession, request_id: str, approver_id: str):
        """Approve a request"""
        request = await self.get_by_id(session, request_id)
        if not request:
            raise NoResultFound(f"Approval request {request_id} not found")
        
        # Add approver to approved_by list
        approved_by = request.approved_by or []
        if approver_id not in approved_by:
            approved_by.append(approver_id)
        
        return await self.update(
            session,
            request_id,
            status=ApprovalStatus.APPROVED,
            approved_by=approved_by
        )

class AuditRepository(BaseRepository):
    """Repository for Audit Log operations"""
    
    def __init__(self):
        super().__init__(AuditLog)
    
    async def create_log(self, session: AsyncSession, user_id: str, action: str, 
                        item_id: str = None, location: str = None, 
                        details: Dict = None, ip_address: str = None):
        """Create audit log entry"""
        log_id = f"LOG_{uuid.uuid4().hex[:8].upper()}"
        
        return await self.create(
            session,
            log_id=log_id,
            user_id=user_id,
            action=action,
            item_id=item_id,
            location=location,
            details=details,
            ip_address=ip_address
        )
    
    async def get_by_user(self, session: AsyncSession, user_id: str, limit: int = 100):
        """Get audit logs for a user"""
        result = await session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_item(self, session: AsyncSession, item_id: str, limit: int = 100):
        """Get audit logs for an item"""
        result = await session.execute(
            select(AuditLog)
            .options(selectinload(AuditLog.user))
            .where(AuditLog.item_id == item_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()

class NotificationRepository(BaseRepository):
    """Repository for Notification operations"""
    
    def __init__(self):
        super().__init__(Notification)
    
    async def get_user_notifications(self, session: AsyncSession, user_id: str, 
                                   unread_only: bool = False):
        """Get notifications for a user"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()
    
    async def mark_as_read(self, session: AsyncSession, notification_id: str):
        """Mark notification as read"""
        return await self.update(
            session,
            notification_id,
            is_read=True,
            read_at=datetime.now()
        )
    
    async def mark_all_read(self, session: AsyncSession, user_id: str):
        """Mark all notifications as read for a user"""
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
            .values(is_read=True, read_at=datetime.now())
        )
        await session.execute(stmt)
        await session.commit()

# Repository instances
user_repo = UserRepository()
inventory_repo = InventoryRepository()
batch_repo = BatchRepository()
alert_repo = AlertRepository()
transfer_repo = TransferRepository()
purchase_order_repo = PurchaseOrderRepository()
approval_repo = ApprovalRepository()
audit_repo = AuditRepository()
notification_repo = NotificationRepository()
location_repo = BaseRepository(Location)
supplier_repo = BaseRepository(Supplier)
budget_repo = BaseRepository(Budget)
