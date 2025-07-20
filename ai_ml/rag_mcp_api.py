"""
RAG and MCP API Integration for Hospital Supply Chain Platform
FastAPI endpoints for Retrieval-Augmented Generation and Model Context Protocol
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

# Import RAG and MCP systems
try:
    import sys
    import os
    
    # Add current directory to path for local imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from rag_system import (
        get_rag_system, enhance_with_rag, RAGContext, Document, DocumentType
    )
    from mcp_server import (
        get_mcp_server, handle_mcp_request, MCPMessage, MCPMessageType
    )
    from llm_integration import LLMEnhancedSupplyAgent
    RAG_MCP_AVAILABLE = True
    logging.info("✅ RAG and MCP systems imported successfully")
except ImportError as e:
    RAG_MCP_AVAILABLE = False
    logging.warning(f"RAG/MCP systems not available: {e}")
    # Create dummy classes for when RAG/MCP is not available
    class RAGContext:
        def __init__(self, **kwargs):
            pass
    
    class Document:
        def __init__(self, **kwargs):
            pass
    
    class DocumentType:
        pass
    
    class MCPMessage:
        def __init__(self, **kwargs):
            pass
    
    class MCPMessageType:
        pass

# Pydantic models for API
class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="Query to search for relevant context")
    context_type: str = Field("general", description="Type of context to retrieve")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of documents to retrieve")

class RAGQueryResponse(BaseModel):
    query: str
    relevant_documents: List[Dict[str, Any]]
    context_summary: str
    confidence_score: float
    retrieved_at: str

class AddKnowledgeRequest(BaseModel):
    content: str = Field(..., description="Content to add to knowledge base")
    doc_type: str = Field(..., description="Document type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    source: str = Field("api", description="Source of the document")

class MCPToolRequest(BaseModel):
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters")
    connection_id: str = Field("default", description="Connection identifier")

class MCPToolResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class EnhancedQueryRequest(BaseModel):
    query: str = Field(..., description="Query to process with enhanced context")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context information")
    include_rag: bool = Field(True, description="Include RAG context")
    include_mcp: bool = Field(True, description="Include MCP context")

class EnhancedQueryResponse(BaseModel):
    content: str
    confidence: float
    reasoning: str
    suggestions: List[str]
    context_used: Dict[str, Any]
    generated_at: str

class RecommendationsRequest(BaseModel):
    context: Dict[str, Any] = Field(..., description="Current system context")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus recommendations on")

# Initialize router
router = APIRouter(prefix="/api/v2/rag-mcp", tags=["RAG & MCP"])

# Global instances
enhanced_agent = None

async def get_enhanced_agent():
    """Get or initialize enhanced agent"""
    global enhanced_agent
    if enhanced_agent is None and RAG_MCP_AVAILABLE:
        enhanced_agent = LLMEnhancedSupplyAgent()
        await enhanced_agent.initialize()
    return enhanced_agent

@router.get("/status")
async def get_rag_mcp_status():
    """Get RAG and MCP system status"""
    status = {
        "rag_mcp_available": RAG_MCP_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if RAG_MCP_AVAILABLE:
        try:
            # Test RAG system
            rag_system = await get_rag_system()
            status["rag_system"] = "available"
            
            # Test MCP server
            mcp_server = get_mcp_server()
            status["mcp_server"] = "available"
            
            # Test enhanced agent
            agent = await get_enhanced_agent()
            status["enhanced_agent"] = "available" if agent else "unavailable"
            
        except Exception as e:
            status["error"] = str(e)
            status["rag_system"] = "error"
            status["mcp_server"] = "error"
    
    return status

@router.post("/rag/query", response_model=RAGQueryResponse)
async def query_rag_system(request: RAGQueryRequest):
    """Query the RAG system for relevant context"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        rag_context = await enhance_with_rag(request.query, request.context_type)
        
        # Convert documents to serializable format
        documents = []
        for doc in rag_context.relevant_documents:
            documents.append({
                "id": doc.id,
                "content": doc.content[:500] + "..." if len(doc.content) > 500 else doc.content,
                "doc_type": doc.doc_type.value,
                "metadata": doc.metadata,
                "source": doc.source,
                "relevance_score": doc.relevance_score
            })
        
        return RAGQueryResponse(
            query=rag_context.query,
            relevant_documents=documents,
            context_summary=rag_context.context_summary,
            confidence_score=rag_context.confidence_score,
            retrieved_at=rag_context.retrieved_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@router.post("/rag/add-knowledge")
async def add_knowledge_to_rag(request: AddKnowledgeRequest, background_tasks: BackgroundTasks):
    """Add new knowledge to the RAG system"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        # Add knowledge in background
        background_tasks.add_task(
            _add_knowledge_background,
            request.content,
            request.doc_type,
            request.metadata,
            request.source
        )
        
        return {
            "success": True,
            "message": "Knowledge addition queued",
            "doc_type": request.doc_type,
            "content_length": len(request.content)
        }
        
    except Exception as e:
        logging.error(f"Add knowledge failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")

async def _add_knowledge_background(content: str, doc_type: str, metadata: Dict[str, Any], source: str):
    """Background task to add knowledge to RAG system"""
    try:
        rag_system = await get_rag_system()
        
        # Convert doc_type string to enum
        doc_type_enum = DocumentType.INVENTORY_DATA  # Default
        for dt in DocumentType:
            if dt.value == doc_type:
                doc_type_enum = dt
                break
        
        document = Document(
            id=f"api_{datetime.now().isoformat()}_{hash(content) % 1000000}",
            content=content,
            doc_type=doc_type_enum,
            metadata=metadata,
            source=source
        )
        
        await rag_system.vector_store.add_document(document)
        logging.info(f"Successfully added knowledge document: {document.id}")
        
    except Exception as e:
        logging.error(f"Background knowledge addition failed: {e}")

@router.get("/mcp/capabilities")
async def get_mcp_capabilities():
    """Get available MCP capabilities"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP system not available")
    
    try:
        mcp_server = get_mcp_server()
        
        # Get tools
        tools_response = await mcp_server._handle_list_tools({}, "api")
        
        # Get resources
        resources_response = await mcp_server._handle_list_resources({}, "api")
        
        # Get prompts
        prompts_response = await mcp_server._handle_list_prompts({}, "api")
        
        return {
            "tools": tools_response.get("tools", []),
            "resources": resources_response.get("resources", []),
            "prompts": prompts_response.get("prompts", []),
            "server_info": mcp_server.server_info
        }
        
    except Exception as e:
        logging.error(f"Get MCP capabilities failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

@router.post("/mcp/tool", response_model=MCPToolResponse)
async def call_mcp_tool(request: MCPToolRequest):
    """Call an MCP tool"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP system not available")
    
    start_time = datetime.now()
    
    try:
        agent = await get_enhanced_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Enhanced agent not available")
        
        result = await agent.process_mcp_tool_request(
            request.tool_name,
            request.parameters,
            {"connection_id": request.connection_id}
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            return MCPToolResponse(
                success=False,
                error=result["error"],
                execution_time=execution_time
            )
        else:
            return MCPToolResponse(
                success=True,
                result=result,
                execution_time=execution_time
            )
            
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logging.error(f"MCP tool call failed: {e}")
        return MCPToolResponse(
            success=False,
            error=str(e),
            execution_time=execution_time
        )

@router.post("/enhanced-query", response_model=EnhancedQueryResponse)
async def process_enhanced_query(request: EnhancedQueryRequest):
    """Process query with RAG and MCP enhancement"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enhanced query system not available")
    
    try:
        agent = await get_enhanced_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Enhanced agent not available")
        
        response = await agent.process_query_with_context(
            request.query,
            request.user_context
        )
        
        # Gather context information
        context_used = {
            "rag_enabled": request.include_rag and agent.rag_system is not None,
            "mcp_enabled": request.include_mcp and agent.mcp_server is not None,
            "user_context_provided": request.user_context is not None
        }
        
        return EnhancedQueryResponse(
            content=response.content,
            confidence=response.confidence,
            reasoning=response.reasoning,
            suggestions=response.suggestions,
            context_used=context_used,
            generated_at=response.generated_at.isoformat()
        )
        
    except Exception as e:
        logging.error(f"Enhanced query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced query failed: {str(e)}")

