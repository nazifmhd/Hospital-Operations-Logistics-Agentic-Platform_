import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Mic, MicOff, AlertCircle, CheckCircle } from 'lucide-react';

const LLMChatInterface = ({ isOpen, onClose, systemContext }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your intelligent supply assistant. You can ask me about inventory, orders, alerts, or any other supply chain questions.',
      timestamp: new Date(),
      confidence: 0.95
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  const recognition = useRef(null);

  // Simple markdown formatter for better chat display
  const formatMessage = (content) => {
    if (!content) return content;
    
    // Split content into lines and process each
    const lines = content.split('\n');
    const formattedLines = lines.map(line => {
      // Remove excessive ** markdown formatting
      let formatted = line;
      
      // Convert **text** to bold spans
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Convert bullet points to proper formatting
      formatted = formatted.replace(/^[-•]\s*/, '• ');
      
      // Convert numbered lists
      formatted = formatted.replace(/^\d+\.\s*/, (match) => `${match} `);
      
      return formatted;
    });
    
    return formattedLines.join('\n');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      recognition.current = new window.webkitSpeechRecognition();
      recognition.current.continuous = false;
      recognition.current.interimResults = false;
      recognition.current.lang = 'en-US';

      recognition.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputValue(transcript);
        setIsListening(false);
      };

      recognition.current.onerror = () => {
        setIsListening(false);
      };

      recognition.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const handleVoiceInput = () => {
    if (recognition.current) {
      if (isListening) {
        recognition.current.stop();
      } else {
        recognition.current.start();
        setIsListening(true);
      }
    }
  };

  const processNaturalLanguageQuery = async (query) => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/llm/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          context: systemContext,
          user_role: 'supply_manager'
        })
      });

      if (!response.ok) throw new Error('Failed to process query');
      return await response.json();
    } catch (error) {
      console.error('LLM Query Error:', error);
      return {
        response: 'I apologize, but I\'m having trouble processing your request right now. Please try again or contact support.',
        confidence: 0.0,
        suggested_actions: ['Try rephrasing your question', 'Check system status', 'Contact technical support']
      };
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Process with LLM
    const llmResponse = await processNaturalLanguageQuery(inputValue);

    const botMessage = {
      id: Date.now() + 1,
      type: 'bot',
      content: llmResponse.response,
      timestamp: new Date(),
      confidence: llmResponse.confidence,
      suggestions: llmResponse.suggested_actions,
      requiresFollowup: llmResponse.requires_followup
    };

    setMessages(prev => [...prev, botMessage]);
    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleQuickAction = (action) => {
    setInputValue(action);
  };

  const quickActions = [
    "Show me critical alerts",
    "What items need reordering?",
    "Check purchase order status",
    "Show inventory summary",
    "List recent transfers",
    "Explain the latest alert"
  ];

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.9) return <CheckCircle className="w-4 h-4" />;
    if (confidence >= 0.7) return <AlertCircle className="w-4 h-4" />;
    return <AlertCircle className="w-4 h-4" />;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-blue-600 text-white rounded-t-lg">
          <div className="flex items-center space-x-2">
            <Bot className="w-6 h-6" />
            <h2 className="text-lg font-semibold">Supply Chain AI Assistant</h2>
            <span className="text-xs bg-blue-500 px-2 py-1 rounded">Beta</span>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Quick Actions */}
        <div className="p-3 border-b bg-gray-50">
          <p className="text-sm text-gray-600 mb-2">Quick Actions:</p>
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => handleQuickAction(action)}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs hover:bg-blue-200 transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl p-3 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <div className="flex items-start space-x-2">
                  {message.type === 'bot' && <Bot className="w-5 h-5 mt-1 text-blue-600" />}
                  {message.type === 'user' && <User className="w-5 h-5 mt-1" />}
                  <div className="flex-1">
                    <div 
                      className="whitespace-pre-wrap"
                      dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                    />
                    
                    
                    {/* Confidence indicator for bot messages */}
                    {message.type === 'bot' && message.confidence !== undefined && (
                      <div className={`flex items-center mt-2 text-xs ${getConfidenceColor(message.confidence)}`}>
                        {getConfidenceIcon(message.confidence)}
                        <span className="ml-1">
                          Confidence: {(message.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}

                    {/* Suggestions */}
                    {message.suggestions && message.suggestions.length > 0 && (
                      <div className="mt-3 space-y-1">
                        <p className="text-xs font-medium text-gray-600">Suggested actions:</p>
                        {message.suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => handleQuickAction(suggestion)}
                            className="block w-full text-left px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
                          >
                            • {suggestion}
                          </button>
                        ))}
                      </div>
                    )}

                    <div className="text-xs opacity-75 mt-1">
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-800 p-3 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Bot className="w-5 h-5 text-blue-600" />
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t bg-gray-50">
          <div className="flex items-center space-x-2">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about inventory, orders, alerts, or anything supply-related..."
                className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="2"
                disabled={isLoading}
              />
            </div>
            
            {/* Voice input button */}
            {recognition.current && (
              <button
                onClick={handleVoiceInput}
                className={`p-3 rounded-lg transition-colors ${
                  isListening 
                    ? 'bg-red-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                disabled={isLoading}
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            )}

            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            {isListening && (
              <span className="text-red-600 animate-pulse">🔴 Listening...</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMChatInterface;
