import React, { useState, useEffect } from 'react';
import { Bot, X, Sparkles } from 'lucide-react';
import LLMChatInterface from './LLMChatInterface';

const FloatingAIAssistant = ({ systemContext = {} }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [llmAvailable, setLlmAvailable] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  // Check LLM availability
  useEffect(() => {
    const checkLLMAvailability = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v2/llm/status');
        if (response.ok) {
          const data = await response.json();
          setLlmAvailable(data.llm_available);
        }
      } catch (error) {
        console.warn('LLM service not available:', error);
        setLlmAvailable(false);
      }
    };

    checkLLMAvailability();
    
    // Recheck every 5 minutes
    const interval = setInterval(checkLLMAvailability, 300000);
    return () => clearInterval(interval);
  }, []);

  // Trigger animation on first load
  useEffect(() => {
    if (llmAvailable) {
      setTimeout(() => setIsAnimating(true), 1000);
      setTimeout(() => setIsAnimating(false), 3000);
    }
  }, [llmAvailable]);

  if (!llmAvailable) return null;

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

          {/* Beta Badge */}
          <div className="absolute -top-1 -right-1 bg-yellow-400 text-yellow-900 text-xs font-bold px-1.5 py-0.5 rounded-full">
            β
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
                <h4 className="text-sm font-semibold text-gray-900">AI Assistant Available!</h4>
                <p className="text-xs text-gray-600 mt-1">
                  Ask questions about inventory, orders, alerts, or get insights about your supply chain.
                </p>
              </div>
            </div>
            <div className="absolute top-full right-8 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-white"></div>
          </div>
        )}
      </div>

      {/* Chat Interface */}
      <LLMChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        systemContext={{
          ...systemContext,
          source: 'floating_assistant',
          timestamp: new Date().toISOString()
        }}
      />
    </>
  );
};

export default FloatingAIAssistant;
