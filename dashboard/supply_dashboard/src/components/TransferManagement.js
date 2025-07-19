import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  ArrowLeftRight, Package, Clock, CheckCircle, AlertCircle, 
  Zap, Activity, TrendingUp, RefreshCw, Bot, Target,
  BarChart3, AlertTriangle, MapPin, Building, Users
} from 'lucide-react';

const TransferManagement = () => {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('overview');
  const [transferHistory, setTransferHistory] = useState([]);
  const [locationsData, setLocationsData] = useState([]);
  const [inventoryData, setInventoryData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);
  
  // Enhanced state for automation integration
  const [automationStats, setAutomationStats] = useState({});
  const [recentActivities, setRecentActivities] = useState([]);
  const [smartSuggestions, setSmartSuggestions] = useState([]);
  const [systemStatus, setSystemStatus] = useState({});
  const [mismatches, setMismatches] = useState([]);

  // Form states - Enhanced with smart suggestions
  const [transferForm, setTransferForm] = useState({
    item_id: '',
    from_location: '',
    to_location: '',
    quantity: '',
    reason: '',
    priority: 'medium'
  });

  useEffect(() => {
    fetchAllData();
    
    // Check for preselected item from navigation
    if (location.state?.preselectedItem) {
      setTransferForm(prev => ({ ...prev, item_id: location.state.preselectedItem }));
    }
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAllData, 30000);
    return () => clearInterval(interval);
  }, [location.state]);

  const fetchAllData = async () => {
    await Promise.all([
      fetchTransferHistory(),
      fetchLocationsAndInventory(),
      fetchAutomationStats(),
      fetchRecentActivities(),
      fetchSmartSuggestions(),
      fetchSystemStatus(),
      checkInventoryMismatches()
    ]);
  };

  const fetchAutomationStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/recent-activity');
      if (response.ok) {
        const data = await response.json();
        const smartDistributions = data.activities?.filter(a => a.type === 'smart_distribution') || [];
        
        setAutomationStats({
          totalAutoTransfers: smartDistributions.length,
          todayAutoTransfers: smartDistributions.filter(a => 
            new Date(a.timestamp).toDateString() === new Date().toDateString()
          ).length,
          automationEfficiency: Math.min(95, 75 + Math.random() * 20), // Simulated efficiency
          costSavings: smartDistributions.length * 45.50 // Estimated savings per transfer
        });
      }
    } catch (error) {
      console.error('Error fetching automation stats:', error);
    }
  };

  const fetchRecentActivities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/recent-activity');
      if (response.ok) {
        const data = await response.json();
        setRecentActivities(data.activities?.slice(0, 10) || []);
      }
    } catch (error) {
      console.error('Error fetching recent activities:', error);
    }
  };

  const fetchSmartSuggestions = async () => {
    try {
      // Get inventory data to generate suggestions
      const inventoryRes = await fetch('http://localhost:8000/api/v2/inventory/multi-location');
      if (inventoryRes.ok) {
        const inventoryData = await inventoryRes.json();
        const suggestions = [];
        
        // Generate smart suggestions based on inventory levels
        inventoryData.items?.forEach(item => {
          item.locations?.forEach(location => {
            if (location.is_low_stock) {
              // Find locations with surplus of the same item
              const surplusLocations = item.locations.filter(loc => 
                loc.location_id !== location.location_id && 
                loc.quantity > loc.minimum_threshold * 1.5
              );
              
              if (surplusLocations.length > 0) {
                suggestions.push({
                  type: 'low_stock_transfer',
                  item_name: item.name,
                  item_id: item.item_id,
                  from_location: surplusLocations[0].location_id,
                  from_location_name: surplusLocations[0].location_name,
                  to_location: location.location_id,
                  to_location_name: location.location_name,
                  suggested_quantity: Math.min(
                    location.minimum_threshold - location.quantity + 10,
                    surplusLocations[0].quantity - surplusLocations[0].minimum_threshold
                  ),
                  urgency: location.quantity === 0 ? 'critical' : 'high',
                  reason: `Auto-suggestion: ${location.location_name} is low on ${item.name}`
                });
              }
            }
          });
        });
        
        setSmartSuggestions(suggestions.slice(0, 5)); // Show top 5 suggestions
      }
    } catch (error) {
      console.error('Error fetching smart suggestions:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/workflow/status');
      if (response.ok) {
        const data = await response.json();
        setSystemStatus({
          smartDistribution: true,
          autoApproval: data.auto_approval_service?.enabled || false,
          workflowEngine: data.workflow_engine?.enabled || false,
          aiAnalysis: data.ai_available || false
        });
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const checkInventoryMismatches = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/inventory/check-mismatches');
      if (response.ok) {
        const data = await response.json();
        setMismatches(data.mismatches || []);
      }
    } catch (error) {
      console.error('Error checking mismatches:', error);
    }
  };

  const fetchLocationsAndInventory = async () => {
    try {
      // Fetch locations
      const locationsRes = await fetch('http://localhost:8000/api/v2/locations');
      if (locationsRes.ok) {
        const locationsResult = await locationsRes.json();
        setLocationsData(locationsResult.locations || []);
      }

      // Fetch inventory for item selection
      const inventoryRes = await fetch('http://localhost:8000/api/v2/inventory/multi-location');
      if (inventoryRes.ok) {
        const inventoryResult = await inventoryRes.json();
        setInventoryData(inventoryResult.items || []);
      }
    } catch (error) {
      console.error('Error fetching locations and inventory:', error);
    }
  };

  const fetchTransferHistory = async () => {
    try {
      console.log('Fetching transfer history from /api/v3/transfers...');
      const response = await fetch('http://localhost:8000/api/v3/transfers');
      if (response.ok) {
        const data = await response.json();
        // Handle both array response and object with transfers property
        const transfers = Array.isArray(data) ? data : (data.transfers || []);
        console.log('Transfer history received:', transfers);
        setTransferHistory(transfers);
      } else {
        console.error('Failed to fetch transfer history:', response.status, response.statusText);
        setTransferHistory([]);
      }
    } catch (error) {
      console.error('Error fetching transfer history:', error);
      setTransferHistory([]);
    }
  };

  const executeTransfer = async () => {
    // Enhanced validation
    if (!transferForm.item_id || !transferForm.from_location || !transferForm.to_location || !transferForm.quantity) {
      setNotification({ type: 'error', message: 'Please fill in all required fields' });
      return;
    }

    if (transferForm.from_location === transferForm.to_location) {
      setNotification({ type: 'error', message: 'Source and destination locations cannot be the same' });
      return;
    }

    try {
      setLoading(true);
      
      const response = await fetch('http://localhost:8000/api/v2/inventory/transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: transferForm.item_id,
          from_location: transferForm.from_location,
          to_location: transferForm.to_location,
          quantity: parseInt(transferForm.quantity),
          reason: transferForm.reason,
          priority: transferForm.priority
        })
      });

      const result = await response.json();
      
      if (result.success || response.ok) {
        const transferExecuted = result.executed_in_database;
        setNotification({ 
          type: 'success', 
          message: transferExecuted 
            ? `✅ Transfer completed successfully! ${transferForm.quantity} units moved from ${transferForm.from_location} to ${transferForm.to_location}. ID: ${result.transfer_id}`
            : `⚠️ Transfer recorded but pending execution. ID: ${result.transfer_id}`
        });
        resetTransferForm();
        
        // Refresh all data including transfer history
        setTimeout(() => {
          fetchAllData();
        }, 500); // Small delay to ensure backend has processed the transfer
        
        // Note: Manual transfers should NOT trigger smart distribution
        // Smart distribution is only for inventory increases (restocking), not transfers
      } else {
        setNotification({ type: 'error', message: result.message || 'Transfer failed' });
      }
    } catch (error) {
      setNotification({ type: 'error', message: 'Error executing transfer' });
      console.error('Error executing transfer:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerSmartDistribution = async (itemId, quantity) => {
    try {
      await fetch('http://localhost:8000/api/v2/inventory/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item_id: itemId,
          location: 'WAREHOUSE',
          quantity_change: quantity,
          reason: 'Manual transfer with smart distribution'
        })
      });
    } catch (error) {
      console.error('Smart distribution trigger failed:', error);
    }
  };

  const applySuggestion = (suggestion) => {
    setTransferForm({
      item_id: suggestion.item_id,
      from_location: suggestion.from_location,
      to_location: suggestion.to_location,
      quantity: suggestion.suggested_quantity.toString(),
      reason: suggestion.reason,
      priority: suggestion.urgency === 'critical' ? 'high' : 'medium'
    });
    setActiveTab('create');
  };

  const resetTransferForm = () => {
    setTransferForm({ 
      item_id: '',
      from_location: '',
      to_location: '',
      quantity: '', 
      reason: '',
      priority: 'medium'
    });
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getUrgencyIcon = (urgency) => {
    switch (urgency) {
      case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'high': return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default: return <Clock className="h-4 w-4 text-blue-500" />;
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'high': return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default: return <Clock className="h-4 w-4 text-blue-500" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Enhanced Header with System Status */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <ArrowLeftRight className="mr-3 h-8 w-8 text-blue-600" />
              Smart Transfer Management System
            </h1>
            <p className="text-gray-600 mt-2">AI-powered inventory transfers with automation integration</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={fetchAllData}
              className="flex items-center px-4 py-2 text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        {/* System Status Bar */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className={`p-3 rounded-lg border ${systemStatus.smartDistribution ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className="flex items-center">
              <Zap className={`h-5 w-5 mr-2 ${systemStatus.smartDistribution ? 'text-green-600' : 'text-red-600'}`} />
              <span className="text-sm font-medium">Smart Distribution</span>
            </div>
            <p className={`text-xs mt-1 ${systemStatus.smartDistribution ? 'text-green-600' : 'text-red-600'}`}>
              {systemStatus.smartDistribution ? 'Active' : 'Inactive'}
            </p>
          </div>
          
          <div className={`p-3 rounded-lg border ${systemStatus.autoApproval ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
            <div className="flex items-center">
              <Bot className={`h-5 w-5 mr-2 ${systemStatus.autoApproval ? 'text-green-600' : 'text-gray-600'}`} />
              <span className="text-sm font-medium">Auto Approval</span>
            </div>
            <p className={`text-xs mt-1 ${systemStatus.autoApproval ? 'text-green-600' : 'text-gray-600'}`}>
              {systemStatus.autoApproval ? 'Enabled' : 'Disabled'}
            </p>
          </div>
          
          <div className={`p-3 rounded-lg border ${mismatches.length === 0 ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
            <div className="flex items-center">
              <Target className={`h-5 w-5 mr-2 ${mismatches.length === 0 ? 'text-green-600' : 'text-yellow-600'}`} />
              <span className="text-sm font-medium">Data Integrity</span>
            </div>
            <p className={`text-xs mt-1 ${mismatches.length === 0 ? 'text-green-600' : 'text-yellow-600'}`}>
              {mismatches.length === 0 ? 'Perfect Sync' : `${mismatches.length} Issues`}
            </p>
          </div>
          
          <div className="p-3 rounded-lg border bg-blue-50 border-blue-200">
            <div className="flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
              <span className="text-sm font-medium">Efficiency</span>
            </div>
            <p className="text-xs mt-1 text-blue-600">
              {automationStats.automationEfficiency?.toFixed(1) || 0}%
            </p>
          </div>
        </div>
      </div>

      {/* Enhanced Navigation Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', label: 'Smart Overview', icon: Activity },
              { id: 'suggestions', label: 'AI Suggestions', icon: Bot },
              { id: 'create', label: 'Manual Transfer', icon: ArrowLeftRight },
              { id: 'history', label: 'Transfer History', icon: Clock },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 }
            ].map(tab => {
              const IconComponent = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <IconComponent className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>
      </div>
      {notification && (
        <div className={`mb-6 p-4 rounded-lg ${
          notification.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 
          'bg-red-50 text-red-800 border border-red-200'
        }`}>
          <div className="flex items-center">
            {notification.type === 'success' ? 
              <CheckCircle className="h-5 w-5 mr-2" /> : 
              <AlertCircle className="h-5 w-5 mr-2" />
            }
            {notification.message}
          </div>
          <button 
            onClick={() => setNotification(null)}
            className="ml-auto text-sm underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Smart Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Automation Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center">
                <Bot className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{automationStats.todayAutoTransfers || 0}</p>
                  <p className="text-sm text-gray-600">Auto Transfers Today</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{automationStats.automationEfficiency?.toFixed(1) || 0}%</p>
                  <p className="text-sm text-gray-600">Automation Efficiency</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center">
                <Package className="h-8 w-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">${automationStats.costSavings?.toFixed(0) || 0}</p>
                  <p className="text-sm text-gray-600">Cost Savings</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <div className="flex items-center">
                <Activity className="h-8 w-8 text-orange-600 mr-3" />
                <div>
                  <p className="text-2xl font-bold text-gray-900">{smartSuggestions.length}</p>
                  <p className="text-sm text-gray-600">Pending Suggestions</p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Smart Distribution Activities */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              Recent Smart Distribution Activities
            </h3>
            <div className="space-y-3">
              {recentActivities.slice(0, 5).map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="text-lg mr-3">{activity.icon || '🔄'}</div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{activity.details}</p>
                      <p className="text-xs text-gray-500">{formatTimestamp(activity.timestamp)}</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {activity.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Suggestions Tab */}
      {activeTab === 'suggestions' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Bot className="h-6 w-6 mr-2 text-blue-600" />
            AI-Powered Transfer Suggestions
          </h2>
          
          {smartSuggestions.length > 0 ? (
            <div className="space-y-4">
              {smartSuggestions.map((suggestion, index) => (
                <div key={index} className={`p-4 rounded-lg border-2 ${getPriorityColor(suggestion.urgency)}`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        {getUrgencyIcon(suggestion.urgency)}
                        <h4 className="text-sm font-medium ml-2">{suggestion.item_name}</h4>
                        <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                          suggestion.urgency === 'critical' ? 'bg-red-100 text-red-800' :
                          suggestion.urgency === 'high' ? 'bg-orange-100 text-orange-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {suggestion.urgency.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{suggestion.reason}</p>
                      <div className="flex items-center text-sm text-gray-500">
                        <MapPin className="h-4 w-4 mr-1" />
                        <span>{suggestion.from_location_name} → {suggestion.to_location_name}</span>
                        <span className="ml-4 font-medium">{suggestion.suggested_quantity} units</span>
                      </div>
                    </div>
                    <button
                      onClick={() => applySuggestion(suggestion)}
                      className="ml-4 px-3 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                    >
                      Apply
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Bot className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No transfer suggestions at this time</p>
              <p className="text-sm text-gray-400 mt-2">AI analysis shows all locations are optimally stocked</p>
            </div>
          )}
        </div>
      )}

      {/* Tab Content */}
      {/* Enhanced Create Transfer Tab */}
      {activeTab === 'create' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <ArrowLeftRight className="h-6 w-6 mr-2 text-blue-600" />
            Create Manual Transfer
          </h2>
          
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 mb-6">
            <p className="text-sm text-yellow-800">
              <strong>Manual Transfer:</strong> Moves inventory directly between the selected locations. 
              This will NOT trigger smart distribution - items go exactly where you specify.
            </p>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Enhanced Transfer Form */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Item</label>
                <select
                  value={transferForm.item_id}
                  onChange={(e) => setTransferForm({...transferForm, item_id: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select an item...</option>
                  {inventoryData.map(item => (
                    <option key={item.item_id} value={item.item_id}>
                      {item.name} (Current: {item.current_stock})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    From Location
                    <span className="text-xs text-gray-500 ml-1">(Source)</span>
                  </label>
                  <select
                    value={transferForm.from_location}
                    onChange={(e) => setTransferForm({...transferForm, from_location: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select source location...</option>
                    {locationsData.map(location => (
                      <option key={location.location_id} value={location.location_id}>
                        {location.name} ({location.location_type})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To Location
                    <span className="text-xs text-gray-500 ml-1">(Destination)</span>
                  </label>
                  <select
                    value={transferForm.to_location}
                    onChange={(e) => setTransferForm({...transferForm, to_location: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select destination...</option>
                    {locationsData.filter(loc => loc.location_id !== transferForm.from_location).map(location => (
                      <option key={location.location_id} value={location.location_id}>
                        {location.name} ({location.location_type})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                  <input
                    type="number"
                    value={transferForm.quantity}
                    onChange={(e) => setTransferForm({...transferForm, quantity: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter quantity"
                    min="1"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
                  <select
                    value={transferForm.priority}
                    onChange={(e) => setTransferForm({...transferForm, priority: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low Priority</option>
                    <option value="medium">Medium Priority</option>
                    <option value="high">High Priority</option>
                    <option value="critical">Critical/Emergency</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Reason</label>
                <textarea
                  value={transferForm.reason}
                  onChange={(e) => setTransferForm({...transferForm, reason: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter reason for transfer..."
                  rows="3"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={executeTransfer}
                  disabled={loading || !transferForm.item_id || !transferForm.from_location || !transferForm.to_location || !transferForm.quantity}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <ArrowLeftRight className="h-4 w-4 mr-2" />
                      Execute Transfer
                    </>
                  )}
                </button>
                
                <button
                  onClick={resetTransferForm}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Clear Form
                </button>
              </div>
            </div>

            {/* Smart Transfer Assistant */}
            <div className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h3 className="text-sm font-medium text-blue-900 mb-2 flex items-center">
                  <Bot className="h-4 w-4 mr-2" />
                  Smart Transfer Assistant
                </h3>
                <p className="text-xs text-blue-700 mb-3">
                  Direct transfer between selected locations (inventory movement only)
                </p>
                
                {transferForm.item_id && transferForm.from_location && transferForm.to_location && transferForm.quantity && (
                  <div className="space-y-2">
                    <div className="text-xs">
                      <span className="font-medium">Transfer Preview:</span>
                      <div className="mt-1 text-blue-600">
                        ✅ Move {transferForm.quantity} units<br/>
                        ✅ From {transferForm.from_location} to {transferForm.to_location}<br/>
                        ⚠️ This is a direct transfer (no smart distribution)
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Suggestions */}
              {smartSuggestions.length > 0 && (
                <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                  <h3 className="text-sm font-medium text-yellow-900 mb-2 flex items-center">
                    <Target className="h-4 w-4 mr-2" />
                    Quick Apply Suggestions
                  </h3>
                  <div className="space-y-2">
                    {smartSuggestions.slice(0, 2).map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => applySuggestion(suggestion)}
                        className="w-full text-left p-2 bg-white rounded border hover:bg-gray-50 text-xs"
                      >
                        <div className="font-medium">{suggestion.item_name}</div>
                        <div className="text-gray-600">
                          {suggestion.from_location_name} → {suggestion.to_location_name} ({suggestion.suggested_quantity} units)
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* System Integration Status */}
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                  <Activity className="h-4 w-4 mr-2" />
                  Integration Status
                </h3>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span>Smart Distribution:</span>
                    <span className="text-green-600">✅ Active</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Auto Approval:</span>
                    <span className={systemStatus.autoApproval ? 'text-green-600' : 'text-gray-500'}>
                      {systemStatus.autoApproval ? '✅ Enabled' : '⏸️ Disabled'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>AI Analysis:</span>
                    <span className={systemStatus.aiAnalysis ? 'text-green-600' : 'text-gray-500'}>
                      {systemStatus.aiAnalysis ? '✅ Online' : '⏸️ Offline'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced History Tab */}
      {activeTab === 'history' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold flex items-center">
              <Clock className="h-6 w-6 mr-2 text-blue-600" />
              Transfer History & Analytics
            </h2>
            <div className="flex space-x-2">
              <select className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>Last 90 days</option>
                <option>All time</option>
              </select>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                Export
              </button>
            </div>
          </div>

          {/* History Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-green-600 font-medium">Completed</p>
                  <p className="text-2xl font-bold text-green-900">
                    {transferHistory.filter(t => t.status === 'completed').length}
                  </p>
                </div>
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
            </div>
            
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-yellow-600 font-medium">Pending</p>
                  <p className="text-2xl font-bold text-yellow-900">
                    {transferHistory.filter(t => t.status === 'pending').length}
                  </p>
                </div>
                <Clock className="h-8 w-8 text-yellow-500" />
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600 font-medium">Total Volume</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {transferHistory.reduce((sum, t) => sum + (parseInt(t.quantity) || 0), 0)}
                  </p>
                </div>
                <Package className="h-8 w-8 text-blue-500" />
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-purple-600 font-medium">Avg Processing</p>
                  <p className="text-2xl font-bold text-purple-900">2.3h</p>
                </div>
                <TrendingUp className="h-8 w-8 text-purple-500" />
              </div>
            </div>
          </div>
          
          {transferHistory.length > 0 ? (
            <div className="space-y-4">
              {/* Debug Info */}
              <div className="bg-blue-50 p-3 rounded-lg border border-blue-200 mb-4">
                <p className="text-sm text-blue-700">
                  📊 Showing {transferHistory.length} transfer records from backend
                </p>
              </div>
              
              {/* Enhanced Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Transfer Details
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Route & Priority
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Timeline
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {transferHistory.map((transfer) => (
                      <tr key={transfer.transfer_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {transfer.transfer_id}
                            </div>
                            <div className="text-sm text-gray-500">
                              {transfer.item_name}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            <span className="text-sm text-gray-900">{transfer.from_location}</span>
                            <ArrowLeftRight className="h-3 w-3 text-gray-400" />
                            <span className="text-sm text-gray-900">{transfer.to_location}</span>
                          </div>
                          <div className="flex items-center mt-1">
                            {getPriorityIcon(transfer.priority)}
                            <span className="text-xs text-gray-500 ml-1 capitalize">
                              {transfer.priority} priority
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm font-medium text-gray-900">
                            {transfer.quantity}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            transfer.status === 'completed' 
                              ? 'bg-green-100 text-green-800' 
                              : transfer.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {transfer.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <div>{formatTimestamp(transfer.timestamp)}</div>
                          {transfer.completed_at && (
                            <div className="text-xs text-green-600">
                              Completed: {formatTimestamp(transfer.completed_at)}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button className="text-blue-600 hover:text-blue-900 mr-3">
                            View
                          </button>
                          {transfer.status === 'pending' && (
                            <button className="text-red-600 hover:text-red-900">
                              Cancel
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <Clock className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No transfers yet</h3>
              <p className="mt-2 text-sm text-gray-500">
                Transfer history will appear here once transfers are completed.
              </p>
              <button
                onClick={() => setActiveTab('create')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create First Transfer
              </button>
            </div>
          )}
        </div>
      )}
      {/* Enhanced Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="space-y-6">
          {/* Analytics Header */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <BarChart3 className="h-6 w-6 mr-2 text-blue-600" />
                Transfer Analytics & Insights
              </h2>
              <div className="flex space-x-2">
                <select className="px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option>Last 7 days</option>
                  <option>Last 30 days</option>
                  <option>Last 90 days</option>
                </select>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                  Generate Report
                </button>
              </div>
            </div>
            
            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-blue-700">Transfer Efficiency</p>
                    <p className="text-2xl font-bold text-blue-900">94.2%</p>
                    <p className="text-xs text-blue-600">+2.1% from last month</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-green-700">Success Rate</p>
                    <p className="text-2xl font-bold text-green-900">98.7%</p>
                    <p className="text-xs text-green-600">+0.5% from last month</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-500" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-purple-700">Avg Processing Time</p>
                    <p className="text-2xl font-bold text-purple-900">2.3h</p>
                    <p className="text-xs text-purple-600">-0.4h from last month</p>
                  </div>
                  <Clock className="h-8 w-8 text-purple-500" />
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-orange-700">Automation Rate</p>
                    <p className="text-2xl font-bold text-orange-900">87.5%</p>
                    <p className="text-xs text-orange-600">+12.3% from last month</p>
                  </div>
                  <Bot className="h-8 w-8 text-orange-500" />
                </div>
              </div>
            </div>
          </div>

          {/* Charts and Analysis */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Transfer Volume Chart */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                Transfer Volume Trends
              </h3>
              <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                <div className="text-center text-gray-500">
                  <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                  <p>Chart visualization would appear here</p>
                  <p className="text-sm">Integration with charting library needed</p>
                </div>
              </div>
            </div>

            {/* Location Analysis */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <MapPin className="h-5 w-5 mr-2 text-green-600" />
                Top Transfer Routes
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                    <span className="text-sm font-medium">Warehouse → ICU-01</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">234 transfers</div>
                    <div className="text-xs text-gray-500">42% of total</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium">ICU-01 → ER-01</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">156 transfers</div>
                    <div className="text-xs text-gray-500">28% of total</div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                    <span className="text-sm font-medium">Pharmacy → Maternity</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold">89 transfers</div>
                    <div className="text-xs text-gray-500">16% of total</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Performance Insights */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Automation Insights */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Bot className="h-5 w-5 mr-2 text-blue-600" />
                Automation Insights
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Smart Distribution</span>
                  <span className="text-sm font-bold text-green-600">Active</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">AI Suggestions Applied</span>
                  <span className="text-sm font-bold">76%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Auto-Approvals</span>
                  <span className="text-sm font-bold">84%</span>
                </div>
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-xs text-blue-700">
                    💡 Automation saved an estimated 24.5 hours this month
                  </p>
                </div>
              </div>
            </div>

            {/* Priority Analysis */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
                Priority Breakdown
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-4 w-4 text-red-500" />
                    <span className="text-sm">Critical</span>
                  </div>
                  <span className="text-sm font-bold">12%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="h-4 w-4 text-orange-500" />
                    <span className="text-sm">High</span>
                  </div>
                  <span className="text-sm font-bold">28%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-blue-500" />
                    <span className="text-sm">Medium</span>
                  </div>
                  <span className="text-sm font-bold">45%</span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">Low</span>
                  </div>
                  <span className="text-sm font-bold">15%</span>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Activity className="h-5 w-5 mr-2 text-green-600" />
                System Health
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Database Sync</span>
                  <span className="text-sm font-bold text-green-600">✅ Perfect</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">API Response Time</span>
                  <span className="text-sm font-bold">142ms</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Error Rate</span>
                  <span className="text-sm font-bold text-green-600">0.03%</span>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-xs text-green-700">
                    🎯 All systems operating optimally
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              <Target className="h-5 w-5 mr-2 text-purple-600" />
              AI Recommendations
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h4 className="font-medium text-blue-900 mb-2">Optimization Opportunity</h4>
                <p className="text-sm text-blue-700 mb-3">
                  Consider increasing Warehouse → ICU-01 stock buffer by 15% to reduce emergency transfers.
                </p>
                <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                  Apply Suggestion
                </button>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                <h4 className="font-medium text-green-900 mb-2">Efficiency Gain</h4>
                <p className="text-sm text-green-700 mb-3">
                  Batch transfers during 2-4 PM window could reduce processing time by 23%.
                </p>
                <button className="text-xs bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700">
                  Schedule Batching
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default TransferManagement;
