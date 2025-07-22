import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Database, 
  MessageSquare, 
  Search, 
  Lightbulb, 
  CheckCircle, 
  XCircle,
  Loader,
  Cpu,
  Zap
} from 'lucide-react';

const RAGMCPInterface = () => {
  const [ragStatus, setRagStatus] = useState({ available: false, loading: true });
  const [mcpStatus, setMcpStatus] = useState({ available: false, loading: true });
  const [query, setQuery] = useState('');
  const [responses, setResponses] = useState({
    query: null,
    rag: null,
    mcp: null,
    recommendations: null
  });
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('query');
  const [knowledgeStats, setKnowledgeStats] = useState(null);

  // Check system status on component mount
  useEffect(() => {
    checkSystemStatus();
    getKnowledgeStats();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/status');
      const data = await response.json();
      
      setRagStatus({
        available: data.rag_system === 'available',
        loading: false
      });
      
      setMcpStatus({
        available: data.mcp_server === 'available',
        loading: false
      });
    } catch (error) {
      console.error('Error checking system status:', error);
      setRagStatus({ available: false, loading: false });
      setMcpStatus({ available: false, loading: false });
    }
  };

  const getKnowledgeStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/knowledge-stats');
      if (response.ok) {
        const data = await response.json();
        setKnowledgeStats(data);
      }
    } catch (error) {
      console.error('Error fetching knowledge stats:', error);
    }
  };

  const handleEnhancedQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/enhanced-query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          user_context: {
            role: 'inventory_manager',
            department: 'supply_chain',
            connection_id: 'web_interface'
          },
          include_rag: true,
          include_mcp: true
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResponses(prev => ({ ...prev, query: data }));
      } else {
        setResponses(prev => ({ ...prev, query: {
          error: 'Failed to process query',
          content: 'Please try again or check system status.'
        }}));
      }
    } catch (error) {
      console.error('Error processing enhanced query:', error);
      setResponses(prev => ({ ...prev, query: {
        error: 'Network error',
        content: 'Unable to connect to the enhanced query system.'
      }}));
    } finally {
      setLoading(false);
    }
  };

  const handleRAGQuery = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          context_type: 'general',
          limit: 5
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResponses(prev => ({ ...prev, rag: {
          type: 'rag',
          ...data
        }}));
      }
    } catch (error) {
      console.error('Error processing RAG query:', error);
      setResponses(prev => ({ ...prev, rag: {
        error: 'RAG query failed',
        content: 'Unable to search knowledge base.'
      }}));
    } finally {
      setLoading(false);
    }
  };

  const callMCPTool = async (toolName, parameters = {}) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/mcp/tool', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool_name: toolName,
          parameters: parameters,
          connection_id: 'web_interface'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResponses(prev => ({ ...prev, mcp: {
          type: 'mcp_tool',
          tool_name: toolName,
          ...data
        }}));
      }
    } catch (error) {
      console.error('Error calling MCP tool:', error);
      setResponses(prev => ({ ...prev, mcp: {
        error: 'MCP tool call failed',
        content: 'Unable to execute tool.'
      }}));
    } finally {
      setLoading(false);
    }
  };

  const getRecommendations = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v2/rag-mcp/recommendations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: {
            current_inventory_value: 125000,
            low_stock_items: 15,
            pending_orders: 8,
            patient_census: 285,
            time_of_day: new Date().getHours(),
            day_of_week: new Date().getDay()
          }
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResponses(prev => ({ ...prev, recommendations: {
          type: 'recommendations',
          ...data
        }}));
      }
    } catch (error) {
      console.error('Error getting recommendations:', error);
      setResponses(prev => ({ ...prev, recommendations: {
        error: 'Recommendations failed',
        content: 'Unable to generate recommendations.'
      }}));
    } finally {
      setLoading(false);
    }
  };

  const StatusIndicator = ({ status, label }) => (
    <div className="flex items-center space-x-2">
      {status.loading ? (
        <Loader className="w-4 h-4 animate-spin text-blue-500" />
      ) : status.available ? (
        <CheckCircle className="w-4 h-4 text-green-500" />
      ) : (
        <XCircle className="w-4 h-4 text-red-500" />
      )}
      <span className={`text-sm ${status.available ? 'text-green-700' : 'text-red-700'}`}>
        {label}
      </span>
    </div>
  );

  const renderResponse = () => {
    const response = responses[activeTab];
    if (!response) return null;

    if (response.error) {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 className="text-red-800 font-medium mb-2">Error</h4>
          <p className="text-red-700">{response.content || response.error}</p>
        </div>
      );
    }

    if (response.type === 'rag') {
      return (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-blue-800 font-medium mb-2">RAG Search Results</h4>
            <p className="text-blue-700">
              Found <strong>{response.total_results}</strong> relevant results for: <em>"{response.query}"</em>
            </p>
            {response.search_metadata && (
              <div className="mt-2 text-sm text-blue-600">
                Search time: {response.search_metadata.search_time} | 
                Index coverage: {response.search_metadata.index_coverage} | 
                Relevance threshold: {response.search_metadata.relevance_threshold}
              </div>
            )}
          </div>
          
          {response.results && response.results.length > 0 && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="text-gray-800 font-medium mb-2">Knowledge Base Results</h4>
              <div className="space-y-3">
                {response.results.map((result, index) => (
                  <div key={index} className="bg-white border border-gray-300 rounded p-3">
                    <div className="flex justify-between items-start mb-2">
                      <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                        {result.metadata?.type || 'Document'}
                      </span>
                      <span className="text-xs text-gray-500">
                        Score: {(result.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-sm text-gray-800 mb-2 leading-relaxed">
                      {result.content}
                    </div>
                    {result.metadata && (
                      <div className="text-xs text-gray-500 space-y-1">
                        {result.metadata.source && (
                          <div>Source: {result.metadata.source}</div>
                        )}
                        {result.metadata.category && (
                          <div>Category: {result.metadata.category}</div>
                        )}
                        {result.metadata.department && (
                          <div>Department: {result.metadata.department}</div>
                        )}
                        {result.metadata.last_updated && (
                          <div>Last updated: {result.metadata.last_updated}</div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!response.results || response.results.length === 0) && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <h4 className="text-yellow-800 font-medium mb-2">No Results Found</h4>
              <p className="text-yellow-700">No relevant documents found for your search query. Try using different keywords or check your spelling.</p>
            </div>
          )}
        </div>
      );
    }

    if (response.type === 'mcp_tool') {
      return (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-green-800 font-medium mb-2">
            MCP Tool: {response.tool_name}
          </h4>
          {response.success ? (
            <div className="space-y-3">
              {/* Render different tool results based on tool name */}
              {response.tool_name === 'get_approval_status' && (
                <div className="space-y-3">
                  {response.result.pending_approvals && response.result.pending_approvals.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-800 mb-2">Pending Approvals</h5>
                      <div className="space-y-2">
                        {response.result.pending_approvals.map((approval, index) => (
                          <div key={index} className="bg-white p-3 rounded border">
                            <div className="flex justify-between items-start">
                              <div>
                                <p className="font-medium text-gray-800">{approval.item}</p>
                                <p className="text-sm text-gray-600">Order ID: {approval.order_id}</p>
                              </div>
                              <div className="text-right">
                                <p className="font-medium text-green-700">${approval.value.toLocaleString()}</p>
                                <span className="inline-block px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded">
                                  {approval.status}
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-2xl font-bold text-green-600">{response.result.approved_today}</p>
                      <p className="text-sm text-gray-600">Approved Today</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-2xl font-bold text-yellow-600">{response.result.pending_count}</p>
                      <p className="text-sm text-gray-600">Pending</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-lg font-bold text-blue-600">{response.result.average_approval_time}</p>
                      <p className="text-sm text-gray-600">Avg. Time</p>
                    </div>
                  </div>
                </div>
              )}

              {response.tool_name === 'get_inventory_status' && (
                <div className="space-y-3">
                  {response.result.low_stock_items && response.result.low_stock_items.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-800 mb-2">Low Stock Items</h5>
                      <div className="space-y-2">
                        {response.result.low_stock_items.map((item, index) => (
                          <div key={index} className="bg-white p-3 rounded border">
                            <div className="flex justify-between items-center">
                              <div>
                                <p className="font-medium text-gray-800">{item.item}</p>
                                <p className="text-sm text-gray-600">Department: {item.department}</p>
                              </div>
                              <div className="text-right">
                                <p className="text-lg font-bold text-red-600">{item.current}</p>
                                <p className="text-xs text-gray-500">Min: {item.threshold}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-4 gap-3 mt-4">
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-blue-600">{response.result.total_items || 'N/A'}</p>
                      <p className="text-xs text-gray-600">Total Items</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-red-600">{response.result.low_stock || response.result.total_low_stock || 'N/A'}</p>
                      <p className="text-xs text-gray-600">Low Stock</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-green-600">{response.result.normal_stock || 'N/A'}</p>
                      <p className="text-xs text-gray-600">Normal Stock</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-orange-600">{response.result.critical_stock || response.result.critical_level || 'N/A'}</p>
                      <p className="text-xs text-gray-600">Critical</p>
                    </div>
                  </div>
                </div>
              )}

              {response.tool_name === 'get_usage_analytics' && (
                <div className="space-y-3">
                  {response.result.analytics?.top_consumed_items && response.result.analytics.top_consumed_items.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-800 mb-2">Top Consumed Items</h5>
                      <div className="space-y-2">
                        {response.result.analytics.top_consumed_items.map((item, index) => (
                          <div key={index} className="bg-white p-3 rounded border">
                            <div className="flex justify-between items-center">
                              <div>
                                <p className="font-medium text-gray-800">{item}</p>
                                <p className="text-sm text-gray-600">Rank #{index + 1}</p>
                              </div>
                              <div className="text-right">
                                <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                                  High Usage
                                </span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-blue-600">{response.result.analytics?.average_daily_consumption || 'N/A'}</p>
                      <p className="text-sm text-gray-600">Daily Consumption</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-xl font-bold text-green-600">{response.result.analytics?.efficiency_score || 'N/A'}%</p>
                      <p className="text-sm text-gray-600">Efficiency Score</p>
                    </div>
                    <div className="bg-white p-3 rounded text-center">
                      <p className="text-lg font-bold text-purple-600">{response.result.period || 'N/A'}</p>
                      <p className="text-sm text-gray-600">Analysis Period</p>
                    </div>
                  </div>
                  
                  {response.result.analytics?.consumption_trend && (
                    <div className="bg-white p-3 rounded text-center mt-3">
                      <p className="text-lg font-bold text-indigo-600">{response.result.analytics.consumption_trend}</p>
                      <p className="text-sm text-gray-600">Consumption Trend</p>
                    </div>
                  )}
                </div>
              )}
              
              {/* Default JSON display for other tools */}
              {!['get_approval_status', 'get_inventory_status', 'get_usage_analytics'].includes(response.tool_name) && (
                <pre className="text-green-700 text-sm whitespace-pre-wrap bg-white p-3 rounded">
                  {JSON.stringify(response.result, null, 2)}
                </pre>
              )}
            </div>
          ) : (
            <p className="text-red-700">{response.error}</p>
          )}
          {response.execution_time && (
            <div className="text-xs text-green-600 mt-2">
              Execution time: {response.execution_time.toFixed(3)}s
            </div>
          )}
        </div>
      );
    }

    if (response.type === 'recommendations') {
      return (
        <div className="space-y-4">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="text-purple-800 font-medium mb-2">Intelligent Recommendations</h4>
            
            {Object.entries(response).map(([key, value]) => {
              if (key.startsWith('_') || ['type', 'error', 'generated_at', 'reasoning'].includes(key)) return null;
              
              return (
                <div key={key} className="mb-3">
                  <h5 className="font-medium text-purple-800 capitalize">
                    {key.replace(/_/g, ' ')}
                  </h5>
                  {Array.isArray(value) && value.length > 0 ? (
                    <ul className="list-disc list-inside text-purple-700 text-sm mt-1">
                      {value.map((item, index) => (
                        <li key={index}>{item}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-purple-600 text-sm">No recommendations available</p>
                  )}
                </div>
              );
            })}
            
            {response.confidence_score && (
              <div className="text-xs text-purple-600 mt-2">
                Confidence: {(response.confidence_score * 100).toFixed(1)}%
              </div>
            )}
          </div>
        </div>
      );
    }

    // Default enhanced query response
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <h4 className="text-green-800 font-medium mb-2">Enhanced Response</h4>
        <div className="text-green-700 whitespace-pre-line mb-3">{response.content}</div>
        
        {response.suggestions && response.suggestions.length > 0 && (
          <div className="mb-3">
            <h5 className="font-medium text-green-800 mb-1">Suggestions</h5>
            <ul className="list-disc list-inside text-green-700 text-sm">
              {response.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="text-xs text-green-600">
          Confidence: {(response.confidence * 100).toFixed(1)}% | 
          Generated: {new Date(response.generated_at).toLocaleTimeString()}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
          <h1 className="text-2xl font-bold text-white flex items-center">
            <Brain className="w-8 h-8 mr-3" />
            RAG & MCP Intelligence System
          </h1>
          <p className="text-blue-100 mt-1">
            Retrieval-Augmented Generation and Model Context Protocol
          </p>
        </div>

        {/* Status Bar */}
        <div className="bg-gray-50 px-6 py-3 border-b flex items-center justify-between">
          <div className="flex space-x-6">
            <StatusIndicator status={ragStatus} label="RAG System" />
            <StatusIndicator status={mcpStatus} label="MCP Server" />
          </div>
          
          {knowledgeStats && (
            <div className="text-sm text-gray-600">
              Knowledge Base: {knowledgeStats.document_count} documents | 
              Backend: {knowledgeStats.backend_type}
            </div>
          )}
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('query')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'query'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Enhanced Query
          </button>
          <button
            onClick={() => setActiveTab('rag')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'rag'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Search className="w-4 h-4 inline mr-2" />
            RAG Search
          </button>
          <button
            onClick={() => setActiveTab('mcp')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'mcp'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Cpu className="w-4 h-4 inline mr-2" />
            MCP Tools
          </button>
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'recommendations'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-blue-600'
            }`}
          >
            <Lightbulb className="w-4 h-4 inline mr-2" />
            Recommendations
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'query' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Ask a question about hospital supply chain management
                </label>
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., How can I optimize inventory costs while maintaining safety?"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleEnhancedQuery()}
                  />
                  <button
                    onClick={handleEnhancedQuery}
                    disabled={loading || !query.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {loading ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <Zap className="w-4 h-4" />
                    )}
                    <span className="ml-2">Enhance</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'rag' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Search knowledge base for relevant information
                </label>
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., emergency procedures, cost optimization"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    onKeyPress={(e) => e.key === 'Enter' && handleRAGQuery()}
                  />
                  <button
                    onClick={handleRAGQuery}
                    disabled={loading || !query.trim()}
                    className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {loading ? (
                      <Loader className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                    <span className="ml-2">Search</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'mcp' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Available MCP Tools</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <button
                  onClick={() => callMCPTool('get_inventory_status', { low_stock_only: true })}
                  disabled={loading}
                  className="p-4 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <Database className="w-6 h-6 text-blue-600 mb-2" />
                  <h4 className="font-medium text-gray-800">Inventory Status</h4>
                  <p className="text-sm text-gray-600">Get current inventory levels</p>
                </button>

                <button
                  onClick={() => callMCPTool('get_usage_analytics', { time_period: '30d', metric: 'consumption' })}
                  disabled={loading}
                  className="p-4 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <Zap className="w-6 h-6 text-green-600 mb-2" />
                  <h4 className="font-medium text-gray-800">Usage Analytics</h4>
                  <p className="text-sm text-gray-600">Analyze supply consumption</p>
                </button>

                <button
                  onClick={() => callMCPTool('get_approval_status', {})}
                  disabled={loading}
                  className="p-4 border border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
                >
                  <CheckCircle className="w-6 h-6 text-purple-600 mb-2" />
                  <h4 className="font-medium text-gray-800">Approval Status</h4>
                  <p className="text-sm text-gray-600">Check pending approvals</p>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="space-y-4">
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-800 mb-2">
                  Get Intelligent Recommendations
                </h3>
                <p className="text-gray-600 mb-4">
                  AI-powered recommendations based on current hospital context
                </p>
                <button
                  onClick={getRecommendations}
                  disabled={loading}
                  className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center mx-auto"
                >
                  {loading ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : (
                    <Lightbulb className="w-4 h-4" />
                  )}
                  <span className="ml-2">Generate Recommendations</span>
                </button>
              </div>
            </div>
          )}

          {/* Response Display */}
          {responses[activeTab] && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-800 mb-3">Response</h3>
              {renderResponse()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RAGMCPInterface;
