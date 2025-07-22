import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { TrendingUp, Package, DollarSign, Calendar, Download, FileSpreadsheet, Share2, RefreshCw } from 'lucide-react';

const Analytics = () => {
  const { dashboardData, getUsageAnalytics, getProcurementRecommendations, loading } = useSupplyData();
  const [selectedItem, setSelectedItem] = useState(null);
  const [usageData, setUsageData] = useState(null);
  const [usageLoading, setUsageLoading] = useState(false);
  const [procurementRecommendations, setProcurementRecommendations] = useState([]);
  const [insightsLoading, setInsightsLoading] = useState(false);

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

  // Fetch procurement recommendations on component mount
  useEffect(() => {
    fetchProcurementRecommendations();
  }, []);

  const fetchProcurementRecommendations = async () => {
    try {
      setInsightsLoading(true);
      const recommendations = await getProcurementRecommendations();
      setProcurementRecommendations(recommendations.recommendations || []);
    } catch (error) {
      console.error('Failed to fetch procurement recommendations:', error);
      setProcurementRecommendations([]);
    } finally {
      setInsightsLoading(false);
    }
  };

  const fetchUsageData = async (itemId) => {
    try {
      setUsageLoading(true);
      // Add cache-busting timestamp to ensure fresh data
      const timestamp = new Date().getTime();
      const data = await getUsageAnalytics(itemId, timestamp);
      setUsageData(data);
    } catch (error) {
      console.error('Failed to fetch usage data:', error);
      setUsageData(null); // Reset on error
    } finally {
      setUsageLoading(false);
    }
  };

  // Manual refresh function
  const handleRefreshUsageData = async () => {
    if (selectedItem) {
      console.log('🔄 Manually refreshing usage data for:', selectedItem);
      await fetchUsageData(selectedItem);
    }
  };

  // Export functions
  const handleExportCSV = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/analytics/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format: 'csv',
          include_charts: false,
          data_points: ['inventory', 'usage', 'categories']
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert('✅ CSV report exported successfully!');
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Error exporting CSV:', error);
      alert('❌ Failed to export CSV. Please try again.');
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/analytics/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          format: 'pdf',
          include_charts: true,
          data_points: ['inventory', 'usage', 'categories', 'recommendations']
        })
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        alert('✅ PDF report exported successfully!');
      } else {
        throw new Error('Export failed');
      }
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('❌ Failed to export PDF. Please try again.');
    }
  };

  const handleShareReport = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/analytics/share', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipients: ['management@hospital.com'],
          report_type: 'analytics_summary',
          include_attachments: true
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`📧 Report shared successfully!\n\nShare ID: ${result.share_id}\nRecipients: ${result.recipients_count}\nExpires: ${result.expiry_date}`);
      } else {
        throw new Error('Share failed');
      }
    } catch (error) {
      console.error('Error sharing report:', error);
      alert('❌ Failed to share report. Please try again.');
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
      .reduce((sum, item) => sum + (item.total_value || 0), 0)
  }));

  const stockLevelData = inventory.map(item => ({
    name: item.name.substring(0, 20) + (item.name.length > 20 ? '...' : ''),
    current: item.current_stock || 0,
    minimum: item.minimum_stock || 0,
    maximum: item.maximum_stock || 0,
    id: item.item_id
  }));

  const valueData = inventory
    .sort((a, b) => (b.total_value || 0) - (a.total_value || 0))
    .slice(0, 10)
    .map(item => ({
      name: item.name.substring(0, 15) + (item.name.length > 15 ? '...' : ''),
      value: item.total_value || 0,
      quantity: item.current_stock || 0
    }));

  const isLowStock = (item) => item.current_stock <= item.minimum_stock;
  const isExpired = (item) => item.expiry_date && new Date(item.expiry_date) < new Date();
  const isExpiringSoon = (item) => {
    if (!item.expiry_date) return false;
    const daysUntilExpiry = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry <= 30 && daysUntilExpiry > 0;
  };

  const pieData = [
    { name: 'Normal Stock', value: inventory.filter(item => !isLowStock(item) && !isExpired(item)).length, color: '#10B981' },
    { name: 'Low Stock', value: inventory.filter(item => isLowStock(item)).length, color: '#F59E0B' },
    { name: 'Expired', value: inventory.filter(item => isExpired(item)).length, color: '#EF4444' },
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <TrendingUp className="h-6 w-6 mr-2" />
              Supply Analytics
            </h1>
            <p className="mt-2 text-gray-600">
              Detailed analytics and insights for supply inventory management
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleExportCSV}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
            >
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              Export CSV
            </button>
            <button
              onClick={handleExportPDF}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 flex items-center"
            >
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </button>
            <button
              onClick={handleShareReport}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center"
            >
              <Share2 className="h-4 w-4 mr-2" />
              Share Report
            </button>
          </div>
        </div>
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
                ${inventory.length > 0 ? (inventory.reduce((sum, item) => sum + (item.total_value || 0), 0) / inventory.length).toFixed(0) : '0'}
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
              <p className="text-sm font-medium text-gray-600">Low Stock %</p>
              <p className="text-2xl font-bold text-gray-900">
                {inventory.length > 0 ? ((inventory.filter(item => isLowStock(item)).length / inventory.length) * 100).toFixed(1) : '0.0'}%
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
                {inventory.filter(item => isExpiringSoon(item)).length}
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
          <div className="flex items-center space-x-3">
            <h3 className="text-lg font-medium text-gray-900">Usage Analytics</h3>
            {selectedItem && (
              <button
                onClick={handleRefreshUsageData}
                disabled={usageLoading}
                className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-50 text-blue-600 border border-blue-200 rounded-md hover:bg-blue-100 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${usageLoading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            )}
          </div>
          <select
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={selectedItem || ''}
            onChange={(e) => setSelectedItem(e.target.value)}
          >
            <option value="">Select an item to analyze</option>
            {inventory.map(item => (
              <option key={item.item_id} value={item.item_id}>
                {item.name}
              </option>
            ))}
          </select>
        </div>

        {usageData && !usageLoading ? (
          <div className="space-y-6">
            {/* Show usage data even if zero */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-md font-medium text-gray-700">
                    Daily Usage Pattern 
                    {usageData.total_usage === 0 && (
                      <span className="text-sm text-green-600 ml-2">(No usage recorded)</span>
                    )}
                    {usageData.total_usage > 0 && (
                      <span className="text-sm text-blue-600 ml-2">({usageData.total_usage} units used)</span>
                    )}
                  </h4>
                  {usageData.total_usage > 0 && (
                    <div className="text-xs text-gray-500">
                      Last updated: {new Date().toLocaleTimeString()}
                    </div>
                  )}
                </div>
                {usageData.total_usage > 0 && (
                  <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-lg">
                    <p className="text-xs text-blue-700">
                      📊 This chart shows real usage data from department stock decreases. Use the refresh button to see the latest data after inventory operations.
                    </p>
                  </div>
                )}
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={usageData.usage_history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="usage" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
                {usageData.total_usage === 0 && (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-700">
                      ✅ No usage recorded for this item in the last 30 days. This indicates:
                    </p>
                    <ul className="text-xs text-green-600 mt-1 ml-4">
                      <li>• Item has not been transferred between departments</li>
                      <li>• Stock levels remain stable</li>
                      <li>• Current inventory may be sufficient</li>
                    </ul>
                  </div>
                )}
              </div>
              
              <div className="space-y-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-gray-700">Average Daily Usage</h5>
                  <p className={`text-2xl font-bold ${usageData.total_usage === 0 ? 'text-green-600' : 'text-blue-600'}`}>
                    {usageData.summary?.average_daily_usage || usageData.average_daily_usage || 0}
                  </p>
                  {usageData.total_usage === 0 && (
                    <p className="text-xs text-green-600 mt-1">No daily consumption</p>
                  )}
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-gray-700">Total Usage (30 days)</h5>
                  <p className={`text-2xl font-bold ${usageData.total_usage === 0 ? 'text-green-600' : 'text-green-600'}`}>
                    {usageData.summary?.total_usage || usageData.total_usage_last_30_days || 0}
                  </p>
                  {usageData.total_usage === 0 && (
                    <p className="text-xs text-green-600 mt-1">Zero consumption recorded</p>
                  )}
                </div>
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="text-sm font-medium text-gray-700">
                    {usageData.total_usage === 0 ? 'Stock Status' : 'Projected Depletion'}
                  </h5>
                  {usageData.total_usage === 0 ? (
                    <p className="text-sm text-green-600 font-medium">
                      Stock Stable
                    </p>
                  ) : (
                    <p className="text-sm text-gray-600">
                      {Math.round((inventory.find(item => item.item_id === selectedItem)?.current_stock || 0) / ((usageData.summary?.average_daily_usage || usageData.average_daily_usage) || 1))} days
                    </p>
                  )}
                </div>
                {usageData.summary?.trend && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="text-sm font-medium text-gray-700">Usage Trend</h5>
                    <p className={`text-sm font-medium ${
                      usageData.summary.trend === 'increasing' ? 'text-red-600' : 
                      usageData.summary.trend === 'decreasing' ? 'text-green-600' : 
                      usageData.summary.trend === 'no_usage' ? 'text-green-600' :
                      'text-gray-600'
                    }`}>
                      {usageData.summary.trend === 'no_usage' ? 'No Usage' : 
                       (usageData.summary.trend || '').charAt(0).toUpperCase() + (usageData.summary.trend || '').slice(1)}
                    </p>
                  </div>
                )}
                
                {/* Data Source Information */}
                <div className="bg-blue-50 rounded-lg p-3">
                  <h5 className="text-xs font-medium text-blue-700">Data Source</h5>
                  <p className="text-xs text-blue-600">
                    {usageData.data_source === 'real_database_transfers' ? '✅ Real transfer data' :
                     usageData.data_source === 'real_database_no_transfers' ? '✅ Database confirmed (no transfers)' :
                     usageData.data_source === 'database_error' ? '⚠️ Database error' :
                     usageData.data_source === 'no_database' ? '⚠️ No database connection' :
                     '❓ Unknown source'}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Department Usage Section */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="text-md font-medium text-gray-700 mb-3">Department Usage</h5>
              {usageData.departments && usageData.departments.length > 0 ? (
                <div className="space-y-2">
                  {usageData.departments.slice(0, 4).map((dept, index) => (
                    <div key={index} className="flex justify-between text-sm">
                      <span>{dept.department}</span>
                      <div className="text-right">
                        <span className="font-medium">{dept.usage} units</span>
                        <span className="text-gray-500 ml-2">({dept.percentage})</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-sm text-green-600">✅ No department transfers recorded</p>
                  <p className="text-xs text-gray-500 mt-1">All departments have maintained their inventory levels</p>
                </div>
              )}
            </div>
            
            {/* Usage Patterns and Forecasting */}
            {usageData.patterns && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h5 className="text-md font-medium text-gray-700 mb-3">Weekly Usage Patterns</h5>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Peak Usage Day:</span>
                      <span className="font-medium text-blue-600">{usageData.patterns.peak_day}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Lowest Usage Day:</span>
                      <span className="font-medium text-green-600">{usageData.patterns.low_day}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Weekday Average:</span>
                      <span className="font-medium">{usageData.patterns.weekday_vs_weekend?.weekday_avg}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Weekend Average:</span>
                      <span className="font-medium">{usageData.patterns.weekday_vs_weekend?.weekend_avg}</span>
                    </div>
                  </div>
                </div>
                
                {usageData.forecasting && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h5 className="text-md font-medium text-gray-700 mb-3">7-Day Forecast</h5>
                    <div className="space-y-2">
                      {usageData.forecasting.next_7_days_estimated?.slice(0, 3).map((forecast, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span>{forecast.date}</span>
                          <span className="font-medium">{forecast.estimated_usage} units</span>
                        </div>
                      ))}
                      <div className="pt-2 border-t border-gray-200">
                        <div className="flex justify-between text-sm">
                          <span>Confidence Level:</span>
                          <span className="font-medium text-blue-600">{(usageData.forecasting.confidence * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Method:</span>
                          <span>{usageData.forecasting.method}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
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
          <div className="text-center py-8">
            <div className="text-gray-500 mb-4">
              Select an item to view detailed usage analytics
            </div>
            <div className="max-w-md mx-auto p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h5 className="text-sm font-medium text-blue-700 mb-2">💡 How to generate usage data:</h5>
              <ol className="text-xs text-blue-600 space-y-1">
                <li>1. Go to Department Inventory page</li>
                <li>2. Select a department (e.g., ICU-01)</li>
                <li>3. Use the decrease stock buttons (-1, -5, custom)</li>
                <li>4. Return here and select that item to see usage charts</li>
              </ol>
            </div>
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
                {inventory.filter(item => isLowStock(item)).length} items are currently below minimum threshold
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-red-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {inventory.filter(item => isExpiringSoon(item)).length} items have expiring batches
              </li>
              <li className="flex items-start">
                <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                Total inventory value: ${inventory.reduce((sum, item) => sum + (item.total_value || 0), 0).toLocaleString()}
              </li>
              {/* Dynamic insights from usage analytics */}
              {usageData && usageData.insights && usageData.insights.map((insight, index) => (
                <li key={`insight-${index}`} className="flex items-start">
                  <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  {insight}
                </li>
              ))}
            </ul>
          </div>
          
          <div>
            <h4 className="text-md font-medium text-gray-700 mb-3">Recommendations</h4>
            {insightsLoading ? (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-xs text-gray-500">Loading recommendations...</p>
              </div>
            ) : (
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                  Review procurement for {inventory.filter(item => isLowStock(item)).length} low-stock items
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
                {/* Dynamic recommendations from procurement API */}
                {procurementRecommendations.slice(0, 3).map((rec, index) => (
                  <li key={`rec-${index}`} className="flex items-start">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                    {rec.description || `${rec.reason || rec.action || 'Reorder'}: ${rec.item_name} (${rec.recommended_quantity || rec.suggested_quantity || 'N/A'} units)`}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
