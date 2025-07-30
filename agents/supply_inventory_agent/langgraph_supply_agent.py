"""
LangGraph-based Supply Inventory Agent for Hospital Operations Platform

This agent uses LangGraph and LangChain to autonomously monitor, manage, and optimize 
hospital supply inventory with a state machine approach for better workflow control.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Annotated, TypedDict
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import operator
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# LangGraph and LangChain imports
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import clean data models and enums (no legacy mock data)
from data_models import (
    SupplyCategory, AlertLevel, UserRole, PurchaseOrderStatus, 
    QualityStatus, TransferStatus, InventoryBatch, LocationStock,
    TransferRequest, SupplyItem, User, SupplyAlert, AuditLog, 
    Supplier, PurchaseOrder, Budget, ComplianceRecord
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LangGraph State Definition
class SupplyAgentState(TypedDict):
    """State for the LangGraph Supply Agent"""
    messages: Annotated[List, add_messages]
    inventory: Dict[str, SupplyItem]
    alerts: List[SupplyAlert]
    suppliers: Dict[str, Supplier]
    users: Dict[str, User]
    locations: Dict[str, Dict]
    purchase_orders: Dict[str, PurchaseOrder]
    transfer_requests: Dict[str, TransferRequest]
    audit_logs: List[AuditLog]
    budgets: Dict[str, Budget]
    compliance_records: Dict[str, ComplianceRecord]
    usage_patterns: Dict[str, List]
    transfers: List[Dict]
    current_operation: str
    operation_context: Dict[str, Any]
    monitoring_enabled: bool
    last_check: Optional[datetime]
    agent_status: str
    processed_items: List[str]
    recommendations: List[Dict]
    current_user: Optional[str]

@tool
def check_inventory_levels(item_ids: List[str] = None) -> Dict[str, Any]:
    """Check current inventory levels for specified items or all items"""
    return {
        "action": "check_inventory",
        "item_ids": item_ids or [],
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }

@tool  
def generate_alerts(alert_criteria: Dict[str, Any]) -> Dict[str, Any]:
    """Generate alerts based on specified criteria"""
    return {
        "action": "generate_alerts", 
        "criteria": alert_criteria,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }

@tool
def analyze_usage_patterns(item_id: str, days: int = 30) -> Dict[str, Any]:
    """Analyze usage patterns for inventory optimization"""
    return {
        "action": "analyze_usage",
        "item_id": item_id,
        "analysis_period": days,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }

@tool
def create_purchase_order(supplier_id: str, items: List[Dict]) -> Dict[str, Any]:
    """Create a purchase order for specified items"""
    return {
        "action": "create_purchase_order",
        "supplier_id": supplier_id,
        "items": items,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }

@tool
def process_transfer_request(transfer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process inter-location transfer requests"""
    return {
        "action": "process_transfer",
        "transfer_data": transfer_data,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }

