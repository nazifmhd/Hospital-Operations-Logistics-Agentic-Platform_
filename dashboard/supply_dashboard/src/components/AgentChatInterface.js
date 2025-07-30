import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader, Zap, CheckCircle, AlertCircle, Activity } from 'lucide-react';

const AgentChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [agentCapabilities, setAgentCapabilities] = useState([]);
  const [agentStatus, setAgentStatus] = useState('unknown');
  const chatEndRef = useRef(null);

  useEffect(() => {
    // Initialize agent and get capabilities
    initializeAgent();
    // Add welcome message
    setMessages([{
      id: 'welcome',
      type: 'agent',
      content: `🤖 **Welcome to the AI-Powered Hospital Supply Assistant!** 

I'm your intelligent agent for complete supply chain management. I can help you with:

• **Inventory Management** - Check stock levels, monitor consumption, set alerts
• **Procurement Operations** - Create orders, manage suppliers, handle approvals  
• **Real-time Monitoring** - Active alerts, trends analysis, recommendations
• **Department Operations** - Department-specific inventory and workflows
• **Analytics & Reporting** - Generate insights, forecasting, performance analysis
• **Workflow Automation** - Manage automated processes and approvals

**Try asking me things like:**
- "What's the current inventory status in the ICU?"
- "I need to order more N95 masks urgently"
- "Show me all active alerts and recommendations"
- "Generate analytics report for the pharmacy department"
- "What supplies are running low in the emergency room?"

How can I assist you today?`,
      timestamp: new Date().toISOString(),
      actions: [],
      confidence: 1.0
    }]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initializeAgent = async () => {
    try {
      const response = await fetch('/api/v3/agent/capabilities');
      const data = await response.json();
      setAgentCapabilities(data.capabilities || []);
      setAgentStatus(data.agent_status || 'unknown');
    } catch (error) {
      console.error('Failed to initialize agent:', error);
      setAgentStatus('error');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch('/api/v3/agent/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          user_id: 'dashboard_user',
          session_id: sessionId,
          context: {
            timestamp: new Date().toISOString(),
            source: 'dashboard_chat'
          }
        })
      });

      const data = await response.json();
      
      if (!sessionId && data.session_id) {
        setSessionId(data.session_id);
      }

      const agentMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response || 'I apologize, but I encountered an issue processing your request.',
        timestamp: data.timestamp || new Date().toISOString(),
        actions: data.actions_performed || [],
        intent: data.intent_analysis || {},
        confidence: data.confidence || 0.5,
        agent_status: data.agent_status || 'active'
      };

      setMessages(prev => [...prev, agentMessage]);
      setAgentStatus(data.agent_status || 'active');

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'I apologize, but I encountered a technical issue. Please try again or contact support if the problem persists.',
        timestamp: new Date().toISOString(),
        actions: [],
        confidence: 0.0,
        agent_status: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
      setAgentStatus('error');
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const executeQuickAction = async (actionText) => {
    setInputMessage(actionText);
    // Small delay to show the text in input before sending
    setTimeout(() => sendMessage(), 100);
  };

  const formatContent = (content) => {
    // Simple markdown-like formatting for better display
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/• /g, '• ')
      .replace(/\n/g, '<br />');
  };

  const getStatusIcon = () => {
    switch (agentStatus) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'limited':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusText = () => {
    switch (agentStatus) {
      case 'active':
        return 'AI Agent Active';
      case 'limited':
        return 'Limited Mode';
      case 'error':
        return 'Agent Error';
      default:
        return 'Connecting...';
    }
  };

  const quickActions = [
    "Check ICU inventory status",
    "Show all active alerts", 
    "Order more N95 masks",
    "Emergency room supplies status",
    "Generate pharmacy analytics report",
    "What supplies are running low?",
    "Transfer supplies between departments",
    "Show autonomous operations status"
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg h-full flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6" />
            <h2 className="text-xl font-bold">AI Supply Assistant</h2>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            {getStatusIcon()}
            <span>{getStatusText()}</span>
          </div>
        </div>
        <p className="text-blue-100 text-sm mt-1">
          Intelligent agent for complete supply chain management
        </p>
      </div>

      {/* Quick Actions */}
      <div className="p-3 border-b bg-gray-50">
        <div className="flex flex-wrap gap-2">
          {quickActions.slice(0, 4).map((action, index) => (
            <button
              key={index}
              onClick={() => executeQuickAction(action)}
              className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs hover:bg-blue-200 transition-colors"
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'agent' && (
                  <Bot className="w-5 h-5 mt-0.5 text-blue-600" />
                )}
                {message.type === 'user' && (
                  <User className="w-5 h-5 mt-0.5 text-white" />
                )}
                <div className="flex-1">
                  <div 
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: formatContent(message.content) }}
                  />
                  
                  {/* Show actions performed */}
                  {message.actions && message.actions.length > 0 && (
                    <div className="mt-2 p-2 bg-blue-50 rounded border-l-4 border-blue-200">
                      <div className="text-xs text-blue-700 font-semibold flex items-center">
                        <Zap className="w-3 h-3 mr-1" />
                        Actions Performed ({message.actions.length})
                      </div>
                      <ul className="text-xs text-blue-600 mt-1">
                        {message.actions.slice(0, 3).map((action, index) => (
                          <li key={index}>• {action.description || action.action_type}</li>
                        ))}
                        {message.actions.length > 3 && (
                          <li>• ... and {message.actions.length - 3} more actions</li>
                        )}
                      </ul>
                    </div>
                  )}

                  {/* Show confidence and intent for agent messages */}
                  {message.type === 'agent' && message.confidence !== undefined && (
                    <div className="text-xs text-gray-500 mt-2 flex items-center justify-between">
                      <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                      {message.intent && message.intent.primary_intent && (
                        <span>Intent: {message.intent.primary_intent.replace('_', ' ')}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 px-4 py-3 rounded-lg">
              <div className="flex items-center space-x-2">
                <Bot className="w-5 h-5 text-blue-600" />
                <div className="flex space-x-1">
                  <Loader className="w-4 h-4 animate-spin text-blue-600" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t p-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about hospital supply management..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="2"
            disabled={isTyping}
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* Additional Quick Actions */}
        <div className="mt-2">
          <div className="flex flex-wrap gap-1">
            {quickActions.slice(4).map((action, index) => (
              <button
                key={index + 4}
                onClick={() => executeQuickAction(action)}
                className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs hover:bg-gray-200 transition-colors"
                disabled={isTyping}
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentChatInterface;
