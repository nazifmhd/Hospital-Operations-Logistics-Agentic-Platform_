"""
Setup and Initialization Script for RAG and MCP Systems
Initializes the Retrieval-Augmented Generation and Model Context Protocol systems
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add AI/ML modules to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_rag_system():
    """Setup and initialize the RAG system"""
    try:
        logger.info("🔍 Setting up RAG system...")
        
        from rag_system import get_rag_system, Document, DocumentType
        
        # Initialize RAG system
        rag_system = await get_rag_system()
        
        # Add some test knowledge
        test_documents = [
            {
                "content": """
                Hospital Supply Chain Emergency Procedures:
                
                1. Critical Supply Shortage Protocol:
                - Notify department heads immediately
                - Check emergency stock reserves
                - Contact backup suppliers within 1 hour
                - Implement rationing if necessary
                
                2. Equipment Malfunction Response:
                - Isolate affected equipment immediately
                - Notify biomedical engineering
                - Activate backup equipment protocols
                - Document incident for compliance
                
                3. Supplier Disruption Management:
                - Assess inventory impact within 2 hours
                - Activate alternative supplier agreements
                - Communicate with clinical departments
                - Update procurement timelines
                """,
                "doc_type": DocumentType.PROCEDURE_GUIDE,
                "metadata": {
                    "category": "emergency_procedures",
                    "priority": "critical",
                    "last_updated": "2024-07-20"
                },
                "source": "emergency_manual"
            },
            {
                "content": """
                Cost Optimization Strategies for Hospital Supply Chain:
                
                1. Bulk Purchasing Benefits:
                - 10-15% savings on high-volume items
                - Reduced order processing costs
                - Better supplier relationship leverage
                - Requires adequate storage capacity
                
                2. Just-in-Time Inventory:
                - Reduces carrying costs by 20-30%
                - Minimizes waste from expiration
                - Requires reliable supplier performance
                - Risk mitigation strategies essential
                
                3. Standardization Programs:
                - Reduce SKU complexity by 40%
                - Improve staff training efficiency
                - Enhance purchasing power
                - Simplify maintenance requirements
                """,
                "doc_type": DocumentType.POLICY_DOCUMENT,
                "metadata": {
                    "category": "cost_optimization",
                    "financial_impact": "high",
                    "implementation_complexity": "medium"
                },
                "source": "financial_guidelines"
            }
        ]
        
        # Add test documents
        for doc_data in test_documents:
            document = Document(
                id=f"setup_{doc_data['doc_type'].value}_{datetime.now().isoformat()}",
                content=doc_data["content"],
                doc_type=doc_data["doc_type"],
                metadata=doc_data["metadata"],
                source=doc_data["source"]
            )
            
            success = await rag_system.vector_store.add_document(document)
            if success:
                logger.info(f"✅ Added document: {document.id}")
            else:
                logger.warning(f"⚠️ Failed to add document: {document.id}")
        
        # Test RAG retrieval
        test_query = "What should I do if there's a critical supply shortage?"
        context = await rag_system.get_context(test_query)
        
        if context.relevant_documents:
            logger.info(f"✅ RAG system test successful - found {len(context.relevant_documents)} relevant documents")
            logger.info(f"Context summary: {context.context_summary[:100]}...")
        else:
            logger.warning("⚠️ RAG system test - no relevant documents found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG system setup failed: {e}")
        return False

async def setup_mcp_server():
    """Setup and initialize the MCP server"""
    try:
        logger.info("🔗 Setting up MCP server...")
        
        from mcp_server import get_mcp_server
        
        # Initialize MCP server
        mcp_server = get_mcp_server()
        
        # Test server capabilities
        tools_response = await mcp_server._handle_list_tools({}, "setup_test")
        resources_response = await mcp_server._handle_list_resources({}, "setup_test")
        prompts_response = await mcp_server._handle_list_prompts({}, "setup_test")
        
        logger.info(f"✅ MCP server initialized with:")
        logger.info(f"  - {len(tools_response.get('tools', []))} tools available")
        logger.info(f"  - {len(resources_response.get('resources', []))} resources available")
        logger.info(f"  - {len(prompts_response.get('prompts', []))} prompts available")
        
        # Test a simple tool call
        test_result = await mcp_server._handle_get_inventory_status({}, "setup_test")
        if test_result and test_result.get("status") == "success":
            logger.info("✅ MCP tool test successful")
        else:
            logger.warning("⚠️ MCP tool test failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MCP server setup failed: {e}")
        return False

async def setup_enhanced_agent():
    """Setup and test the enhanced LLM agent"""
    try:
        logger.info("🤖 Setting up Enhanced LLM Agent...")
        
        from llm_integration import LLMEnhancedSupplyAgent
        
        # Initialize enhanced agent
        agent = LLMEnhancedSupplyAgent()
        await agent.initialize()
        
        # Test enhanced query processing
        test_query = "How can I optimize inventory costs while maintaining patient safety?"
        test_context = {
            "user_role": "inventory_manager",
            "department": "supply_chain",
            "connection_id": "setup_test"
        }
        
        response = await agent.process_query_with_context(test_query, test_context)
        
        if response and response.content:
            logger.info("✅ Enhanced agent test successful")
            logger.info(f"Response confidence: {response.confidence:.2f}")
        else:
            logger.warning("⚠️ Enhanced agent test failed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced agent setup failed: {e}")
        return False

async def run_integration_test():
    """Run a comprehensive integration test"""
    try:
        logger.info("🧪 Running integration test...")
        
        from rag_mcp_api import get_enhanced_agent
        
        # Get the enhanced agent
        agent = await get_enhanced_agent()
        if not agent:
            logger.error("❌ Could not get enhanced agent for integration test")
            return False
        
        # Test RAG-enhanced query
        test_query = "What are the emergency procedures for critical supply shortages and how can I optimize costs?"
        
        response = await agent.process_query_with_context(test_query)
        
        if response and response.content:
            logger.info("✅ Integration test successful")
            logger.info(f"Generated response length: {len(response.content)} characters")
            logger.info(f"Confidence: {response.confidence:.2f}")
            
            # Test recommendations
            context = {
                "current_inventory_value": 125000,
                "low_stock_items": 15,
                "pending_orders": 8,
                "patient_census": 285
            }
            
            recommendations = await agent.get_intelligent_recommendations(context)
            
            if recommendations and not recommendations.get("error"):
                logger.info("✅ Recommendations generation successful")
                logger.info(f"Recommendation categories: {len([k for k in recommendations.keys() if not k.startswith('_')])}")
            else:
                logger.warning("⚠️ Recommendations generation failed")
            
            return True
        else:
            logger.warning("⚠️ Integration test failed - no response")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Starting RAG and MCP System Setup...")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    results = {
        "rag_system": False,
        "mcp_server": False,
        "enhanced_agent": False,
        "integration_test": False
    }
    
    # Setup RAG system
    results["rag_system"] = await setup_rag_system()
    
    # Setup MCP server
    results["mcp_server"] = await setup_mcp_server()
    
    # Setup enhanced agent
    results["enhanced_agent"] = await setup_enhanced_agent()
    
    # Run integration test
    if all([results["rag_system"], results["mcp_server"], results["enhanced_agent"]]):
        results["integration_test"] = await run_integration_test()
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("📊 SETUP SUMMARY:")
    logger.info("="*50)
    
    for component, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{component.replace('_', ' ').title()}: {status}")
    
    overall_success = all(results.values())
    logger.info(f"\nOverall Setup: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    if overall_success:
        logger.info("\n🎉 RAG and MCP systems are ready for use!")
        logger.info("You can now:")
        logger.info("  - Query the knowledge base with contextual responses")
        logger.info("  - Use MCP tools for structured operations")
        logger.info("  - Get intelligent recommendations")
        logger.info("  - Access enhanced LLM capabilities")
    else:
        logger.info("\n⚠️ Some components failed to initialize.")
        logger.info("Check the logs above for specific error details.")
        logger.info("The system may still work with reduced functionality.")
    
    return overall_success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed with unexpected error: {e}")
        sys.exit(1)
