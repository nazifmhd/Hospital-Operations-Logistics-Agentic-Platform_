import React, { useState } from 'react';
import { Bot, X, MessageSquare } from 'lucide-react';
import { useSupplyData } from '../context/SupplyDataContext';
import StatsCards from './StatsCards';
import InventoryOverview from './InventoryOverview';
import AlertsOverview from './AlertsOverview';
import ProcurementRecommendations from './ProcurementRecommendations';
import AgentChatInterface from './AgentChatInterface';

const Dashboard = () => {
  const { dashboardData, loading, error } = useSupplyData();
  const [showAgentChat, setShowAgentChat] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 relative">
      {/* Page Header with AI Agent Toggle */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Supply Inventory Dashboard</h1>
            <p className="mt-2 text-gray-600">
              Real-time monitoring and management of hospital supply inventory
            </p>
          </div>
          <button
            onClick={() => setShowAgentChat(!showAgentChat)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
          >
            <Bot className="w-5 h-5" />
            <span>{showAgentChat ? 'Hide AI Assistant' : 'Ask AI Assistant'}</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsCards summary={dashboardData.summary} />

      {/* Main Content Grid - Adjusted for AI Chat */}
      <div className={`grid gap-6 ${showAgentChat ? 'grid-cols-1 lg:grid-cols-3' : 'grid-cols-1 lg:grid-cols-2'}`}>
        {/* AI Agent Chat Interface */}
        {showAgentChat && (
          <div className="lg:col-span-1 order-first lg:order-last">
            <div className="sticky top-4">
              <AgentChatInterface />
            </div>
          </div>
        )}

        {/* Inventory Overview */}
        <div className="lg:col-span-1">
          <InventoryOverview inventory={dashboardData.inventory} />
        </div>

        {/* Alerts Overview */}
        <div className="lg:col-span-1">
          <AlertsOverview alerts={dashboardData.alerts} />
        </div>
      </div>

      {/* Procurement Recommendations */}
      <div className={showAgentChat ? 'lg:pr-80' : ''}>
        <ProcurementRecommendations recommendations={dashboardData.recommendations} />
      </div>

      {/* Floating AI Assistant Button for Mobile */}
      {!showAgentChat && (
        <button
          onClick={() => setShowAgentChat(true)}
          className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg z-50 lg:hidden"
        >
          <MessageSquare className="w-6 h-6" />
        </button>
      )}

      {/* Mobile AI Chat Overlay */}
      {showAgentChat && (
        <div className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-50">
          <div className="absolute right-0 top-0 w-full max-w-md h-full bg-white">
            <div className="h-full flex flex-col">
              <div className="p-4 border-b bg-blue-600 text-white flex justify-between items-center">
                <h3 className="font-semibold">AI Assistant</h3>
                <button
                  onClick={() => setShowAgentChat(false)}
                  className="text-white hover:text-gray-200"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
              <div className="flex-1">
                <AgentChatInterface />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
