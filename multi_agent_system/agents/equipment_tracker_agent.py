"""
Equipment Tracker Agent - Complete Implementation
Manages real-time location tracking, availability, and maintenance of medical equipment
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TypedDict
from enum import Enum

# LangGraph imports
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import select, update, and_, or_, func
from sqlalchemy.orm import selectinload

# Database imports
try:
    from database.config import db_manager
    from database.models import (
        MedicalEquipment, EquipmentMaintenance, Department, StaffMember,
        EquipmentStatus, EquipmentType, BedStatus, Bed
    )
except ImportError:
    from database.config import db_manager
    from database.models import (
        MedicalEquipment, EquipmentMaintenance, Department, StaffMember,
        EquipmentStatus, EquipmentType, BedStatus, Bed
    )

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Equipment Tracker State
class EquipmentTrackingState(TypedDict):
    """State for equipment tracking workflows"""
    messages: List[Any]
    equipment_request: Dict[str, Any]
    equipment_id: Optional[str]
    location_data: Dict[str, Any]
    availability_status: str
    maintenance_schedule: List[Dict[str, Any]]
    allocation_result: Dict[str, Any]
    workflow_status: str
    error_info: Optional[str]
    tracking_metadata: Dict[str, Any]

class EquipmentWorkflowType(Enum):
    ALLOCATION_REQUEST = "allocation_request"
    MAINTENANCE_SCHEDULING = "maintenance_scheduling"
    LOCATION_TRACKING = "location_tracking"
    FAULT_REPORTING = "fault_reporting"
    INVENTORY_AUDIT = "inventory_audit"

class EquipmentTrackerAgent:
    """
    Advanced Equipment Tracker Agent with LangGraph workflows and RAG integration
    """
    
    def __init__(self, coordinator=None):
        self.agent_id = f"equipment_tracker_{uuid.uuid4().hex[:8]}"
        self.agent_type = "equipment_tracker"
        self.coordinator = coordinator
        self.llm = None  # Initialize later
        self.memory = MemorySaver()
        self.workflow_graph = None
        self.active_requests = {}
        self.location_cache = {}
        self.is_initialized = True  # Professional compatibility
        
        # Performance metrics for professional monitoring
        self.performance_metrics = {
            "requests_processed": 0,
            "average_response_time": 0.0,
            "error_count": 0,
            "last_activity": None
        }
        
        logger.info(f"🔧 Equipment Tracker Agent initialized: {self.agent_id}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Professional health monitoring for API compatibility"""
        error_rate = (
            self.performance_metrics["error_count"] / 
            max(self.performance_metrics["requests_processed"], 1)
        ) * 100 if self.performance_metrics["requests_processed"] > 0 else 0
        
        health_status = "healthy"
        if error_rate > 10:
            health_status = "degraded"
        elif error_rate > 25:
            health_status = "unhealthy"
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "status": health_status,
            "is_initialized": self.is_initialized,
            "performance": self.performance_metrics,
            "error_rate_percent": round(error_rate, 2)
        }
    
    def get_available_actions(self) -> List[str]:
        """Return list of available actions for this agent"""
        return ["track_equipment", "locate_equipment", "schedule_maintenance", "optimize_distribution"]
    
    def _initialize_llm(self):
        """Initialize LLM when needed"""
        if self.llm is None:
            try:
                import os
                from pathlib import Path
                # Load environment variables from .env file
                try:
                    from dotenv import load_dotenv
                    # Get the project root directory (two levels up from agents/)
                    project_root = Path(__file__).parent.parent.parent
                    env_file = project_root / ".env"
                    load_dotenv(dotenv_path=str(env_file))
                except ImportError:
                    pass  # dotenv not available, use system env
                
                api_key = os.getenv('GEMINI_API_KEY')
                if api_key and api_key != 'your_gemini_api_key_here':
                    # Initialize with explicit API key
                    self.llm = ChatGoogleGenerativeAI(
                        model="gemini-1.5-flash", 
                        temperature=0.1,
                        google_api_key=api_key
                    )
                    logger.info("✅ Equipment Tracker LLM initialized")
                else:
                    logger.warning("⚠️ Equipment Tracker LLM not initialized - missing API key")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Equipment Tracker LLM: {e}")
                self.llm = None
    
    async def initialize(self):
        """Initialize the equipment tracking workflow"""
        self._initialize_llm()
        await self._build_workflow_graph()
        logger.info("🔧 Equipment Tracker Agent workflow initialized")
    
    async def _build_workflow_graph(self):
        """Build the LangGraph workflow for equipment tracking"""
        
        # Define workflow nodes
        workflow = StateGraph(EquipmentTrackingState)
        
        # Add nodes for equipment tracking workflow
        workflow.add_node("analyze_request", self._analyze_equipment_request)
        workflow.add_node("check_availability", self._check_equipment_availability)
        workflow.add_node("locate_equipment", self._locate_equipment)
        workflow.add_node("allocate_equipment", self._allocate_equipment)
        workflow.add_node("schedule_maintenance", self._schedule_maintenance)
        workflow.add_node("update_status", self._update_equipment_status)
        workflow.add_node("notify_staff", self._notify_staff)
        workflow.add_node("complete_request", self._complete_equipment_request)
        
        # Define workflow edges and conditions
        workflow.add_edge(START, "analyze_request")
        
        workflow.add_conditional_edges(
            "analyze_request",
            self._route_equipment_workflow,
            {
                "check_availability": "check_availability",
                "schedule_maintenance": "schedule_maintenance",
                "locate_equipment": "locate_equipment",
                "complete_request": "complete_request"
            }
        )
        
        workflow.add_conditional_edges(
            "check_availability",
            self._evaluate_availability,
            {
                "allocate": "allocate_equipment",
                "locate": "locate_equipment",
                "maintenance": "schedule_maintenance",
                "notify": "notify_staff"
            }
        )
        
        workflow.add_edge("locate_equipment", "allocate_equipment")
        workflow.add_edge("allocate_equipment", "update_status")
        workflow.add_edge("schedule_maintenance", "notify_staff")
        workflow.add_edge("update_status", "notify_staff")
        workflow.add_edge("notify_staff", "complete_request")
        workflow.add_edge("complete_request", END)
        
        # Compile the workflow
        self.workflow_graph = workflow.compile(checkpointer=self.memory)
        logger.info("🔧 Equipment tracking workflow graph compiled successfully")
    
    async def _analyze_equipment_request(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Analyze incoming equipment request"""
        logger.info("🔍 Analyzing equipment request...")
        
        request = state["equipment_request"]
        workflow_type = request.get("type", "allocation_request")
        
        # Enhanced request analysis with RAG
        if self.llm:
            analysis_prompt = f"""
            Analyze this equipment request and determine the best workflow:
            
            Request Type: {workflow_type}
            Equipment Needed: {request.get('equipment_type', 'unknown')}
            Urgency: {request.get('urgency', 'normal')}
            Location: {request.get('location', 'unknown')}
            Special Requirements: {request.get('requirements', {})}
            
            Consider:
            1. Equipment availability and location
            2. Maintenance schedules
            3. Urgency level
            4. Allocation rules and policies
            
            Recommend the optimal workflow path.
            """
            
            try:
                response = await asyncio.to_thread(
                    self.llm.invoke,
                    [HumanMessage(content=analysis_prompt)]
                )
                state["tracking_metadata"]["analysis"] = response.content
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}")
        
        state["workflow_status"] = "analyzed"
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "analyze_request",
            "action": "Equipment request analyzed",
            "workflow_type": workflow_type
        })
        
        return state
    
    async def _check_equipment_availability(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Check real-time equipment availability"""
        logger.info("📊 Checking equipment availability...")
        
        request = state["equipment_request"]
        equipment_type = request.get("equipment_type")
        location = request.get("location")
        requirements = request.get("requirements", {})
        
        try:
            async with self.db_manager.get_async_session() as session:
                # Query available equipment of requested type
                query = select(MedicalEquipment).where(
                    and_(
                        MedicalEquipment.equipment_type == equipment_type,
                        MedicalEquipment.status == EquipmentStatus.AVAILABLE
                    )
                ).options(selectinload(MedicalEquipment.department))
                
                # Add location filter if specified
                if location:
                    query = query.join(Department).where(
                        Department.name.ilike(f"%{location}%")
                    )
                
                result = await session.execute(query)
                available_equipment = result.scalars().all()
                
                # Score equipment based on requirements and location
                scored_equipment = []
                for equipment in available_equipment:
                    score = await self._score_equipment_match(equipment, requirements, location)
                    scored_equipment.append({
                        "equipment": equipment,
                        "score": score,
                        "location": equipment.current_location or equipment.department.name if equipment.department else "Unknown"
                    })
                
                # Sort by score (highest first)
                scored_equipment.sort(key=lambda x: x["score"], reverse=True)
                
                state["availability_status"] = "checked"
                state["tracking_metadata"]["available_equipment"] = [
                    {
                        "id": eq["equipment"].id,
                        "name": eq["equipment"].name,
                        "location": eq["location"],
                        "score": eq["score"],
                        "last_maintenance": eq["equipment"].last_maintenance_date.isoformat() if eq["equipment"].last_maintenance_date else None
                    }
                    for eq in scored_equipment[:5]  # Top 5 matches
                ]
                
                logger.info(f"Found {len(available_equipment)} available {equipment_type} units")
                
        except Exception as e:
            logger.error(f"Error checking equipment availability: {e}")
            state["error_info"] = str(e)
            state["availability_status"] = "error"
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "check_availability",
            "action": f"Checked availability for {equipment_type}",
            "available_count": len(state["tracking_metadata"].get("available_equipment", []))
        })
        
        return state
    
    async def _locate_equipment(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Advanced equipment location tracking with RFID/Bluetooth and RAG-powered analytics"""
        logger.info("📍 Advanced equipment location tracking with real-time systems...")
        
        equipment_id = state.get("equipment_id")
        request = state["equipment_request"]
        
        try:
            # Enhanced real-time tracking with multiple methods
            location_data = await self._get_advanced_realtime_location(equipment_id, request)
            
            # RAG-powered equipment manual and specifications lookup
            equipment_specs = await self._query_equipment_specs_via_rag(equipment_id)
            
            # Check tracking system status and accuracy
            tracking_health = await self._check_tracking_system_health()
            
            # Anomaly detection for unusual location patterns
            anomaly_analysis = await self._detect_location_anomalies(equipment_id, location_data)
            
            if equipment_id:
                # Enhanced database query with detailed tracking info
                async with self.db_manager.get_async_session() as session:
                    result = await session.execute(
                        select(MedicalEquipment).where(MedicalEquipment.id == equipment_id)
                        .options(selectinload(MedicalEquipment.department))
                    )
                    equipment = result.scalar_one_or_none()
                    
                    if equipment:
                        # Multi-source location verification
                        verified_location = await self._verify_location_multi_source(equipment, location_data)
                        
                        # Update comprehensive location cache
                        self.location_cache[equipment_id] = {
                            "location": verified_location,
                            "timestamp": datetime.now(),
                            "accuracy": tracking_health.get("accuracy_level", "medium"),
                            "tracking_methods": ["rfid", "bluetooth", "manual_scan"],
                            "confidence_score": verified_location.get("confidence", 0.85),
                            "anomaly_score": anomaly_analysis.get("anomaly_score", 0.1),
                            "equipment_specs": equipment_specs
                        }
                        
                        state["location_data"] = verified_location
                        state["tracking_confidence"] = verified_location.get("confidence", 0.85)
                        state["anomaly_alerts"] = anomaly_analysis.get("alerts", [])
                        
                        logger.info(f"Advanced tracking: {equipment.name} at {verified_location.get('current_location')} "
                                  f"(confidence: {verified_location.get('confidence', 0):.2f})")
                        
                        # Generate location-based recommendations
                        location_recommendations = await self._generate_location_recommendations(
                            equipment, verified_location, request
                        )
                        state["location_recommendations"] = location_recommendations
                        
            else:
                # Advanced equipment discovery and optimal selection
                optimal_equipment = await self._find_optimal_equipment_with_ml(request, state)
                if optimal_equipment:
                    state["equipment_id"] = optimal_equipment["id"]
                    state["location_data"] = optimal_equipment["location_data"]
                    state["selection_reasoning"] = optimal_equipment["reasoning"]
                
        except Exception as e:
            logger.error(f"Error in advanced equipment location tracking: {e}")
            state["error_info"] = str(e)
        
        # Enhanced messaging with detailed tracking info
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "locate_equipment_advanced",
            "action": "Advanced equipment location tracking completed",
            "equipment_id": state.get("equipment_id"),
            "location": state.get("location_data", {}).get("current_location"),
            "confidence": state.get("tracking_confidence"),
            "tracking_methods": ["rfid", "bluetooth", "database"],
            "anomaly_detection": state.get("anomaly_alerts", [])
        })
        
        return state
    
    async def _allocate_equipment(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Allocate equipment to requesting department/staff"""
        logger.info("🎯 Allocating equipment...")
        
        equipment_id = state.get("equipment_id")
        request = state["equipment_request"]
        requesting_staff = request.get("requesting_staff")
        department = request.get("department")
        
        try:
            async with self.db_manager.get_async_session() as session:
                if equipment_id:
                    # Update equipment status to IN_USE
                    await session.execute(
                        update(MedicalEquipment)
                        .where(MedicalEquipment.id == equipment_id)
                        .values(
                            status=EquipmentStatus.IN_USE,
                            current_location=department or "In Transit",
                            last_used_date=datetime.now(),
                            updated_at=datetime.now()
                        )
                    )
                    
                    # Log the allocation
                    allocation_result = {
                        "equipment_id": equipment_id,
                        "allocated_to": requesting_staff or department,
                        "allocation_time": datetime.now().isoformat(),
                        "expected_return": (datetime.now() + timedelta(hours=4)).isoformat(),
                        "status": "allocated"
                    }
                    
                    state["allocation_result"] = allocation_result
                    
                    # Notify coordinator about successful allocation
                    if self.coordinator:
                        await self.coordinator.receive_agent_update(
                            agent_id=self.agent_id,
                            update_type="equipment_allocated",
                            data=allocation_result
                        )
                    
                    await session.commit()
                    logger.info(f"Equipment {equipment_id} allocated successfully")
                    
        except Exception as e:
            logger.error(f"Error allocating equipment: {e}")
            state["error_info"] = str(e)
            state["allocation_result"] = {"status": "failed", "error": str(e)}
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "allocate_equipment",
            "action": "Equipment allocation completed",
            "result": state["allocation_result"]["status"]
        })
        
        return state
    
    async def _schedule_maintenance(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Schedule preventive or corrective maintenance"""
        logger.info("🔧 Scheduling equipment maintenance...")
        
        equipment_id = state.get("equipment_id")
        request = state["equipment_request"]
        maintenance_type = request.get("maintenance_type", "preventive")
        urgency = request.get("urgency", "normal")
        
        try:
            async with self.db_manager.get_async_session() as session:
                if equipment_id:
                    # Create maintenance record
                    maintenance_record = EquipmentMaintenance(
                        id=f"maint_{uuid.uuid4().hex[:8]}",
                        equipment_id=equipment_id,
                        maintenance_type=maintenance_type,
                        scheduled_date=datetime.now() + timedelta(days=1 if urgency == "high" else 7),
                        status="scheduled",
                        description=request.get("description", f"{maintenance_type} maintenance"),
                        created_at=datetime.now()
                    )
                    
                    session.add(maintenance_record)
                    
                    # Update equipment status if necessary
                    if urgency == "high" or maintenance_type == "corrective":
                        await session.execute(
                            update(MedicalEquipment)
                            .where(MedicalEquipment.id == equipment_id)
                            .values(
                                status=EquipmentStatus.MAINTENANCE,
                                updated_at=datetime.now()
                            )
                        )
                    
                    await session.commit()
                    
                    state["maintenance_schedule"] = [{
                        "maintenance_id": maintenance_record.id,
                        "equipment_id": equipment_id,
                        "type": maintenance_type,
                        "scheduled_date": maintenance_record.scheduled_date.isoformat(),
                        "urgency": urgency
                    }]
                    
                    logger.info(f"Maintenance scheduled for equipment {equipment_id}")
                    
        except Exception as e:
            logger.error(f"Error scheduling maintenance: {e}")
            state["error_info"] = str(e)
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "schedule_maintenance",
            "action": "Maintenance scheduled",
            "maintenance_type": maintenance_type,
            "urgency": urgency
        })
        
        return state
    
    async def _update_equipment_status(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Update equipment status in database"""
        logger.info("📝 Updating equipment status...")
        
        equipment_id = state.get("equipment_id")
        allocation_result = state.get("allocation_result", {})
        
        if equipment_id and allocation_result.get("status") == "allocated":
            try:
                async with self.db_manager.get_async_session() as session:
                    # Additional status updates based on allocation
                    await session.execute(
                        update(MedicalEquipment)
                        .where(MedicalEquipment.id == equipment_id)
                        .values(updated_at=datetime.now())
                    )
                    await session.commit()
                    
            except Exception as e:
                logger.error(f"Error updating equipment status: {e}")
                state["error_info"] = str(e)
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "update_status",
            "action": "Equipment status updated"
        })
        
        return state
    
    async def _notify_staff(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Notify relevant staff about equipment status/allocation"""
        logger.info("📢 Notifying staff...")
        
        request = state["equipment_request"]
        allocation_result = state.get("allocation_result", {})
        maintenance_schedule = state.get("maintenance_schedule", [])
        
        # Determine notification recipients and content
        notifications = []
        
        if allocation_result.get("status") == "allocated":
            notifications.append({
                "recipient": request.get("requesting_staff"),
                "type": "equipment_allocated",
                "message": f"Equipment {state.get('equipment_id')} has been allocated and is ready for use",
                "location": state.get("location_data", {}).get("current_location"),
                "timestamp": datetime.now().isoformat()
            })
        
        if maintenance_schedule:
            for maintenance in maintenance_schedule:
                notifications.append({
                    "recipient": "biomedical_engineering",
                    "type": "maintenance_scheduled",
                    "message": f"Maintenance scheduled for equipment {maintenance['equipment_id']}",
                    "scheduled_date": maintenance["scheduled_date"],
                    "urgency": maintenance.get("urgency", "normal"),
                    "timestamp": datetime.now().isoformat()
                })
        
        # In a real implementation, this would send actual notifications
        # (email, SMS, system alerts, etc.)
        state["tracking_metadata"]["notifications"] = notifications
        
        logger.info(f"Generated {len(notifications)} staff notifications")
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "notify_staff",
            "action": "Staff notifications sent",
            "notification_count": len(notifications)
        })
        
        return state
    
    async def _complete_equipment_request(self, state: EquipmentTrackingState) -> EquipmentTrackingState:
        """Complete the equipment request workflow"""
        logger.info("✅ Completing equipment request...")
        
        # Finalize workflow status
        state["workflow_status"] = "completed"
        
        # Generate summary
        summary = {
            "request_id": state["equipment_request"].get("request_id"),
            "equipment_type": state["equipment_request"].get("equipment_type"),
            "status": "completed",
            "allocated_equipment": state.get("equipment_id"),
            "location": state.get("location_data", {}).get("current_location"),
            "allocation_result": state.get("allocation_result"),
            "maintenance_scheduled": len(state.get("maintenance_schedule", [])) > 0,
            "completion_time": datetime.now().isoformat(),
            "processing_duration": len(state["messages"])  # Approximate processing steps
        }
        
        state["tracking_metadata"]["completion_summary"] = summary
        
        # Remove from active requests
        request_id = state["equipment_request"].get("request_id")
        if request_id in self.active_requests:
            del self.active_requests[request_id]
        
        state["messages"].append({
            "timestamp": datetime.now().isoformat(),
            "node": "complete_request",
            "action": "Equipment request completed",
            "summary": summary
        })
        
        logger.info(f"Equipment request {request_id} completed successfully")
        return state
    
    async def _route_equipment_workflow(self, state: EquipmentTrackingState) -> str:
        """Route workflow based on request type and conditions"""
        request = state["equipment_request"]
        workflow_type = request.get("type", "allocation_request")
        urgency = request.get("urgency", "normal")
        
        if workflow_type == "maintenance_scheduling":
            return "schedule_maintenance"
        elif workflow_type == "location_tracking":
            return "locate_equipment"
        elif urgency == "emergency":
            return "check_availability"
        else:
            return "check_availability"
    
    async def _evaluate_availability(self, state: EquipmentTrackingState) -> str:
        """Evaluate equipment availability and determine next action"""
        available_equipment = state["tracking_metadata"].get("available_equipment", [])
        request = state["equipment_request"]
        urgency = request.get("urgency", "normal")
        
        if available_equipment:
            if urgency == "emergency":
                return "locate"
            else:
                return "allocate"
        else:
            # No equipment available
            return "notify"
    
    async def _score_equipment_match(self, equipment, requirements: Dict, preferred_location: str = None) -> float:
        """Score equipment match based on requirements and location"""
        score = 100.0  # Base score
        
        # Location proximity scoring
        if preferred_location and equipment.department:
            if preferred_location.lower() in equipment.department.name.lower():
                score += 20.0
        
        # Maintenance status scoring
        if equipment.last_maintenance_date:
            days_since_maintenance = (datetime.now() - equipment.last_maintenance_date).days
            if days_since_maintenance < 30:
                score += 10.0  # Recently maintained
            elif days_since_maintenance > 180:
                score -= 5.0   # Needs maintenance soon
        
        # Availability scoring (already available, so full points)
        if equipment.status == EquipmentStatus.AVAILABLE:
            score += 15.0
        
        # Requirements matching (example: specific features)
        if requirements:
            features_needed = requirements.get("features", [])
            equipment_specs = equipment.specifications or {}
            
            for feature in features_needed:
                if feature in str(equipment_specs).lower():
                    score += 5.0
        
        return score
    
    async def _get_realtime_location(self, equipment) -> Dict[str, Any]:
        """Simulate real-time location tracking (RFID/Bluetooth/GPS)"""
        # In real implementation, this would call actual tracking APIs
        base_location = equipment.current_location or (
            equipment.department.name if equipment.department else "Unknown"
        )
        
        return {
            "current_location": base_location,
            "precise_coordinates": f"{base_location} - Room {hash(equipment.id) % 100 + 1}",
            "last_seen": datetime.now().isoformat(),
            "tracking_method": "simulated_rfid",
            "accuracy_meters": 2.0,
            "movement_detected": False
        }
    
    # Public interface methods
    async def process_equipment_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an equipment allocation, tracking, or maintenance request"""
        request_id = request.get("request_id", f"eq_req_{uuid.uuid4().hex[:8]}")
        request["request_id"] = request_id
        
        logger.info(f"🔧 Processing equipment request: {request_id}")
        
        # Initialize workflow state
        initial_state = EquipmentTrackingState(
            messages=[],
            equipment_request=request,
            equipment_id=request.get("equipment_id"),
            location_data={},
            availability_status="pending",
            maintenance_schedule=[],
            allocation_result={},
            workflow_status="initiated",
            error_info=None,
            tracking_metadata={}
        )
        
        # Store active request
        self.active_requests[request_id] = {
            "start_time": datetime.now(),
            "status": "processing",
            "request": request
        }
        
        try:
            # Execute workflow
            config = {"configurable": {"thread_id": request_id}}
            final_state = await self.workflow_graph.ainvoke(initial_state, config)
            
            # Update request status
            self.active_requests[request_id]["status"] = "completed"
            self.active_requests[request_id]["completion_time"] = datetime.now()
            
            return {
                "status": "success",
                "request_id": request_id,
                "result": final_state["tracking_metadata"].get("completion_summary", {}),
                "workflow_messages": final_state["messages"]
            }
            
        except Exception as e:
            logger.error(f"Equipment request processing failed: {e}")
            self.active_requests[request_id]["status"] = "failed"
            self.active_requests[request_id]["error"] = str(e)
            
            return {
                "status": "error",
                "request_id": request_id,
                "error": str(e)
            }
    
    async def get_equipment_status(self, equipment_type: str = None, location: str = None) -> Dict[str, Any]:
        """Get current status of all equipment or filtered by type/location"""
        try:
            async with self.db_manager.get_async_session() as session:
                query = select(MedicalEquipment).options(selectinload(MedicalEquipment.department))
                
                if equipment_type:
                    query = query.where(MedicalEquipment.equipment_type == equipment_type)
                
                if location:
                    query = query.join(Department).where(
                        Department.name.ilike(f"%{location}%")
                    )
                
                result = await session.execute(query)
                equipment_list = result.scalars().all()
                
                # Aggregate status information
                status_summary = {}
                equipment_details = []
                
                for equipment in equipment_list:
                    status = equipment.status.value
                    status_summary[status] = status_summary.get(status, 0) + 1
                    
                    equipment_details.append({
                        "id": equipment.id,
                        "name": equipment.name,
                        "type": equipment.equipment_type.value if equipment.equipment_type else "unknown",
                        "status": status,
                        "location": equipment.current_location or (
                            equipment.department.name if equipment.department else "Unknown"
                        ),
                        "last_maintenance": equipment.last_maintenance_date.isoformat() if equipment.last_maintenance_date else None,
                        "last_used": equipment.last_used_date.isoformat() if equipment.last_used_date else None
                    })
                
                return {
                    "total_equipment": len(equipment_list),
                    "status_summary": status_summary,
                    "equipment_details": equipment_details,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting equipment status: {e}")
            return {"error": str(e)}
    
    async def get_active_requests(self) -> Dict[str, Any]:
        """Get all active equipment requests"""
        return {
            "active_requests": self.active_requests,
            "total_active": len(self.active_requests),
            "timestamp": datetime.now().isoformat()
        }
    
    async def emergency_equipment_override(self, equipment_id: str, override_reason: str) -> Dict[str, Any]:
        """Emergency override to immediately allocate equipment regardless of status"""
        logger.warning(f"🚨 Emergency override requested for equipment {equipment_id}")
        
        try:
            async with self.db_manager.get_async_session() as session:
                await session.execute(
                    update(MedicalEquipment)
                    .where(MedicalEquipment.id == equipment_id)
                    .values(
                        status=EquipmentStatus.IN_USE,
                        current_location="Emergency Override",
                        updated_at=datetime.now(),
                        notes=f"Emergency override: {override_reason}"
                    )
                )
                await session.commit()
                
                return {
                    "status": "success",
                    "equipment_id": equipment_id,
                    "override_reason": override_reason,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Emergency override failed: {e}")
            return {"status": "error", "error": str(e)}

    # =================== ADVANCED REAL-TIME TRACKING METHODS ===================
    
    async def _get_advanced_realtime_location(self, equipment_id: str, request: dict) -> dict:
        """Advanced multi-source real-time location tracking with RFID/Bluetooth"""
        try:
            # Simulate advanced tracking methods (RFID, Bluetooth, WiFi triangulation)
            tracking_methods = {
                "rfid": await self._track_via_rfid(equipment_id),
                "bluetooth": await self._track_via_bluetooth(equipment_id),
                "wifi": await self._track_via_wifi_triangulation(equipment_id),
                "manual_scan": await self._get_last_manual_scan(equipment_id)
            }
            
            # Weight and combine location sources
            location_confidence = 0.0
            primary_location = None
            
            # RFID has highest priority (95% accuracy)
            if tracking_methods["rfid"]["status"] == "active":
                primary_location = tracking_methods["rfid"]["location"]
                location_confidence = 0.95
            # Bluetooth second priority (85% accuracy)
            elif tracking_methods["bluetooth"]["status"] == "active":
                primary_location = tracking_methods["bluetooth"]["location"]
                location_confidence = 0.85
            # WiFi triangulation third (75% accuracy)
            elif tracking_methods["wifi"]["status"] == "active":
                primary_location = tracking_methods["wifi"]["location"]
                location_confidence = 0.75
            # Manual scan last resort (60% accuracy due to time delay)
            elif tracking_methods["manual_scan"]["status"] == "recent":
                primary_location = tracking_methods["manual_scan"]["location"]
                location_confidence = 0.60
            
            return {
                "current_location": primary_location or "Location Unknown",
                "confidence": location_confidence,
                "tracking_methods": tracking_methods,
                "last_updated": datetime.now().isoformat(),
                "accuracy_radius": self._calculate_accuracy_radius(location_confidence)
            }
            
        except Exception as e:
            logger.error(f"Advanced location tracking error: {e}")
            return {
                "current_location": "Tracking System Error",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _track_via_rfid(self, equipment_id: str) -> dict:
        """RFID-based equipment tracking"""
        # Simulate RFID reader data
        import random
        if random.random() > 0.1:  # 90% success rate
            locations = ["OR-1", "ICU-Bay-3", "Emergency-Room-2", "Radiology-Suite-A", "Storage-Room-B"]
            return {
                "status": "active",
                "location": random.choice(locations),
                "signal_strength": random.uniform(0.7, 1.0),
                "reader_id": f"RFID-Reader-{random.randint(1, 20)}"
            }
        return {"status": "no_signal", "location": None}
    
    async def _track_via_bluetooth(self, equipment_id: str) -> dict:
        """Bluetooth beacon-based tracking"""
        import random
        if random.random() > 0.15:  # 85% success rate
            locations = ["Nurses-Station-2A", "Patient-Room-205", "Pharmacy", "Lab-Central", "Corridor-East-Wing"]
            return {
                "status": "active",
                "location": random.choice(locations),
                "beacon_strength": random.uniform(0.6, 0.9),
                "beacon_id": f"BLE-{random.randint(100, 999)}"
            }
        return {"status": "out_of_range", "location": None}
    
    async def _track_via_wifi_triangulation(self, equipment_id: str) -> dict:
        """WiFi triangulation-based positioning"""
        import random
        if random.random() > 0.25:  # 75% success rate
            areas = ["North-Wing-Floor-2", "South-Wing-Floor-1", "Central-Hub", "Cafeteria-Area", "Admin-Wing"]
            return {
                "status": "active",
                "location": random.choice(areas),
                "access_points": random.randint(3, 8),
                "triangulation_accuracy": random.uniform(0.5, 0.8)
            }
        return {"status": "insufficient_aps", "location": None}
    
    async def _get_last_manual_scan(self, equipment_id: str) -> dict:
        """Get last manual barcode/QR scan location"""
        # Check database for last scan
        try:
            async with self.db_manager.get_async_session() as session:
                # Simulate manual scan data
                import random
                scan_time = datetime.now() - timedelta(hours=random.randint(1, 24))
                if (datetime.now() - scan_time).total_seconds() < 3600:  # Recent if < 1 hour
                    locations = ["Equipment-Storage", "Maintenance-Shop", "Sterilization-Unit", "Loading-Dock"]
                    return {
                        "status": "recent",
                        "location": random.choice(locations),
                        "scan_time": scan_time.isoformat(),
                        "scanned_by": f"Staff-{random.randint(100, 999)}"
                    }
                return {"status": "outdated", "location": None}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _query_equipment_specs_via_rag(self, equipment_id: str) -> dict:
        """Advanced RAG-powered equipment knowledge base with comprehensive manual integration"""
        try:
            # Enhanced RAG query with multiple knowledge sources
            equipment_knowledge = await self._comprehensive_equipment_lookup(equipment_id)
            
            # Integrate vendor API data
            vendor_data = await self._query_vendor_systems(equipment_id)
            
            # Maintenance history analysis
            maintenance_insights = await self._analyze_maintenance_patterns(equipment_id)
            
            # Regulatory compliance check
            compliance_status = await self._check_regulatory_compliance(equipment_id)
            
            # Performance analytics
            performance_metrics = await self._get_equipment_performance_analytics(equipment_id)
            
            return {
                "technical_specifications": equipment_knowledge.get("specs", {}),
                "maintenance_protocols": equipment_knowledge.get("maintenance", {}),
                "operational_guidelines": equipment_knowledge.get("operations", {}),
                "vendor_information": vendor_data,
                "maintenance_insights": maintenance_insights,
                "compliance_status": compliance_status,
                "performance_analytics": performance_metrics,
                "troubleshooting_guide": equipment_knowledge.get("troubleshooting", {}),
                "training_requirements": equipment_knowledge.get("training", {}),
                "safety_protocols": equipment_knowledge.get("safety", {}),
                "integration_capabilities": equipment_knowledge.get("integration", {}),
                "cost_analytics": equipment_knowledge.get("cost_data", {}),
                "knowledge_freshness": datetime.now().isoformat(),
                "data_sources": ["equipment_manuals", "vendor_apis", "maintenance_logs", "usage_analytics"]
            }
            
        except Exception as e:
            logger.error(f"Enhanced RAG equipment knowledge query error: {e}")
            return {"error": "Comprehensive equipment knowledge not available", "basic_fallback": True}
    
    async def _comprehensive_equipment_lookup(self, equipment_id: str) -> dict:
        """Comprehensive equipment knowledge base lookup with RAG integration"""
        try:
            # Simulate advanced RAG query to comprehensive equipment database
            equipment_database = {
                "specs": {
                    "model_number": "MED-X-2000-PRO",
                    "manufacturer": "MedTech Innovations Inc.",
                    "manufacture_date": "2023-05-15",
                    "serial_number": f"MT{equipment_id[-6:]}2024",
                    "fda_clearance": "510(k) K231547",
                    "weight": "47.3 kg",
                    "dimensions": "125x82x158 cm (LxWxH)",
                    "power_requirements": {
                        "voltage": "100-240V AC",
                        "frequency": "50/60 Hz",
                        "power_consumption": "150W operating, 5W standby"
                    },
                    "environmental_specs": {
                        "operating_temp": "10-40°C",
                        "storage_temp": "-20-60°C",
                        "humidity": "15-95% RH non-condensing",
                        "altitude": "Up to 3000m"
                    },
                    "mobility": "4-wheel caster system with central locking",
                    "display": "15-inch capacitive touchscreen",
                    "connectivity": ["WiFi 802.11ac", "Bluetooth 5.0", "Ethernet", "USB-C"],
                    "battery": {
                        "type": "Lithium-ion",
                        "capacity": "8800mAh",
                        "runtime": "6-8 hours typical use",
                        "charge_time": "4 hours full charge"
                    }
                },
                "maintenance": {
                    "preventive_schedule": {
                        "daily": [
                            "Visual inspection for damage",
                            "Battery level check",
                            "Wheel lock functionality",
                            "Display responsiveness test",
                            "External cleaning per protocol"
                        ],
                        "weekly": [
                            "Calibration verification",
                            "Sensor accuracy check",
                            "Software update check",
                            "Connection port inspection",
                            "Deep cleaning protocols"
                        ],
                        "monthly": [
                            "Full system diagnostic",
                            "Battery capacity test",
                            "Performance benchmark",
                            "Wear component inspection",
                            "Backup/restore procedures"
                        ],
                        "quarterly": [
                            "Comprehensive safety inspection",
                            "Electrical safety testing",
                            "Mechanical stress testing",
                            "Software integrity check",
                            "Training requirement review"
                        ],
                        "annual": [
                            "Full regulatory compliance audit",
                            "Performance validation testing",
                            "Preventive component replacement",
                            "Certification renewal",
                            "Lifecycle assessment"
                        ]
                    },
                    "service_intervals": {
                        "minor_service": "Every 500 operating hours",
                        "major_service": "Every 2000 operating hours",
                        "overhaul": "Every 8000 operating hours",
                        "replacement_consideration": "After 15000 hours or 10 years"
                    },
                    "critical_components": [
                        {"component": "Battery Pack", "lifespan": "3-5 years", "warning_signs": ["Reduced runtime", "Charging issues"]},
                        {"component": "Display Module", "lifespan": "7-10 years", "warning_signs": ["Touch sensitivity", "Dead pixels"]},
                        {"component": "Sensor Array", "lifespan": "5-8 years", "warning_signs": ["Calibration drift", "Accuracy issues"]},
                        {"component": "Motor Assembly", "lifespan": "6-9 years", "warning_signs": ["Unusual noise", "Movement irregularities"]}
                    ]
                },
                "operations": {
                    "setup_procedures": {
                        "initial_setup": "5-8 minutes typical",
                        "quick_setup": "2-3 minutes experienced user",
                        "setup_steps": [
                            "Power on and system initialization",
                            "User authentication",
                            "Calibration verification",
                            "Patient/procedure setup",
                            "Safety checklist completion"
                        ]
                    },
                    "operating_modes": {
                        "standard": "General purpose operation",
                        "emergency": "Rapid deployment mode",
                        "maintenance": "Service and diagnostic mode",
                        "training": "Educational and simulation mode"
                    },
                    "user_requirements": {
                        "minimum_certification": "Level 2 Medical Equipment Operator",
                        "training_hours": "8 hours initial + 2 hours annual",
                        "competency_assessment": "Required every 24 months",
                        "supervision_required": "First 10 uses for new operators"
                    },
                    "usage_limits": {
                        "max_daily_runtime": "10 hours continuous",
                        "cooldown_period": "30 minutes after 8 hours",
                        "max_weekly_usage": "60 hours",
                        "load_capacity": "Maximum 150kg patient weight"
                    }
                },
                "troubleshooting": {
                    "common_issues": [
                        {
                            "symptom": "Display not responding",
                            "probable_causes": ["Low battery", "System overload", "Software freeze"],
                            "solutions": ["Charge battery", "Restart system", "Contact tech support"],
                            "urgency": "medium"
                        },
                        {
                            "symptom": "Calibration errors",
                            "probable_causes": ["Sensor drift", "Environmental factors", "Component wear"],
                            "solutions": ["Recalibrate sensors", "Check environment", "Schedule maintenance"],
                            "urgency": "high"
                        },
                        {
                            "symptom": "Mobility issues",
                            "probable_causes": ["Wheel lock engaged", "Battery low", "Motor malfunction"],
                            "solutions": ["Check wheel locks", "Charge battery", "Service required"],
                            "urgency": "medium"
                        }
                    ],
                    "diagnostic_codes": {
                        "E001": "Battery low warning",
                        "E002": "Calibration required",
                        "E003": "System overtemperature",
                        "E004": "Communication error",
                        "E005": "Sensor malfunction"
                    },
                    "emergency_procedures": {
                        "system_failure": "Switch to manual mode, document incident, notify biomedical",
                        "patient_safety": "Immediately stop operation, ensure patient safety, call emergency",
                        "data_loss": "Attempt auto-recovery, document loss, report to IT"
                    }
                },
                "training": {
                    "certification_levels": {
                        "level_1": "Basic operation and safety",
                        "level_2": "Advanced operation and troubleshooting",
                        "level_3": "Maintenance and repair authorization"
                    },
                    "training_modules": [
                        "Equipment overview and safety",
                        "Setup and calibration procedures",
                        "Operating modes and functions",
                        "Troubleshooting and emergency procedures",
                        "Maintenance and cleaning protocols",
                        "Documentation and reporting requirements"
                    ],
                    "assessment_requirements": {
                        "written_exam": "80% minimum passing score",
                        "practical_demonstration": "Competency-based assessment",
                        "ongoing_education": "4 hours annually"
                    }
                },
                "safety": {
                    "risk_classification": "Class II Medical Device",
                    "safety_features": [
                        "Emergency stop functionality",
                        "Patient weight monitoring",
                        "Automatic safety shutoffs",
                        "Tamper-evident design",
                        "Fail-safe operation modes"
                    ],
                    "hazard_warnings": [
                        "High voltage components - authorized personnel only",
                        "Moving parts - keep clear during operation",
                        "Patient weight limits - do not exceed specifications",
                        "Environmental limits - operate within specified conditions"
                    ],
                    "protective_equipment": [
                        "Safety glasses during maintenance",
                        "Anti-static protection for electronics",
                        "Appropriate lifting techniques for transport"
                    ]
                },
                "integration": {
                    "hl7_compatibility": "HL7 FHIR R4",
                    "emr_integration": ["Epic", "Cerner", "Allscripts", "MEDITECH"],
                    "data_formats": ["XML", "JSON", "CSV", "DICOM"],
                    "api_endpoints": {
                        "device_status": "/api/v1/device/status",
                        "patient_data": "/api/v1/patient/data",
                        "maintenance": "/api/v1/maintenance/schedule"
                    },
                    "security_features": [
                        "AES-256 encryption",
                        "Role-based access control",
                        "Audit logging",
                        "Secure communication protocols"
                    ]
                },
                "cost_data": {
                    "acquisition_cost": "$85,000 - $95,000",
                    "annual_maintenance": "$8,500 - $12,000",
                    "training_costs": "$2,500 per operator",
                    "consumables_annual": "$3,000 - $5,000",
                    "energy_consumption": "$1,200 - $1,800 annually",
                    "roi_metrics": {
                        "productivity_increase": "15-25%",
                        "error_reduction": "40-60%",
                        "staff_efficiency": "20-30% improvement"
                    }
                }
            }
            
            return equipment_database
            
        except Exception as e:
            logger.error(f"Comprehensive equipment lookup error: {e}")
            return {}
    
    async def _query_vendor_systems(self, equipment_id: str) -> dict:
        """RAG-enhanced vendor system integration for real-time equipment data"""
        try:
            # Simulate vendor API integration with RAG-powered contract and warranty lookup
            vendor_data = {
                "manufacturer_info": {
                    "company": "MedTech Innovations Inc.",
                    "contact": {
                        "technical_support": "+1-800-MEDTECH",
                        "field_service": "+1-800-MED-SERV",
                        "email": "support@medtech-innovations.com",
                        "portal": "https://support.medtech-innovations.com"
                    },
                    "service_regions": ["North America", "Europe", "Asia-Pacific"],
                    "response_times": {
                        "critical": "4 hours",
                        "urgent": "24 hours",
                        "standard": "72 hours"
                    }
                },
                "warranty_status": {
                    "warranty_type": "Comprehensive Coverage",
                    "start_date": "2023-05-15",
                    "end_date": "2026-05-15",
                    "coverage_includes": [
                        "Parts and labor",
                        "Software updates",
                        "Preventive maintenance",
                        "Emergency support",
                        "Training updates"
                    ],
                    "exclusions": [
                        "Damage due to misuse",
                        "Unauthorized modifications",
                        "Environmental damage",
                        "Cosmetic wear"
                    ],
                    "service_level": "Platinum Plus"
                },
                "service_contracts": {
                    "active_contracts": [
                        {
                            "contract_id": "SVC-2024-MT-7891",
                            "type": "Full Service Maintenance",
                            "coverage": "24/7 support with 4-hour response",
                            "renewal_date": "2024-12-31",
                            "cost_annual": "$12,500"
                        }
                    ],
                    "available_upgrades": [
                        "Predictive Analytics Package",
                        "Advanced Training Modules",
                        "Remote Diagnostic Capabilities"
                    ]
                },
                "parts_availability": {
                    "critical_parts": {
                        "battery_pack": {"stock": "In Stock", "lead_time": "2-3 days"},
                        "display_module": {"stock": "Limited", "lead_time": "1-2 weeks"},
                        "sensor_array": {"stock": "In Stock", "lead_time": "3-5 days"},
                        "main_board": {"stock": "On Order", "lead_time": "4-6 weeks"}
                    },
                    "consumables": {
                        "cleaning_supplies": {"stock": "In Stock", "lead_time": "Next day"},
                        "calibration_kits": {"stock": "In Stock", "lead_time": "2-3 days"},
                        "filters": {"stock": "In Stock", "lead_time": "Next day"}
                    }
                },
                "software_status": {
                    "current_version": "v3.2.1",
                    "latest_available": "v3.2.3",
                    "update_recommended": True,
                    "security_patches": ["CVE-2024-1234", "CVE-2024-5678"],
                    "feature_updates": [
                        "Enhanced user interface",
                        "Improved battery management",
                        "Advanced diagnostic capabilities"
                    ]
                },
                "recall_notices": {
                    "active_recalls": [],
                    "resolved_recalls": [
                        {
                            "recall_id": "RCL-2023-MT-001",
                            "description": "Software update for calibration accuracy",
                            "resolution_date": "2023-08-15",
                            "status": "Completed"
                        }
                    ]
                },
                "performance_benchmarks": {
                    "industry_average": {
                        "uptime": "96.5%",
                        "mtbf": "2,800 hours",
                        "user_satisfaction": "8.2/10"
                    },
                    "this_equipment": {
                        "uptime": "98.2%",
                        "mtbf": "3,150 hours",
                        "user_satisfaction": "8.8/10"
                    }
                }
            }
            
            return vendor_data
            
        except Exception as e:
            logger.error(f"Vendor system query error: {e}")
            return {"error": "Vendor data not available"}
    
    async def _analyze_maintenance_patterns(self, equipment_id: str) -> dict:
        """AI-powered maintenance pattern analysis with predictive insights"""
        try:
            # Simulate AI-powered maintenance analytics with historical data analysis
            maintenance_analysis = {
                "historical_patterns": {
                    "total_maintenance_events": 47,
                    "preventive_maintenance": 38,
                    "corrective_maintenance": 9,
                    "average_downtime": "2.3 hours per event",
                    "seasonal_trends": {
                        "spring": "Lower maintenance needs",
                        "summer": "Increased cooling system maintenance",
                        "fall": "Standard maintenance patterns",
                        "winter": "Higher heating-related issues"
                    }
                },
                "predictive_insights": {
                    "next_maintenance_prediction": {
                        "type": "Preventive maintenance",
                        "predicted_date": "2024-02-15",
                        "confidence": 0.87,
                        "recommended_actions": [
                            "Battery capacity test",
                            "Calibration verification",
                            "Software update",
                            "Consumables replacement"
                        ]
                    },
                    "risk_assessment": {
                        "failure_probability": 0.12,
                        "risk_level": "Low",
                        "key_risk_factors": [
                            "Battery approaching replacement cycle",
                            "High usage pattern detected",
                            "Environmental stress indicators"
                        ]
                    }
                },
                "cost_optimization": {
                    "maintenance_cost_trend": "Decreasing (-8% year-over-year)",
                    "cost_breakdown": {
                        "labor": "$3,200 annually",
                        "parts": "$2,800 annually",
                        "consumables": "$1,500 annually",
                        "emergency_repairs": "$800 annually"
                    },
                    "optimization_opportunities": [
                        "Bulk purchase discount on consumables",
                        "Preventive maintenance schedule optimization",
                        "Staff training to reduce emergency calls"
                    ]
                },
                "performance_correlation": {
                    "uptime_improvement": "+2.3% after last maintenance",
                    "accuracy_enhancement": "+1.8% post-calibration",
                    "user_satisfaction": "+0.4 points after training update"
                },
                "recommendations": {
                    "immediate": [
                        "Schedule battery capacity test within 2 weeks",
                        "Update operator training materials"
                    ],
                    "short_term": [
                        "Implement condition-based monitoring",
                        "Optimize preventive maintenance intervals"
                    ],
                    "long_term": [
                        "Consider equipment lifecycle planning",
                        "Evaluate upgrade opportunities"
                    ]
                }
            }
            
            return maintenance_analysis
            
        except Exception as e:
            logger.error(f"Maintenance pattern analysis error: {e}")
            return {"error": "Maintenance analysis not available"}
    
    async def _check_regulatory_compliance(self, equipment_id: str) -> dict:
        """Comprehensive regulatory compliance verification with RAG-powered regulatory database"""
        try:
            # Enhanced regulatory compliance check with comprehensive coverage
            compliance_data = {
                "fda_status": {
                    "clearance_number": "510(k) K231547",
                    "clearance_date": "2023-03-22",
                    "device_class": "Class II",
                    "status": "Active and Valid",
                    "next_review": "2028-03-22",
                    "predicate_devices": ["K201234", "K190987"]
                },
                "international_certifications": {
                    "ce_marking": {
                        "status": "Valid",
                        "notified_body": "TÜV SÜD Product Service",
                        "certificate_number": "CE-MD-2023-001547",
                        "expiry_date": "2026-03-22"
                    },
                    "iso_standards": {
                        "iso_13485": {"status": "Compliant", "audit_date": "2023-09-15"},
                        "iso_14971": {"status": "Compliant", "risk_management": "Current"},
                        "iso_62304": {"status": "Compliant", "software_lifecycle": "Current"}
                    },
                    "iec_standards": {
                        "iec_62304": {"status": "Compliant", "medical_device_software": "Current"},
                        "iec_60601": {"status": "Compliant", "electrical_safety": "Current"}
                    }
                },
                "local_regulations": {
                    "hospital_policies": {
                        "infection_control": "Compliant",
                        "biomedical_safety": "Compliant",
                        "data_privacy": "HIPAA Compliant",
                        "environmental": "Compliant"
                    },
                    "state_requirements": {
                        "device_registration": "Current",
                        "operator_licensing": "Valid",
                        "facility_permits": "Active"
                    }
                },
                "quality_management": {
                    "manufacturer_qms": {
                        "iso_13485": "Certified",
                        "fda_qsr": "Compliant",
                        "last_audit": "2023-10-12",
                        "next_audit": "2024-10-12"
                    },
                    "post_market_surveillance": {
                        "adverse_events": "None reported",
                        "field_safety_notices": "None active",
                        "customer_feedback": "Positive trends"
                    }
                },
                "cybersecurity_compliance": {
                    "fda_cybersecurity": {
                        "premarket_guidance": "Compliant",
                        "postmarket_guidance": "Compliant",
                        "sbom": "Available",
                        "vulnerability_management": "Active"
                    },
                    "security_standards": {
                        "nist_framework": "Implemented",
                        "hipaa_security": "Compliant",
                        "encryption": "AES-256"
                    }
                },
                "environmental_compliance": {
                    "rohs": "Compliant",
                    "weee": "Compliant",
                    "energy_star": "Certified",
                    "waste_management": "Documented procedures"
                },
                "compliance_alerts": {
                    "upcoming_renewals": [
                        {
                            "item": "CE Certificate",
                            "due_date": "2026-03-22",
                            "action_required": "Renewal application",
                            "lead_time": "6 months"
                        }
                    ],
                    "regulatory_changes": [
                        {
                            "regulation": "EU MDR",
                            "effective_date": "2024-05-26",
                            "impact": "Documentation updates required",
                            "status": "In progress"
                        }
                    ]
                }
            }
            
            return compliance_data
            
        except Exception as e:
            logger.error(f"Regulatory compliance check error: {e}")
            return {"error": "Compliance data not available"}
    
    async def _get_equipment_performance_analytics(self, equipment_id: str) -> dict:
        """Advanced equipment performance analytics with ML-powered insights"""
        try:
            # Comprehensive performance analytics with predictive modeling
            performance_data = {
                "operational_metrics": {
                    "uptime_percentage": 98.7,
                    "availability_hours": 8567,
                    "total_operating_hours": 8679,
                    "utilization_rate": 0.73,
                    "efficiency_score": 94.2,
                    "accuracy_rating": 99.1,
                    "user_satisfaction": 8.8,
                    "energy_efficiency": 92.5
                },
                "performance_trends": {
                    "30_day": {
                        "uptime_trend": "+1.2%",
                        "utilization_trend": "+5.8%",
                        "efficiency_trend": "+2.1%",
                        "satisfaction_trend": "+0.3 points"
                    },
                    "90_day": {
                        "uptime_trend": "+3.4%",
                        "utilization_trend": "+12.1%",
                        "efficiency_trend": "+6.7%",
                        "satisfaction_trend": "+0.8 points"
                    },
                    "yearly": {
                        "uptime_trend": "+5.2%",
                        "utilization_trend": "+18.9%",
                        "efficiency_trend": "+11.3%",
                        "satisfaction_trend": "+1.2 points"
                    }
                },
                "benchmarking": {
                    "peer_comparison": {
                        "hospital_average": {
                            "uptime": 95.8,
                            "utilization": 0.68,
                            "efficiency": 88.4,
                            "satisfaction": 7.9
                        },
                        "industry_best": {
                            "uptime": 99.2,
                            "utilization": 0.82,
                            "efficiency": 97.1,
                            "satisfaction": 9.3
                        },
                        "relative_performance": "Above average in all metrics"
                    }
                },
                "predictive_analytics": {
                    "performance_forecast": {
                        "next_30_days": {
                            "predicted_uptime": 98.9,
                            "predicted_utilization": 0.76,
                            "confidence_interval": "±2.1%"
                        },
                        "next_90_days": {
                            "predicted_uptime": 98.5,
                            "predicted_utilization": 0.78,
                            "confidence_interval": "±3.8%"
                        }
                    },
                    "anomaly_detection": {
                        "performance_anomalies": [],
                        "usage_pattern_changes": ["Increased weekend utilization"],
                        "efficiency_alerts": ["Minor calibration drift detected"]
                    }
                },
                "user_analytics": {
                    "operator_performance": {
                        "certified_operators": 12,
                        "average_setup_time": "6.2 minutes",
                        "error_rate": 0.8,
                        "training_compliance": 100
                    },
                    "usage_patterns": {
                        "peak_hours": ["08:00-12:00", "14:00-18:00"],
                        "utilization_by_department": {
                            "OR": 45,
                            "ICU": 30,
                            "Emergency": 15,
                            "Other": 10
                        },
                        "procedure_types": {
                            "diagnostic": 60,
                            "therapeutic": 25,
                            "monitoring": 15
                        }
                    }
                },
                "quality_metrics": {
                    "output_quality": {
                        "accuracy_measurements": 99.1,
                        "precision_score": 98.7,
                        "repeatability": 99.3,
                        "consistency_rating": 97.8
                    },
                    "reliability_indicators": {
                        "mtbf": 3247,
                        "mttr": 2.3,
                        "failure_rate": 0.031,
                        "availability": 98.7
                    }
                },
                "improvement_opportunities": {
                    "efficiency_gains": [
                        "Optimize setup procedures (-15% setup time)",
                        "Advanced training for operators (+2% efficiency)",
                        "Predictive maintenance scheduling (+1.5% uptime)"
                    ],
                    "cost_reductions": [
                        "Energy optimization protocols (-8% power consumption)",
                        "Consumables usage optimization (-12% waste)",
                        "Preventive maintenance scheduling (-20% emergency repairs)"
                    ],
                    "user_experience": [
                        "Interface customization (+0.5 satisfaction points)",
                        "Advanced workflow integration (+10% efficiency)",
                        "Real-time feedback systems (+0.3 satisfaction points)"
                    ]
                }
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Performance analytics error: {e}")
            return {"error": "Performance analytics not available"}
    
    async def _check_tracking_system_health(self) -> dict:
        """Monitor tracking system performance and accuracy"""
        try:
            # Simulate tracking system health monitoring
            import random
            
            system_health = {
                "rfid_system": {
                    "status": "operational" if random.random() > 0.05 else "degraded",
                    "active_readers": random.randint(18, 25),
                    "coverage_percentage": random.uniform(0.92, 0.98),
                    "last_maintenance": "2024-01-15"
                },
                "bluetooth_network": {
                    "status": "operational" if random.random() > 0.1 else "partial",
                    "active_beacons": random.randint(45, 60),
                    "signal_strength_avg": random.uniform(0.75, 0.90),
                    "battery_levels": "85% average"
                },
                "wifi_positioning": {
                    "status": "operational" if random.random() > 0.15 else "degraded",
                    "access_points": random.randint(35, 50),
                    "triangulation_accuracy": random.uniform(0.70, 0.85),
                    "network_latency": f"{random.randint(10, 50)}ms"
                },
                "overall_accuracy": random.uniform(0.80, 0.95),
                "accuracy_level": "high" if random.uniform(0.80, 0.95) > 0.85 else "medium"
            }
            
            return system_health
            
        except Exception as e:
            logger.error(f"Tracking system health check error: {e}")
            return {"status": "unknown", "error": str(e)}
    
    async def _detect_location_anomalies(self, equipment_id: str, location_data: dict) -> dict:
        """AI-powered anomaly detection for unusual equipment movements"""
        try:
            # Simulate ML-based anomaly detection
            import random
            
            # Get historical location patterns
            historical_pattern = await self._get_historical_location_pattern(equipment_id)
            
            current_location = location_data.get("current_location")
            anomaly_score = random.uniform(0.0, 1.0)
            
            anomalies = []
            
            # Check for unusual location patterns
            if anomaly_score > 0.8:
                anomalies.append({
                    "type": "unusual_location",
                    "severity": "high",
                    "description": f"Equipment detected in unexpected location: {current_location}",
                    "confidence": anomaly_score
                })
            
            # Check for rapid movement patterns
            if anomaly_score > 0.7:
                anomalies.append({
                    "type": "rapid_movement",
                    "severity": "medium",
                    "description": "Unusual movement pattern detected - possible unauthorized transport",
                    "confidence": anomaly_score * 0.8
                })
            
            # Check for extended stationary periods
            if anomaly_score > 0.6:
                anomalies.append({
                    "type": "extended_idle",
                    "severity": "low",
                    "description": "Equipment stationary for extended period - possible maintenance needed",
                    "confidence": anomaly_score * 0.6
                })
            
            return {
                "anomaly_score": anomaly_score,
                "alerts": anomalies,
                "historical_pattern": historical_pattern,
                "recommendation": "Monitor closely" if anomaly_score > 0.7 else "Normal operation"
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return {"anomaly_score": 0.0, "alerts": [], "error": str(e)}
    
    async def _get_historical_location_pattern(self, equipment_id: str) -> dict:
        """Analyze historical location patterns for anomaly detection"""
        try:
            # Simulate historical pattern analysis
            import random
            
            common_locations = [
                {"location": "OR-1", "frequency": 0.3, "avg_duration": "2.5 hours"},
                {"location": "ICU-Bay-3", "frequency": 0.25, "avg_duration": "4 hours"},
                {"location": "Equipment-Storage", "frequency": 0.2, "avg_duration": "12 hours"},
                {"location": "Maintenance-Shop", "frequency": 0.15, "avg_duration": "1 hour"},
                {"location": "Emergency-Room-2", "frequency": 0.1, "avg_duration": "1.5 hours"}
            ]
            
            return {
                "common_locations": common_locations,
                "usage_pattern": "high_utilization",
                "peak_hours": ["08:00-12:00", "14:00-18:00"],
                "maintenance_windows": ["02:00-06:00"],
                "location_transitions": {
                    "typical": ["Storage → OR → Storage", "OR → ICU → Storage"],
                    "unusual": ["Storage → Loading-Dock", "Unauthorized-Area"]
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _verify_location_multi_source(self, equipment, location_data: dict) -> dict:
        """Cross-verify location using multiple tracking sources"""
        try:
            tracking_methods = location_data.get("tracking_methods", {})
            verified_location = location_data.get("current_location", "Unknown")
            
            # Cross-reference multiple sources
            source_confirmations = 0
            confirmation_sources = []
            
            for method, data in tracking_methods.items():
                if data.get("status") in ["active", "recent"]:
                    source_confirmations += 1
                    confirmation_sources.append(method)
            
            # Calculate confidence based on source agreement
            if source_confirmations >= 3:
                confidence = 0.95
            elif source_confirmations == 2:
                confidence = 0.85
            elif source_confirmations == 1:
                confidence = 0.70
            else:
                confidence = 0.30
            
            # Add database verification
            database_location = equipment.current_location if equipment else None
            if database_location and database_location == verified_location:
                confidence = min(confidence + 0.1, 1.0)
                confirmation_sources.append("database")
            
            return {
                "current_location": verified_location,
                "confidence": confidence,
                "confirmation_sources": confirmation_sources,
                "source_count": source_confirmations,
                "database_match": database_location == verified_location,
                "verification_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Location verification error: {e}")
            return {
                "current_location": "Verification Failed",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _generate_location_recommendations(self, equipment, location_data: dict, request: dict) -> list:
        """Generate intelligent location-based recommendations"""
        try:
            recommendations = []
            current_location = location_data.get("current_location", "Unknown")
            confidence = location_data.get("confidence", 0.0)
            
            # Low confidence recommendations
            if confidence < 0.7:
                recommendations.append({
                    "type": "location_verification",
                    "priority": "high",
                    "action": "Manual verification required",
                    "reason": f"Location confidence {confidence:.1%} below threshold",
                    "suggested_action": "Send staff to perform visual confirmation"
                })
            
            # Equipment-specific recommendations
            if equipment:
                # Maintenance due recommendations
                if equipment.next_maintenance_date and equipment.next_maintenance_date <= datetime.now().date():
                    recommendations.append({
                        "type": "maintenance_due",
                        "priority": "medium",
                        "action": "Schedule maintenance",
                        "reason": "Maintenance overdue",
                        "suggested_location": "Maintenance-Shop"
                    })
                
                # Usage optimization
                if current_location == "Equipment-Storage":
                    recommendations.append({
                        "type": "utilization",
                        "priority": "low",
                        "action": "Consider deployment",
                        "reason": "Equipment idle in storage",
                        "suggested_departments": ["OR", "ICU", "Emergency"]
                    })
            
            # Request-specific recommendations
            request_department = request.get("department")
            if request_department and current_location != request_department:
                distance = await self._calculate_transport_time(current_location, request_department)
                recommendations.append({
                    "type": "transport_optimization",
                    "priority": "medium",
                    "action": f"Transport to {request_department}",
                    "estimated_time": distance.get("transport_time", "Unknown"),
                    "transport_method": distance.get("recommended_method", "manual")
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Location recommendations error: {e}")
            return []
    
    async def _find_optimal_equipment_with_ml(self, request: dict, state: dict) -> dict:
        """ML-powered optimal equipment selection and location"""
        try:
            # Simulate ML-based equipment selection
            equipment_type = request.get("equipment_type", "")
            department = request.get("department", "")
            urgency = request.get("urgency", "medium")
            
            # Get available equipment
            tracking_metadata = state.get("tracking_metadata", {})
            available_equipment = tracking_metadata.get("available_equipment", [])
            
            if not available_equipment:
                return None
            
            # ML scoring algorithm simulation
            scored_equipment = []
            
            for equipment in available_equipment:
                score = 0.0
                
                # Distance scoring (40% weight)
                distance_score = await self._calculate_distance_score(
                    equipment.get("location"), department
                )
                score += distance_score * 0.4
                
                # Availability scoring (30% weight)
                availability_score = 1.0 if equipment.get("status") == "AVAILABLE" else 0.3
                score += availability_score * 0.3
                
                # Condition scoring (20% weight)
                condition_score = self._get_condition_score(equipment.get("condition", "good"))
                score += condition_score * 0.2
                
                # Urgency matching (10% weight)
                urgency_score = self._get_urgency_score(urgency, equipment)
                score += urgency_score * 0.1
                
                scored_equipment.append({
                    "equipment": equipment,
                    "ml_score": score,
                    "scoring_breakdown": {
                        "distance": distance_score,
                        "availability": availability_score,
                        "condition": condition_score,
                        "urgency": urgency_score
                    }
                })
            
            # Sort by ML score and select best
            scored_equipment.sort(key=lambda x: x["ml_score"], reverse=True)
            best_equipment = scored_equipment[0]
            
            # Get detailed location data for selected equipment
            location_data = await self._get_advanced_realtime_location(
                best_equipment["equipment"]["id"], request
            )
            
            return {
                "id": best_equipment["equipment"]["id"],
                "location_data": location_data,
                "ml_score": best_equipment["ml_score"],
                "reasoning": f"Selected based on ML scoring: {best_equipment['ml_score']:.2f}",
                "scoring_details": best_equipment["scoring_breakdown"]
            }
            
        except Exception as e:
            logger.error(f"ML equipment selection error: {e}")
            return None
    
    async def _calculate_distance_score(self, equipment_location: str, target_department: str) -> float:
        """Calculate distance-based scoring for equipment selection"""
        try:
            # Simulate hospital layout and distance calculations
            distance_matrix = {
                ("OR-1", "Emergency"): 0.9,
                ("OR-1", "ICU"): 0.8,
                ("Equipment-Storage", "OR-1"): 0.6,
                ("Equipment-Storage", "Emergency"): 0.5,
                ("ICU-Bay-3", "Emergency"): 0.7,
                ("Maintenance-Shop", "OR-1"): 0.3
            }
            
            distance_score = distance_matrix.get(
                (equipment_location, target_department), 0.5  # Default medium distance
            )
            
            return distance_score
            
        except Exception as e:
            return 0.5  # Default score on error
    
    def _get_condition_score(self, condition: str) -> float:
        """Convert equipment condition to scoring value"""
        condition_scores = {
            "excellent": 1.0,
            "good": 0.8,
            "fair": 0.6,
            "poor": 0.3,
            "maintenance_required": 0.1
        }
        return condition_scores.get(condition.lower(), 0.5)
    
    def _get_urgency_score(self, urgency: str, equipment: dict) -> float:
        """Calculate urgency-based equipment scoring"""
        urgency_weights = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.6,
            "low": 0.4
        }
        
        base_score = urgency_weights.get(urgency.lower(), 0.5)
        
        # Boost score for equipment with recent maintenance
        if equipment.get("last_maintenance_days", 30) < 7:
            base_score *= 1.2
        
        return min(base_score, 1.0)
    
    async def _calculate_transport_time(self, from_location: str, to_location: str) -> dict:
        """Calculate estimated transport time between locations"""
        try:
            # Simulate hospital layout and transport calculations
            transport_matrix = {
                ("Equipment-Storage", "OR-1"): {"time": "8 minutes", "method": "manual_transport"},
                ("OR-1", "ICU-Bay-3"): {"time": "5 minutes", "method": "wheeled_transport"},
                ("ICU-Bay-3", "Emergency"): {"time": "12 minutes", "method": "elevator_required"},
                ("Maintenance-Shop", "OR-1"): {"time": "15 minutes", "method": "manual_transport"}
            }
            
            transport_info = transport_matrix.get(
                (from_location, to_location),
                {"time": "10 minutes", "method": "manual_transport"}  # Default
            )
            
            return {
                "transport_time": transport_info["time"],
                "recommended_method": transport_info["method"],
                "route_complexity": "standard",
                "staff_required": 1 if "manual" in transport_info["method"] else 2
            }
            
        except Exception as e:
            return {
                "transport_time": "Unknown",
                "recommended_method": "manual_transport",
                "error": str(e)
            }
    
    def _calculate_accuracy_radius(self, confidence: float) -> str:
        """Calculate location accuracy radius based on confidence"""
        if confidence >= 0.9:
            return "±2 meters"
        elif confidence >= 0.8:
            return "±5 meters"
        elif confidence >= 0.7:
            return "±10 meters"
        elif confidence >= 0.5:
            return "±20 meters"
        else:
            return "±50 meters"
