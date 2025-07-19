import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentTextIcon,
  TruckIcon,
  UserGroupIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  CogIcon,
  BoltIcon
} from '@heroicons/react/24/outline';

export default function AutonomousWorkflow() {
  // State management
  const [activeTab, setActiveTab] = useState('pending_orders');
  const [loading, setLoading] = useState(true);
  const [workflowStatus, setWorkflowStatus] = useState(null);

  // Autonomous System State
  const [autonomousSystem, setAutonomousSystem] = useState({
    enabled: true,
    last_check: null,
    items_monitored: 0,
    pending_orders: 0,
    transfers_today: 0,
    orders_today: 0
  });
  
  // Workflow Data
  const [pendingOrders, setPendingOrders] = useState([]);
  const [transferHistory, setTransferHistory] = useState([]);
  const [orderHistory, setOrderHistory] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  
  // Order Management
  const [selectedOrder, setSelectedOrder] = useState(null);

  // Fetch autonomous workflow data
  const fetchAutonomousData = useCallback(async () => {
    try {
      // Get supply agent status and autonomous system info
      const [agentRes, ordersRes, transfersRes] = await Promise.all([
        axios.get('http://localhost:8000/api/v2/supply-agent/status'),
        axios.get('http://localhost:8000/api/v2/workflow/purchase_order/all'),
        axios.get('http://localhost:8000/api/v3/transfers')
      ]);

      // Extract autonomous system status
      const agentData = agentRes.data;
      setAutonomousSystem({
        enabled: agentData.agent_status === 'running',
        last_check: agentData.last_check || new Date().toISOString(),
        items_monitored: agentData.total_items || 0,
        pending_orders: agentData.pending_orders || 0,
        transfers_today: 0,
        orders_today: agentData.orders_today || 0
      });

      // Get pending orders that need approval  
      const allOrders = ordersRes.data.purchase_orders || [];
      const pending = allOrders.filter(order => 
        order.status === 'pending' || 
        order.status === 'awaiting_approval' ||
        order.status === 'submitted' ||
        order.approval_status === 'pending'
      );
      setPendingOrders(pending);

      // Get recent transfer history
      const transfers = transfersRes.data.value || transfersRes.data.transfers || [];
      const today = new Date().toDateString();
      const todayTransfers = transfers.filter(t => 
        new Date(t.timestamp || t.created_at).toDateString() === today
      );
      setTransferHistory(transfers.slice(0, 20));
      
      // Update transfers count
      setAutonomousSystem(prev => ({
        ...prev,
        transfers_today: todayTransfers.length
      }));

      // Get order history (approved/completed orders)
      const completedOrders = allOrders
        .filter(order => 
          order.status === 'approved' || 
          order.status === 'completed' ||
          order.status === 'delivered' ||
          order.approval_status === 'approved'
        )
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 20);
      setOrderHistory(completedOrders);

    } catch (error) {
      console.error('Error fetching autonomous data:', error);
      setAutonomousSystem({
        enabled: false,
        last_check: new Date().toISOString(),
        items_monitored: 0,
        pending_orders: 0,
        transfers_today: 0,
        orders_today: 0
      });
      setPendingOrders([]);
      setTransferHistory([]);
      setOrderHistory([]);
    }
  }, []);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Check workflow status first
      const statusResponse = await axios.get('http://localhost:8000/api/v2/workflow/status');
      setWorkflowStatus(statusResponse.data);

      if (statusResponse.data.workflow_available) {
        // Fetch autonomous data
        await fetchAutonomousData();
        
        // Fetch suppliers
        const suppliersRes = await axios.get('http://localhost:8000/api/v2/workflow/supplier/all');
        setSuppliers(suppliersRes.data.suppliers || []);
      }
    } catch (error) {
      console.error('Error fetching workflow data:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchAutonomousData]);

  useEffect(() => {
    fetchAllData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchAutonomousData, 30000);
    return () => clearInterval(interval);
  }, [fetchAllData, fetchAutonomousData]);

  // Approve order with supplier assignment
  const approveOrder = async (orderId, supplierId, notes = '') => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v2/workflow/purchase_order/${orderId}/approve`, {
        supplier_id: supplierId,
        notes: notes,
        approved_by: 'Supply Manager',
        approval_date: new Date().toISOString()
      });
      
      if (response.data.success) {
        alert('Order approved successfully! Database updated.');
        await fetchAutonomousData();
      }
    } catch (error) {
      console.error('Error approving order:', error);
      alert('Error approving order');
    }
  };

  const rejectOrder = async (orderId, reason = '') => {
    try {
      const response = await axios.post(`http://localhost:8000/api/v2/workflow/purchase_order/${orderId}/reject`, {
        reason: reason,
        rejected_by: 'Supply Manager',
        rejection_date: new Date().toISOString()
      });
      
      if (response.data.success) {
        alert('Order rejected. Database updated.');
        await fetchAutonomousData();
      }
    } catch (error) {
      console.error('Error rejecting order:', error);
      alert('Error rejecting order');
    }
  };

  const forceSystemCheck = async () => {
    try {
      await axios.post('http://localhost:8000/api/v2/supply-agent/force-check');
      alert('System check initiated - transfers and orders will be processed automatically');
      await fetchAutonomousData();
    } catch (error) {
      console.error('Error forcing system check:', error);
      alert('Error forcing system check');
    }
  };

  // Status badge components
  const StatusBadge = ({ status }) => {
    const getStatusColor = (status) => {
      switch (status?.toLowerCase()) {
        case 'pending':
        case 'awaiting_approval':
          return 'bg-yellow-100 text-yellow-800';
        case 'approved':
          return 'bg-green-100 text-green-800';
        case 'rejected':
          return 'bg-red-100 text-red-800';
        case 'completed':
          return 'bg-blue-100 text-blue-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
        {status}
      </span>
    );
  };

  const PriorityBadge = ({ priority }) => {
    const getPriorityColor = (priority) => {
      switch (priority?.toLowerCase()) {
        case 'emergency':
        case 'urgent':
          return 'bg-red-100 text-red-800';
        case 'high':
          return 'bg-orange-100 text-orange-800';
        case 'normal':
          return 'bg-green-100 text-green-800';
        case 'low':
          return 'bg-gray-100 text-gray-800';
        default:
          return 'bg-blue-100 text-blue-800';
      }
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(priority)}`}>
        {priority || 'Normal'}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!workflowStatus?.workflow_available) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <XCircleIcon className="h-5 w-5 text-red-400" />
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Workflow System Unavailable</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>The workflow automation system is currently unavailable. Please check system status.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">Supply Inventory Agent - Autonomous Workflow</h1>
          <p className="mt-1 text-sm text-gray-600">
            Automatic transfer management, supplier ordering, and approval workflow system
          </p>
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 overflow-hidden shadow rounded-lg">
          <div className="p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-blue-700 truncate">Location Instances</dt>
                  <dd className="text-lg font-medium text-blue-900">{autonomousSystem.items_monitored}</dd>
                  <dd className="text-xs text-blue-600">30 unique items across locations</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 overflow-hidden shadow rounded-lg">
          <div className="p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-6 w-6 text-yellow-400" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-yellow-700 truncate">Pending Orders</dt>
                  <dd className="text-lg font-medium text-yellow-900">{pendingOrders.length}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-green-50 overflow-hidden shadow rounded-lg">
          <div className="p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TruckIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-green-700 truncate">Transfers Today</dt>
                  <dd className="text-lg font-medium text-green-900">{autonomousSystem.transfers_today}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 overflow-hidden shadow rounded-lg">
          <div className="p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-6 w-6 text-purple-400" />
              </div>
              <div className="ml-3 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-purple-700 truncate">Orders Today</dt>
                  <dd className="text-lg font-medium text-purple-900">{autonomousSystem.orders_today}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex flex-wrap">
            {[
              { id: 'pending_orders', name: 'Pending Orders', icon: ExclamationTriangleIcon },
              { id: 'transfer_history', name: 'Transfer History', icon: ArrowPathIcon },
              { id: 'order_history', name: 'Order History', icon: ClockIcon },
              { id: 'system_control', name: 'System Control', icon: CogIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-4 px-4 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className={`-ml-0.5 mr-2 h-5 w-5 ${
                  activeTab === tab.id ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
                }`} />
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Pending Orders Tab */}
          {activeTab === 'pending_orders' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900">Orders Awaiting Approval</h3>
                <p className="text-sm text-gray-500">
                  {pendingOrders.length} orders need supplier assignment and approval
                </p>
              </div>

              {pendingOrders.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No Pending Orders</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    All orders are processed. The system will automatically create new orders when needed.
                  </p>
                </div>
              ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {pendingOrders.map((order) => (
                      <li key={order.id}>
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center">
                              <div className="flex-shrink-0">
                                <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                              </div>
                              <div className="ml-4">
                                <div className="text-sm font-medium text-gray-900">
                                  Order #{order.po_number || order.id}
                                </div>
                                <div className="text-sm text-gray-500">
                                  {order.item_name || order.items?.[0]?.name || 'Multiple Items'} 
                                  {order.quantity && ` - Qty: ${order.quantity}`}
                                  {order.items?.[0]?.quantity && ` - Qty: ${order.items[0].quantity}`}
                                </div>
                                <div className="text-xs text-gray-400">
                                  Created: {new Date(order.created_at).toLocaleDateString()}
                                </div>
                                {order.reason && (
                                  <div className="text-xs text-blue-600">
                                    Reason: {order.reason}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center space-x-4">
                              <StatusBadge status={order.status || order.approval_status} />
                              <PriorityBadge priority={order.priority} />
                              <div className="flex space-x-2">
                                <select 
                                  className="text-sm border-gray-300 rounded-md"
                                  onChange={(e) => {
                                    if (e.target.value) {
                                      const notes = prompt('Add approval notes (optional):');
                                      approveOrder(order.id, e.target.value, notes || '');
                                    }
                                  }}
                                  defaultValue=""
                                >
                                  <option value="">Select Supplier</option>
                                  {suppliers.map(supplier => (
                                    <option key={supplier.id} value={supplier.id}>
                                      {supplier.name}
                                    </option>
                                  ))}
                                </select>
                                <button
                                  onClick={() => {
                                    const reason = prompt('Rejection reason:');
                                    if (reason) rejectOrder(order.id, reason);
                                  }}
                                  className="inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                                >
                                  Reject
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Transfer History Tab */}
          {activeTab === 'transfer_history' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Automatic Transfer History</h3>
              <p className="text-sm text-gray-600">
                Items automatically transferred between locations to optimize stock levels
              </p>

              {transferHistory.length === 0 ? (
                <div className="text-center py-8">
                  <ArrowPathIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No Transfer History</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Transfer history will appear here when the system moves items between locations.
                  </p>
                </div>
              ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {transferHistory.map((transfer) => (
                      <li key={transfer.transfer_id || transfer.id} className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {transfer.item_name} (Qty: {transfer.quantity})
                            </div>
                            <div className="text-sm text-gray-500">
                              {transfer.from_location_name || transfer.from_location} → {transfer.to_location_name || transfer.to_location}
                            </div>
                            <div className="text-xs text-gray-400">
                              {new Date(transfer.timestamp || transfer.created_at).toLocaleString()}
                            </div>
                            {transfer.reason && (
                              <div className="text-xs text-gray-500 mt-1">
                                Reason: {transfer.reason}
                              </div>
                            )}
                          </div>
                          <StatusBadge status={transfer.status} />
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Order History Tab */}
          {activeTab === 'order_history' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Approved Order History</h3>
              <p className="text-sm text-gray-600">
                Orders that have been approved and sent to suppliers
              </p>

              {orderHistory.length === 0 ? (
                <div className="text-center py-8">
                  <ClockIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No Order History</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Approved orders will appear here.
                  </p>
                </div>
              ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {orderHistory.map((order) => (
                      <li key={order.id} className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              Order #{order.po_number || order.id}
                            </div>
                            <div className="text-sm text-gray-500">
                              {order.item_name || order.items?.[0]?.name || 'Multiple Items'} 
                              {order.quantity && ` - Qty: ${order.quantity}`}
                              {order.items?.[0]?.quantity && ` - Qty: ${order.items[0].quantity}`}
                            </div>
                            <div className="text-xs text-gray-400">
                              Created: {new Date(order.created_at).toLocaleString()}
                            </div>
                            {order.approved_at && (
                              <div className="text-xs text-green-600">
                                Approved: {new Date(order.approved_at).toLocaleString()}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center space-x-2">
                            <StatusBadge status={order.status || order.approval_status} />
                            <span className="text-sm text-gray-500">
                              ${order.total_amount || order.amount || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* System Control Tab */}
          {activeTab === 'system_control' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium text-gray-900">Autonomous System Control</h3>
              
              <div className="bg-blue-50 rounded-lg p-6">
                <div className="flex items-center">
                  <BoltIcon className="h-6 w-6 text-blue-400" />
                  <div className="ml-3">
                    <h4 className="text-md font-medium text-blue-900">System Status</h4>
                    <p className="text-sm text-blue-700">
                      Status: <span className="font-medium">{autonomousSystem.enabled ? 'Running' : 'Stopped'}</span>
                    </p>
                    <p className="text-sm text-blue-700">
                      Last Check: {autonomousSystem.last_check ? new Date(autonomousSystem.last_check).toLocaleString() : 'Never'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-md font-medium text-gray-900 mb-4">Manual System Operations</h4>
                <div className="space-y-4">
                  <button
                    onClick={forceSystemCheck}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <ArrowPathIcon className="h-4 w-4 mr-2" />
                    Force System Check
                  </button>
                  <p className="text-sm text-gray-600">
                    Manually trigger inventory analysis for transfers and orders
                  </p>
                </div>
              </div>

              <div className="bg-green-50 rounded-lg p-6">
                <h4 className="text-md font-medium text-green-900 mb-2">How the System Works</h4>
                <div className="text-sm text-green-700 space-y-2">
                  <p>• <strong>Step 1:</strong> System detects low stock in any location</p>
                  <p>• <strong>Step 2:</strong> Checks if other locations have surplus stock</p>
                  <p>• <strong>Step 3:</strong> Automatically transfers between locations if possible</p>
                  <p>• <strong>Step 4:</strong> Creates supplier orders if no internal stock available</p>
                  <p>• <strong>Step 5:</strong> Presents orders here for supplier assignment and approval</p>
                  <p>• <strong>Step 6:</strong> Updates database automatically after approval</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
