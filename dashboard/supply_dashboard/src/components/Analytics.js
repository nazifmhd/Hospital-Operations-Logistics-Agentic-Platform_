import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Package, DollarSign, Calendar } from 'lucide-react';

const Analytics = () => {
  const { dashboardData, getUsageAnalytics, loading } = useSupplyData();
  const [selectedItem, setSelectedItem] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [usageLoading, setUsageLoading] = useState(false);

  useEffect(() => {
    if (selectedItem) {
      setUsageData(null); // Reset usage data when selection changes
      setUsageLoading(true); // Set loading state
      fetchUsageData(selectedItem);
    } else {
      setUsageData(null); // Clear data when no item is selected
      setUsageLoading(false); // Clear loading state
    }
  }, [selectedItem]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchUsageData = async (itemId) => {
    try {
      setUsageLoading(true);
      const data = await getUsageAnalytics(itemId);
      setUsageData(data);
    } catch (error) {
      console.error('Failed to fetch usage data:', error);
      setUsageData(null); // Reset on error
    } finally {
      setUsageLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const inventory = dashboardData?.inventory || [];

  // Prepare data for charts
  const categoryData = inventory.reduce((acc, item) => {
    const category = item.category.replace('_', ' ').toUpperCase();
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const categoryChartData = Object.entries(categoryData).map(([category, count]) => ({
    category,
    count,
    value: inventory
      .filter(item => item.category.replace('_', ' ').toUpperCase() === category)
      .reduce((sum, item) => sum + item.total_value, 0)
  }));

  const stockLevelData = inventory.map(item => ({
    name: item.name.substring(0, 20) + (item.name.length > 20 ? '...' : ''),
    current: item.total_quantity || 0,
    minimum: item.minimum_threshold || 0,
    maximum: item.maximum_capacity || 0,
    id: item.id
  }));

  const valueData = inventory
    .sort((a, b) => b.total_value - a.total_value)
    .slice(0, 10)
    .map(item => ({
      name: item.name.substring(0, 15) + (item.name.length > 15 ? '...' : ''),
      value: item.total_value,
      quantity: item.total_quantity || 0
    }));

  const pieData = [
    { name: 'Normal Stock', value: inventory.filter(item => !item.is_low_stock && !item.has_expired).length, color: '#10B981' },
    { name: 'Low Stock', value: inventory.filter(item => item.is_low_stock).length, color: '#F59E0B' },
    { name: 'Expired', value: inventory.filter(item => item.has_expired).length, color: '#EF4444' },
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <TrendingUp className="h-6 w-6 mr-2" />
          Supply Analytics
        </h1>
        <p className="mt-2 text-gray-600">
          Detailed analytics and insights for supply inventory management
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-500">
              <Package className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Categories</p>
              <p className="text-2xl font-bold text-gray-900">{Object.keys(categoryData).length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-500">
              <DollarSign className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Item Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${(inventory.reduce((sum, item) => sum + item.total_value, 0) / inventory.length || 0).toFixed(0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-yellow-500">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Stock Turnover</p>
              <p className="text-2xl font-bold text-gray-900">
                {((inventory.filter(item => item.is_low_stock).length / inventory.length) * 100).toFixed(1)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-500">
              <Calendar className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Items Expiring Soon</p>
              <p className="text-2xl font-bold text-gray-900">
                {inventory.filter(item => item.expiring_soon_count && item.expiring_soon_count > 0).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Items by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="category" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Stock Status Distribution */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Stock Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Items by Value */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Items by Value</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={valueData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={80} fontSize={12} />
              <Tooltip />
              <Bar dataKey="value" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Stock Levels */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Stock Levels Overview</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stockLevelData.slice(0, 8)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="name" 
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={10}
              />
              <YAxis />
              <Tooltip />
              <Bar dataKey="current" fill="#3B82F6" name="Current Stock" />
              <Bar dataKey="minimum" fill="#EF4444" name="Minimum Threshold" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Usage Analytics Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Usage Analytics</h3>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={selectedItem || ''}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            <option value="">Select an item to analyze</option>
            {inventory.map(item => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        {usageData && !usageLoading ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <h4 className="text-md font-medium text-gray-700 mb-3">Daily Usage Pattern</h4>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={usageData.usage_history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="usage" stroke="#3B82F6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="space-y-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="text-sm font-medium text-gray-700">Average Daily Usage</h5>
                <p className="text-2xl font-bold text-blue-600">{usageData.average_daily_usage}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="text-sm font-medium text-gray-700">Total Usage (30 days)</h5>
                <p className="text-2xl font-bold text-green-600">{usageData.total_usage_last_30_days}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h5 className="text-sm font-medium text-gray-700">Projected Depletion</h5>
                <p className="text-sm text-gray-600">
                  {Math.round((inventory.find(item => item.id === selectedItem)?.total_quantity || 0) / (usageData.average_daily_usage || 1))} days
                </p>
              </div>
            </div>
          </div>
        ) : selectedItem && usageLoading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-500">Loading usage data...</p>
          </div>
        ) : selectedItem && !usageLoading ? (
          <div className="text-center py-8 text-gray-500">
            <p>No usage data available for this item.</p>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Select an item to view detailed usage analytics
          </div>
        )}
      </div>

      {/* Insights and Recommendations */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Insights & Recommendations</h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <h4 className="text-md font-medium text-gray-700 mb-3">Key Insights</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {categoryChartData.sort((a, b) => b.count - a.count)[0]?.category} has the most items ({categoryChartData.sort((a, b) => b.count - a.count)[0]?.count})
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {inventory.filter(item => item.is_low_stock).length} items are currently below minimum threshold
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {inventory.filter(item => item.expiring_soon_count && item.expiring_soon_count > 0).length} items have expiring batches
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Total inventory value: ${inventory.reduce((sum, item) => sum + item.total_value, 0).toLocaleString()}
              </li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-md font-medium text-gray-700 mb-3">Recommendations</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Review procurement for {inventory.filter(item => item.is_low_stock).length} low-stock items
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Implement automated reordering for high-usage items
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Consider bulk purchasing for {categoryChartData.sort((a, b) => b.count - a.count)[0]?.category} category
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-teal-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Set up expiry alerts for better waste management
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
