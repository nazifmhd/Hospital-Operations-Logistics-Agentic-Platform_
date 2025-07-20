"""
Model Context Protocol (MCP) Server for Hospital Supply Chain Platform
Provides structured context and capabilities to AI models through standardized protocol
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
import inspect

# MCP Protocol Types
class MCPVersion(Enum):
    V1_0 = "1.0"

class MCPMessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"

class MCPCapabilityType(Enum):
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    CONTEXT = "context"

@dataclass
class MCPMessage:
    """Base MCP message structure"""
    id: str
    type: MCPMessageType
    method: str
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None

@dataclass
class MCPResource:
    """MCP resource definition"""
    uri: str
    name: str
    description: str
    mime_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MCPPrompt:
    """MCP prompt template"""
    name: str
    description: str
    template: str
    parameters: List[str] = field(default_factory=list)

@dataclass
class MCPContext:
    """MCP context information"""
    hospital_info: Dict[str, Any]
    current_user: Dict[str, Any]
    inventory_state: Dict[str, Any]
    active_alerts: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    system_metrics: Dict[str, Any]

class MCPServer:
    """Model Context Protocol Server for Hospital Supply Chain"""
    
    def __init__(self):
        self.version = MCPVersion.V1_0
        self.server_info = {
            "name": "hospital-supply-mcp-server",
            "version": "1.0.0",
            "description": "MCP Server for Hospital Supply Chain Operations",
            "protocol_version": self.version.value
        }
        
        # MCP capabilities
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        
        # Context providers
        self.context_providers: Dict[str, Callable] = {}
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        
        # Active connections
        self.connections: Dict[str, Dict[str, Any]] = {}
        
        self._register_core_capabilities()
        self._register_message_handlers()
    
    def _register_core_capabilities(self):
        """Register core hospital supply chain capabilities"""
        
        # Tools
        self._register_inventory_tools()
        self._register_analytics_tools()
        self._register_workflow_tools()
        
        # Resources
        self._register_resources()
        
        # Prompts
        self._register_prompts()
        
        # Context providers
        self._register_context_providers()
    
    def _register_inventory_tools(self):
        """Register inventory management tools"""
        
        # Get inventory status tool
        self.tools["get_inventory_status"] = MCPTool(
            name="get_inventory_status",
            description="Get current inventory status for items, departments, or locations",
            input_schema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string", "description": "Specific item ID (optional)"},
                    "department": {"type": "string", "description": "Department name (optional)"},
                    "location": {"type": "string", "description": "Location ID (optional)"},
                    "category": {"type": "string", "description": "Supply category (optional)"},
                    "low_stock_only": {"type": "boolean", "description": "Show only low stock items"}
                },
                "additionalProperties": False
            },
            handler=self._handle_get_inventory_status
        )
        
        # Create purchase order tool
        self.tools["create_purchase_order"] = MCPTool(
            name="create_purchase_order",
            description="Create a new purchase order for supplies",
            input_schema={
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "quantity": {"type": "number"},
                                "urgency": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                            },
                            "required": ["item_id", "quantity"]
                        }
                    },
                    "supplier_id": {"type": "string"},
                    "justification": {"type": "string"},
                    "requestor": {"type": "string"}
                },
                "required": ["items", "justification", "requestor"]
            },
            handler=self._handle_create_purchase_order
        )
        
        # Transfer supplies tool
        self.tools["transfer_supplies"] = MCPTool(
            name="transfer_supplies",
            description="Transfer supplies between departments or locations",
            input_schema={
                "type": "object",
                "properties": {
                    "from_location": {"type": "string"},
                    "to_location": {"type": "string"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_id": {"type": "string"},
                                "quantity": {"type": "number"}
                            },
                            "required": ["item_id", "quantity"]
                        }
                    },
                    "reason": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
                },
                "required": ["from_location", "to_location", "items", "reason"]
            },
            handler=self._handle_transfer_supplies
        )
    
    def _register_analytics_tools(self):
        """Register analytics and reporting tools"""
        
        # Get usage analytics
        self.tools["get_usage_analytics"] = MCPTool(
            name="get_usage_analytics",
            description="Get supply usage analytics and trends",
            input_schema={
                "type": "object",
                "properties": {
                    "time_period": {"type": "string", "enum": ["7d", "30d", "90d", "1y"]},
                    "item_id": {"type": "string", "description": "Specific item (optional)"},
                    "department": {"type": "string", "description": "Department filter (optional)"},
                    "metric": {"type": "string", "enum": ["consumption", "cost", "waste", "efficiency"]}
                },
                "required": ["time_period", "metric"]
            },
            handler=self._handle_get_usage_analytics
        )
        
        # Forecast demand
        self.tools["forecast_demand"] = MCPTool(
            name="forecast_demand",
            description="Forecast future demand for supplies",
            input_schema={
                "type": "object",
                "properties": {
                    "item_id": {"type": "string"},
                    "forecast_days": {"type": "number", "minimum": 1, "maximum": 365},
                    "include_seasonality": {"type": "boolean", "default": True},
                    "confidence_level": {"type": "number", "minimum": 0.5, "maximum": 0.99, "default": 0.95}
                },
                "required": ["item_id", "forecast_days"]
            },
            handler=self._handle_forecast_demand
        )
    
    def _register_workflow_tools(self):
        """Register workflow and automation tools"""
        
        # Get approval status
        self.tools["get_approval_status"] = MCPTool(
            name="get_approval_status",
            description="Get status of pending approvals and workflows",
            input_schema={
                "type": "object",
                "properties": {
                    "request_id": {"type": "string", "description": "Specific request ID (optional)"},
                    "requestor": {"type": "string", "description": "Filter by requestor (optional)"},
                    "status": {"type": "string", "enum": ["pending", "approved", "rejected", "expired"]}
                },
                "additionalProperties": False
            },
            handler=self._handle_get_approval_status
        )
        
        # Submit for approval
        self.tools["submit_for_approval"] = MCPTool(
            name="submit_for_approval",
            description="Submit a request for approval",
            input_schema={
                "type": "object",
                "properties": {
                    "request_type": {"type": "string", "enum": ["purchase_order", "transfer", "budget_request"]},
                    "details": {"type": "object"},
                    "urgency": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                    "justification": {"type": "string"}
                },
                "required": ["request_type", "details", "justification"]
            },
            handler=self._handle_submit_for_approval
        )
    
    def _register_resources(self):
        """Register MCP resources"""
        
        # Current inventory resource
        self.resources["current_inventory"] = MCPResource(
            uri="hospital://inventory/current",
            name="Current Inventory",
            description="Real-time inventory levels across all departments",
            mime_type="application/json",
            metadata={"refresh_rate": "5min", "scope": "hospital_wide"}
        )
        
        # Low stock alerts resource
        self.resources["low_stock_alerts"] = MCPResource(
            uri="hospital://alerts/low_stock",
            name="Low Stock Alerts",
            description="Current low stock alerts and recommendations",
            mime_type="application/json",
            metadata={"priority": "high", "auto_refresh": True}
        )
        
        # Usage trends resource
        self.resources["usage_trends"] = MCPResource(
            uri="hospital://analytics/usage_trends",
            name="Usage Trends",
            description="Historical usage patterns and trend analysis",
            mime_type="application/json",
            metadata={"time_range": "configurable", "granularity": "daily"}
        )
        
        # Supplier catalog resource
        self.resources["supplier_catalog"] = MCPResource(
            uri="hospital://suppliers/catalog",
            name="Supplier Catalog",
            description="Available items from approved suppliers with pricing",
            mime_type="application/json",
            metadata={"update_frequency": "daily", "includes_pricing": True}
        )
    
    def _register_prompts(self):
        """Register MCP prompt templates"""
        
        # Inventory analysis prompt
        self.prompts["inventory_analysis"] = MCPPrompt(
            name="inventory_analysis",
            description="Analyze inventory status and provide recommendations",
            template="""
            Based on the current inventory data:
            {inventory_data}
            
            And recent usage patterns:
            {usage_patterns}
            
            Please provide:
            1. Summary of current inventory status
            2. Items at risk of stockout
            3. Recommendations for reordering
            4. Cost optimization opportunities
            5. Any compliance concerns
            
            Consider the hospital's typical usage patterns and upcoming requirements.
            """,
            parameters=["inventory_data", "usage_patterns"]
        )
        
        # Alert triage prompt
        self.prompts["alert_triage"] = MCPPrompt(
            name="alert_triage",
            description="Triage and prioritize supply chain alerts",
            template="""
            Current alerts requiring attention:
            {active_alerts}
            
            Hospital context:
            - Current time: {current_time}
            - Day of week: {day_of_week}
            - Current patient census: {patient_census}
            - Upcoming procedures: {scheduled_procedures}
            
            Please prioritize these alerts and recommend immediate actions:
            1. Critical alerts requiring immediate action
            2. High priority alerts for next 4 hours
            3. Medium priority alerts for next 24 hours
            4. Recommendations for automation improvements
            """,
            parameters=["active_alerts", "current_time", "day_of_week", "patient_census", "scheduled_procedures"]
        )
        
        # Purchase justification prompt
        self.prompts["purchase_justification"] = MCPPrompt(
            name="purchase_justification",
            description="Generate purchase order justification",
            template="""
            Purchase request details:
            Items: {requested_items}
            Total cost: {total_cost}
            Requestor: {requestor}
            Department: {department}
            
            Current inventory status:
            {current_inventory}
            
            Usage history:
            {usage_history}
            
            Please generate a comprehensive justification including:
            1. Business need assessment
            2. Usage forecast validation
            3. Cost-benefit analysis
            4. Alternative options considered
            5. Risk assessment if not approved
            6. Recommended approval decision
            """,
            parameters=["requested_items", "total_cost", "requestor", "department", "current_inventory", "usage_history"]
        )
    
    def _register_context_providers(self):
        """Register context providers"""
        
        self.context_providers["hospital_state"] = self._get_hospital_state_context
        self.context_providers["inventory_context"] = self._get_inventory_context
        self.context_providers["user_context"] = self._get_user_context
        self.context_providers["alert_context"] = self._get_alert_context
    
    def _register_message_handlers(self):
        """Register MCP message handlers"""
        
        self.message_handlers["initialize"] = self._handle_initialize
        self.message_handlers["list_tools"] = self._handle_list_tools
        self.message_handlers["list_resources"] = self._handle_list_resources
        self.message_handlers["list_prompts"] = self._handle_list_prompts
        self.message_handlers["get_resource"] = self._handle_get_resource
        self.message_handlers["call_tool"] = self._handle_call_tool
        self.message_handlers["get_context"] = self._handle_get_context
    
    async def handle_message(self, message: MCPMessage, connection_id: str) -> MCPMessage:
        """Handle incoming MCP message"""
        try:
            handler = self.message_handlers.get(message.method)
            if not handler:
                return MCPMessage(
                    id=message.id,
                    type=MCPMessageType.RESPONSE,
                    method=message.method,
                    error={
                        "code": -32601,
                        "message": f"Method not found: {message.method}"
                    }
                )
            
            result = await handler(message.params or {}, connection_id)
            
            return MCPMessage(
                id=message.id,
                type=MCPMessageType.RESPONSE,
                method=message.method,
                result=result
            )
            
        except Exception as e:
            logging.error(f"Error handling MCP message {message.method}: {e}")
            return MCPMessage(
                id=message.id,
                type=MCPMessageType.RESPONSE,
                method=message.method,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def _handle_initialize(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle initialization request"""
        client_info = params.get("clientInfo", {})
        
        # Store connection info
        self.connections[connection_id] = {
            "client_info": client_info,
            "capabilities": params.get("capabilities", []),
            "connected_at": datetime.now(),
            "context": {}
        }
        
        return {
            "protocolVersion": self.version.value,
            "serverInfo": self.server_info,
            "capabilities": {
                "tools": {"list_changed": True},
                "resources": {"list_changed": True},
                "prompts": {"list_changed": True},
                "context": {"enabled": True}
            }
        }
    
    async def _handle_list_tools(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle list tools request"""
        tools_list = []
        for tool in self.tools.values():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            })
        
        return {"tools": tools_list}
    
    async def _handle_list_resources(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle list resources request"""
        resources_list = []
        for resource in self.resources.values():
            resources_list.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type,
                "metadata": resource.metadata
            })
        
        return {"resources": resources_list}
    
    async def _handle_list_prompts(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle list prompts request"""
        prompts_list = []
        for prompt in self.prompts.values():
            prompts_list.append({
                "name": prompt.name,
                "description": prompt.description,
                "parameters": prompt.parameters
            })
        
        return {"prompts": prompts_list}
    
    async def _handle_get_resource(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle get resource request"""
        uri = params.get("uri")
        if not uri:
            raise ValueError("URI parameter required")
        
        # Find resource by URI
        resource = None
        for r in self.resources.values():
            if r.uri == uri:
                resource = r
                break
        
        if not resource:
            raise ValueError(f"Resource not found: {uri}")
        
        # Generate resource content based on URI
        content = await self._generate_resource_content(resource)
        
        return {
            "contents": [{
                "uri": resource.uri,
                "mimeType": resource.mime_type,
                "text": json.dumps(content, indent=2) if isinstance(content, dict) else str(content)
            }]
        }
    
    async def _handle_call_tool(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle tool call request"""
        tool_name = params.get("name")
        tool_params = params.get("arguments", {})
        
        if not tool_name:
            raise ValueError("Tool name required")
        
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        if tool.handler:
            result = await tool.handler(tool_params, connection_id)
        else:
            result = {"error": "Tool handler not implemented"}
        
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(result, indent=2)
            }]
        }
    
    async def _handle_get_context(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Handle get context request"""
        context_type = params.get("type", "full")
        
        context = MCPContext(
            hospital_info=await self._get_hospital_state_context(),
            current_user=await self._get_user_context(connection_id),
            inventory_state=await self._get_inventory_context(),
            active_alerts=await self._get_alert_context(),
            recent_activities=await self._get_recent_activities(),
            system_metrics=await self._get_system_metrics()
        )
        
        return {"context": asdict(context)}
    
    # Tool handlers (implement actual functionality)
    async def _handle_get_inventory_status(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Get inventory status"""
        # This would integrate with your actual inventory system
        return {
            "status": "success",
            "message": "Inventory status retrieved",
            "data": {
                "total_items": 1250,
                "low_stock_items": 23,
                "out_of_stock_items": 2,
                "overstocked_items": 8
            }
        }
    
    async def _handle_create_purchase_order(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Create purchase order"""
        return {
            "status": "success",
            "message": "Purchase order created",
            "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}",
            "estimated_cost": 1250.00,
            "approval_required": True
        }
    
    async def _handle_transfer_supplies(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Transfer supplies"""
        return {
            "status": "success",
            "message": "Transfer initiated",
            "transfer_id": f"TR-{uuid.uuid4().hex[:8]}",
            "estimated_completion": "2 hours"
        }
    
    async def _handle_get_usage_analytics(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Get usage analytics"""
        return {
            "status": "success",
            "analytics": {
                "period": params.get("time_period", "30d"),
                "trend": "increasing",
                "average_daily_usage": 125.5,
                "projected_needs": 3800
            }
        }
    
    async def _handle_forecast_demand(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Forecast demand"""
        return {
            "status": "success",
            "forecast": {
                "item_id": params.get("item_id"),
                "forecast_days": params.get("forecast_days"),
                "predicted_usage": 850,
                "confidence": 0.87
            }
        }
    
    async def _handle_get_approval_status(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Get approval status"""
        return {
            "status": "success",
            "pending_approvals": 5,
            "approved_today": 12,
            "rejected_today": 1
        }
    
    async def _handle_submit_for_approval(self, params: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
        """Submit for approval"""
        return {
            "status": "success",
            "request_id": f"REQ-{uuid.uuid4().hex[:8]}",
            "estimated_approval_time": "4 hours"
        }
    
    # Context providers
    async def _get_hospital_state_context(self) -> Dict[str, Any]:
        """Get hospital state context"""
        return {
            "name": "General Hospital",
            "current_time": datetime.now().isoformat(),
            "patient_census": 285,
            "bed_utilization": 0.78,
            "operating_status": "normal"
        }
    
    async def _get_inventory_context(self) -> Dict[str, Any]:
        """Get inventory context"""
        return {
            "total_value": 125000.00,
            "items_below_minimum": 15,
            "items_expired_soon": 8,
            "pending_orders": 23
        }
    
    async def _get_user_context(self, connection_id: str) -> Dict[str, Any]:
        """Get user context"""
        connection = self.connections.get(connection_id, {})
        return {
            "connection_id": connection_id,
            "role": "inventory_manager",
            "department": "supply_chain",
            "permissions": ["read", "write", "approve"]
        }
    
    async def _get_alert_context(self) -> List[Dict[str, Any]]:
        """Get alert context"""
        return [
            {
                "id": "alert_001",
                "type": "low_stock",
                "item": "Surgical Gloves",
                "level": "critical",
                "created_at": datetime.now().isoformat()
            }
        ]
    
    async def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Get recent activities"""
        return [
            {
                "id": "activity_001",
                "type": "purchase_order",
                "description": "PO created for medical supplies",
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "uptime": "99.9%",
            "response_time": "125ms",
            "active_users": 45,
            "data_freshness": "< 5min"
        }
    
    async def _generate_resource_content(self, resource: MCPResource) -> Dict[str, Any]:
        """Generate content for a resource"""
        if resource.uri == "hospital://inventory/current":
            return await self._get_inventory_context()
        elif resource.uri == "hospital://alerts/low_stock":
            return {"alerts": await self._get_alert_context()}
        elif resource.uri == "hospital://analytics/usage_trends":
            return {"trends": "sample_trend_data"}
        elif resource.uri == "hospital://suppliers/catalog":
            return {"catalog": "sample_catalog_data"}
        else:
            return {"error": "Resource content not available"}

# Global MCP server instance
mcp_server = None

def get_mcp_server() -> MCPServer:
    """Get or create global MCP server instance"""
    global mcp_server
    if mcp_server is None:
        mcp_server = MCPServer()
    return mcp_server

async def handle_mcp_request(message_data: Dict[str, Any], connection_id: str) -> Dict[str, Any]:
    """Handle MCP request and return response"""
    server = get_mcp_server()
    
    message = MCPMessage(
        id=message_data.get("id", str(uuid.uuid4())),
        type=MCPMessageType(message_data.get("type", "request")),
        method=message_data.get("method", ""),
        params=message_data.get("params")
    )
    
    response = await server.handle_message(message, connection_id)
    
    return {
        "id": response.id,
        "type": response.type.value,
        "method": response.method,
        "result": response.result,
        "error": response.error
    }