class LangGraphSupplyAgent:
    """
    LangGraph-based Supply Inventory Agent with state machine workflow control
    """
    
    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM with fallback
        self.llm = None
        try:
            # Check for OPENAI_API_KEY
            openai_key = os.environ.get("OPENAI_API_KEY")
            
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
                self.llm = ChatOpenAI(
                    model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
                    temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1"))
                )
                self.logger.info("✅ LLM initialized with provided OpenAI API key")
            elif openai_key:
                self.llm = ChatOpenAI(
                    model=os.environ.get("LLM_MODEL", "gpt-3.5-turbo"),
                    temperature=float(os.environ.get("LLM_TEMPERATURE", "0.1"))
                )
                self.logger.info("✅ LLM initialized with OPENAI_API_KEY from environment")
            else:
                self.logger.warning("⚠️ No OpenAI API key provided, LLM features will be limited")
        except Exception as e:
            self.logger.warning(f"⚠️ LLM initialization failed: {e}. Continuing without LLM features.")
            self.llm = None
        
        # Initialize tools
        self.tools = [
            check_inventory_levels,
            generate_alerts,
            analyze_usage_patterns,
            create_purchase_order,
            process_transfer_request
        ]
        
        # Create LangGraph workflow
        self.workflow = self._create_workflow()
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)
        
        # Agent data - migrated from original agent
        self.inventory: Dict[str, SupplyItem] = {}
        self.alerts: List[SupplyAlert] = []
        self.suppliers: Dict[str, Supplier] = {}
        self.users: Dict[str, User] = {}
        self.locations: Dict[str, Dict] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.transfer_requests: Dict[str, TransferRequest] = {}
        self.audit_logs: List[AuditLog] = []
        self.budgets: Dict[str, Budget] = {}
        self.compliance_records: Dict[str, ComplianceRecord] = {}
        self.usage_patterns: Dict[str, List] = {}
        self.transfers = []
        self.is_running = False
        
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for supply management"""
        
        # Define the workflow graph
        workflow = StateGraph(SupplyAgentState)
        
        # Add nodes for different agent operations
        workflow.add_node("monitor_inventory", self._monitor_inventory_node)
        workflow.add_node("analyze_demand", self._analyze_demand_node)
        workflow.add_node("generate_recommendations", self._generate_recommendations_node)
        workflow.add_node("process_alerts", self._process_alerts_node)
        workflow.add_node("manage_procurement", self._manage_procurement_node)
        workflow.add_node("handle_transfers", self._handle_transfers_node)
        workflow.add_node("update_compliance", self._update_compliance_node)
        workflow.add_node("finalize_operations", self._finalize_operations_node)
        
        # Define workflow edges (state transitions)
        workflow.add_edge(START, "monitor_inventory")
        workflow.add_edge("monitor_inventory", "analyze_demand")
        workflow.add_edge("analyze_demand", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "process_alerts")
        workflow.add_edge("process_alerts", "manage_procurement")
        workflow.add_edge("manage_procurement", "handle_transfers")
        workflow.add_edge("handle_transfers", "update_compliance")
        workflow.add_edge("update_compliance", "finalize_operations")
        workflow.add_edge("finalize_operations", END)
        
        return workflow
    
    async def _monitor_inventory_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Monitor inventory levels and update state"""
        self.logger.info("🔍 Monitoring inventory levels...")
        
        # Check critical inventory levels
        critical_items = []
        low_stock_items = []
        
        for item_id, item in state["inventory"].items():
            if item.total_available_quantity <= 0:
                critical_items.append(item_id)
            elif item.needs_reorder:
                low_stock_items.append(item_id)
        
        # Update monitoring results
        state["current_operation"] = "inventory_monitoring"
        state["operation_context"] = {
            "critical_items": critical_items,
            "low_stock_items": low_stock_items,
            "total_items_checked": len(state["inventory"]),
            "timestamp": datetime.now().isoformat()
        }
        state["processed_items"] = critical_items + low_stock_items
        state["last_check"] = datetime.now()
        
        # Add monitoring message
        monitoring_message = AIMessage(
            content=f"Inventory monitoring completed. Found {len(critical_items)} critical and {len(low_stock_items)} low stock items."
        )
        state["messages"].append(monitoring_message)
        
        return state
    
    async def _analyze_demand_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Analyze demand patterns and forecast needs"""
        self.logger.info("📊 Analyzing demand patterns...")
        
        processed_items = state["processed_items"]
        demand_analysis = {}
        
        for item_id in processed_items:
            if item_id in state["inventory"]:
                item = state["inventory"][item_id]
                # Simple demand analysis (can be enhanced with ML)
                usage_history = state["usage_patterns"].get(item_id, [])
                
                if usage_history:
                    avg_daily_usage = sum(usage_history[-30:]) / min(30, len(usage_history))
                    predicted_stockout_days = item.total_available_quantity / max(avg_daily_usage, 1)
                else:
                    avg_daily_usage = 0
                    predicted_stockout_days = 0
                
                demand_analysis[item_id] = {
                    "avg_daily_usage": avg_daily_usage,
                    "predicted_stockout_days": predicted_stockout_days,
                    "priority": "high" if predicted_stockout_days < 7 else "medium" if predicted_stockout_days < 14 else "low"
                }
        
        state["operation_context"]["demand_analysis"] = demand_analysis
        
        # Add analysis message
        analysis_message = AIMessage(
            content=f"Demand analysis completed for {len(demand_analysis)} items."
        )
        state["messages"].append(analysis_message)
        
        return state
    
    async def _generate_recommendations_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Generate AI-powered recommendations"""
        self.logger.info("🤖 Generating intelligent recommendations...")
        
        # Create prompt for recommendation generation
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert hospital supply chain analyst. Based on the inventory data and demand analysis, 
             generate specific recommendations for inventory management, procurement, and optimization.
             Focus on patient safety, cost efficiency, and operational continuity."""),
            ("human", """Current inventory status:
             Critical items: {critical_items}
             Low stock items: {low_stock_items}
             Demand analysis: {demand_analysis}
             
             Please provide specific recommendations for:
             1. Immediate actions needed
             2. Procurement suggestions
             3. Transfer opportunities
             4. Risk mitigation strategies""")
        ])
        
        # Generate recommendations using LLM
        context = state["operation_context"]
        
        try:
            if self.llm:
                chain = prompt | self.llm
                response = await chain.ainvoke({
                    "critical_items": context.get("critical_items", []),
                    "low_stock_items": context.get("low_stock_items", []),
                    "demand_analysis": context.get("demand_analysis", {})
                })
                
                recommendations = [
                    {
                        "type": "ai_recommendation",
                        "content": response.content,
                        "timestamp": datetime.now().isoformat(),
                        "priority": "high"
                    }
                ]
            else:
                # Fallback recommendations without LLM
                critical_items = context.get("critical_items", [])
                low_stock_items = context.get("low_stock_items", [])
                
                recommendations = []
                if critical_items:
                    recommendations.append({
                        "type": "critical_stock_recommendation",
                        "content": f"URGENT: {len(critical_items)} items are out of stock and need immediate reordering: {', '.join(critical_items[:5])}",
                        "timestamp": datetime.now().isoformat(),
                        "priority": "critical"
                    })
                
                if low_stock_items:
                    recommendations.append({
                        "type": "low_stock_recommendation", 
                        "content": f"LOW STOCK: {len(low_stock_items)} items are below reorder point and should be replenished: {', '.join(low_stock_items[:5])}",
                        "timestamp": datetime.now().isoformat(),
                        "priority": "high"
                    })
                
                if not critical_items and not low_stock_items:
                    recommendations.append({
                        "type": "status_recommendation",
                        "content": "Inventory levels are within acceptable ranges. Continue regular monitoring.",
                        "timestamp": datetime.now().isoformat(),
                        "priority": "low"
                    })
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            recommendations = [
                {
                    "type": "fallback_recommendation", 
                    "content": "Review critical and low stock items for immediate action",
                    "timestamp": datetime.now().isoformat(),
                    "priority": "high"
                }
            ]
        
        state["recommendations"] = recommendations
        
        # Add recommendation message
        rec_message = AIMessage(
            content=f"Generated {len(recommendations)} recommendations for inventory optimization."
        )
        state["messages"].append(rec_message)
        
        return state
    
    async def _process_alerts_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Process and generate alerts based on current state"""
        self.logger.info("🚨 Processing alerts...")
        
        new_alerts = []
        context = state["operation_context"]
        
        # Generate alerts for critical items
        for item_id in context.get("critical_items", []):
            if item_id in state["inventory"]:
                item = state["inventory"][item_id]
                alert = SupplyAlert(
                    id=str(uuid.uuid4()),
                    item_id=item_id,
                    alert_type="stock_critical",
                    level=AlertLevel.CRITICAL,
                    message=f"CRITICAL: {item.name} is out of stock",
                    description=f"Item {item.name} has zero available quantity across all locations",
                    created_at=datetime.now(),
                    created_by="langgraph_agent",
                    assigned_to=None,
                    department=item.category.value,
                    location=None
                )
                new_alerts.append(alert)
        
        # Generate alerts for low stock items  
        for item_id in context.get("low_stock_items", []):
            if item_id in state["inventory"]:
                item = state["inventory"][item_id]
                alert = SupplyAlert(
                    id=str(uuid.uuid4()),
                    item_id=item_id,
                    alert_type="stock_low",
                    level=AlertLevel.HIGH,
                    message=f"LOW STOCK: {item.name} needs reorder",
                    description=f"Item {item.name} has fallen below minimum threshold",
                    created_at=datetime.now(),
                    created_by="langgraph_agent",
                    assigned_to=None,
                    department=item.category.value,
                    location=None
                )
                new_alerts.append(alert)
        
        # Add to state
        state["alerts"].extend(new_alerts)
        
        # Add alert message
        alert_message = AIMessage(
            content=f"Generated {len(new_alerts)} new alerts for inventory issues."
        )
        state["messages"].append(alert_message)
        
        return state
    
    async def _manage_procurement_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Manage procurement processes"""
        self.logger.info("🛒 Managing procurement processes...")
        
        new_purchase_orders = []
        context = state["operation_context"]
        
        # Create purchase orders for critical items
        critical_items = context.get("critical_items", [])
        if critical_items:
            for item_id in critical_items[:5]:  # Limit to top 5 critical items
                if item_id in state["inventory"]:
                    item = state["inventory"][item_id]
                    # Find preferred supplier (simplified logic)
                    preferred_supplier = None
                    for supplier_id, supplier in state["suppliers"].items():
                        if item.category.value in supplier.capabilities:
                            preferred_supplier = supplier_id
                            break
                    
                    if preferred_supplier:
                        po = PurchaseOrder(
                            po_id=str(uuid.uuid4()),
                            po_number=f"PO-{datetime.now().strftime('%Y%m%d')}-{len(new_purchase_orders)+1:03d}",
                            supplier_id=preferred_supplier,
                            items=[{
                                "item_id": item_id,
                                "quantity": item.reorder_quantity or 100,
                                "unit_price": item.unit_cost
                            }],
                            status=PurchaseOrderStatus.DRAFT,
                            created_date=datetime.now(),
                            created_by="langgraph_agent",
                            department=item.category.value,
                            total_amount=item.unit_cost * (item.reorder_quantity or 100),
                            urgency_level="high"
                        )
                        new_purchase_orders.append(po)
                        state["purchase_orders"][po.po_id] = po
        
        state["operation_context"]["new_purchase_orders"] = len(new_purchase_orders)
        
        # Add procurement message
        procurement_message = AIMessage(
            content=f"Created {len(new_purchase_orders)} draft purchase orders for critical items."
        )
        state["messages"].append(procurement_message)
        
        return state
    
    async def _handle_transfers_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Handle inter-location transfers"""
        self.logger.info("🔄 Handling inventory transfers...")
        
        new_transfers = []
        context = state["operation_context"]
        
        # Look for transfer opportunities
        for item_id in context.get("low_stock_items", []):
            if item_id in state["inventory"]:
                item = state["inventory"][item_id]
                
                # Find locations with surplus and deficit
                surplus_locations = []
                deficit_locations = []
                
                for location_id, location_stock in item.locations.items():
                    if location_stock.available_quantity > location_stock.minimum_threshold * 2:
                        surplus_locations.append((location_id, location_stock.available_quantity))
                    elif location_stock.available_quantity <= location_stock.minimum_threshold:
                        deficit_locations.append((location_id, location_stock.minimum_threshold - location_stock.available_quantity))
                
                # Create transfers from surplus to deficit locations
                for surplus_loc, surplus_qty in surplus_locations:
                    for deficit_loc, needed_qty in deficit_locations:
                        if surplus_loc != deficit_loc and surplus_qty > needed_qty:
                            transfer = TransferRequest(
                                transfer_id=str(uuid.uuid4()),
                                item_id=item_id,
                                from_location=surplus_loc,
                                to_location=deficit_loc,
                                quantity=min(needed_qty, surplus_qty // 2),
                                status=TransferStatus.PENDING,
                                requested_date=datetime.now(),
                                requested_by="langgraph_agent",
                                reason="Automated rebalancing",
                                priority="normal"
                            )
                            new_transfers.append(transfer)
                            state["transfer_requests"][transfer.transfer_id] = transfer
                            break  # One transfer per deficit location
        
        state["operation_context"]["new_transfers"] = len(new_transfers)
        
        # Add transfer message
        transfer_message = AIMessage(
            content=f"Created {len(new_transfers)} transfer requests for inventory rebalancing."
        )
        state["messages"].append(transfer_message)
        
        return state
    
    async def _update_compliance_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Update compliance and audit records"""
        self.logger.info("📋 Updating compliance records...")
        
        # Create audit log for this operation cycle
        audit_log = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id="langgraph_agent",
            action="autonomous_inventory_cycle",
            item_id=None,
            location=None,
            details={
                "operation": state["current_operation"],
                "items_processed": len(state["processed_items"]),
                "alerts_generated": len([a for a in state["alerts"] if a.created_at >= datetime.now() - timedelta(minutes=5)]),
                "purchase_orders_created": state["operation_context"].get("new_purchase_orders", 0),
                "transfers_created": state["operation_context"].get("new_transfers", 0)
            },
            ip_address="localhost",
            user_agent="LangGraph-Agent/1.0",
            before_state=None,
            after_state=None
        )
        
        state["audit_logs"].append(audit_log)
        
        # Add compliance message
        compliance_message = AIMessage(
            content="Compliance records updated and audit log created for this operation cycle."
        )
        state["messages"].append(compliance_message)
        
        return state
    
    async def _finalize_operations_node(self, state: SupplyAgentState) -> SupplyAgentState:
        """Finalize operations and prepare for next cycle"""
        self.logger.info("✅ Finalizing operations...")
        
        # Update agent status
        state["agent_status"] = "completed_cycle"
        state["current_operation"] = "cycle_complete"
        
        # Summary of operations
        summary = {
            "cycle_completed_at": datetime.now().isoformat(),
            "items_processed": len(state["processed_items"]),
            "recommendations_generated": len(state["recommendations"]),
            "alerts_created": len([a for a in state["alerts"] if a.created_at >= datetime.now() - timedelta(minutes=10)]),
            "purchase_orders_created": state["operation_context"].get("new_purchase_orders", 0),
            "transfers_created": state["operation_context"].get("new_transfers", 0)
        }
        
        state["operation_context"]["cycle_summary"] = summary
        
        # Add completion message
        completion_message = AIMessage(
            content=f"Operations cycle completed successfully. Processed {summary['items_processed']} items, "
                   f"generated {summary['recommendations_generated']} recommendations, "
                   f"created {summary['alerts_created']} alerts."
        )
        state["messages"].append(completion_message)
        
        return state
    
    async def initialize(self):
        """Initialize the LangGraph-based agent with comprehensive data"""
        self.logger.info("🚀 Initializing LangGraph Supply Agent...")
        
        # Load all necessary data (reusing methods from original agent)
        await self._load_locations()
        await self._load_users()
        await self._load_enhanced_inventory()
        await self._load_enhanced_suppliers()
        await self._load_budgets()
        await self._load_sample_transfers()
        
        # Create initial state
        initial_state: SupplyAgentState = {
            "messages": [SystemMessage(content="LangGraph Supply Agent initialized and ready for operations.")],
            "inventory": self.inventory,
            "alerts": self.alerts,
            "suppliers": self.suppliers,
            "users": self.users,
            "locations": self.locations,
            "purchase_orders": self.purchase_orders,
            "transfer_requests": self.transfer_requests,
            "audit_logs": self.audit_logs,
            "budgets": self.budgets,
            "compliance_records": self.compliance_records,
            "usage_patterns": self.usage_patterns,
            "transfers": self.transfers,
            "current_operation": "initialization",
            "operation_context": {},
            "monitoring_enabled": True,
            "last_check": datetime.now(),
            "agent_status": "initialized",
            "processed_items": [],
            "recommendations": [],
            "current_user": None
        }
        
        self.current_state = initial_state
        self.is_running = True
        self.logger.info("✅ LangGraph Supply Agent initialized successfully")
    
    async def run_monitoring_cycle(self):
        """Run a complete monitoring and optimization cycle using LangGraph"""
        if not self.is_running:
            await self.initialize()
        
        self.logger.info("🔄 Starting LangGraph monitoring cycle...")
        
        try:
            # Prepare input for the workflow
            input_data = {
                "messages": [HumanMessage(content="Execute inventory monitoring and optimization cycle")],
                **self.current_state
            }
            
            # Run the workflow
            result = await self.app.ainvoke(
                input_data,
                config={"configurable": {"thread_id": f"supply_agent_{datetime.now().isoformat()}"}}
            )
            
            # Update current state with results
            self.current_state = result
            
            # Extract key metrics from the cycle
            cycle_summary = result["operation_context"].get("cycle_summary", {})
            
            self.logger.info(f"✅ Monitoring cycle completed: {cycle_summary}")
            
            return {
                "status": "success",
                "summary": cycle_summary,
                "processed_items": result["processed_items"],
                "recommendations": result["recommendations"],
                "new_alerts": len([a for a in result["alerts"] if a.created_at >= datetime.now() - timedelta(minutes=10)])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in monitoring cycle: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def start_monitoring(self):
        """Start continuous monitoring with LangGraph workflows"""
        self.logger.info("🎯 Starting continuous LangGraph monitoring...")
        
        while self.is_running:
            try:
                await self.run_monitoring_cycle()
                await asyncio.sleep(300)  # 5-minute cycles
            except Exception as e:
                self.logger.error(f"Error in continuous monitoring: {e}")
                await asyncio.sleep(60)  # Shorter sleep on error
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.logger.info("🛑 Stopping LangGraph monitoring...")
        self.is_running = False
    
    # Include all original data loading methods from the original agent
    # (These methods remain largely unchanged but adapted for the new class structure)
    
    async def _load_locations(self):
        """Load hospital locations and departments"""
        self.locations = {
            "ICU": {
                "name": "Intensive Care Unit",
                "type": "patient_care",
                "capacity": 50,
                "head": "Dr. Sarah Johnson",
                "contact": "icu@hospital.com"
            },
            "ER": {
                "name": "Emergency Room", 
                "type": "emergency",
                "capacity": 100,
                "head": "Dr. Michael Brown",
                "contact": "er@hospital.com"
            },
            "SURGERY": {
                "name": "Operating Theaters",
                "type": "surgical", 
                "capacity": 30,
                "head": "Dr. Emily Davis",
                "contact": "surgery@hospital.com"
            },
            "PHARMACY": {
                "name": "Central Pharmacy",
                "type": "pharmacy",
                "capacity": 200,
                "head": "PharmD John Smith", 
                "contact": "pharmacy@hospital.com"
            },
            "WAREHOUSE": {
                "name": "Central Warehouse",
                "type": "storage",
                "capacity": 1000,
                "head": "Manager Lisa Wilson",
                "contact": "warehouse@hospital.com"
            },
            "LAB": {
                "name": "Laboratory",
                "type": "diagnostics",
                "capacity": 75,
                "head": "Dr. Robert Taylor",
                "contact": "lab@hospital.com"
            }
        }
    
    async def _load_users(self):
        """Load system users with role-based permissions"""
        self.users = {
            "admin001": User(
                user_id="admin001",
                username="admin",
                email="admin@hospital.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                department="IT",
                permissions=["all"],
                is_active=True,
                created_date=datetime.now() - timedelta(days=365),
                last_login=datetime.now() - timedelta(hours=2)
            )
            # Add more users as needed...
        }
    
    async def _load_enhanced_inventory(self):
        """Load enhanced inventory with realistic hospital supplies"""
        # Sample inventory items (abbreviated for space)
        inventory_items = [
            {
                "id": "MED001",
                "name": "Surgical Gloves (Box of 100)",
                "category": SupplyCategory.PPE,
                "description": "Sterile latex surgical gloves",
                "unit": "box",
                "unit_cost": 12.50,
                "locations": {
                    "SURGERY": {"current": 25, "reserved": 5, "min_threshold": 10, "max_capacity": 100},
                    "ER": {"current": 15, "reserved": 2, "min_threshold": 8, "max_capacity": 50},
                    "ICU": {"current": 8, "reserved": 1, "min_threshold": 5, "max_capacity": 30}
                }
            },
            {
                "id": "MED002", 
                "name": "N95 Respirator Masks",
                "category": SupplyCategory.PPE,
                "description": "N95 respiratory protection masks",
                "unit": "box",
                "unit_cost": 45.00,
                "locations": {
                    "ICU": {"current": 5, "reserved": 2, "min_threshold": 10, "max_capacity": 50},
                    "ER": {"current": 8, "reserved": 1, "min_threshold": 12, "max_capacity": 60}
                }
            }
            # Add more items as needed...
        ]
        
        for item_data in inventory_items:
            locations = {}
            for loc_id, loc_data in item_data["locations"].items():
                locations[loc_id] = LocationStock(
                    location_id=loc_id,
                    location_name=self.locations[loc_id]["name"],
                    current_quantity=loc_data["current"],
                    reserved_quantity=loc_data["reserved"],
                    minimum_threshold=loc_data["min_threshold"],
                    maximum_capacity=loc_data["max_capacity"]
                )
            
            supply_item = SupplyItem(
                id=item_data["id"],
                name=item_data["name"],
                category=item_data["category"],
                description=item_data["description"],
                sku=item_data.get("sku", f"SKU-{item_data['id']}"),
                manufacturer=item_data.get("manufacturer", "Unknown"),
                model_number=item_data.get("model_number"),
                unit_of_measure=item_data["unit"],
                unit_cost=item_data["unit_cost"],
                reorder_point=sum(loc.minimum_threshold for loc in locations.values()),
                reorder_quantity=sum(loc.maximum_capacity for loc in locations.values()) // 2,
                abc_classification=item_data.get("abc_classification", "B"),
                criticality_level=item_data.get("criticality_level", "Medium"),
                storage_requirements=item_data.get("storage_requirements", "room_temperature"),
                regulatory_info=item_data.get("regulatory_info", {}),
                supplier_id=item_data.get("supplier_id", ""),
                alternative_suppliers=item_data.get("alternative_suppliers", []),
                last_updated=datetime.now(),
                created_by="langgraph_agent",
                locations=locations,
                batches=[],
                usage_history=[]
            )
            
            self.inventory[item_data["id"]] = supply_item
    
    async def _load_enhanced_suppliers(self):
        """Load enhanced supplier data"""
        suppliers_data = [
            {
                "id": "SUP001",
                "name": "MedSupply Corp",
                "contact_person": "John Adams",
                "email": "orders@medsupply.com",
                "phone": "1-800-555-0101",
                "address": "123 Medical Way, City, State 12345",
                "capabilities": ["PPE", "medical_supplies"]
            }
            # Add more suppliers...
        ]
        
        for supplier_data in suppliers_data:
            supplier = Supplier(
                supplier_id=supplier_data["id"],
                name=supplier_data["name"],
                contact_person=supplier_data["contact_person"],
                email=supplier_data["email"],
                phone=supplier_data["phone"],
                address=supplier_data["address"],
                tax_id="12-3456789",
                payment_terms="Net 30",
                lead_time_days=7,
                minimum_order_value=500.0,
                reliability_score=4.5,
                quality_rating=4.8,
                delivery_performance=4.7,
                price_competitiveness=4.2,
                certifications=["ISO 9001", "FDA Registered"],
                preferred_categories=[SupplyCategory.PPE, SupplyCategory.MEDICAL_SUPPLIES],
                contract_start_date=datetime.now() - timedelta(days=180),
                contract_end_date=datetime.now() + timedelta(days=365),
                is_active=True
            )
            self.suppliers[supplier_data["id"]] = supplier
    
    async def _load_budgets(self):
        """Load budget information"""
        # Simple budget loading
        self.budgets = {}
        
    async def _load_sample_transfers(self):
        """Load sample transfer data"""
        # Simple transfer loading
        self.transfers = []
    
    # Additional methods for compatibility with existing system
    def get_agent_status(self):
        """Get current agent status for API compatibility"""
        return {
            "agent_status": self.current_state.get("agent_status", "initialized") if hasattr(self, 'current_state') else "not_initialized",
            "is_running": self.is_running,
            "last_check": self.current_state.get("last_check", datetime.now()) if hasattr(self, 'current_state') else datetime.now(),
            "monitoring_enabled": self.current_state.get("monitoring_enabled", True) if hasattr(self, 'current_state') else True,
            "total_items": len(self.inventory),
            "pending_orders": len([po for po in self.purchase_orders.values() if po.status == PurchaseOrderStatus.PENDING_APPROVAL]),
            "active_alerts": len([alert for alert in self.alerts if not alert.resolved])
        }
    
    def get_all_inventory(self):
        """Get all inventory items for API compatibility"""
        return list(self.inventory.values())
    
    def get_all_alerts(self):
        """Get all alerts for API compatibility"""
        return self.alerts
    
    def get_all_suppliers(self):
        """Get all suppliers for API compatibility"""
        return list(self.suppliers.values())
    
    # Additional compatibility methods for existing API endpoints
    def add_inventory_item(self, item_data: Dict):
        """Add new inventory item"""
        # Implementation for adding items
        pass
    
    def update_inventory_item(self, item_id: str, updates: Dict):
        """Update existing inventory item"""
        # Implementation for updating items
        pass
    
    def delete_inventory_item(self, item_id: str):
        """Delete inventory item"""
        # Implementation for deleting items
        pass
    
    def get_inventory_by_location(self, location_id: str):
        """Get inventory for specific location"""
        location_inventory = []
        for item in self.inventory.values():
            if location_id in item.locations:
                location_stock = item.locations[location_id]
                location_inventory.append({
                    "item": item,
                    "location_stock": location_stock
                })
        return location_inventory
    
    def create_transfer(self, transfer_data: Dict):
        """Create transfer request"""
        transfer = TransferRequest(
            transfer_id=str(uuid.uuid4()),
            **transfer_data
        )
        self.transfer_requests[transfer.transfer_id] = transfer
        return transfer
    
    def get_low_stock_items(self):
        """Get items with low stock"""
        return [item for item in self.inventory.values() if item.needs_reorder]
    
    def get_critical_items(self):
        """Get items with critical stock levels"""
        return [item for item in self.inventory.values() if item.total_available_quantity <= 0]
    
    async def _check_inventory_levels(self):
        """Check inventory levels - compatibility method for API endpoints"""
        try:
            # Use the existing monitoring cycle functionality
            await self.run_monitoring_cycle()
            return {
                "success": True,
                "message": "Inventory check completed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error in inventory check: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "", resolved_by: str = "system"):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                alert.resolved_by = resolved_by
                alert.resolution_notes = resolution_notes
                return True
        return False
    
    def get_purchase_orders(self, status_filter: Optional[str] = None):
        """Get purchase orders with optional status filter"""
        if status_filter:
            return [po for po in self.purchase_orders.values() if po.status.value == status_filter]
        return list(self.purchase_orders.values())
    
    def update_purchase_order_status(self, po_id: str, new_status: str):
        """Update purchase order status"""
        if po_id in self.purchase_orders:
            self.purchase_orders[po_id].status = PurchaseOrderStatus(new_status)
            return True
        return False
    
    def get_transfers(self):
        """Get all transfer requests"""
        return list(self.transfer_requests.values())
    
    def update_transfer_status(self, transfer_id: str, new_status: str):
        """Update transfer status"""
        if transfer_id in self.transfer_requests:
            self.transfer_requests[transfer_id].status = TransferStatus(new_status)
            return True
        return False
    
    def get_audit_logs(self, limit: int = 100):
        """Get recent audit logs"""
        return sorted(self.audit_logs, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def add_audit_log(self, action: str, details: Dict, user_id: str = "system"):
        """Add new audit log entry"""
        audit_log = AuditLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            item_id=details.get("item_id"),
            location=details.get("location"),
            details=details,
            ip_address="localhost",
            user_agent="LangGraph-Agent/1.0",
            before_state=None,
            after_state=None
        )
        self.audit_logs.append(audit_log)
        return audit_log
    
    def get_usage_analytics(self, item_id: Optional[str] = None, days: int = 30):
        """Get usage analytics"""
        if item_id:
            return self.usage_patterns.get(item_id, [])
        else:
            # Return summary analytics
            return {
                "total_items": len(self.inventory),
                "items_with_usage_data": len(self.usage_patterns),
                "analysis_period_days": days
            }
    
    def get_department_summary(self, department: str):
        """Get summary for specific department"""
        dept_items = [item for item in self.inventory.values() if item.category.value == department]
        return {
            "department": department,
            "total_items": len(dept_items),
            "low_stock_items": len([item for item in dept_items if item.needs_reorder]),
            "critical_items": len([item for item in dept_items if item.total_available_quantity <= 0]),
            "total_value": sum(item.unit_cost * item.total_available_quantity for item in dept_items)
        }
    
    def create_purchase_order_professional(self, items: List[Dict], reason: str = "Auto-reorder") -> Dict:
        """
        Professional purchase order creation method for automated reordering
        
        Args:
            items: List of items to order with quantities
            reason: Reason for creating the purchase order
            
        Returns:
            Dictionary with purchase order details
        """
        try:
            # Create unique PO ID with microseconds and random component
            import uuid
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_suffix = str(uuid.uuid4())[:8]
            po_id = f"PO-{timestamp}-{unique_suffix}"
            
            # Calculate total amount
            total_amount = 0
            order_items = []
            
            for item_data in items:
                item_id = item_data.get('item_id')
                quantity = item_data.get('quantity', 0)
                
                # Find item in inventory
                if item_id in self.inventory:
                    item = self.inventory[item_id]
                    unit_cost = item.unit_cost
                    line_total = quantity * unit_cost
                    total_amount += line_total
                    
                    order_items.append({
                        'item_id': item_id,
                        'item_name': item.name,
                        'quantity': quantity,
                        'unit_cost': unit_cost,
                        'line_total': line_total
                    })
                else:
                    # Use provided cost or default
                    unit_cost = item_data.get('unit_cost', 10.0)
                    line_total = quantity * unit_cost
                    total_amount += line_total
                    
                    order_items.append({
                        'item_id': item_id,
                        'item_name': item_data.get('name', f'Item {item_id}'),
                        'quantity': quantity,
                        'unit_cost': unit_cost,
                        'line_total': line_total
                    })
            
            # Create purchase order
            purchase_order = PurchaseOrder(
                po_id=po_id,
                po_number=po_id,  # Use po_id as po_number for simplicity
                supplier_id="AUTO-SUPPLIER",
                created_by="system",
                created_date=datetime.now(),
                required_date=datetime.now() + timedelta(days=3),
                status=PurchaseOrderStatus.PENDING_APPROVAL,
                total_amount=total_amount,
                currency="USD",
                payment_terms="NET30",
                delivery_address="Hospital Main",
                items=order_items,
                approval_workflow=[],
                delivery_tracking={},
                invoice_details=None,
                notes=f"Automated purchase order: {reason}"
            )
            
            # Store purchase order
            self.purchase_orders[po_id] = purchase_order
            
            # Log the action
            self.add_audit_log(
                action="CREATE_PURCHASE_ORDER",
                details={
                    "po_id": po_id,
                    "items": order_items,
                    "total_amount": total_amount,
                    "reason": reason
                },
                user_id="system"
            )
            
            self.logger.info(f"✅ Created purchase order {po_id} for {len(order_items)} items (${total_amount:.2f})")
            
            return {
                "success": True,
                "po_id": po_id,
                "total_amount": total_amount,
                "items": order_items,
                "status": "pending",
                "message": f"Purchase order {po_id} created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create purchase order: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create purchase order"
            }

# Create global instance for backward compatibility
try:
    # Try to get API key from environment or use None for fallback
    api_key = os.environ.get("OPENAI_API_KEY")
    langgraph_agent = LangGraphSupplyAgent(api_key=api_key)
    logging.info("✅ LangGraph agent initialized successfully")
except Exception as e:
    logging.warning(f"Failed to initialize LangGraph agent: {e}")
    # Create a minimal agent without LLM for basic functionality
    try:
        langgraph_agent = LangGraphSupplyAgent()
        logging.info("✅ LangGraph agent initialized in fallback mode")
    except Exception as e2:
        logging.error(f"Failed to initialize LangGraph agent even in fallback mode: {e2}")
        langgraph_agent = None
