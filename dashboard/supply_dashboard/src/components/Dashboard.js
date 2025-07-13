import React from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import StatsCards from './StatsCards';
import InventoryOverview from './InventoryOverview';
import AlertsOverview from './AlertsOverview';
import ProcurementRecommendations from './ProcurementRecommendations';

const Dashboard = () => {
  const { dashboardData, loading, error } = useSupplyData();

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
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900">Supply Inventory Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Real-time monitoring and management of hospital supply inventory
        </p>
      </div>

      {/* Stats Cards */}
      <StatsCards summary={dashboardData.summary} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
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
      <ProcurementRecommendations recommendations={dashboardData.recommendations} />
    </div>
  );
};

export default Dashboard;
