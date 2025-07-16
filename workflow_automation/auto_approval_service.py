"""
Automatic Approval Request Generation Service
Monitors inventory levels and automatically creates approval requests for low stock items
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

from .workflow_engine import WorkflowEngine

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
        
        # Mock inventory data - in production, this would connect to your inventory database
        self.inventory_items: Dict[str, InventoryItem] = {
            "MED001": InventoryItem(
                item_id="MED001",
                name="Surgical Gloves (Box of 100)",
                current_quantity=15,
                minimum_threshold=50,
                location="ICU",
                unit_price=25.00,
                supplier_id="SUP-MEDICAL01",
                category="medical_supplies"
            ),
            "MED002": InventoryItem(
                item_id="MED002",
                name="Paracetamol 500mg (Box)",
                current_quantity=8,
                minimum_threshold=30,
                location="Pharmacy",
                unit_price=12.50,
                supplier_id="SUP-PHARMA01",
                category="pharmaceuticals"
            ),
            "MED003": InventoryItem(
                item_id="MED003",
                name="Sterile Gauze Pads",
                current_quantity=25,
                minimum_threshold=100,
                location="Emergency",
                unit_price=8.75,
                supplier_id="SUP-MEDICAL01",
                category="medical_supplies"
            ),
            "MED004": InventoryItem(
                item_id="MED004",
                name="Disposable Syringes (10ml)",
                current_quantity=12,
                minimum_threshold=200,
                location="ICU",
                unit_price=15.00,
                supplier_id="SUP-MEDICAL01",
                category="medical_supplies"
            )
        }

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
        """Check all inventory items and generate approval requests for low stock"""
        self.logger.info("Checking inventory levels for auto-approval generation")
        
        low_stock_items = []
        emergency_items = []
        
        for item in self.inventory_items.values():
            if self._needs_approval_request(item):
                if self._is_emergency_level(item):
                    emergency_items.append(item)
                else:
                    low_stock_items.append(item)

        # Process emergency items first
        if emergency_items:
            self.logger.warning(f"Found {len(emergency_items)} emergency low stock items")
            for item in emergency_items:
                # First try inter-departmental transfer
                transfer_success = await self._attempt_interdepartmental_transfer(item, is_emergency=True)
                if not transfer_success:
                    # If transfer fails, create supplier request
                    await self._create_approval_request(item, is_emergency=True)

        # Process regular low stock items
        if low_stock_items:
            self.logger.info(f"Found {len(low_stock_items)} low stock items")
            for item in low_stock_items:
                # First try inter-departmental transfer
                transfer_success = await self._attempt_interdepartmental_transfer(item, is_emergency=False)
                if not transfer_success:
                    # If transfer fails, create supplier request
                    await self._create_approval_request(item, is_emergency=False)

        # Clean up old pending requests
        self._cleanup_pending_requests()

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
        Attempt to transfer stock from other departments before requesting from suppliers
        Returns True if transfer was successful, False otherwise
        """
        try:
            if not self.supply_agent:
                return False
            
            # Calculate how much we need
            needed_quantity = low_stock_item.minimum_threshold - low_stock_item.current_quantity
            if is_emergency:
                needed_quantity = max(needed_quantity, int(low_stock_item.minimum_threshold * 1.5))
            
            # Use the supply agent's method to find departments with surplus
            surplus_departments = self.supply_agent.find_departments_with_surplus(
                low_stock_item.name, 
                needed_quantity
            )
            
            if not surplus_departments:
                self.logger.info(f"No surplus stock found for {low_stock_item.name} in other departments")
                return False
            
            # Execute transfers
            total_transferred = 0
            for dept_info in surplus_departments:
                if total_transferred >= needed_quantity:
                    break
                    
                transfer_qty = min(dept_info['can_transfer'], needed_quantity - total_transferred)
                
                if transfer_qty <= 0:
                    continue
                
                # Execute the transfer using supply agent
                result = self.supply_agent.execute_inter_department_transfer(
                    item_name=low_stock_item.name,
                    from_dept=dept_info['department'],
                    to_dept=low_stock_item.location,
                    quantity=transfer_qty
                )
                
                if result['success']:
                    total_transferred += transfer_qty
                    
                    self.logger.info(
                        f"✅ INTER-DEPT TRANSFER: {transfer_qty} units of {low_stock_item.name} "
                        f"from {dept_info['department']} to {low_stock_item.location} "
                        f"(Transfer ID: {result['transfer_id']})"
                    )
                    
                    # Update local tracking
                    low_stock_item.current_quantity += transfer_qty
                else:
                    self.logger.warning(f"Transfer failed: {result['message']}")
            
            # Check if we satisfied the need
            if total_transferred >= needed_quantity * 0.8:  # 80% threshold
                self.logger.info(
                    f"✅ AUTONOMOUS TRANSFER SUCCESS: {total_transferred} units transferred for {low_stock_item.name}, "
                    f"avoiding supplier request"
                )
                return True
            elif total_transferred > 0:
                self.logger.info(
                    f"⚠️ PARTIAL TRANSFER: {total_transferred} units transferred for {low_stock_item.name}, "
                    f"still need {needed_quantity - total_transferred} from supplier"
                )
                
        except Exception as e:
            self.logger.error(f"Error in inter-departmental transfer attempt: {e}")
        
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