@router.post("/recommendations")
async def get_intelligent_recommendations(request: RecommendationsRequest):
    """Get intelligent recommendations based on current context"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="Recommendations system not available")
    
    try:
        agent = await get_enhanced_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Enhanced agent not available")
        
        recommendations = await agent.get_intelligent_recommendations(request.context)
        
        return recommendations
        
    except Exception as e:
        logging.error(f"Recommendations generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

@router.get("/knowledge-stats")
async def get_knowledge_base_stats():
    """Get statistics about the knowledge base"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        rag_system = await get_rag_system()
        
        # Get basic stats from vector store
        stats = {
            "backend_type": rag_system.vector_store.backend,
            "cache_size": len(rag_system.context_cache),
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to get document count based on backend
        if rag_system.vector_store.backend == "chromadb":
            try:
                collection_info = rag_system.vector_store.collection.count()
                stats["document_count"] = collection_info
            except:
                stats["document_count"] = "unavailable"
        elif rag_system.vector_store.backend in ["sklearn", "fallback"]:
            try:
                cursor = rag_system.vector_store.documents_db.cursor()
                cursor.execute("SELECT COUNT(*) FROM documents")
                count = cursor.fetchone()[0]
                stats["document_count"] = count
            except:
                stats["document_count"] = "unavailable"
        
        return stats
        
    except Exception as e:
        logging.error(f"Knowledge stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")

# Additional utility endpoints

@router.delete("/knowledge/clear")
async def clear_knowledge_cache():
    """Clear knowledge base cache (admin function)"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        rag_system = await get_rag_system()
        rag_system.context_cache.clear()
        
        return {
            "success": True,
            "message": "Knowledge cache cleared",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@router.post("/mcp/context")
async def get_mcp_context(connection_id: str = "default"):
    """Get current MCP context"""
    if not RAG_MCP_AVAILABLE:
        raise HTTPException(status_code=503, detail="MCP system not available")
    
    try:
        mcp_server = get_mcp_server()
        context = await mcp_server._handle_get_context({}, connection_id)
        
        return context
        
    except Exception as e:
        logging.error(f"MCP context retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {str(e)}")

# Export router for integration
__all__ = ["router"]
