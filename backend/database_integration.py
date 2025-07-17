"""
Database Integration for Professional Hospital Supply API
Replaces mock data with live PostgreSQL database operations
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Database imports
try:
    from database.database import db_manager
    from database.data_access import data_access
    from database.init_db import init_database
    from database.models import (
        ItemCategory, AlertLevel, UserRole, QualityStatus, 
        TransferStatus, PurchaseOrderStatus, ApprovalStatus
    )
except ImportError as e:
    logging.error(f"Database import error: {e}")
    logging.info("Make sure PostgreSQL database modules are properly installed")
    raise

class DatabaseIntegrationManager:
    """Manages the integration between API endpoints and database operations"""
    
    def __init__(self):
        self.data_access = data_access
        self.db_manager = db_manager
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize database connection and create tables if needed"""
        if self.is_initialized:
            return
        
        try:
            logging.info("Initializing database integration...")
            
            # Initialize database connection
            await self.db_manager.initialize()
            
            # Check if database needs initialization
            if await self._needs_initialization():
                logging.info("Database appears to be empty, initializing with sample data...")
                await init_database()
            
            self.is_initialized = True
            logging.info("Database integration initialized successfully")
            
        except Exception as e:
            logging.error(f"Database initialization failed: {e}")
            raise
    
    async def _needs_initialization(self) -> bool:
        """Check if database needs to be initialized with sample data"""
        try:
            async with await self.db_manager.get_async_session() as session:
                # Check if any inventory items exist
                items = await self.data_access.get_inventory_items()
                return len(items) == 0
        except Exception:
            return True
    
    # ==================== INVENTORY OPERATIONS ====================
    
    async def get_inventory_data(self) -> List[Dict[str, Any]]:
        """Get all inventory items - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_inventory_items()
    
    async def get_inventory_item_details(self, item_id: str) -> Dict[str, Any]:
        """Get specific inventory item - replaces mock data"""
        await self.initialize()
        item = await self.data_access.get_inventory_item(item_id)
        if not item:
            raise ValueError(f"Item {item_id} not found")
        return item
    
    async def update_inventory_item(self, item_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update inventory item - replaces mock data"""
        await self.initialize()
        item = await self.data_access.update_inventory_item(item_id, update_data)
        if not item:
            raise ValueError(f"Item {item_id} not found")
        return item
    
    async def create_inventory_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new inventory item - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_inventory_item(item_data)
    
    # ==================== BATCH OPERATIONS ====================
    
    async def update_batch_status(self, batch_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update batch status - replaces mock data"""
        await self.initialize()
        batch = await self.data_access.update_batch_status(batch_id, status_data)
        if not batch:
            raise ValueError(f"Batch {batch_id} not found")
        return batch
    
    async def create_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new batch - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_batch(batch_data)
    
    async def get_expiring_batches(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get expiring batches - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_expiring_batches(days)
    
    # ==================== ALERT OPERATIONS ====================
    
    async def get_alerts_data(self) -> List[Dict[str, Any]]:
        """Get all alerts - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_alerts()
    
    async def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new alert - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_alert(alert_data)
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> Dict[str, Any]:
        """Resolve alert - replaces mock data"""
        await self.initialize()
        alert = await self.data_access.resolve_alert(alert_id, resolved_by)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        return alert
    
    # ==================== TRANSFER OPERATIONS ====================
    
    async def get_transfers_data(self) -> List[Dict[str, Any]]:
        """Get all transfers - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_transfers()
    
    async def create_transfer(self, transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new transfer - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_transfer(transfer_data)
    
    async def update_transfer_status(self, transfer_id: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update transfer status - replaces mock data"""
        await self.initialize()
        transfer = await self.data_access.update_transfer_status(transfer_id, status_data)
        if not transfer:
            raise ValueError(f"Transfer {transfer_id} not found")
        return transfer
    
    # ==================== PURCHASE ORDER OPERATIONS ====================
    
    async def get_purchase_orders_data(self) -> List[Dict[str, Any]]:
        """Get all purchase orders - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_purchase_orders()
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new purchase order - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_purchase_order(po_data)
    
    # ==================== APPROVAL OPERATIONS ====================
    
    async def get_approval_requests_data(self) -> List[Dict[str, Any]]:
        """Get all approval requests - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_approval_requests()
    
    async def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new approval request - replaces mock data"""
        await self.initialize()
        return await self.data_access.create_approval_request(approval_data)
    
    async def submit_approval_decision(self, approval_id: str, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit approval decision - replaces mock data"""
        await self.initialize()
        approval = await self.data_access.submit_approval_decision(approval_id, decision_data)
        if not approval:
            raise ValueError(f"Approval request {approval_id} not found")
        return approval
    
    # ==================== LOCATION & USER OPERATIONS ====================
    
    async def get_locations_data(self) -> List[Dict[str, Any]]:
        """Get all locations - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_locations()
    
    async def get_users_data(self) -> List[Dict[str, Any]]:
        """Get all users - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_users()
    
    # ==================== DASHBOARD OPERATIONS ====================
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data - replaces mock data"""
        await self.initialize()
        return await self.data_access.get_dashboard_data()
    
    # ==================== UTILITY FUNCTIONS ====================
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status including database health"""
        try:
            await self.initialize()
            
            # Check database health
            db_health = await self.db_manager.health_check()
            
            # Get basic counts
            inventory_count = len(await self.data_access.get_inventory_items())
            alerts_count = len(await self.data_access.get_alerts())
            transfers_count = len(await self.data_access.get_transfers())
            
            return {
                "status": "operational",
                "database": {
                    "status": "connected" if db_health else "disconnected",
                    "type": "PostgreSQL",
                    "health": db_health
                },
                "data_summary": {
                    "inventory_items": inventory_count,
                    "active_alerts": alerts_count,
                    "active_transfers": transfers_count
                },
                "features": {
                    "real_time_monitoring": True,
                    "autonomous_operations": True,
                    "database_persistence": True,
                    "live_data_sync": True
                },
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logging.error(f"System status check failed: {e}")
            return {
                "status": "error",
                "database": {
                    "status": "error",
                    "error": str(e)
                },
                "last_updated": datetime.now().isoformat()
            }
    
    async def close(self):
        """Close database connections"""
        if self.is_initialized:
            await self.db_manager.close()
            self.is_initialized = False

# Create global integration manager instance
db_integration = DatabaseIntegrationManager()

# Async context manager for database operations
class DatabaseSession:
    """Context manager for database operations"""
    
    def __init__(self):
        self.integration = db_integration
    
    async def __aenter__(self):
        await self.integration.initialize()
        return self.integration
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(f"Database operation error: {exc_val}")
        # Don't close connection here as it's shared

# Convenience functions for direct use in API endpoints
async def get_db_integration():
    """Get initialized database integration manager"""
    await db_integration.initialize()
    return db_integration

async def with_database(func):
    """Decorator to ensure database is initialized before function execution"""
    async def wrapper(*args, **kwargs):
        await db_integration.initialize()
        return await func(*args, **kwargs)
    return wrapper
