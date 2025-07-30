import React, { useState, useEffect } from 'react';
import { Bot, X, Sparkles } from 'lucide-react';
import AgentChatInterface from './AgentChatInterface';

const FloatingAIAssistant = ({ systemContext = {} }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [agentAvailable, setAgentAvailable] = useState(true); // Always available since it's self-contained
  const [isAnimating, setIsAnimating] = useState(false);

  // Trigger animation on first load
  useEffect(() => {
    if (agentAvailable) {
      setTimeout(() => setIsAnimating(true), 1000);
      setTimeout(() => setIsAnimating(false), 3000);
    }
  }, [agentAvailable]);

  if (!agentAvailable) return null;

  return (
    <>
      {/* Floating Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsOpen(true)}
          className={`relative group bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 ${
            isAnimating ? 'animate-bounce' : ''
          }`}
        >
          <Bot className="w-6 h-6" />
          
          {/* Pulsing Ring */}
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 animate-ping opacity-20"></div>
          
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <div className="bg-gray-900 text-white text-sm px-3 py-2 rounded-lg whitespace-nowrap">
              Ask AI Assistant
              <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>

          {/* Agent Badge */}
          <div className="absolute -top-1 -right-1 bg-green-400 text-green-900 text-xs font-bold px-1.5 py-0.5 rounded-full">
            AI
          </div>

          {/* Sparkle Effect */}
          {isAnimating && (
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-yellow-300 animate-pulse" />
            </div>
          )}
        </button>

        {/* Feature Hint (shows on first visit) */}
        {isAnimating && (
          <div className="absolute bottom-full right-0 mb-4 bg-white rounded-lg shadow-xl p-4 max-w-xs border">
            <div className="flex items-start space-x-2">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">AI Agent Available!</h4>
                <p className="text-xs text-gray-600 mt-1">
                  Ask questions about inventory, perform actions through conversation, or get intelligent insights about your supply chain.
                </p>
              </div>
            </div>
            <div className="absolute top-full right-8 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
          </div>
        )}
      </div>

      {/* Comprehensive AI Agent Chat Interface */}
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold flex items-center">
                <Bot className="w-6 h-6 mr-2 text-blue-600" />
                AI Agent Assistant
                <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-normal">
                  Powered by RAG + LLM
                </span>
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <AgentChatInterface />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default FloatingAIAssistant;
