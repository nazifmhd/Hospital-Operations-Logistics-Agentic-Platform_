# RAG and Model Context Protocol (MCP) Integration Documentation

## Overview

The Hospital Operations & Logistics Agentic Platform now includes advanced **Retrieval-Augmented Generation (RAG)** and **Model Context Protocol (MCP)** capabilities that significantly enhance the AI/LLM integration for more intelligent and context-aware responses.

## 🧠 RAG System (Retrieval-Augmented Generation)

### What is RAG?
RAG enhances language model responses by retrieving relevant information from a knowledge base before generating answers. This ensures responses are grounded in factual, domain-specific information.

### Key Features

#### 1. **Vector Storage with Multiple Backends**
- **ChromaDB**: Production-ready vector database (preferred)
- **Scikit-learn TF-IDF**: Fallback option with cosine similarity
- **SQLite Fallback**: Simple text matching for minimal setups

#### 2. **Document Management**
- **Document Types**: Procedure guides, policies, inventory data, compliance docs
- **Metadata Support**: Rich metadata for filtering and context
- **Dynamic Knowledge**: Real-time addition of new knowledge
- **Source Tracking**: Track where information comes from

#### 3. **Smart Retrieval**
- **Semantic Search**: Find contextually relevant information
- **Confidence Scoring**: Reliability assessment of retrieved context
- **Caching**: Reduce redundant searches with intelligent caching
- **Context Summarization**: Condensed, relevant information extraction

### Usage Examples

```python
# Basic RAG query
from rag_system import enhance_with_rag

context = await enhance_with_rag(
    "What should I do during a critical supply shortage?",
    context_type="emergency"
)

# Add dynamic knowledge
await rag_system.add_dynamic_context(
    content="New emergency protocol for pandemic response...",
    doc_type=DocumentType.PROCEDURE_GUIDE,
    metadata={"urgency": "high", "effective_date": "2024-07-20"}
)
```

### API Endpoints

- `POST /api/v2/rag-mcp/rag/query` - Query knowledge base
- `POST /api/v2/rag-mcp/rag/add-knowledge` - Add new knowledge
- `GET /api/v2/rag-mcp/knowledge-stats` - Get knowledge base statistics

## 🔗 Model Context Protocol (MCP)

### What is MCP?
MCP provides a standardized way for AI models to access tools, resources, and contextual information from external systems, enabling more structured and reliable AI interactions.

### Key Components

#### 1. **Tools**
Structured functions the AI can call:
- **Inventory Management**: Get status, create orders, transfer supplies
- **Analytics**: Usage patterns, demand forecasting
- **Workflow**: Approval status, workflow management

#### 2. **Resources**
Static or dynamic data sources:
- **Current Inventory**: Real-time inventory levels
- **Low Stock Alerts**: Critical alerts requiring attention
- **Usage Trends**: Historical patterns and analytics
- **Supplier Catalog**: Available items and pricing

#### 3. **Prompts**
Template-based prompt generation:
- **Inventory Analysis**: Analyze and recommend actions
- **Alert Triage**: Prioritize and respond to alerts
- **Purchase Justification**: Generate approval documentation

#### 4. **Context Providers**
Real-time system state information:
- **Hospital State**: Current operations status
- **User Context**: Role-based access and permissions
- **Alert Context**: Active alerts and priorities

### Usage Examples

```python
# Call MCP tool
result = await mcp_server.handle_message(
    MCPMessage(
        method="call_tool",
        params={
            "name": "get_inventory_status",
            "arguments": {"low_stock_only": True}
        }
    ),
    connection_id="user_123"
)

# Get contextual information
context = await mcp_server._handle_get_context({}, "user_123")
```

### API Endpoints

- `GET /api/v2/rag-mcp/mcp/capabilities` - List available tools/resources
- `POST /api/v2/rag-mcp/mcp/tool` - Execute MCP tool
- `POST /api/v2/rag-mcp/mcp/context` - Get current context

## 🚀 Enhanced LLM Integration

### LLMEnhancedSupplyAgent

The enhanced agent combines RAG and MCP capabilities:

```python
agent = LLMEnhancedSupplyAgent()
await agent.initialize()

# Process query with full context
response = await agent.process_query_with_context(
    "How can I optimize costs while maintaining safety?",
    user_context={"role": "inventory_manager", "department": "supply_chain"}
)

# Get intelligent recommendations
recommendations = await agent.get_intelligent_recommendations({
    "current_inventory_value": 125000,
    "low_stock_items": 15,
    "patient_census": 285
})
```

### API Endpoints

- `POST /api/v2/rag-mcp/enhanced-query` - Enhanced query processing
- `POST /api/v2/rag-mcp/recommendations` - Get AI recommendations
- `GET /api/v2/rag-mcp/status` - System status check

## 📋 Installation and Setup

### 1. Install Dependencies

```bash
# Install RAG and MCP dependencies
pip install -r ai_ml/requirements_rag_mcp.txt
```

