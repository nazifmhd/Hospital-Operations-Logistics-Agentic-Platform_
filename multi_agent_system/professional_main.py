#!/usr/bin/env python3
"""
Professional Hospital Operations API Server
Enterprise-grade FastAPI server with full monitoring and management
"""
import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import our professional components
from core.coordinator import MultiAgentCoordinator
from core.base_agent import AgentRequest, AgentResponse
from database.config import db_manager

# Configure professional logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hospital_operations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("hospital_api")

# Global coordinator instance
coordinator: MultiAgentCoordinator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Professional application lifecycle management"""
    global coordinator
    
    # Startup
    logger.info("🚀 Starting Hospital Operations API Server")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        logger.info("🗄️ Initializing database...")
        db_manager.initialize()  # This is not async
        
        # Initialize coordinator and agents
        logger.info("🎯 Initializing Multi-Agent Coordinator...")
        coordinator = MultiAgentCoordinator()
        await coordinator.initialize_all_agents()
        
        logger.info("✅ Hospital Operations API Server is ready!")
        logger.info("🏥 All agents operational and ready to serve")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Shutting down Hospital Operations API Server")
        if coordinator:
            await coordinator.shutdown_all_agents()
        await db_manager.close()
        logger.info("✅ Graceful shutdown completed")

# Professional API Models
class ActionRequest(BaseModel):
    """Professional API request model"""
    agent_type: str = Field(..., description="Type of agent (bed_management, equipment_tracker, staff_allocation, supply_inventory)")
    action: str = Field(..., description="Action to execute")
    data: Dict[str, Any] = Field(default_factory=dict, description="Action data")
    priority: str = Field(default="normal", description="Request priority")
    
class CoordinationRequest(BaseModel):
    """Multi-agent coordination request"""
    scenario: str = Field(..., description="Coordination scenario")
    data: Dict[str, Any] = Field(default_factory=dict, description="Scenario data")
    priority: str = Field(default="normal", description="Request priority")

class HealthResponse(BaseModel):
    """System health response"""
    status: str
    timestamp: datetime
    agents: Dict[str, Any]
    database: Dict[str, Any]
    system_metrics: Dict[str, Any]

# Create FastAPI app with professional configuration
app = FastAPI(
    title="Hospital Operations Management API",
    description="Professional multi-agent hospital operations platform",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Professional middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Professional error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )

# Professional API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """API root endpoint"""
    return {
        "service": "Hospital Operations Management API",
        "version": "2.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Professional system health check"""
    try:
        # Check agents
        agent_health = {}
        if coordinator and hasattr(coordinator, 'agents'):
            for agent_type, agent in coordinator.agents.items():
                try:
                    agent_health[agent_type] = agent.get_health_status()
                except Exception as e:
                    agent_health[agent_type] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        # Check database
        try:
            db_healthy = await db_manager.is_healthy()
        except Exception:
            db_healthy = False
            
        db_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "connection_pool": "active" if db_healthy else "inactive"
        }
        
        # System metrics with safe access
        try:
            uptime = time.time() - coordinator.startup_time if coordinator and hasattr(coordinator, 'startup_time') else 0
            total_requests = 0
            if coordinator and hasattr(coordinator, 'agents'):
                for agent in coordinator.agents.values():
                    if hasattr(agent, 'performance_metrics'):
                        total_requests += agent.performance_metrics.get("requests_processed", 0)
        except Exception:
            uptime = 0
            total_requests = 0
            
        system_metrics = {
            "uptime_seconds": uptime,
            "total_requests": total_requests
        }
        
        # Determine overall status
        overall_status = "healthy"
        if not db_healthy:
            overall_status = "degraded"
        elif coordinator and hasattr(coordinator, 'agents'):
            try:
                if not all(getattr(agent, 'is_initialized', False) for agent in coordinator.agents.values()):
                    overall_status = "degraded"
            except Exception:
                overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            agents=agent_health,
            database=db_status,
            system_metrics=system_metrics
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Health check failed")

@app.post("/agents/{agent_type}/action", response_model=AgentResponse)
async def execute_agent_action(agent_type: str, request: ActionRequest):
    """Execute action on specific agent"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="System not ready")
    
    if agent_type not in coordinator.agents:
        raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")
    
    try:
        agent = coordinator.agents[agent_type]
        response = await agent.execute_action(request.action, request.data)
        return response
        
    except Exception as e:
        logger.error(f"Agent action failed: {e}")
        raise HTTPException(status_code=500, detail=f"Action execution failed: {str(e)}")

@app.post("/coordination/execute", response_model=Dict[str, Any])
async def execute_coordination(request: CoordinationRequest):
    """Execute multi-agent coordination scenario"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="System not ready")
    
    try:
        result = await coordinator.process_coordination_request(request.scenario, request.data)
        return {
            "success": True,
            "scenario": request.scenario,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Coordination failed: {e}")
        raise HTTPException(status_code=500, detail=f"Coordination failed: {str(e)}")

@app.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """List all available agents and their capabilities"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="System not ready")
    
    agents_info = {}
    for agent_type, agent in coordinator.agents.items():
        agents_info[agent_type] = {
            "agent_id": agent.agent_id,
            "status": agent.get_health_status(),
            "available_actions": agent.get_available_actions()
        }
    
    return {
        "agents": agents_info,
        "total_agents": len(agents_info),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics():
    """Professional system metrics endpoint"""
    if not coordinator:
        raise HTTPException(status_code=503, detail="System not ready")
    
    metrics = {
        "system": {
            "uptime_seconds": time.time() - coordinator.startup_time,
            "timestamp": datetime.now().isoformat()
        },
        "agents": {}
    }
    
    for agent_type, agent in coordinator.agents.items():
        metrics["agents"][agent_type] = agent.performance_metrics
    
    return metrics

# Professional server configuration
if __name__ == "__main__":
    logger.info("🏥 Starting Hospital Operations Professional Server")
    
    uvicorn.run(
        "professional_main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to False for production
        log_level="info",
        access_log=True,
        workers=1  # Adjust for production load
    )
