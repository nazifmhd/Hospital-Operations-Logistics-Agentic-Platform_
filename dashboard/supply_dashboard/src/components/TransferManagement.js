import React, { useState, useEffect } from 'react';
import { ArrowLeftRight, Package, Search, Clock, CheckCircle, AlertCircle, TrendingUp, Building } from 'lucide-react';

const TransferManagement = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [transferHistory, setTransferHistory] = useState([]);
  const [surplusData, setSurplusData] = useState({});
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState(null);

  // Form states
  const [transferForm, setTransferForm] = useState({
    itemName: '',
    fromDepartment: '',
    toDepartment: '',
    quantity: '',
    reason: ''
  });

  const departments = ['ICU', 'ER', 'SURGERY', 'PHARMACY', 'WAREHOUSE', 'LAB'];
  
  const commonItems = [
    'Surgical Gloves (Box of 100)',
    'N95 Respirator Masks (20 pack)',
    'IV Bags (1000ml)',
    'Paracetamol 500mg (100 tablets)',
    'Morphine 10mg/ml (10ml vial)',
    'Disposable Syringes 10ml (100 pack)',
    'Sterile Gauze Pads 4x4 (200 pack)',
    'Blood Collection Tubes (100 pack)'
  ];

  useEffect(() => {
    fetchTransferHistory();
  }, []);

  const fetchTransferHistory = async () => {
    try {
      const response = await fetch('/api/v2/transfers/history');
      if (response.ok) {
        const data = await response.json();
        setTransferHistory(data.transfers || []);
      }
    } catch (error) {
      console.error('Error fetching transfer history:', error);
    }
  };

  const checkSurplusStock = async (itemName) => {
    if (!itemName) return;
    
    try {
      setLoading(true);
      const response = await fetch(`/api/v2/transfers/surplus/${encodeURIComponent(itemName)}?required_quantity=${transferForm.quantity || 1}`);
      if (response.ok) {
        const data = await response.json();
        setSurplusData(data);
      }
    } catch (error) {
      console.error('Error checking surplus:', error);
    } finally {
      setLoading(false);
    }
  };

  const executeTransfer = async () => {
    if (!transferForm.itemName || !transferForm.fromDepartment || !transferForm.toDepartment || !transferForm.quantity) {
      setNotification({ type: 'error', message: 'Please fill in all required fields' });
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('/api/v2/transfers/inter-department', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_name: transferForm.itemName,
          from_department: transferForm.fromDepartment,
          to_department: transferForm.toDepartment,
          quantity: parseInt(transferForm.quantity),
          reason: transferForm.reason
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        setNotification({ type: 'success', message: `Transfer completed successfully! ID: ${result.transfer_id}` });
        setTransferForm({ itemName: '', fromDepartment: '', toDepartment: '', quantity: '', reason: '' });
        setSurplusData({});
        fetchTransferHistory();
      } else {
        setNotification({ type: 'error', message: result.message });
      }
    } catch (error) {
      setNotification({ type: 'error', message: 'Error executing transfer' });
      console.error('Error executing transfer:', error);
    } finally {
      setLoading(false);
    }
  };

  const triggerAutonomousCheck = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v2/transfers/autonomous-check', {
        method: 'POST'
      });
      
      if (response.ok) {
        const result = await response.json();
        setNotification({ 
          type: 'success', 
          message: `Autonomous check completed. ${result.count} transfers executed.` 
        });
        fetchTransferHistory();
      }
    } catch (error) {
      setNotification({ type: 'error', message: 'Error triggering autonomous check' });
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <ArrowLeftRight className="mr-3 h-8 w-8 text-blue-600" />
              Inter-Departmental Transfer Management
            </h1>
            <p className="text-gray-600 mt-2">Manage inventory transfers between hospital departments</p>
          </div>
          <button
            onClick={triggerAutonomousCheck}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50"
          >
            <TrendingUp className="h-4 w-4" />
            <span>Run Autonomous Check</span>
          </button>
        </div>
      </div>

      {/* Notification */}
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

      {/* Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'create', name: 'Create Transfer', icon: Package },
              { id: 'history', name: 'Transfer History', icon: Clock },
              { id: 'surplus', name: 'Surplus Stock', icon: Search }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'create' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Create New Transfer</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Transfer Form */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Item Name</label>
                <select
                  value={transferForm.itemName}
                  onChange={(e) => {
                    setTransferForm({...transferForm, itemName: e.target.value});
                    checkSurplusStock(e.target.value);
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select an item...</option>
                  {commonItems.map(item => (
                    <option key={item} value={item}>{item}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">From Department</label>
                  <select
                    value={transferForm.fromDepartment}
                    onChange={(e) => setTransferForm({...transferForm, fromDepartment: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select department...</option>
                    {departments.map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">To Department</label>
                  <select
                    value={transferForm.toDepartment}
                    onChange={(e) => setTransferForm({...transferForm, toDepartment: e.target.value})}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select department...</option>
                    {departments.filter(dept => dept !== transferForm.fromDepartment).map(dept => (
                      <option key={dept} value={dept}>{dept}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                <input
                  type="number"
                  value={transferForm.quantity}
                  onChange={(e) => {
                    setTransferForm({...transferForm, quantity: e.target.value});
                    if (transferForm.itemName) checkSurplusStock(transferForm.itemName);
                  }}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter quantity"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Reason</label>
                <textarea
                  value={transferForm.reason}
                  onChange={(e) => setTransferForm({...transferForm, reason: e.target.value})}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter reason for transfer"
                  rows="3"
                />
              </div>

              <button
                onClick={executeTransfer}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                <ArrowLeftRight className="h-4 w-4" />
                <span>{loading ? 'Processing...' : 'Execute Transfer'}</span>
              </button>
            </div>

            {/* Surplus Information */}
            <div>
              <h3 className="text-lg font-medium mb-4">Available Surplus Stock</h3>
              {surplusData.surplus_departments && surplusData.surplus_departments.length > 0 ? (
                <div className="space-y-3">
                  {surplusData.surplus_departments.map((dept, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Building className="h-4 w-4 text-gray-500" />
                          <span className="font-medium">{dept.department}</span>
                        </div>
                        <span className="text-sm text-gray-600">
                          {dept.available_stock} available
                        </span>
                      </div>
                      <div className="mt-2 text-sm text-gray-600">
                        Can transfer: <span className="font-medium text-green-600">{dept.can_transfer} units</span>
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        Surplus: {dept.surplus} units above minimum
                      </div>
                    </div>
                  ))}
                </div>
              ) : transferForm.itemName ? (
                <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
                  <p className="text-yellow-800">No surplus stock available for this item</p>
                </div>
              ) : (
                <div className="p-4 border border-gray-200 rounded-lg">
                  <p className="text-gray-500">Select an item to see surplus availability</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'history' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Transfer History</h2>
          
          {transferHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Transfer ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Item
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      From → To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transferHistory.map((transfer) => (
                    <tr key={transfer.transfer_id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {transfer.transfer_id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {transfer.item_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center space-x-2">
                          <span>{transfer.from_department}</span>
                          <ArrowLeftRight className="h-3 w-3 text-gray-400" />
                          <span>{transfer.to_department}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {transfer.quantity}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          transfer.status === 'completed' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {transfer.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatTimestamp(transfer.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8">
              <Clock className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No transfers yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Transfer history will appear here once transfers are completed.
              </p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'surplus' && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-xl font-semibold mb-4">Check Surplus Stock</h2>
          <p className="text-gray-600 mb-6">
            Search for available surplus stock across all departments for any item.
          </p>
          
          <div className="max-w-md">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Item</label>
            <select
              onChange={(e) => checkSurplusStock(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose an item to check...</option>
              {commonItems.map(item => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </div>

          {surplusData.surplus_departments && (
            <div className="mt-6">
              <h3 className="text-lg font-medium mb-4">
                Surplus Stock for: {surplusData.item_name}
              </h3>
              
              {surplusData.surplus_departments.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {surplusData.surplus_departments.map((dept, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{dept.department}</h4>
                        <span className="text-sm text-gray-500">{dept.available_stock} total</span>
                      </div>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Can transfer:</span>
                          <span className="font-medium text-green-600">{dept.can_transfer}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Surplus:</span>
                          <span className="text-blue-600">{dept.surplus}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Minimum:</span>
                          <span className="text-gray-500">{dept.min_threshold}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg">
                  <p className="text-yellow-800">No departments have surplus stock for this item</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TransferManagement;
