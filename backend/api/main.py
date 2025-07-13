"""
FastAPI Backend for Supply Inventory Agent
Provides RESTful API endpoints for the hospital supply management system
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime
import logging

# Import the Supply Inventory Agent
import sys
import os
# Add the project root to the path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from agents.supply_inventory_agent.supply_agent import SupplyInventoryAgent, SupplyCategory, AlertLevel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Hospital Supply Inventory API",
    description="RESTful API for managing hospital supply inventory with autonomous agent",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
supply_agent: Optional[SupplyInventoryAgent] = None
websocket_connections: List[WebSocket] = []

# Pydantic models for API requests/responses
class InventoryUpdate(BaseModel):
    item_id: str
    quantity_change: int
    reason: str = "Manual update"

class SupplyItemCreate(BaseModel):
    name: str
    category: str
    current_quantity: int
    minimum_threshold: int
    maximum_capacity: int
    unit_cost: float
    supplier_id: str
    location: str
    expiration_date: Optional[str] = None

class AlertUpdate(BaseModel):
    alert_id: str
    resolved: bool

class ProcurementRecommendation(BaseModel):
    item_id: str
    item_name: str
    current_quantity: int
    recommended_order: int
    supplier: str
    estimated_cost: float
    urgency: str

class PurchaseOrderRequest(BaseModel):
    recommendations: List[ProcurementRecommendation]

class PurchaseOrderItem(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    unit_cost: float
    total_cost: float
    supplier: str

class PurchaseOrder(BaseModel):
    order_id: str
    supplier: str
    items: List[PurchaseOrderItem]
    total_cost: float
    order_date: str
    expected_delivery: str
    status: str = "pending"

@app.on_event("startup")
async def startup_event():
    """Initialize the supply agent on startup"""
    global supply_agent
    try:
        supply_agent = SupplyInventoryAgent()
        await supply_agent.initialize()
        
        # Start monitoring in background
        asyncio.create_task(supply_agent.start_monitoring())
        
        # Start WebSocket broadcasting
        asyncio.create_task(broadcast_updates())
        
        logger.info("Supply Inventory Agent started successfully")
    except Exception as e:
        logger.error(f"Failed to start Supply Inventory Agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean shutdown of the supply agent"""
    global supply_agent
    if supply_agent:
        await supply_agent.stop_monitoring()
        logger.info("Supply Inventory Agent stopped")

