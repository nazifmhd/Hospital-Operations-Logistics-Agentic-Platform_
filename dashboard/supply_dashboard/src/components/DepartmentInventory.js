import React, { useState, useEffect } from 'react';
import { Minus, Package, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';

const DepartmentInventory = () => {
  const [departments, setDepartments] = useState([]);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [departmentInventory, setDepartmentInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activities, setActivities] = useState([]);
  const [activeActions, setActiveActions] = useState([]);

  useEffect(() => {
    fetchDepartments();
    fetchRecentActivities();
    fetchActiveActions();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v3/departments');
      const data = await response.json();
      console.log('Departments API response:', data); // Debug log
      setDepartments(data.departments || []);
    } catch (error) {
      console.error('Error fetching departments:', error);
    }
  };

  const fetchDepartmentInventory = async (departmentId) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v3/departments/${departmentId}/inventory`);
      const data = await response.json();
      console.log('Department inventory response:', data); // Debug log
      
      // Ensure we always set an array
      let inventoryData = [];
      if (data && data.inventory && data.inventory.items && Array.isArray(data.inventory.items)) {
        inventoryData = data.inventory.items;
      } else if (data && data.inventory && Array.isArray(data.inventory)) {
        inventoryData = data.inventory;
      } else if (data && Array.isArray(data)) {
        inventoryData = data;
      } else if (data && data.items && Array.isArray(data.items)) {
        inventoryData = data.items;
      }
      
      console.log('Processed inventory data:', inventoryData); // Debug log
      setDepartmentInventory(inventoryData);
      setSelectedDepartment(departmentId);
    } catch (error) {
      console.error('Error fetching department inventory:', error);
      setDepartmentInventory([]); // Ensure we set an empty array on error
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentActivities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v3/enhanced-agent/activities');
      const data = await response.json();
      console.log('Activities response:', data); // Debug log
      setActivities(data.activities || []);
    } catch (error) {
      console.error('Error fetching activities:', error);
      setActivities([]);
    }
  };

  const fetchActiveActions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v3/enhanced-agent/active-actions');
      const data = await response.json();
      console.log('Active actions response:', data); // Debug log
      setActiveActions(data.active_actions || []);
    } catch (error) {
      console.error('Error fetching active actions:', error);
      setActiveActions([]);
    }
  };

  const decreaseStock = async (itemId, quantity, reason = 'consumption') => {
    if (!selectedDepartment) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/v3/departments/${selectedDepartment}/decrease-stock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          item_id: itemId,
          quantity: quantity,
          reason: reason
        })
      });
      
      const data = await response.json();
      console.log('Stock decrease response:', data); // Debug log
      
      if (data.success) {
        // Refresh inventory
        await fetchDepartmentInventory(selectedDepartment);
        await fetchRecentActivities();
        await fetchActiveActions();
        
        // Show success message
        alert(`Stock decreased successfully! New level: ${data.new_stock_level}`);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error decreasing stock:', error);
      alert('Error decreasing stock');
    }
  };

  const triggerAnalysis = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v3/enhanced-agent/analyze', {
        method: 'POST'
      });
      const data = await response.json();
      if (data.success) {
        alert(`Analysis completed! ${data.actions_triggered} automated actions triggered.`);
        await fetchRecentActivities();
        await fetchActiveActions();
      }
    } catch (error) {
      console.error('Error triggering analysis:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'low': return 'text-yellow-600 bg-yellow-50';
      case 'overstocked': return 'text-blue-600 bg-blue-50';
      default: return 'text-green-600 bg-green-50';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'critical': return <AlertTriangle className="w-4 h-4" />;
      case 'low': return <Clock className="w-4 h-4" />;
      case 'overstocked': return <Package className="w-4 h-4" />;
      default: return <CheckCircle className="w-4 h-4" />;
    }
  };

  const getActionTypeColor = (actionType) => {
    switch (actionType) {
      case 'reorder': return 'bg-blue-100 text-blue-800';
      case 'inter_transfer': return 'bg-purple-100 text-purple-800';
      case 'auto_transfer': return 'bg-green-100 text-green-800';
      case 'multi_auto_transfer': return 'bg-emerald-100 text-emerald-800';
      case 'auto_purchase_order': return 'bg-orange-100 text-orange-800';
      case 'stock_decrease': return 'bg-gray-100 text-gray-800';
      case 'stock_adjustment': return 'bg-yellow-100 text-yellow-800';
      case 'critical_alert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">
          🏥 Department Inventory Management
        </h1>
        <button
          onClick={triggerAnalysis}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <RefreshCw className="w-4 h-4" />
          Trigger Analysis
        </button>
      </div>

      {/* Department Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            <Package className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p>No departments found. Make sure the backend is running.</p>
          </div>
        ) : (
          departments.map((dept) => (
            <div
              key={dept.department_id}
              className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                selectedDepartment === dept.department_id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
              onClick={() => fetchDepartmentInventory(dept.department_id)}
            >
              <h3 className="font-semibold text-gray-900">{dept.department_name}</h3>
              <div className="mt-2 space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Total Items:</span>
                  <span>{dept.total_items || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Critical:</span>
                  <span className="text-red-600 font-medium">{dept.critical_items || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Low Stock:</span>
                  <span className="text-yellow-600 font-medium">{dept.low_stock_items || 0}</span>
                </div>
              </div>
              <div className={`mt-2 px-2 py-1 rounded text-xs font-medium ${getStatusColor(dept.status || 'normal')}`}>
                <div className="flex items-center gap-1">
                  {getStatusIcon(dept.status || 'normal')}
                  {(dept.status || 'normal').toUpperCase()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Department Inventory Table */}
      {selectedDepartment && (
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Inventory: {departments.find(d => d.department_id === selectedDepartment)?.department_name}
            </h2>
          </div>
          
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading inventory...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Item</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Stock</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Min / Reorder</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {!Array.isArray(departmentInventory) || departmentInventory.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-4 py-8 text-center text-gray-500">
                        <Package className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                        No inventory items found for this department.
                      </td>
                    </tr>
                  ) : (
                    departmentInventory.map((item) => (
                      <tr key={item.item_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <div className="text-sm font-medium text-gray-900">{item.item_name || 'Unknown Item'}</div>
                          <div className="text-xs text-gray-500">{item.item_id}</div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm font-medium text-gray-900">{item.current_stock || 0}</div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-sm text-gray-600">
                            Min: {item.minimum_stock || 0} / Reorder: {item.reorder_point || 0}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.status || 'normal')}`}>
                            {getStatusIcon(item.status || 'normal')}
                            {(item.status || 'normal').toUpperCase()}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex gap-2">
                            <button
                              onClick={() => decreaseStock(item.item_id, 1)}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              <Minus className="w-3 h-3" />
                              -1
                            </button>
                            <button
                              onClick={() => decreaseStock(item.item_id, 5)}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            >
                              <Minus className="w-3 h-3" />
                              -5
                            </button>
                            <button
                              onClick={() => {
                                const qty = prompt('Enter quantity to decrease:');
                                if (qty && !isNaN(qty) && parseInt(qty) > 0) {
                                  decreaseStock(item.item_id, parseInt(qty));
                                }
                              }}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                            >
                              Custom
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Recent Activities and Active Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activities */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">🤖 Recent Automated Activities</h3>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {activities.length === 0 ? (
              <p className="text-gray-500 text-center">No recent activities</p>
            ) : (
              activities.map((activity, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getActionTypeColor(activity.action_type || 'unknown')}`}>
                    {(activity.action_type || 'unknown').replace('_', ' ').toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{activity.item_name || 'Unknown Item'}</div>
                    <div className="text-xs text-gray-600">
                      {activity.reason || activity.location_details || 'No reason provided'}
                    </div>
                    {activity.quantity && (
                      <div className="text-xs text-blue-600 mt-1">
                        Quantity: {activity.quantity} units
                        {activity.total_amount && ` | Amount: $${activity.total_amount.toFixed(2)}`}
                        {activity.po_id && ` | PO: ${activity.po_id}`}
                      </div>
                    )}
                    <div className="text-xs text-gray-500 mt-1">
                      {activity.timestamp ? new Date(activity.timestamp).toLocaleString() : 'Unknown time'}
                      {activity.status && ` | Status: ${activity.status}`}
                      {activity.priority && ` | Priority: ${activity.priority}`}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Actions */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">⚡ Active Automated Actions</h3>
          </div>
          <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
            {activeActions.length === 0 ? (
              <p className="text-gray-500 text-center">No active actions</p>
            ) : (
              activeActions.map((action, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${getActionTypeColor(action.action_type || 'unknown')}`}>
                    {(action.action_type || 'unknown').replace('_', ' ').toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">{action.item_name || 'Unknown Item'}</div>
                    <div className="text-xs text-blue-600 font-medium">{(action.status || 'unknown').toUpperCase()}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Started: {action.created_at ? new Date(action.created_at).toLocaleString() : 'Unknown time'}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DepartmentInventory;
