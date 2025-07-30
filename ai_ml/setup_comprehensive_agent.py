"""
Setup script for Comprehensive AI Agent System
Initializes all components: RAG, Vector DB, Knowledge Base, and Agent
"""

import asyncio
import logging
import os
import sys
import json
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root / "backend"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'chromadb', 'sentence_transformers', 'google.generativeai',
        'sqlalchemy', 'fastapi', 'numpy', 'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Install with: pip install -r requirements_rag_enhanced.txt")
        return False
    
    logger.info("✅ All dependencies are installed")
    return True

async def setup_rag_system():
    """Initialize RAG system and vector database"""
    try:
        import chromadb
        from chromadb.config import Settings
        import sentence_transformers
        from sentence_transformers import SentenceTransformer
        
        # Create RAG data directory
        rag_dir = current_dir / "rag_data"
        rag_dir.mkdir(exist_ok=True)
        
        chroma_dir = rag_dir / "chromadb"
        chroma_dir.mkdir(exist_ok=True)
        
        # Initialize ChromaDB with updated configuration
        client = chromadb.PersistentClient(path=str(chroma_dir))
        
        # Create or get collection
        collection = client.get_or_create_collection(
            name="hospital_supply_knowledge",
            metadata={"description": "Hospital supply chain knowledge base"}
        )
        
        # Initialize embedding model
        logger.info("📥 Downloading embedding model (this may take a few minutes)...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Create comprehensive knowledge base
        knowledge_items = [
            {
                "id": "inventory_management_overview",
                "content": "Hospital inventory management involves systematic tracking of medical supplies, pharmaceuticals, equipment, and consumables. Key components include real-time stock monitoring, automated reordering, consumption tracking, expiration date management, and multi-location coordination. The system maintains optimal stock levels while minimizing waste and ensuring availability of critical supplies for patient care.",
                "category": "inventory",
                "tags": ["inventory", "management", "tracking", "supplies"]
            },
            {
                "id": "procurement_workflow",
                "content": "Procurement workflow encompasses the complete process from identifying supply needs to receiving and updating inventory. Steps include: demand identification, vendor selection, purchase order creation, approval workflows, order tracking, goods receipt, quality verification, and inventory updates. Emergency procurement procedures ensure rapid acquisition of critical supplies during urgent situations.",
                "category": "procurement",
                "tags": ["procurement", "workflow", "purchasing", "vendors", "orders"]
            },
            {
                "id": "alert_monitoring_system",
                "content": "The alert monitoring system provides real-time notifications for various supply chain events including low stock warnings, critical inventory alerts, expiration date notifications, quality issues, compliance violations, and system anomalies. Alerts are prioritized by urgency and automatically trigger appropriate workflows including reordering, transfers, and quality control measures.",
                "category": "alerts",
                "tags": ["alerts", "monitoring", "notifications", "warnings", "automation"]
            },
            {
                "id": "department_operations_icu",
                "content": "ICU (Intensive Care Unit) operations require specialized medical supplies including ventilators, monitoring equipment, IV fluids, medications, disposable supplies, and emergency equipment. Stock levels are maintained at higher thresholds due to critical patient needs. Consumption patterns are monitored continuously with automated reordering for essential items.",
                "category": "departments",
                "tags": ["ICU", "intensive care", "critical supplies", "ventilators", "monitoring"]
            },
            {
                "id": "department_operations_er",
                "content": "Emergency Room operations demand rapid access to diverse medical supplies including trauma supplies, diagnostic equipment, medications, PPE, and emergency kits. The ER maintains buffer stock for unpredictable demand patterns and coordinates with other departments for critical supply transfers during emergencies.",
                "category": "departments", 
                "tags": ["ER", "emergency", "trauma", "diagnostics", "emergency supplies"]
            },
            {
                "id": "department_operations_surgery",
                "content": "Surgical department operations require specialized instruments, sterile supplies, implants, sutures, anesthesia supplies, and post-operative care materials. Inventory is synchronized with surgical schedules, and sterile supply tracking ensures compliance with safety protocols. Case-specific supply kits are prepared based on surgical procedures.",
                "category": "departments",
                "tags": ["surgery", "surgical", "sterile", "instruments", "procedures"]
            },
            {
                "id": "department_operations_pharmacy",
                "content": "Pharmacy operations involve management of pharmaceuticals, controlled substances, IV preparations, clinical trial medications, and over-the-counter supplies. Strict temperature control, expiration tracking, lot number management, and regulatory compliance are essential. Automated dispensing systems reduce errors and improve efficiency.",
                "category": "departments",
                "tags": ["pharmacy", "pharmaceuticals", "medications", "controlled substances", "dispensing"]
            },
            {
                "id": "supply_categories_ppe",
                "content": "Personal Protective Equipment (PPE) includes masks, gloves, gowns, face shields, respirators, and protective eyewear. PPE inventory is critical for infection control and staff safety. Usage patterns vary based on patient acuity, seasonal factors, and regulatory requirements. Emergency stockpiles are maintained for pandemic preparedness.",
                "category": "supplies",
                "tags": ["PPE", "personal protective equipment", "masks", "gloves", "infection control"]
            },
            {
                "id": "supply_categories_medical_devices",
                "content": "Medical devices encompass diagnostic equipment, monitoring devices, therapeutic instruments, and disposable medical supplies. Device inventory includes tracking of maintenance schedules, calibration requirements, warranty status, and replacement planning. Critical devices have backup systems to ensure continuous patient care.",
                "category": "supplies",
                "tags": ["medical devices", "equipment", "diagnostics", "monitoring", "therapeutic"]
            },
            {
                "id": "autonomous_operations",
                "content": "Autonomous operations leverage AI and machine learning for automated supply management including predictive reordering, demand forecasting, inter-department transfers, supplier management, and workflow optimization. The system learns from historical patterns, current usage, and external factors to make intelligent decisions without human intervention while maintaining oversight capabilities.",
                "category": "automation",
                "tags": ["autonomous", "AI", "machine learning", "automation", "predictive analytics"]
            },
            {
                "id": "compliance_quality_control",
                "content": "Compliance and quality control ensure adherence to healthcare regulations, FDA requirements, Joint Commission standards, and institutional policies. Quality control processes include incoming inspection, batch tracking, recall management, temperature monitoring, sterility verification, and documentation requirements for regulatory audits.",
                "category": "compliance",
                "tags": ["compliance", "quality control", "regulations", "FDA", "standards"]
            },
            {
                "id": "emergency_response_protocols",
                "content": "Emergency response protocols activate during crisis situations including natural disasters, pandemic outbreaks, mass casualty events, and supply chain disruptions. Emergency procedures include inventory rationing, alternative sourcing, expedited procurement, inter-facility transfers, and coordination with external agencies for supply acquisition.",
                "category": "emergency",
                "tags": ["emergency", "crisis", "disaster", "pandemic", "mass casualty"]
            },
            {
                "id": "analytics_reporting",
                "content": "Analytics and reporting provide insights into consumption patterns, cost analysis, supplier performance, inventory turnover, waste reduction, and operational efficiency. Reports support decision-making for budget planning, contract negotiations, process improvements, and strategic initiatives. Real-time dashboards enable immediate response to supply chain issues.",
                "category": "analytics",
                "tags": ["analytics", "reporting", "insights", "KPIs", "performance metrics"]
            },
            {
                "id": "integration_systems",
                "content": "System integration connects supply chain management with EHR systems, financial systems, clinical applications, and external vendor platforms. Integration enables seamless data flow, automated workflows, real-time updates, and comprehensive visibility across all hospital operations while maintaining data security and privacy compliance.",
                "category": "integration",
                "tags": ["integration", "EHR", "systems", "workflows", "interoperability"]
            }
        ]
        
        # Add knowledge to vector database
        logger.info("🔄 Building knowledge base...")
        for item in knowledge_items:
            # Generate embedding
            embedding = embedding_model.encode(item['content']).tolist()
            
            # Add to vector database
            collection.add(
                documents=[item['content']],
                embeddings=[embedding],
                ids=[item['id']],
                metadatas=[{
                    'category': item['category'],
                    'tags': ','.join(item['tags']),
                    'title': item['id'].replace('_', ' ').title()
                }]
            )
        
        logger.info(f"✅ RAG system initialized with {len(knowledge_items)} knowledge items")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG system setup failed: {e}")
        return False

async def test_comprehensive_agent():
    """Test the comprehensive agent with sample queries"""
    try:
        from comprehensive_ai_agent import get_comprehensive_agent
        
        logger.info("🧪 Testing Comprehensive AI Agent...")
        agent = await get_comprehensive_agent()
        
        test_queries = [
            "What's the current inventory status?",
            "Show me ICU supplies",
            "I need to order more masks urgently",
            "What alerts are active right now?",
            "Generate analytics for pharmacy department"
        ]
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"🔍 Test {i}: {query}")
            try:
                response = await agent.process_conversation(query, "test_user")
                logger.info(f"✅ Response generated successfully")
                logger.info(f"📊 Actions performed: {len(response.get('actions', []))}")
            except Exception as e:
                logger.error(f"❌ Test {i} failed: {e}")
        
        logger.info("🎉 Agent testing completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent testing failed: {e}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Starting Comprehensive AI Agent Setup...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("❌ Setup failed: Missing dependencies")
        return False
    
    # Setup RAG system
    if not await setup_rag_system():
        logger.error("❌ Setup failed: RAG system initialization failed")
        return False
    
    # Test comprehensive agent
    if not await test_comprehensive_agent():
        logger.warning("⚠️ Agent testing had issues, but setup completed")
    
    logger.info("🎉 Comprehensive AI Agent setup completed successfully!")
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("1. Start the backend server: python backend/api/professional_main_smart.py")
    logger.info("2. Start the frontend: cd dashboard/supply_dashboard && npm start")
    logger.info("3. Test the AI agent at /api/v3/agent/chat")
    logger.info("4. Use the dashboard's AI Assistant button")
    logger.info("")
    logger.info("🤖 Agent Capabilities:")
    logger.info("   • Natural language inventory queries")
    logger.info("   • Automated procurement recommendations")
    logger.info("   • Real-time alert analysis")
    logger.info("   • Department-specific operations")
    logger.info("   • Analytics and reporting")
    logger.info("   • Workflow automation")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