async def broadcast_updates():
    """Broadcast real-time updates to connected WebSocket clients"""
    while True:
        try:
            if supply_agent and websocket_connections:
                dashboard_data = await supply_agent.get_dashboard_data()
                message = json.dumps({
                    "type": "dashboard_update",
                    "data": dashboard_data,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Send to all connected clients
                disconnected = []
                for websocket in websocket_connections:
                    try:
                        await websocket.send_text(message)
                    except:
                        disconnected.append(websocket)
                
                # Remove disconnected clients
                for ws in disconnected:
                    websocket_connections.remove(ws)
            
            await asyncio.sleep(5)  # Broadcast every 5 seconds
        except Exception as e:
            logger.error(f"Error in broadcast_updates: {e}")
            await asyncio.sleep(10)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_running": supply_agent.is_running if supply_agent else False
    }

# Dashboard data endpoint
@app.get("/api/dashboard")
async def get_dashboard_data():
    """Get complete dashboard data"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        data = await supply_agent.get_dashboard_data()
        return JSONResponse(content=data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Inventory endpoints
@app.get("/api/inventory")
async def get_inventory():
    """Get all inventory items"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        data = await supply_agent.get_dashboard_data()
        return JSONResponse(content=data["inventory"])
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/{item_id}")
async def get_inventory_item(item_id: str):
    """Get specific inventory item"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    if item_id not in supply_agent.inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item = supply_agent.inventory[item_id]
    return {
        "id": item.id,
        "name": item.name,
        "category": item.category.value,
        "current_quantity": item.current_quantity,
        "minimum_threshold": item.minimum_threshold,
        "maximum_capacity": item.maximum_capacity,
        "unit_cost": item.unit_cost,
        "supplier_id": item.supplier_id,
        "location": item.location,
        "expiration_date": item.expiration_date.isoformat() if item.expiration_date else None,
        "last_updated": item.last_updated.isoformat(),
        "is_low_stock": item.is_low_stock,
        "is_expired": item.is_expired,
        "days_until_expiry": item.days_until_expiry
    }

@app.post("/api/inventory/update")
async def update_inventory(update: InventoryUpdate):
    """Update inventory quantity"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    if update.item_id not in supply_agent.inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    
    try:
        await supply_agent.update_inventory(
            update.item_id, 
            update.quantity_change, 
            update.reason
        )
        return {"message": "Inventory updated successfully"}
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Alerts endpoints
@app.get("/api/alerts")
async def get_alerts():
    """Get all active alerts"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        data = await supply_agent.get_dashboard_data()
        return JSONResponse(content=data["alerts"])
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/alerts/resolve")
async def resolve_alert(alert_update: AlertUpdate):
    """Mark an alert as resolved"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    # Find and update the alert
    alert_found = False
    for alert in supply_agent.alerts:
        if alert.id == alert_update.alert_id:
            alert.resolved = alert_update.resolved
            alert_found = True
            break
    
    if not alert_found:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert updated successfully"}

# Procurement recommendations endpoint
@app.get("/api/procurement/recommendations")
async def get_procurement_recommendations():
    """Get procurement recommendations"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        recommendations = await supply_agent._generate_procurement_recommendations()
        return JSONResponse(content=recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Purchase orders endpoint
@app.post("/api/purchase-orders/generate")
async def generate_purchase_orders(request: PurchaseOrderRequest):
    """Generate purchase orders from procurement recommendations"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        import uuid
        from datetime import timedelta
        
        # Group recommendations by supplier
        supplier_groups = {}
        for rec in request.recommendations:
            supplier = rec.supplier
            if supplier not in supplier_groups:
                supplier_groups[supplier] = []
            supplier_groups[supplier].append(rec)
        
        # Generate purchase orders for each supplier
        purchase_orders = []
        for supplier, items in supplier_groups.items():
            order_id = f"PO-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Calculate delivery date based on supplier lead time
            suppliers_data = await supply_agent.get_suppliers()
            lead_time = 7  # Default lead time
            for sup_id, sup_data in suppliers_data.items():
                if sup_data.get('name') == supplier:
                    lead_time = sup_data.get('lead_time_days', 7)
                    break
            
            expected_delivery = (datetime.now() + timedelta(days=lead_time)).strftime('%Y-%m-%d')
            
            # Create order items
            order_items = []
            total_cost = 0
            
            for item in items:
                unit_cost = item.estimated_cost / item.recommended_order
                total_item_cost = item.estimated_cost
                
                order_items.append(PurchaseOrderItem(
                    item_id=item.item_id,
                    item_name=item.item_name,
                    quantity=item.recommended_order,
                    unit_cost=unit_cost,
                    total_cost=total_item_cost,
                    supplier=supplier
                ))
                total_cost += total_item_cost
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                order_id=order_id,
                supplier=supplier,
                items=order_items,
                total_cost=total_cost,
                order_date=datetime.now().strftime('%Y-%m-%d'),
                expected_delivery=expected_delivery,
                status="pending"
            )
            
            purchase_orders.append(purchase_order)
        
        logger.info(f"Generated {len(purchase_orders)} purchase orders")
        return JSONResponse(content=[order.dict() for order in purchase_orders])
        
    except Exception as e:
        logger.error(f"Error generating purchase orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Suppliers endpoint
@app.get("/api/suppliers")
async def get_suppliers():
    """Get all suppliers"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    return JSONResponse(content=supply_agent.suppliers)

# Analytics endpoints
@app.get("/api/analytics/usage/{item_id}")
async def get_usage_analytics(item_id: str):
    """Get usage analytics for a specific item"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    if item_id not in supply_agent.inventory:
        raise HTTPException(status_code=404, detail="Item not found")
    
    usage_data = supply_agent.usage_patterns.get(item_id, [])
    avg_usage = supply_agent._get_average_usage(item_id)
    
    return {
        "item_id": item_id,
        "usage_history": usage_data,
        "average_daily_usage": round(avg_usage, 2),
        "total_usage_last_30_days": sum(day["usage"] for day in usage_data)
    }

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    if not supply_agent:
        raise HTTPException(status_code=503, detail="Supply agent not initialized")
    
    try:
        data = await supply_agent.get_dashboard_data()
        
        # Calculate additional analytics
        categories = {}
        for item in data["inventory"]:
            category = item["category"]
            if category not in categories:
                categories[category] = {
                    "count": 0,
                    "total_value": 0,
                    "low_stock_count": 0
                }
            categories[category]["count"] += 1
            categories[category]["total_value"] += item["total_value"]
            if item["is_low_stock"]:
                categories[category]["low_stock_count"] += 1
        
        return {
            "summary": data["summary"],
            "categories": categories,
            "alerts_by_level": {
                level.value: len([
                    alert for alert in data["alerts"] 
                    if alert["level"] == level.value and not alert["resolved"]
                ])
                for level in AlertLevel
            }
        }
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial data
        if supply_agent:
            dashboard_data = await supply_agent.get_dashboard_data()
            await websocket.send_text(json.dumps({
                "type": "initial_data",
                "data": dashboard_data,
                "timestamp": datetime.now().isoformat()
            }))
        
        # Keep connection alive
        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Export the app for deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
