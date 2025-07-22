"""
Autonomous Supply Management System
Automatically monitors inventory, handles transfers, and creates purchase orders
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import uuid
from sqlalchemy import text

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutonomousSupplyManager:
    """
    Autonomous supply management system that:
    1. Monitors inventory levels across all locations
    2. Automatically transfers stock between locations when possible
    3. Creates purchase orders when stock is not available internally
    4. Updates database with all transactions
    5. Queues orders for approval in workflow system
    """
    
    def __init__(self, db_integration, enhanced_agent):
        self.db_integration = db_integration
        self.enhanced_agent = enhanced_agent
        self.is_running = False
        self.check_interval = 300  # Check every 5 minutes
        self.pending_approvals = []
        
    async def start_monitoring(self):
        """Start the autonomous monitoring loop"""
        self.is_running = True
        logger.info("🤖 Starting Autonomous Supply Management System...")
        
        while self.is_running:
            try:
                await self.check_and_process_inventory()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"❌ Error in autonomous monitoring: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop the autonomous monitoring"""
        self.is_running = False
        logger.info("🛑 Autonomous Supply Management System stopped")
    
    async def check_and_process_inventory(self):
        """Main logic: Check inventory and process low stock items"""
        logger.info("🔍 Checking inventory levels across all locations...")
        
        try:
            # Get current inventory from database
            inventory_data = await self.db_integration.get_inventory_data()
            items = inventory_data.get('items', [])
            
            low_stock_items = []
            critical_items = []
            
            # Identify low stock and critical items
            for item in items:
                current_stock = item.get('current_stock', 0)
                minimum_stock = item.get('minimum_stock', 0)
                reorder_point = item.get('reorder_point', minimum_stock)
                
                if current_stock <= minimum_stock:
                    critical_items.append(item)
                elif current_stock <= reorder_point:
                    low_stock_items.append(item)
            
            logger.info(f"📊 Found {len(critical_items)} critical items and {len(low_stock_items)} low stock items")
            
            # Process critical items first
            for item in critical_items:
                await self.process_low_stock_item(item, priority="critical")
            
            # Process low stock items
            for item in low_stock_items:
                await self.process_low_stock_item(item, priority="normal")
            
            # Proactively redistribute surplus to create safety buffers
            await self.redistribute_surplus_for_safety_buffers()
                
        except Exception as e:
            logger.error(f"❌ Error checking inventory: {e}")
    
    async def process_low_stock_item(self, item, priority="normal"):
        """Process a single low stock item"""
        item_id = item.get('item_id')
        item_name = item.get('name', f'Item {item_id}')
        location_id = item.get('location_id')
        current_stock = item.get('current_stock', 0)
        minimum_stock = item.get('minimum_stock', 0)
        reorder_point = item.get('reorder_point', minimum_stock)
        
        # Calculate base needed quantity (just to reach minimum)
        base_needed = max(minimum_stock - current_stock, reorder_point - current_stock, 1)
        
        logger.info(f"🔄 Processing {priority} item: {item_name} in {location_id} (base need: {base_needed} units)")
        
        # Step 1: Try to find stock in other locations (start with base need)
        available_locations = await self.find_available_stock(item_id, 1, exclude_location=location_id)  # Start with minimum check
        
        if available_locations:
            # Calculate multi-source transfer strategy
            total_available = sum([loc['surplus'] for loc in available_locations])
            target_quantity = min(base_needed + 10, total_available)  # What we want to transfer
            
            logger.info(f"📦 Found {len(available_locations)} source locations with {total_available} total surplus")
            logger.info(f"🎯 Target transfer quantity: {target_quantity} units")
            
            # Plan multi-source transfers
            transfer_plan = await self.plan_multi_source_transfers(available_locations, target_quantity)
            
            if transfer_plan:
                total_to_transfer = sum([t['transfer_amount'] for t in transfer_plan])
                
                # Execute transfers
                await self.execute_multi_transfer_plan(item, transfer_plan, priority)
                
                # Check if we still need more stock after transfers
                remaining_needed = max(0, base_needed + 5 - total_to_transfer)  # Reduced buffer after transfer
                
                if remaining_needed > 0:
                    logger.info(f"📋 After transfer, still need {remaining_needed} units - creating reduced purchase order")
                    await self.create_auto_purchase_order(item, remaining_needed, priority, note=f"Partial need after {total_to_transfer} unit transfer")
                else:
                    logger.info(f"✅ Transfer fully satisfied needs - no purchase order required")
            else:
                logger.warning(f"⚠️ Could not create viable transfer plan")
                needed_quantity = base_needed + 10
                await self.create_auto_purchase_order(item, needed_quantity, priority)
        else:
            # Step 3: No transfer possible, create purchase order with buffer
            needed_quantity = base_needed + 10  # Add buffer for purchase orders
            await self.create_auto_purchase_order(item, needed_quantity, priority)
    
    async def plan_multi_source_transfers(self, available_locations, target_quantity):
        """Plan transfers from multiple source locations to meet target quantity"""
        try:
            transfer_plan = []
            remaining_needed = target_quantity
            
            # Sort by surplus amount (most surplus first)
            sorted_locations = sorted(available_locations, key=lambda x: x['surplus'], reverse=True)
            
            for source_location in sorted_locations:
                if remaining_needed <= 0:
                    break
                
                # Calculate how much we can take from this location
                available_from_source = source_location['surplus']
                transfer_amount = min(remaining_needed, available_from_source)
                
                if transfer_amount > 0:
                    transfer_plan.append({
                        'source_location': source_location,
                        'transfer_amount': transfer_amount
                    })
                    remaining_needed -= transfer_amount
                    
                    logger.info(f"� Plan: {transfer_amount} units from {source_location['location_id']} (has {available_from_source} surplus)")
            
            total_planned = sum([t['transfer_amount'] for t in transfer_plan])
            logger.info(f"📊 Transfer plan: {total_planned} units from {len(transfer_plan)} locations")
            
            return transfer_plan if total_planned > 0 else None
            
        except Exception as e:
            logger.error(f"❌ Error planning multi-source transfers: {e}")
            return None
    
    async def execute_multi_transfer_plan(self, item, transfer_plan, priority):
        """Execute multiple transfers according to the plan"""
        try:
            item_id = item.get('item_id')
            item_name = item.get('name', f'Item {item_id}')
            destination_location = item.get('location_id')
            
            total_transferred = 0
            transfer_ids = []
            
            for i, transfer in enumerate(transfer_plan):
                source_location = transfer['source_location']
                transfer_amount = transfer['transfer_amount']
                source_location_id = source_location['location_id']
                
                # Create unique transfer ID for each transfer
                transfer_id = f"MULTI-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}-{i+1}"
                
                # Update source location (reduce stock)
                await self.update_inventory_stock(item_id, source_location_id, -transfer_amount, 
                                                f"Multi-transfer {i+1}/{len(transfer_plan)} to {destination_location}")
                
                # Update destination location (increase stock) 
                await self.update_inventory_stock(item_id, destination_location, transfer_amount,
                                                f"Multi-transfer {i+1}/{len(transfer_plan)} from {source_location_id}")
                
                # Record individual transfer
                await self.record_transfer(transfer_id, item_id, source_location_id, destination_location, 
                                         transfer_amount, priority)
                
                total_transferred += transfer_amount
                transfer_ids.append(transfer_id)
                
                logger.info(f"✅ Multi-transfer {i+1}/{len(transfer_plan)}: {transfer_amount} units from {source_location_id}")
            
            # Create consolidated notification
            await self.add_to_workflow_notifications({
                "type": "multi_auto_transfer",
                "transfer_ids": transfer_ids,
                "item_id": item_id,
                "item_name": item_name,
                "to_location": destination_location,
                "total_quantity": total_transferred,
                "source_count": len(transfer_plan),
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Transferred {total_transferred} units from {len(transfer_plan)} locations"
            })
            
            logger.info(f"🎉 Multi-transfer completed: {total_transferred} units from {len(transfer_plan)} locations to {destination_location}")
            
        except Exception as e:
            logger.error(f"❌ Error executing multi-transfer plan: {e}")

    async def redistribute_surplus_for_safety_buffers(self):
        """Proactively redistribute surplus stock to create safety buffers at minimum locations"""
        try:
            # Get all items with their location distributions
            async with self.db_integration.engine.begin() as conn:
                query = text("""
                    SELECT item_id, location_id, quantity, minimum_threshold, maximum_capacity,
                           (quantity - minimum_threshold) as surplus_deficit
                    FROM item_locations 
                    WHERE quantity >= minimum_threshold
                    ORDER BY item_id, surplus_deficit DESC
                """)
                
                result = await conn.execute(query)
                locations_data = result.fetchall()
                
                if not locations_data:
                    return
                
                # Group by item_id
                items_by_id = {}
                for row in locations_data:
                    item_id = row[0]
                    if item_id not in items_by_id:
                        items_by_id[item_id] = []
                    
                    items_by_id[item_id].append({
                        'location_id': row[1],
                        'quantity': row[2],
                        'minimum_threshold': row[3],
                        'maximum_capacity': row[4],
                        'surplus_deficit': row[5]
                    })
                
                # Process each item for surplus redistribution
                for item_id, locations in items_by_id.items():
                    await self.process_item_surplus_redistribution(item_id, locations)
                    
        except Exception as e:
            logger.error(f"❌ Error redistributing surplus for safety buffers: {e}")

    async def process_item_surplus_redistribution(self, item_id, locations):
        """Process surplus redistribution for a specific item"""
        try:
            # Find locations with surplus (more than minimum + safety buffer)
            surplus_locations = []
            at_minimum_locations = []
            
            # Consider locations with surplus > 3 as candidates for giving
            # Consider locations with surplus = 0 as candidates for receiving
            for loc in locations:
                if loc['surplus_deficit'] > 3:  # Has significant surplus
                    surplus_locations.append(loc)
                elif loc['surplus_deficit'] == 0:  # Exactly at minimum - vulnerable
                    at_minimum_locations.append(loc)
            
            if not surplus_locations or not at_minimum_locations:
                return  # No redistribution opportunity
            
            # Get item name for logging
            item_name = await self.get_item_name(item_id)
            
            logger.info(f"🔄 Analyzing surplus redistribution for {item_name} ({item_id})")
            logger.info(f"   Surplus locations: {len(surplus_locations)}")
            logger.info(f"   At-minimum locations: {len(at_minimum_locations)}")
            
            # Plan redistribution: give 1-2 units from each surplus location to at-minimum locations
            redistribution_plan = []
            
            for surplus_loc in surplus_locations:
                available_to_give = min(2, surplus_loc['surplus_deficit'] - 2)  # Leave at least 2 buffer
                
                if available_to_give <= 0:
                    continue
                
                # Find at-minimum locations that can receive (haven't exceeded capacity)
                for at_min_loc in at_minimum_locations:
                    if available_to_give <= 0:
                        break
                    
                    # Check if location can receive without exceeding capacity
                    new_quantity = at_min_loc['quantity'] + 1
                    if new_quantity <= at_min_loc['maximum_capacity']:
                        redistribution_plan.append({
                            'from_location': surplus_loc['location_id'],
                            'to_location': at_min_loc['location_id'],
                            'quantity': 1
                        })
                        available_to_give -= 1
                        at_min_loc['quantity'] += 1  # Update for next iteration
            
            # Execute redistribution plan
            if redistribution_plan:
                logger.info(f"🎯 Executing safety buffer redistribution for {item_name}")
                logger.info(f"   Planned transfers: {len(redistribution_plan)}")
                
                for transfer in redistribution_plan:
                    await self.execute_safety_buffer_transfer(
                        item_id, 
                        item_name,
                        transfer['from_location'],
                        transfer['to_location'],
                        transfer['quantity']
                    )
                    
                    # Small delay to avoid overwhelming the system
                    await asyncio.sleep(0.5)
                
                logger.info(f"✅ Completed safety buffer redistribution for {item_name}")
            
        except Exception as e:
            logger.error(f"❌ Error processing surplus redistribution for {item_id}: {e}")

    async def execute_safety_buffer_transfer(self, item_id, item_name, from_location, to_location, quantity):
        """Execute a single safety buffer transfer"""
        try:
            # Generate transfer ID
            transfer_id = f"SAFETY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"
            
            # Update stock levels
            async with self.db_integration.engine.begin() as conn:
                # Decrease source location
                update_source = text("""
                    UPDATE item_locations 
                    SET quantity = quantity - :quantity,
                        last_updated = :timestamp
                    WHERE item_id = :item_id AND location_id = :location_id
                """)
                
                await conn.execute(update_source, {
                    "quantity": quantity,
                    "timestamp": datetime.now(),
                    "item_id": item_id,
                    "location_id": from_location
                })
                
                # Increase destination location
                update_dest = text("""
                    UPDATE item_locations 
                    SET quantity = quantity + :quantity,
                        last_updated = :timestamp
                    WHERE item_id = :item_id AND location_id = :location_id
                """)
                
                await conn.execute(update_dest, {
                    "quantity": quantity,
                    "timestamp": datetime.now(),
                    "item_id": item_id,
                    "location_id": to_location
                })
            
            # Record transfer
            await self.record_transfer(transfer_id, item_id, from_location, to_location, quantity, "preventive")
            
            # Add workflow notification
            await self.add_to_workflow_notifications({
                "type": "safety_buffer_transfer",
                "transfer_id": transfer_id,
                "item_id": item_id,
                "item_name": item_name,
                "from_location": from_location,
                "to_location": to_location,
                "quantity": quantity,
                "priority": "preventive",
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "details": f"Proactive safety buffer: {quantity} units to prevent low stock warning"
            })
            
            logger.info(f"✅ Safety buffer transfer: {quantity} {item_name} from {from_location} → {to_location}")
            
        except Exception as e:
            logger.error(f"❌ Error executing safety buffer transfer: {e}")

    async def get_item_name(self, item_id):
        """Get item name from database"""
        try:
            async with self.db_integration.engine.begin() as conn:
                query = text("SELECT name FROM inventory_items WHERE item_id = :item_id")
                result = await conn.execute(query, {"item_id": item_id})
                row = result.fetchone()
                return row[0] if row else f"Item {item_id}"
        except Exception as e:
            logger.error(f"❌ Error getting item name: {e}")
            return f"Item {item_id}"
    
    async def find_available_stock(self, item_id, needed_quantity, exclude_location=None):
        """Find locations that have available stock for the item"""
        try:
            # Query item_locations table for same item in other locations
            async with self.db_integration.engine.begin() as conn:
                query = text("""
                    SELECT location_id, quantity, minimum_threshold, maximum_capacity
                    FROM item_locations 
                    WHERE item_id = :item_id 
                    AND location_id != :exclude_location
                    AND quantity > minimum_threshold + :needed_quantity
                    ORDER BY (quantity - minimum_threshold) DESC
                """)
                
                result = await conn.execute(query, {
                    "item_id": item_id,
                    "exclude_location": exclude_location or "",
                    "needed_quantity": needed_quantity
                })
                
                available_locations = []
                for row in result.fetchall():
                    surplus = row[1] - row[2]  # quantity - minimum_threshold
                    if surplus >= needed_quantity:
                        available_locations.append({
                            "location_id": row[0],
                            "current_stock": row[1],
                            "minimum_stock": row[2],
                            "surplus": surplus
                        })
                
                logger.info(f"📍 Found {len(available_locations)} locations with available stock for {item_id}")
                return available_locations
                
        except Exception as e:
            logger.error(f"❌ Error finding available stock: {e}")
            return []
    
    async def perform_auto_transfer(self, item, source_location, quantity, priority):
        """Perform automatic inter-location transfer"""
        try:
            item_id = item.get('item_id')
            item_name = item.get('name', f'Item {item_id}')
            destination_location = item.get('location_id')
            source_location_id = source_location['location_id']
            
            # Create transfer ID
            transfer_id = f"AUTO-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
            
            # Update source location (reduce stock)
            await self.update_inventory_stock(item_id, source_location_id, -quantity, f"Auto transfer to {destination_location}")
            
            # Update destination location (increase stock)
            await self.update_inventory_stock(item_id, destination_location, quantity, f"Auto transfer from {source_location_id}")
            
            # Record transfer in database
            await self.record_transfer(transfer_id, item_id, source_location_id, destination_location, quantity, priority)
            
            logger.info(f"✅ Auto transfer completed: {quantity} units of {item_name} from {source_location_id} to {destination_location}")
            
            # Add to autonomous workflow for notification
            await self.add_to_workflow_notifications({
                "type": "auto_transfer",
                "transfer_id": transfer_id,
                "item_id": item_id,
                "item_name": item_name,
                "from_location": source_location_id,
                "to_location": destination_location,
                "quantity": quantity,
                "priority": priority,
                "timestamp": datetime.now().isoformat(),
                "status": "completed"
            })
            
        except Exception as e:
            logger.error(f"❌ Error performing auto transfer: {e}")
    
    async def create_auto_purchase_order(self, item, quantity, priority, note=""):
        """Create automatic purchase order when no internal stock available"""
        try:
            item_id = item.get('item_id')
            item_name = item.get('name', f'Item {item_id}')
            location_id = item.get('location_id')
            unit_cost = item.get('unit_cost', 10.0)
            
            # Create purchase order through enhanced agent
            po_items = [{
                'item_id': item_id,
                'quantity': quantity,
                'unit_cost': unit_cost
            }]
            
            base_reason = f"Autonomous reorder - {priority} shortage in {location_id}"
            reason = f"{base_reason}. {note}" if note else base_reason
            result = self.enhanced_agent.create_purchase_order_professional(
                items=po_items,
                reason=reason
            )
            
            if result.get("success"):
                po_id = result.get("po_id")
                total_amount = result.get("total_amount")
                
                # Record purchase order in database for approval workflow
                await self.record_purchase_order_for_approval(po_id, item, quantity, total_amount, priority, reason)
                
                logger.info(f"✅ Auto purchase order created: {po_id} for {quantity} units of {item_name} (${total_amount})")
                
                # Add to autonomous workflow for approval
                await self.add_to_workflow_approvals({
                    "type": "auto_purchase_order",
                    "po_id": po_id,
                    "item_id": item_id,
                    "item_name": item_name,
                    "location_id": location_id,
                    "quantity": quantity,
                    "total_amount": total_amount,
                    "priority": priority,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                    "status": "pending_approval",
                    "auto_generated": True
                })
            else:
                logger.error(f"❌ Failed to create auto purchase order: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"❌ Error creating auto purchase order: {e}")
    
    async def update_inventory_stock(self, item_id, location_id, quantity_change, reason):
        """Update inventory stock in item_locations table"""
        try:
            async with self.db_integration.engine.begin() as conn:
                # Update the stock in item_locations table
                update_query = text("""
                    UPDATE item_locations 
                    SET quantity = GREATEST(0, quantity + :quantity_change),
                        last_updated = :timestamp
                    WHERE item_id = :item_id AND location_id = :location_id
                """)
                
                await conn.execute(update_query, {
                    "quantity_change": quantity_change,
                    "item_id": item_id,
                    "location_id": location_id,
                    "timestamp": datetime.now()
                })
                
                logger.info(f"📊 Updated stock for {item_id} in {location_id}: {quantity_change:+d} units")
                
        except Exception as e:
            logger.error(f"❌ Error updating inventory stock: {e}")
    
    async def record_transfer(self, transfer_id, item_id, from_location, to_location, quantity, priority):
        """Record transfer in database"""
        try:
            async with self.db_integration.engine.begin() as conn:
                # Check if transfers table exists, create if not
                create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS autonomous_transfers (
                        transfer_id VARCHAR(100) PRIMARY KEY,
                        item_id VARCHAR(50),
                        from_location VARCHAR(50),
                        to_location VARCHAR(50),
                        quantity INTEGER,
                        priority VARCHAR(20),
                        reason TEXT,
                        status VARCHAR(20) DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await conn.execute(create_table_query)
                
                # Insert transfer record
                insert_query = text("""
                    INSERT INTO autonomous_transfers 
                    (transfer_id, item_id, from_location, to_location, quantity, priority, reason, status)
                    VALUES (:transfer_id, :item_id, :from_location, :to_location, :quantity, :priority, :reason, 'completed')
                """)
                
                await conn.execute(insert_query, {
                    "transfer_id": transfer_id,
                    "item_id": item_id,
                    "from_location": from_location,
                    "to_location": to_location,
                    "quantity": quantity,
                    "priority": priority,
                    "reason": f"Autonomous transfer - {priority} shortage"
                })
                
        except Exception as e:
            logger.error(f"❌ Error recording transfer: {e}")
    
    async def record_purchase_order_for_approval(self, po_id, item, quantity, total_amount, priority, reason):
        """Record purchase order in database for approval workflow"""
        try:
            async with self.db_integration.engine.begin() as conn:
                # Create table if not exists
                create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS autonomous_purchase_orders (
                        po_id VARCHAR(100) PRIMARY KEY,
                        item_id VARCHAR(50),
                        item_name VARCHAR(200),
                        location_id VARCHAR(50),
                        quantity INTEGER,
                        unit_cost DECIMAL(10,2),
                        total_amount DECIMAL(10,2),
                        priority VARCHAR(20),
                        reason TEXT,
                        status VARCHAR(20) DEFAULT 'pending_approval',
                        auto_generated BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        approved_at TIMESTAMP NULL,
                        approved_by VARCHAR(100) NULL
                    )
                """)
                await conn.execute(create_table_query)
                
                # Insert purchase order
                insert_query = text("""
                    INSERT INTO autonomous_purchase_orders 
                    (po_id, item_id, item_name, location_id, quantity, unit_cost, total_amount, priority, reason)
                    VALUES (:po_id, :item_id, :item_name, :location_id, :quantity, :unit_cost, :total_amount, :priority, :reason)
                """)
                
                await conn.execute(insert_query, {
                    "po_id": po_id,
                    "item_id": item.get('item_id'),
                    "item_name": item.get('name', f"Item {item.get('item_id')}"),
                    "location_id": item.get('location_id'),
                    "quantity": quantity,
                    "unit_cost": item.get('unit_cost', 10.0),
                    "total_amount": total_amount,
                    "priority": priority,
                    "reason": reason
                })
                
        except Exception as e:
            logger.error(f"❌ Error recording purchase order for approval: {e}")
    
    async def add_to_workflow_notifications(self, notification_data):
        """Add transfer notification to autonomous workflow"""
        try:
            # Store in database for workflow system
            async with self.db_integration.engine.begin() as conn:
                create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS autonomous_workflow_notifications (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(50),
                        data JSONB,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await conn.execute(create_table_query)
                
                # Add updated_at column if it doesn't exist (for existing tables)
                alter_table_query = text("""
                    ALTER TABLE autonomous_workflow_notifications 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                """)
                await conn.execute(alter_table_query)
                
                insert_query = text("""
                    INSERT INTO autonomous_workflow_notifications (type, data)
                    VALUES (:type, :data)
                """)
                
                await conn.execute(insert_query, {
                    "type": notification_data["type"],
                    "data": json.dumps(notification_data)
                })
                
        except Exception as e:
            logger.error(f"❌ Error adding workflow notification: {e}")
    
    async def add_to_workflow_approvals(self, approval_data):
        """Add purchase order to autonomous workflow for approval"""
        try:
            # Store in database for approval workflow
            async with self.db_integration.engine.begin() as conn:
                create_table_query = text("""
                    CREATE TABLE IF NOT EXISTS autonomous_workflow_approvals (
                        id SERIAL PRIMARY KEY,
                        type VARCHAR(50),
                        po_id VARCHAR(100),
                        data JSONB,
                        status VARCHAR(20) DEFAULT 'pending_approval',
                        priority VARCHAR(20) DEFAULT 'normal',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        approved_at TIMESTAMP NULL,
                        approved_by VARCHAR(100) NULL
                    )
                """)
                await conn.execute(create_table_query)
                
                insert_query = text("""
                    INSERT INTO autonomous_workflow_approvals (type, po_id, data, priority)
                    VALUES (:type, :po_id, :data, :priority)
                """)
                
                await conn.execute(insert_query, {
                    "type": approval_data["type"],
                    "po_id": approval_data["po_id"],
                    "data": json.dumps(approval_data),
                    "priority": approval_data["priority"]
                })
                
            # Also add to in-memory pending approvals for immediate access
            self.pending_approvals.append(approval_data)
            
        except Exception as e:
            logger.error(f"❌ Error adding workflow approval: {e}")
    
    async def get_pending_approvals(self):
        """Get all pending approvals for the autonomous workflow page"""
        try:
            async with self.db_integration.engine.begin() as conn:
                query = text("""
                    SELECT po_id, data, priority, created_at
                    FROM autonomous_workflow_approvals 
                    WHERE status = 'pending_approval'
                    ORDER BY 
                        CASE priority 
                            WHEN 'critical' THEN 1 
                            WHEN 'high' THEN 2 
                            ELSE 3 
                        END,
                        created_at ASC
                """)
                
                result = await conn.execute(query)
                approvals = []
                
                for row in result.fetchall():
                    # Handle JSONB data - it might already be a dict or need parsing
                    data = row[1] if isinstance(row[1], dict) else (json.loads(row[1]) if row[1] else {})
                    approvals.append({
                        "po_id": row[0],
                        "data": data,
                        "priority": row[2],
                        "created_at": row[3].isoformat() if row[3] else None
                    })
                
                return approvals
                
        except Exception as e:
            logger.error(f"❌ Error getting pending approvals: {e}")
            return []
    
    async def get_autonomous_activities(self, limit=20):
        """Get recent autonomous activities (transfers and purchase orders)"""
        try:
            activities = []
            
            async with self.db_integration.engine.begin() as conn:
                # Get recent transfers
                transfers_query = text("""
                    SELECT 
                        'auto_transfer' as action_type,
                        item_id,
                        CONCAT('Transfer: ', quantity, ' units from ', from_location, ' to ', to_location) as reason,
                        from_location || ' → ' || to_location as location_details,
                        quantity,
                        created_at as timestamp,
                        status,
                        priority
                    FROM autonomous_transfers 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """)
                
                transfer_results = await conn.execute(transfers_query, {"limit": limit})
                
                for row in transfer_results.fetchall():
                    # Get item name from inventory_items
                    item_query = text("SELECT name FROM inventory_items WHERE item_id = :item_id LIMIT 1")
                    item_result = await conn.execute(item_query, {"item_id": row[1]})
                    item_row = item_result.fetchone()
                    item_name = item_row[0] if item_row else f"Item {row[1]}"
                    
                    activities.append({
                        "action_type": row[0],
                        "item_id": row[1],
                        "item_name": item_name,
                        "reason": row[2],
                        "location_details": row[3],
                        "quantity": row[4],
                        "timestamp": row[5].isoformat() if row[5] else None,
                        "status": row[6],
                        "priority": row[7]
                    })
                
                # Get recent purchase orders
                po_query = text("""
                    SELECT 
                        'auto_purchase_order' as action_type,
                        item_id,
                        CONCAT('Purchase Order: ', quantity, ' units for $', total_amount) as reason,
                        location_id,
                        quantity,
                        created_at as timestamp,
                        status,
                        priority,
                        po_id,
                        total_amount
                    FROM autonomous_purchase_orders 
                    ORDER BY created_at DESC 
                    LIMIT :limit
                """)
                
                po_results = await conn.execute(po_query, {"limit": limit})
                
                for row in po_results.fetchall():
                    # Get item name from inventory_items
                    item_query = text("SELECT name FROM inventory_items WHERE item_id = :item_id LIMIT 1")
                    item_result = await conn.execute(item_query, {"item_id": row[1]})
                    item_row = item_result.fetchone()
                    item_name = item_row[0] if item_row else f"Item {row[1]}"
                    
                    activities.append({
                        "action_type": row[0],
                        "item_id": row[1],
                        "item_name": item_name,
                        "reason": row[2],
                        "location_details": row[3],
                        "quantity": row[4],
                        "timestamp": row[5].isoformat() if row[5] else None,
                        "status": row[6],
                        "priority": row[7],
                        "po_id": row[8],
                        "total_amount": float(row[9]) if row[9] else 0.0
                    })
            
            # Sort all activities by timestamp (most recent first)
            activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
            
            return activities[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error getting autonomous activities: {e}")
            return []

    async def approve_purchase_order(self, po_id, approved_by="system"):
        """Approve a purchase order and update database"""
        try:
            async with self.db_integration.engine.begin() as conn:
                # Update approval status
                update_query = text("""
                    UPDATE autonomous_workflow_approvals 
                    SET status = 'approved', 
                        approved_at = :timestamp,
                        approved_by = :approved_by
                    WHERE po_id = :po_id
                """)
                
                await conn.execute(update_query, {
                    "po_id": po_id,
                    "timestamp": datetime.now(),
                    "approved_by": approved_by
                })
                
                # Also update the purchase order table
                update_po_query = text("""
                    UPDATE autonomous_purchase_orders 
                    SET status = 'approved',
                        approved_at = :timestamp,
                        approved_by = :approved_by
                    WHERE po_id = :po_id
                """)
                
                await conn.execute(update_po_query, {
                    "po_id": po_id,
                    "timestamp": datetime.now(),
                    "approved_by": approved_by
                })
                
            logger.info(f"✅ Purchase order {po_id} approved by {approved_by}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error approving purchase order: {e}")
            return False

# Global instance
autonomous_manager = None

def get_autonomous_manager():
    """Get the global autonomous manager instance"""
    return autonomous_manager

def initialize_autonomous_manager(db_integration, enhanced_agent):
    """Initialize the global autonomous manager"""
    global autonomous_manager
    autonomous_manager = AutonomousSupplyManager(db_integration, enhanced_agent)
    return autonomous_manager
