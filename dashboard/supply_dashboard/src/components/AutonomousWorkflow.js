import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentTextIcon,
  TruckIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  CogIcon,
  BoltIcon,
  ShoppingCartIcon,
  ArrowsRightLeftIcon,
  BellIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';
import EnhancedNotificationPanel from './EnhancedNotificationPanel';

export default function AutonomousWorkflow() {
  // State management
  const [activeTab, setActiveTab] = useState('pending_approvals');
  const [loading, setLoading] = useState(true);

  // Autonomous System State
  const [autonomousStatus, setAutonomousStatus] = useState({
    autonomous_manager_active: false,
    database_connected: false,
    enhanced_agent_available: false,
    last_check: null,
    check_interval_minutes: 5,
    monitoring_enabled: false
  });
  
  // Workflow Data
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [autonomousTransfers, setAutonomousTransfers] = useState([]);
  const [autonomousPurchaseOrders, setAutonomousPurchaseOrders] = useState([]);
  const [autonomousNotifications, setAutonomousNotifications] = useState([]);

  // Fetch autonomous workflow data
  const fetchAutonomousData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Get autonomous system status and data
      const [statusRes, approvalsRes, transfersRes, ordersRes, notificationsRes] = await Promise.all([
        axios.get('http://localhost:8000/api/v2/workflow/autonomous/status'),
        axios.get('http://localhost:8000/api/v2/workflow/autonomous/pending-approvals'),
        axios.get('http://localhost:8000/api/v2/workflow/autonomous/transfers'),
        axios.get('http://localhost:8000/api/v2/workflow/autonomous/purchase-orders'),
        axios.get('http://localhost:8000/api/v2/workflow/autonomous/notifications')
      ]);

      if (statusRes.data.success) {
        setAutonomousStatus(statusRes.data.status);
      }

      if (approvalsRes.data.success) {
        setPendingApprovals(approvalsRes.data.approvals || []);
      }

      if (transfersRes.data.success) {
        setAutonomousTransfers(transfersRes.data.transfers || []);
      }

      if (ordersRes.data.success) {
        setAutonomousPurchaseOrders(ordersRes.data.purchase_orders || []);
      }

      if (notificationsRes.data.success) {
        setAutonomousNotifications(notificationsRes.data.notifications || []);
      }

    } catch (error) {
      console.error('Error fetching autonomous data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Approve a purchase order
  const approvePurchaseOrder = async (poId) => {
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v2/workflow/autonomous/approve/${poId}`,
        { approved_by: "user" }
      );

      if (response.data.success) {
        // Remove from pending approvals
        setPendingApprovals(prev => prev.filter(approval => approval.po_id !== poId));
        
        // Refresh data
        await fetchAutonomousData();
        
        alert(`Purchase order ${poId} approved successfully!`);
      } else {
        alert(`Failed to approve purchase order: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error approving purchase order:', error);
      alert('Error approving purchase order. Please try again.');
    }
  };

  // Force an autonomous system check
  const forceAutonomousCheck = async () => {
    try {
      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/v2/workflow/autonomous/force-check');
      
      if (response.data.success) {
        alert('Autonomous check completed successfully!');
        await fetchAutonomousData();
      } else {
        alert(`Force check failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error forcing autonomous check:', error);
      alert('Error forcing check. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Clear all autonomous notifications
  const clearAllNotifications = async () => {
    try {
      const confirmed = window.confirm('Are you sure you want to clear all notifications? This action cannot be undone.');
      if (!confirmed) return;

      setLoading(true);
      const response = await axios.post('http://localhost:8000/api/v2/workflow/autonomous/notifications/clear-all');
      
      if (response.data.success) {
        alert(`Successfully cleared ${response.data.cleared_count} notifications!`);
        await fetchAutonomousData(); // Refresh the data
      } else {
        alert(`Failed to clear notifications: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error clearing notifications:', error);
      alert('Error clearing notifications. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initialize data
  useEffect(() => {
    fetchAutonomousData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchAutonomousData, 30000);
    return () => clearInterval(interval);
  }, [fetchAutonomousData]);

  // Helper function to get priority badge
  const getPriorityBadge = (priority) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      normal: 'bg-blue-100 text-blue-800 border-blue-200',
      low: 'bg-gray-100 text-gray-800 border-gray-200'
    };
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${colors[priority] || colors.normal}`}>
        {priority?.toUpperCase() || 'NORMAL'}
      </span>
    );
  };

  // Helper function to format timestamp
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <BoltIcon className="h-8 w-8 text-blue-600 mr-3" />
              Autonomous Workflow Management
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Monitor and manage autonomous supply operations, transfers, and purchase order approvals
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={forceAutonomousCheck}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
            >
              <ArrowPathIcon className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Force Check
            </button>
            
            <div className="flex items-center">
              <div className={`h-3 w-3 rounded-full mr-2 ${autonomousStatus.autonomous_manager_active ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="text-sm font-medium text-gray-900">
                {autonomousStatus.autonomous_manager_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>

        {/* System Status Cards */}
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
            <div className="flex items-center">
              <BoltIcon className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-blue-900">Manager Status</p>
                <p className="text-lg font-semibold text-blue-700">
                  {autonomousStatus.autonomous_manager_active ? 'Running' : 'Stopped'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
            <div className="flex items-center">
              <ClockIcon className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-green-900">Last Check</p>
                <p className="text-lg font-semibold text-green-700">
                  {autonomousStatus.last_check ? 
                    new Date(autonomousStatus.last_check).toLocaleTimeString() : 
                    'Never'
                  }
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
            <div className="flex items-center">
              <DocumentTextIcon className="h-8 w-8 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-purple-900">Pending Approvals</p>
                <p className="text-lg font-semibold text-purple-700">
                  {pendingApprovals.length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
            <div className="flex items-center">
              <ArrowsRightLeftIcon className="h-8 w-8 text-orange-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-orange-900">Auto Transfers</p>
                <p className="text-lg font-semibold text-orange-700">
                  {autonomousTransfers.length}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'pending_approvals', name: 'Pending Approvals', icon: DocumentTextIcon, count: pendingApprovals.length },
              { id: 'autonomous_transfers', name: 'Auto Transfers', icon: ArrowsRightLeftIcon, count: autonomousTransfers.length },
              { id: 'purchase_orders', name: 'Purchase Orders', icon: ShoppingCartIcon, count: autonomousPurchaseOrders.length },
              { id: 'notifications', name: 'Notifications', icon: BellIcon, count: autonomousNotifications.length }
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    isActive
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
                >
                  <tab.icon className="h-5 w-5 mr-2" />
                  {tab.name}
                  {tab.count > 0 && (
                    <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      isActive ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {tab.count}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600">Loading autonomous workflow data...</span>
            </div>
          ) : (
            <>
              {/* Pending Approvals Tab */}
              {activeTab === 'pending_approvals' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Pending Purchase Order Approvals</h3>
                    <span className="text-sm text-gray-500">
                      {pendingApprovals.length} items requiring approval
                    </span>
                  </div>

                  {pendingApprovals.length === 0 ? (
                    <div className="text-center py-12">
                      <CheckCircleIcon className="mx-auto h-12 w-12 text-green-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No pending approvals</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        All autonomous purchase orders are up to date.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-white shadow overflow-hidden sm:rounded-md">
                      <ul className="divide-y divide-gray-200">
                        {pendingApprovals.map((approval, index) => {
                          const data = approval.data || {};
                          return (
                            <li key={approval.po_id || index} className="px-6 py-4">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  <div className="flex-shrink-0">
                                    <ShoppingCartIcon className="h-6 w-6 text-gray-400" />
                                  </div>
                                  <div className="ml-4">
                                    <div className="flex items-center">
                                      <p className="text-sm font-medium text-gray-900">
                                        {approval.po_id || 'Unknown PO'}
                                      </p>
                                      <span className="ml-2">
                                        {getPriorityBadge(approval.priority || data.priority)}
                                      </span>
                                    </div>
                                    <div className="mt-1">
                                      <p className="text-sm text-gray-600">
                                        Item: {data.item_name || data.item_id || 'Unknown Item'}
                                      </p>
                                      <p className="text-sm text-gray-600">
                                        Location: {data.location_id || 'Unknown'}
                                      </p>
                                      <p className="text-sm text-gray-600">
                                        Quantity: {data.quantity || 0} | 
                                        Amount: ${data.total_amount || 0}
                                      </p>
                                      <p className="text-sm text-gray-500">
                                        Reason: {data.reason || 'Autonomous reorder'}
                                      </p>
                                    </div>
                                  </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                  <button
                                    onClick={() => approvePurchaseOrder(approval.po_id)}
                                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                                  >
                                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                                    Approve
                                  </button>
                                </div>
                              </div>
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Autonomous Transfers Tab */}
              {activeTab === 'autonomous_transfers' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Autonomous Transfers</h3>
                    <span className="text-sm text-gray-500">
                      {autonomousTransfers.length} automatic transfers
                    </span>
                  </div>

                  {autonomousTransfers.length === 0 ? (
                    <div className="text-center py-12">
                      <TruckIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No autonomous transfers</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        No automatic transfers have been performed yet.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-white shadow overflow-hidden sm:rounded-md">
                      <ul className="divide-y divide-gray-200">
                        {autonomousTransfers.map((transfer, index) => (
                          <li key={transfer.transfer_id || index} className="px-6 py-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center">
                                <div className="flex-shrink-0">
                                  <ArrowsRightLeftIcon className="h-6 w-6 text-blue-400" />
                                </div>
                                <div className="ml-4">
                                  <div className="flex items-center">
                                    <p className="text-sm font-medium text-gray-900">
                                      {transfer.transfer_id}
                                    </p>
                                    <span className="ml-2">
                                      {getPriorityBadge(transfer.priority)}
                                    </span>
                                  </div>
                                  <div className="mt-1">
                                    <p className="text-sm text-gray-600">
                                      {transfer.from_location} → {transfer.to_location}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                      Item: {transfer.item_id} | Quantity: {transfer.quantity}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                      {formatTimestamp(transfer.created_at)}
                                    </p>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center">
                                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-green-100 text-green-800 border border-green-200">
                                  {transfer.status?.toUpperCase() || 'COMPLETED'}
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

              {/* Purchase Orders Tab */}
              {activeTab === 'purchase_orders' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-medium text-gray-900">Autonomous Purchase Orders</h3>
                    <span className="text-sm text-gray-500">
                      {autonomousPurchaseOrders.length} autonomous orders
                    </span>
                  </div>

                  {autonomousPurchaseOrders.length === 0 ? (
                    <div className="text-center py-12">
                      <ShoppingCartIcon className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No purchase orders</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        No autonomous purchase orders have been created yet.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-white shadow overflow-hidden sm:rounded-md">
                      <ul className="divide-y divide-gray-200">
                        {autonomousPurchaseOrders.map((order, index) => (
                          <li key={order.po_id || index} className="px-6 py-4">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center">
                                <div className="flex-shrink-0">
                                  <DocumentTextIcon className="h-6 w-6 text-purple-400" />
                                </div>
                                <div className="ml-4">
                                  <div className="flex items-center">
                                    <p className="text-sm font-medium text-gray-900">
                                      {order.po_id}
                                    </p>
                                    <span className="ml-2">
                                      {getPriorityBadge(order.priority)}
                                    </span>
                                  </div>
                                  <div className="mt-1">
                                    <p className="text-sm text-gray-600">
                                      {order.item_name} | Qty: {order.quantity} | ${order.total_amount}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                      Location: {order.location_id}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                      {formatTimestamp(order.created_at)}
                                    </p>
                                  </div>
                                </div>
                              </div>
                              <div className="flex items-center">
                                <span className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium border ${
                                  order.status === 'approved' 
                                    ? 'bg-green-100 text-green-800 border-green-200'
                                    : order.status === 'pending_approval'
                                    ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                                    : 'bg-gray-100 text-gray-800 border-gray-200'
                                }`}>
                                  {order.status?.toUpperCase().replace('_', ' ') || 'UNKNOWN'}
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

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="space-y-4">
                  <EnhancedNotificationPanel 
                    notifications={autonomousNotifications}
                    onMarkAsRead={(notificationId) => {
                      // Future implementation for marking as read
                      console.log('Mark as read:', notificationId);
                    }}
                    onClearAll={clearAllNotifications}
                    onRefresh={fetchAutonomousData}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
