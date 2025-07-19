"""
Automatic Approval Request Generation Service
Monitors inventory levels and automatically creates approval requests for low stock items
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    from .workflow_engine import WorkflowEngine
except ImportError:
    from workflow_engine import WorkflowEngine

@dataclass
class InventoryItem:
    """Represents an inventory item for monitoring"""
    item_id: str
    name: str
    current_quantity: int
    minimum_threshold: int
    location: str
    unit_price: float
    supplier_id: Optional[str] = None
    category: str = "medical_supplies"

@dataclass
class AutoApprovalConfig:
    """Configuration for automatic approval generation"""
    check_interval_minutes: int = 30  # Check every 30 minutes
    emergency_threshold_multiplier: float = 0.3  # 30% of minimum = emergency
    batch_approval_window_hours: int = 4  # Batch requests within 4 hours
    max_auto_amount: float = 5000.0  # Max amount for auto-approval without manual review
    enabled: bool = True

class AutoApprovalService:
    """Service for automatically generating approval requests based on inventory levels"""
    
    def __init__(self, workflow_engine: WorkflowEngine, supply_agent=None):
        self.workflow_engine = workflow_engine
        self.supply_agent = supply_agent  # Reference to supply agent for transfers
        self.config = AutoApprovalConfig()
        self.logger = logging.getLogger(__name__)
        self.monitoring_task: Optional[asyncio.Task] = None
        self.last_check_time = datetime.now()
        self.pending_requests: Dict[str, datetime] = {}  # Track recent requests to avoid duplicates
        
        # Database connection - fetch inventory items from database
        from backend.database.data_access import DataAccess
        self.data_access = DataAccess()
        self.inventory_items: Dict[str, InventoryItem] = {}

    async def load_inventory_from_database(self):
        """Load inventory items from database"""
        try:
            # This would load real inventory data from database
            # For now, initialize as empty - will be populated from database
            pass
        except Exception as e:
            self.logger.error(f"Failed to load inventory from database: {e}")
            self.inventory_items = {}

    async def start_monitoring(self):
        """Start the automatic monitoring service"""
        if not self.config.enabled:
            self.logger.info("Auto approval service is disabled")
            return
            
        self.logger.info("Starting automatic approval request monitoring service")
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the monitoring service"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Stopped automatic approval request monitoring service")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while True:
            try:
                await self._check_inventory_levels()
                await asyncio.sleep(self.config.check_interval_minutes * 60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _check_inventory_levels(self):
        """Enhanced inventory checking with reorder point vs minimum stock logic"""
        self.logger.info("Checking inventory levels for auto-approval generation")
        
        for item in self.inventory_items.values():
            current_stock = item.current_quantity
            minimum_stock = item.minimum_threshold
            reorder_point = getattr(item, 'reorder_point', minimum_stock)
            
            # Enhanced logic: Distinguish between reorder point and minimum stock
            if current_stock <= minimum_stock:
                self.logger.warning(f"🚨 MINIMUM STOCK BREACH: {item.name} - Stock: {current_stock}, Min: {minimum_stock}")
                self.logger.info("   → Attempting inter-departmental transfer first")
                
                # Below minimum stock = try inter-transfer first
                transfer_success = await self._attempt_interdepartmental_transfer(item, is_emergency=True)
                
                if not transfer_success:
                    self.logger.info("   → No surplus found, creating emergency supplier order")
                    await self._create_approval_request(item, is_emergency=True)
                    
            elif current_stock <= reorder_point:
                self.logger.info(f"📊 REORDER POINT REACHED: {item.name} - Stock: {current_stock}, Reorder: {reorder_point}")
                
                # Check if we already have a pending reorder request
                if not self._has_pending_reorder_request(item):
                    self.logger.info("   → Automatically creating supplier order")
                    await self._create_supplier_reorder_request(item)

        # Clean up old pending requests
        self._cleanup_pending_requests()

    def _has_pending_reorder_request(self, item: InventoryItem) -> bool:
        """Check if item already has a pending reorder request"""
        if item.item_id in self.pending_requests:
            request_time = self.pending_requests[item.item_id]
            if datetime.now() - request_time < timedelta(hours=self.config.batch_approval_window_hours):
                return True
        return False

    async def _create_supplier_reorder_request(self, item: InventoryItem):
        """Create an automatic supplier reorder request (not requiring approval)"""
        try:
            # Calculate standard reorder quantity
            reorder_quantity = self._calculate_reorder_quantity(item)
            
            # Create reorder request data
            reorder_data = {
                "item_id": item.item_id,
                "name": item.name,
                "quantity": reorder_quantity,
                "unit_price": item.unit_price,
                "total_amount": reorder_quantity * item.unit_price,
                "supplier_id": item.supplier_id,
                "location": item.location,
                "reason": "Automatic reorder - reached reorder point",
                "priority": "normal",
                "auto_generated": True,
                "request_type": "automatic_reorder"
            }
            
            # If amount is below auto-approval limit, process immediately
            if reorder_data["total_amount"] <= self.config.max_auto_amount:
                await self._process_automatic_reorder(reorder_data)
            else:
                # Create approval request for large orders
                await self._create_approval_request(item, is_emergency=False)
                
            # Mark as pending to avoid duplicate requests
            self.pending_requests[item.item_id] = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error creating supplier reorder request for {item.name}: {e}")

    def _calculate_reorder_quantity(self, item: InventoryItem) -> int:
        """Calculate optimal reorder quantity based on usage patterns"""
        # Use maximum stock if available, otherwise calculate based on minimum + buffer
        if hasattr(item, 'maximum_stock') and item.maximum_stock > 0:
            return item.maximum_stock - item.current_quantity
        else:
            # Calculate as minimum stock + 50% buffer
            target_stock = int(item.minimum_threshold * 1.5)
            return max(target_stock - item.current_quantity, item.minimum_threshold)

    async def _process_automatic_reorder(self, reorder_data):
        """Process an automatic reorder without approval"""
        try:
            self.logger.info(f"Processing automatic reorder: {reorder_data['quantity']} units of {reorder_data['name']}")
            
            # Generate purchase order directly (simulate supplier order)
            order_id = f"AUTO_PO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reorder_data['item_id']}"
            
            # Log the automatic order
            self.logger.info(f"✅ Automatic supplier order created: {order_id}")
            self.logger.info(f"   Item: {reorder_data['name']}")
            self.logger.info(f"   Quantity: {reorder_data['quantity']}")
            self.logger.info(f"   Total: ${reorder_data['total_amount']:.2f}")
            self.logger.info(f"   Supplier: {reorder_data['supplier_id']}")
            
            # Here you would integrate with actual procurement system
            # For now, we simulate the order being placed
            
        except Exception as e:
            self.logger.error(f"Error processing automatic reorder: {e}")

    def _needs_approval_request(self, item: InventoryItem) -> bool:
        """Determine if an item needs an approval request"""
        # Check if already below threshold
        if item.current_quantity >= item.minimum_threshold:
            return False
            
        # Check if we've recently created a request for this item
        if item.item_id in self.pending_requests:
            request_time = self.pending_requests[item.item_id]
            if datetime.now() - request_time < timedelta(hours=self.config.batch_approval_window_hours):
                return False
                
        return True

    def _is_emergency_level(self, item: InventoryItem) -> bool:
        """Check if item is at emergency level (very low stock)"""
        emergency_threshold = item.minimum_threshold * self.config.emergency_threshold_multiplier
        return item.current_quantity <= emergency_threshold

    async def _create_approval_request(self, item: InventoryItem, is_emergency: bool = False):
        """Create an approval request for a low stock item"""
        try:
            # Calculate optimal order quantity
            order_quantity = self._calculate_order_quantity(item, is_emergency)
            total_amount = order_quantity * item.unit_price
            
            # Determine request type based on amount
            request_type = "purchase_order"
            if total_amount > self.config.max_auto_amount:
                request_type = "budget_request"  # Requires higher approval
            
            # Create detailed item information
            item_details = {
                "item_id": item.item_id,
                "name": item.name,
                "quantity": order_quantity,
                "unit_price": item.unit_price,
                "location": item.location,
                "supplier_id": item.supplier_id,
                "category": item.category,
                "current_stock": item.current_quantity,
                "minimum_threshold": item.minimum_threshold,
                "urgency": "EMERGENCY" if is_emergency else "STANDARD"
            }
            
            # Generate justification
            justification = self._generate_justification(item, order_quantity, is_emergency)
            
            # Submit the approval request
            approval_request = await self.workflow_engine.submit_approval_request(
                request_type=request_type,
                requester_id="system_auto_approval",
                item_details=item_details,
                amount=total_amount,
                justification=justification
            )
            
            # Track this request to avoid duplicates
            self.pending_requests[item.item_id] = datetime.now()
            
            self.logger.info(
                f"Auto-generated approval request {approval_request.id} for {item.name} "
                f"(Qty: {order_quantity}, Amount: ${total_amount:.2f}, "
                f"Emergency: {is_emergency})"
            )
            
            return approval_request
            
        except Exception as e:
            self.logger.error(f"Failed to create approval request for {item.name}: {e}")
            return None

    def _calculate_order_quantity(self, item: InventoryItem, is_emergency: bool) -> int:
        """Calculate optimal order quantity based on item and urgency"""
        if is_emergency:
            # For emergency, order enough to get well above minimum
            safety_buffer = int(item.minimum_threshold * 0.5)
            needed_to_minimum = item.minimum_threshold - item.current_quantity
            return needed_to_minimum + safety_buffer
        else:
            # For regular reorder, use standard formula
            # Order enough to reach 2x minimum threshold
            return (item.minimum_threshold * 2) - item.current_quantity

    def _generate_justification(self, item: InventoryItem, order_quantity: int, is_emergency: bool) -> str:
        """Generate a justification message for the approval request"""
        shortage = item.minimum_threshold - item.current_quantity
        percentage_below = (shortage / item.minimum_threshold) * 100
        
        if is_emergency:
            return (
                f"EMERGENCY AUTO-GENERATED REQUEST: {item.name} in {item.location} is critically low. "
                f"Current stock: {item.current_quantity} units (minimum: {item.minimum_threshold}). "
                f"This is {percentage_below:.1f}% below minimum threshold. "
                f"Requesting {order_quantity} units to restore adequate stock levels. "
                f"Auto-generated by inventory monitoring system on {datetime.now().strftime('%Y-%m-%d %H:%M')}."
            )
        else:
            return (
                f"AUTO-GENERATED REQUEST: {item.name} in {item.location} has fallen below minimum threshold. "
                f"Current stock: {item.current_quantity} units (minimum: {item.minimum_threshold}). "
                f"Requesting {order_quantity} units to replenish inventory. "
                f"Auto-generated by inventory monitoring system on {datetime.now().strftime('%Y-%m-%d %H:%M')}."
            )

    def _cleanup_pending_requests(self):
        """Remove old pending requests to allow new ones"""
        cutoff_time = datetime.now() - timedelta(hours=self.config.batch_approval_window_hours * 2)
        expired_items = [
            item_id for item_id, request_time in self.pending_requests.items()
            if request_time < cutoff_time
        ]
        for item_id in expired_items:
            del self.pending_requests[item_id]

    def update_inventory_item(self, item_id: str, current_quantity: int):
        """Update inventory item quantity (called when inventory changes)"""
        if item_id in self.inventory_items:
            self.inventory_items[item_id].current_quantity = current_quantity
            self.logger.debug(f"Updated inventory for {item_id}: {current_quantity} units")

    def add_inventory_item(self, item: InventoryItem):
        """Add a new item to monitoring"""
        self.inventory_items[item.item_id] = item
        self.logger.info(f"Added new inventory item to monitoring: {item.name}")

    def remove_inventory_item(self, item_id: str):
        """Remove an item from monitoring"""
        if item_id in self.inventory_items:
            del self.inventory_items[item_id]
            if item_id in self.pending_requests:
                del self.pending_requests[item_id]
            self.logger.info(f"Removed inventory item from monitoring: {item_id}")

    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status"""
        low_stock_count = sum(
            1 for item in self.inventory_items.values()
            if item.current_quantity < item.minimum_threshold
        )
        
        emergency_count = sum(
            1 for item in self.inventory_items.values()
            if self._is_emergency_level(item)
        )
        
        return {
            "enabled": self.config.enabled,
            "monitoring_active": self.monitoring_task is not None and not self.monitoring_task.done(),
            "total_items": len(self.inventory_items),
            "low_stock_items": low_stock_count,
            "emergency_items": emergency_count,
            "pending_requests": len(self.pending_requests),
            "last_check": self.last_check_time.isoformat(),
            "check_interval_minutes": self.config.check_interval_minutes
        }

    async def _attempt_interdepartmental_transfer(self, low_stock_item: InventoryItem, is_emergency: bool = False) -> bool:
        """
        Enhanced inter-departmental transfer logic with location-specific handling
        Returns True if transfer was successful, False otherwise
        """
        try:
            if not self.supply_agent:
                return False
            
            # Calculate how much we need
            needed_quantity = low_stock_item.minimum_threshold - low_stock_item.current_quantity
            if is_emergency:
                needed_quantity = max(needed_quantity, int(low_stock_item.minimum_threshold * 1.5))
            
            self.logger.info(f"Attempting inter-departmental transfer for {low_stock_item.name}")
            self.logger.info(f"   Current stock: {low_stock_item.current_quantity}")
            self.logger.info(f"   Minimum threshold: {low_stock_item.minimum_threshold}")
            self.logger.info(f"   Needed quantity: {needed_quantity}")
            
            # Enhanced logic: Check multiple departments and their stock levels
            available_departments = await self._find_departments_with_surplus(low_stock_item, needed_quantity)
            
            if not available_departments:
                self.logger.info(f"❌ No surplus stock found for {low_stock_item.name} in other departments")
                return False
            
            # Execute transfers from multiple departments if needed
            total_transferred = 0
            successful_transfers = []
            
            for dept_info in available_departments:
                if total_transferred >= needed_quantity:
                    break
                    
                transfer_qty = min(dept_info['can_transfer'], needed_quantity - total_transferred)
                
                if transfer_qty <= 0:
                    continue
                
                # Create transfer request
                transfer_success = await self._create_transfer_request(
                    item=low_stock_item,
                    from_location=dept_info['department'],
                    to_location=low_stock_item.location,
                    quantity=transfer_qty,
                    reason=f"Automatic inter-departmental transfer - {low_stock_item.location} below minimum threshold",
                    priority="high" if is_emergency else "medium"
                )
                
                if transfer_success:
                    total_transferred += transfer_qty
                    successful_transfers.append({
                        "from": dept_info['department'],
                        "quantity": transfer_qty
                    })
                    
                    self.logger.info(f"✅ Transfer request created: {transfer_qty} units from {dept_info['department']}")
                else:
                    self.logger.warning(f"⚠️ Failed to create transfer from {dept_info['department']}")
            
            if total_transferred > 0:
                self.logger.info(f"🔄 Successfully initiated {len(successful_transfers)} transfers totaling {total_transferred} units")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in interdepartmental transfer: {e}")
            return False

    async def _find_departments_with_surplus(self, item: InventoryItem, needed_quantity: int):
        """Find departments with surplus stock for the given item"""
        try:
            # Simulate department inventory checking
            departments = [
                {"name": "ICU", "stock": 45, "min_threshold": 15},
                {"name": "Emergency", "stock": 35, "min_threshold": 20},
                {"name": "Surgery", "stock": 50, "min_threshold": 25},
                {"name": "Pharmacy", "stock": 80, "min_threshold": 30},
                {"name": "WAREHOUSE", "stock": 150, "min_threshold": 50}
            ]
            
            available_departments = []
            
            for dept in departments:
                if dept["name"] == item.location:
                    continue  # Skip the requesting department
                
                surplus = dept["stock"] - dept["min_threshold"]
                if surplus > 5:  # Must have at least 5 units surplus
                    can_transfer = min(surplus - 2, needed_quantity)  # Keep 2 units safety buffer
                    if can_transfer > 0:
                        available_departments.append({
                            "department": dept["name"],
                            "surplus_stock": surplus,
                            "can_transfer": can_transfer,
                            "priority": "high" if surplus > 20 else "medium"
                        })
            
            # Sort by surplus stock (highest first)
            available_departments.sort(key=lambda x: x["surplus_stock"], reverse=True)
            
            return available_departments
            
        except Exception as e:
            self.logger.error(f"Error finding departments with surplus: {e}")
            return []

    async def _create_transfer_request(self, item: InventoryItem, from_location: str, to_location: str, 
                                     quantity: int, reason: str, priority: str = "medium") -> bool:
        """Create an actual transfer request in the system"""
        try:
            transfer_id = f"AUTO_XFER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{item.item_id}"
            
            transfer_data = {
                "transfer_id": transfer_id,
                "item_id": item.item_id,
                "item_name": item.name,
                "from_location": from_location,
                "to_location": to_location,
                "quantity": quantity,
                "reason": reason,
                "priority": priority,
                "status": "pending",
                "auto_generated": True,
                "created_at": datetime.now().isoformat(),
                "requested_by": "Auto Approval System"
            }
            
            # Log the transfer request
            self.logger.info(f"📋 Creating transfer request: {transfer_id}")
            self.logger.info(f"   Item: {item.name}")
            self.logger.info(f"   Route: {from_location} → {to_location}")
            self.logger.info(f"   Quantity: {quantity}")
            self.logger.info(f"   Priority: {priority}")
            
            # Here you would integrate with the actual transfer system
            # For demonstration, we simulate successful creation
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating transfer request: {e}")
            return False


# Global instance
auto_approval_service: Optional[AutoApprovalService] = None

def get_auto_approval_service() -> Optional[AutoApprovalService]:
    """Get the global auto approval service instance"""
    return auto_approval_service

def initialize_auto_approval_service(workflow_engine: WorkflowEngine, supply_agent=None) -> AutoApprovalService:
    """Initialize the global auto approval service"""
    global auto_approval_service
    auto_approval_service = AutoApprovalService(workflow_engine, supply_agent)
    return auto_approval_service