### 2. Setup Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_gemini_api_key_here
HOSPITAL_NAME=General Hospital
HOSPITAL_TYPE=General Acute Care
```

### 3. Initialize System

```bash
# Run setup script
cd ai_ml
python setup_rag_mcp.py
```

### 4. Integration Check

The system automatically integrates with your existing FastAPI backend. Check status:

```bash
curl http://localhost:8000/api/v2/rag-mcp/status
```

## 🎯 Frontend Integration

### React Component

The `RAGMCPInterface` component provides:
- **Enhanced Query Interface**: Natural language queries with context
- **RAG Search**: Direct knowledge base search
- **MCP Tool Access**: Structured tool execution
- **Intelligent Recommendations**: AI-powered insights

### Navigation

Access via sidebar: **RAG & MCP Intelligence**

## 📊 Benefits

### 1. **Improved Response Quality**
- **Factual Accuracy**: Responses grounded in hospital-specific knowledge
- **Context Awareness**: Understands current hospital state and operations
- **Specialized Knowledge**: Domain-specific expertise in healthcare supply chain

### 2. **Structured Interactions**
- **Reliable Tool Access**: Standardized way to execute system functions
- **Consistent Context**: Unified context across all AI interactions
- **Audit Trail**: Track what information was used in responses

### 3. **Enhanced User Experience**
- **Natural Language Interface**: Ask questions in plain English
- **Intelligent Recommendations**: Proactive suggestions for optimization
- **Multi-modal Interaction**: Query, search, and execute actions seamlessly

## 🔧 Configuration

### Vector Database Selection

```python
# In rag_system.py, the system auto-selects:
# 1. ChromaDB (if available) - Production recommended
# 2. Scikit-learn TF-IDF (fallback)
# 3. SQLite text search (minimal fallback)
```

### Knowledge Base Customization

```python
# Add hospital-specific knowledge
documents = [
    {
        "content": "Your hospital's specific procedures...",
        "doc_type": DocumentType.PROCEDURE_GUIDE,
        "metadata": {"department": "ICU", "priority": "critical"}
    }
]
```

### MCP Tool Extension

```python
# Add custom tools in mcp_server.py
self.tools["custom_tool"] = MCPTool(
    name="custom_tool",
    description="Description of your custom tool",
    input_schema={...},
    handler=self._handle_custom_tool
)
```

## 🚨 Troubleshooting

### Common Issues

1. **ChromaDB Installation**: If ChromaDB fails to install, the system falls back to scikit-learn
2. **Gemini API**: Ensure your API key is valid and has sufficient quota
3. **Memory Usage**: Vector databases can be memory-intensive; monitor usage
4. **Path Issues**: Ensure proper Python path configuration for module imports

### Debug Commands

```python
# Check system status
curl http://localhost:8000/api/v2/rag-mcp/status

# Test RAG query
curl -X POST http://localhost:8000/api/v2/rag-mcp/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "limit": 3}'

# Check knowledge base stats
curl http://localhost:8000/api/v2/rag-mcp/knowledge-stats
```

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Embeddings**: Integration with specialized medical embeddings
2. **Multi-modal RAG**: Support for images, documents, and structured data
3. **Federated Search**: Search across multiple hospital systems
4. **Real-time Learning**: Continuous learning from user interactions
5. **Advanced Analytics**: Usage patterns and effectiveness metrics

### Integration Opportunities

1. **EHR Integration**: Link supply usage to patient outcomes
2. **IoT Sensors**: Real-time inventory updates from smart shelves
3. **Voice Interface**: Voice-activated queries and commands
4. **Mobile Apps**: Native mobile access to RAG/MCP capabilities

## 📚 API Reference

### RAG Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v2/rag-mcp/rag/query` | POST | Query knowledge base |
| `/api/v2/rag-mcp/rag/add-knowledge` | POST | Add new knowledge |
| `/api/v2/rag-mcp/knowledge-stats` | GET | Knowledge base statistics |

### MCP Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v2/rag-mcp/mcp/capabilities` | GET | List capabilities |
| `/api/v2/rag-mcp/mcp/tool` | POST | Execute tool |
| `/api/v2/rag-mcp/mcp/context` | POST | Get context |

### Enhanced LLM Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/v2/rag-mcp/enhanced-query` | POST | Enhanced query processing |
| `/api/v2/rag-mcp/recommendations` | POST | Get recommendations |
| `/api/v2/rag-mcp/status` | GET | System status |

## 🎓 Best Practices

### 1. **Knowledge Management**
- Regularly update knowledge base with latest procedures
- Use meaningful metadata for better retrieval
- Maintain source attribution for compliance

### 2. **Query Optimization**
- Be specific in queries for better results
- Use domain-specific terminology
- Provide context when asking complex questions

### 3. **Security**
- Implement proper access controls for sensitive tools
- Audit knowledge base contents regularly
- Monitor AI responses for accuracy

### 4. **Performance**
- Cache frequently accessed information
- Monitor vector database performance
- Optimize embedding models for your domain

This RAG and MCP integration transforms your hospital supply chain platform into an intelligent, context-aware system that can understand, reason about, and act upon complex supply chain challenges with the power of advanced AI technologies.
