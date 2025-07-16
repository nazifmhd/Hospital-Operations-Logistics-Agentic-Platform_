import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  DocumentTextIcon,
  TruckIcon,
  UserGroupIcon,
  PlusIcon
} from '@heroicons/react/24/outline';

export default function WorkflowAutomation() {
  // State management
  const [activeTab, setActiveTab] = useState('approvals');
  const [loading, setLoading] = useState(true);
  const [workflowStatus, setWorkflowStatus] = useState(null);

  // Approval Requests
  const [approvals, setApprovals] = useState([]);
  const [approvalForm, setApprovalForm] = useState({
    request_type: 'purchase_order',
    requester_id: 'admin001',
    amount: '',
    justification: '',
    item_details: { item_id: '', quantity: '', description: '' }
  });

  // Purchase Orders  
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [poForm, setPoForm] = useState({
    approval_request_id: '',
    supplier_id: ''
  });

  // Suppliers
  const [suppliers, setSuppliers] = useState([]);
  const [supplierForm, setSupplierForm] = useState({
    name: '',
    contact_person: '',
    email: '',
    phone: '',
    address: '',
    tax_id: ''
  });

  // Analytics
  const [analytics, setAnalytics] = useState(null);

  // Auto Approval Service State
  const [autoApprovalStatus, setAutoApprovalStatus] = useState(null);
  const [monitoredInventory, setMonitoredInventory] = useState([]);
  const [autoApprovalConfig, setAutoApprovalConfig] = useState({
    check_interval_minutes: 30,
    emergency_threshold_multiplier: 0.3,
    batch_approval_window_hours: 4,
    max_auto_amount: 5000.0
  });

  // Fetch auto approval data - defined first
  const fetchAutoApprovalData = useCallback(async () => {
    try {
      // Use the main workflow status endpoint which contains auto-approval data
      const statusRes = await axios.get('http://localhost:8000/api/v2/workflow/status');
      
      setAutoApprovalStatus(statusRes.data.auto_approval_service);
      // Use the inventory endpoint to get monitored items
      const inventoryRes = await axios.get('http://localhost:8000/api/v2/inventory');
      setMonitoredInventory(inventoryRes.data.inventory || []);
    } catch (error) {
      console.error('Error fetching auto approval data:', error);
    }
  }, []);

  const fetchAllData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Check workflow status first - using full backend URL for reliability
      const statusResponse = await axios.get('http://localhost:8000/api/v2/workflow/status');
      setWorkflowStatus(statusResponse.data);

      if (statusResponse.data.workflow_available) {
        // Fetch all workflow data with full backend URLs
        const [approvalsRes, posRes, suppliersRes, analyticsRes] = await Promise.all([
          axios.get('http://localhost:8000/api/v2/workflow/approval/all'),
          axios.get('http://localhost:8000/api/v2/workflow/purchase_order/all'),
          axios.get('http://localhost:8000/api/v2/workflow/supplier/all'),
          axios.get('http://localhost:8000/api/v2/workflow/analytics/dashboard')
        ]);

        setApprovals(approvalsRes.data.approvals || []);
        setPurchaseOrders(posRes.data.purchase_orders || []);
        setSuppliers(suppliersRes.data.suppliers || []);
        setAnalytics(analyticsRes.data.analytics || {});
        
        // Fetch auto approval data
        await fetchAutoApprovalData();
      }
    } catch (error) {
      console.error('Error fetching workflow data:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchAutoApprovalData]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Toggle auto approval service
  const toggleAutoApproval = async () => {
    try {
      // Note: This system is running in full autonomous mode
      alert('System is running in autonomous mode. Auto-approval is permanently enabled.');
    } catch (error) {
      console.error('Error toggling auto approval:', error);
      alert('Error toggling auto approval service');
    }
  };

  // Trigger manual inventory check
  const triggerManualCheck = async () => {
    try {
      // The system automatically checks every 5 minutes
      alert('System automatically checks inventory every 5 minutes. Manual check not needed.');
    } catch (error) {
      console.error('Error triggering manual check:', error);
      alert('Error triggering manual check');
    }
  };

  // Update auto approval configuration
  const updateAutoApprovalConfig = async () => {
    try {
      await axios.post('http://localhost:8000/api/v2/workflow/auto-approval/config', autoApprovalConfig);
      await fetchAutoApprovalData();
      alert('Configuration updated successfully');
    } catch (error) {
      console.error('Error updating config:', error);
      alert('Error updating configuration');
    }
  };

  // Submit Approval Request
  const submitApproval = async () => {
    try {
      const payload = {
        request_type: approvalForm.request_type,
        requester_id: approvalForm.requester_id,
        item_details: approvalForm.item_details,
        amount: parseFloat(approvalForm.amount),
        justification: approvalForm.justification
      };

      const response = await axios.post('http://localhost:8000/api/v2/workflow/approval/submit', payload);
      setApprovals([...approvals, response.data]);
      
      // Reset form
      setApprovalForm({
        request_type: 'purchase_order',
        requester_id: 'admin001',
        amount: '',
        justification: '',
        item_details: { item_id: '', quantity: '', description: '' }
      });

      alert('Approval request submitted successfully!');
    } catch (error) {
      console.error('Error submitting approval:', error);
      alert('Error submitting approval request');
    }
  };

  // Process Approval Action
  const processApproval = async (approvalId, action, comments = '') => {
    try {
      await axios.post(`http://localhost:8000/api/v2/workflow/approval/${approvalId}/demo-action`, {
        action,
        comments
      });
      
      // Refresh approvals
      const response = await axios.get('/api/v2/workflow/approval/all');
      setApprovals(response.data.approvals || []);
      
      alert(`Approval ${action}ed successfully!`);
    } catch (error) {
      console.error('Error processing approval:', error);
      alert('Error processing approval');
    }
  };

  // Create Purchase Order
  const createPO = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/v2/workflow/purchase_order/create', poForm);
      setPurchaseOrders([...purchaseOrders, response.data]);
      
      // Reset form
      setPoForm({ approval_request_id: '', supplier_id: '' });
      alert('Purchase order created successfully!');
    } catch (error) {
      console.error('Error creating PO:', error);
      alert('Error creating purchase order');
    }
  };

  // Add Supplier
  const addSupplier = async () => {
    try {
      const response = await axios.post('http://localhost:8000/api/v2/workflow/supplier/add', supplierForm);
      setSuppliers([...suppliers, response.data]);
      
      // Reset form
      setSupplierForm({
        name: '',
        contact_person: '',
        email: '',
        phone: '',
        address: '',
        tax_id: ''
      });
      
      alert('Supplier added successfully!');
    } catch (error) {
      console.error('Error adding supplier:', error);
      alert('Error adding supplier');
    }
  };

  // Status badge component
  const StatusBadge = ({ status }) => {
    const statusClasses = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      draft: 'bg-gray-100 text-gray-800',
      submitted: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!workflowStatus?.workflow_available) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">Workflow Automation Unavailable</h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>The workflow automation engine is not available. Please check the backend configuration.</p>
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
          <h1 className="text-2xl font-bold text-gray-900">Workflow Automation</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage approval processes, purchase orders, and supplier integration
          </p>
        </div>
      </div>

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <DocumentTextIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Total Approvals</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {analytics.approval_metrics?.total_requests || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <TruckIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Purchase Orders</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {analytics.po_metrics?.total_pos || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <UserGroupIcon className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Active Suppliers</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {analytics.supplier_metrics?.active_suppliers || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircleIcon className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">Approval Rate</dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {((analytics.approval_metrics?.approval_rate || 0) * 100).toFixed(1)}%
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white shadow rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex">
            {[
              { id: 'approvals', name: 'Approval Requests', icon: DocumentTextIcon },
              { id: 'purchase_orders', name: 'Purchase Orders', icon: TruckIcon },
              { id: 'suppliers', name: 'Suppliers', icon: UserGroupIcon },
              { id: 'auto_approval', name: 'Auto Approval', icon: CheckCircleIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group inline-flex items-center py-4 px-6 border-b-2 font-medium text-sm ${
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
          {/* Approval Requests Tab */}
          {activeTab === 'approvals' && (
            <div className="space-y-6">
              {/* Create Approval Form */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Submit Approval Request</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Request Type</label>
                    <select
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={approvalForm.request_type}
                      onChange={(e) => setApprovalForm({...approvalForm, request_type: e.target.value})}
                    >
                      <option value="purchase_order">Purchase Order</option>
                      <option value="inventory_transfer">Inventory Transfer</option>
                      <option value="budget_request">Budget Request</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Amount ($)</label>
                    <input
                      type="number"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={approvalForm.amount}
                      onChange={(e) => setApprovalForm({...approvalForm, amount: e.target.value})}
                      placeholder="0.00"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700">Justification</label>
                    <textarea
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      rows={3}
                      value={approvalForm.justification}
                      onChange={(e) => setApprovalForm({...approvalForm, justification: e.target.value})}
                      placeholder="Provide justification for this request..."
                    />
                  </div>
                  <div className="md:col-span-2">
                    <button
                      onClick={submitApproval}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                      Submit Request
                    </button>
                  </div>
                </div>
              </div>

              {/* Approvals List */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Approval Requests</h3>
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Approver</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {approvals.map((approval) => (
                        <tr key={approval.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {approval.id}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {approval.request_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${approval.amount?.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <StatusBadge status={approval.status} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {approval.current_approver || 'Completed'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                            {approval.status === 'pending' && (
                              <>
                                <button
                                  onClick={() => processApproval(approval.id, 'approve')}
                                  className="text-green-600 hover:text-green-900"
                                >
                                  <CheckCircleIcon className="h-5 w-5" />
                                </button>
                                <button
                                  onClick={() => processApproval(approval.id, 'reject')}
                                  className="text-red-600 hover:text-red-900"
                                >
                                  <XCircleIcon className="h-5 w-5" />
                                </button>
                              </>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Purchase Orders Tab */}
          {activeTab === 'purchase_orders' && (
            <div className="space-y-6">
              {/* Create PO Form */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Create Purchase Order</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Approval Request ID</label>
                    <select
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={poForm.approval_request_id}
                      onChange={(e) => setPoForm({...poForm, approval_request_id: e.target.value})}
                    >
                      <option value="">Select approved request...</option>
                      {approvals.filter(a => a.status === 'approved').map(approval => (
                        <option key={approval.id} value={approval.id}>{approval.id}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Supplier</label>
                    <select
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={poForm.supplier_id}
                      onChange={(e) => setPoForm({...poForm, supplier_id: e.target.value})}
                    >
                      <option value="">Select supplier...</option>
                      {suppliers.filter(s => s.status === 'active').map(supplier => (
                        <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <button
                      onClick={createPO}
                      disabled={!poForm.approval_request_id || !poForm.supplier_id}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                      Create Purchase Order
                    </button>
                  </div>
                </div>
              </div>

              {/* PO List */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Purchase Orders</h3>
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PO Number</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Supplier</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {purchaseOrders.map((po) => (
                        <tr key={po.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {po.po_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {suppliers.find(s => s.id === po.supplier_id)?.name || 'Unknown'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            ${po.total_amount?.toFixed(2)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <StatusBadge status={po.status} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(po.created_at).toLocaleDateString()}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Suppliers Tab */}
          {activeTab === 'suppliers' && (
            <div className="space-y-6">
              {/* Add Supplier Form */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Supplier</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Company Name</label>
                    <input
                      type="text"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.name}
                      onChange={(e) => setSupplierForm({...supplierForm, name: e.target.value})}
                      placeholder="Supplier Company Name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Contact Person</label>
                    <input
                      type="text"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.contact_person}
                      onChange={(e) => setSupplierForm({...supplierForm, contact_person: e.target.value})}
                      placeholder="Contact Person Name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <input
                      type="email"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.email}
                      onChange={(e) => setSupplierForm({...supplierForm, email: e.target.value})}
                      placeholder="supplier@company.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                    <input
                      type="tel"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.phone}
                      onChange={(e) => setSupplierForm({...supplierForm, phone: e.target.value})}
                      placeholder="+1-555-0123"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Address</label>
                    <input
                      type="text"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.address}
                      onChange={(e) => setSupplierForm({...supplierForm, address: e.target.value})}
                      placeholder="Company Address"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Tax ID</label>
                    <input
                      type="text"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                      value={supplierForm.tax_id}
                      onChange={(e) => setSupplierForm({...supplierForm, tax_id: e.target.value})}
                      placeholder="Tax ID Number"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <button
                      onClick={addSupplier}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
                      Add Supplier
                    </button>
                  </div>
                </div>
              </div>

              {/* Suppliers List */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Suppliers</h3>
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Lead Time</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {suppliers.map((supplier) => (
                        <tr key={supplier.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {supplier.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {supplier.contact_person}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {supplier.email}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <StatusBadge status={supplier.status} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {supplier.lead_time_days} days
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Auto Approval Tab */}
          {activeTab === 'auto_approval' && (
            <div className="space-y-6">
              {/* Auto Approval Status Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Auto Approval Service Status
                  </h3>
                  
                  {autoApprovalStatus && (
                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
                      <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <CheckCircleIcon className={`h-6 w-6 ${autoApprovalStatus.enabled ? 'text-green-400' : 'text-gray-400'}`} />
                            </div>
                            <div className="ml-5 w-0 flex-1">
                              <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Service Status</dt>
                                <dd className={`text-lg font-medium ${autoApprovalStatus.enabled ? 'text-green-900' : 'text-gray-900'}`}>
                                  {autoApprovalStatus.enabled ? 'Enabled' : 'Disabled'}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <XCircleIcon className="h-6 w-6 text-orange-400" />
                            </div>
                            <div className="ml-5 w-0 flex-1">
                              <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Low Stock Items</dt>
                                <dd className="text-lg font-medium text-orange-900">
                                  {autoApprovalStatus.low_stock_items || 0}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="bg-gray-50 overflow-hidden shadow rounded-lg">
                        <div className="p-5">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <XCircleIcon className="h-6 w-6 text-red-400" />
                            </div>
                            <div className="ml-5 w-0 flex-1">
                              <dl>
                                <dt className="text-sm font-medium text-gray-500 truncate">Emergency Items</dt>
                                <dd className="text-lg font-medium text-red-900">
                                  {autoApprovalStatus.emergency_items || 0}
                                </dd>
                              </dl>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Control Buttons */}
                  <div className="mt-6 flex space-x-3">
                    <button
                      onClick={toggleAutoApproval}
                      className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                        autoApprovalStatus?.enabled 
                          ? 'bg-red-600 hover:bg-red-700' 
                          : 'bg-green-600 hover:bg-green-700'
                      } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                    >
                      {autoApprovalStatus?.enabled ? 'Disable' : 'Enable'} Auto Approval
                    </button>
                    
                    <button
                      onClick={triggerManualCheck}
                      className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Trigger Manual Check
                    </button>
                  </div>
                </div>
              </div>

              {/* Configuration Card */}
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                    Configuration Settings
                  </h3>
                  
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Check Interval (minutes)
                      </label>
                      <input
                        type="number"
                        value={autoApprovalConfig.check_interval_minutes}
                        onChange={(e) => setAutoApprovalConfig({
                          ...autoApprovalConfig,
                          check_interval_minutes: parseInt(e.target.value)
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Emergency Threshold (%)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={autoApprovalConfig.emergency_threshold_multiplier * 100}
                        onChange={(e) => setAutoApprovalConfig({
                          ...autoApprovalConfig,
                          emergency_threshold_multiplier: parseFloat(e.target.value) / 100
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Batch Window (hours)
                      </label>
                      <input
                        type="number"
                        value={autoApprovalConfig.batch_approval_window_hours}
                        onChange={(e) => setAutoApprovalConfig({
                          ...autoApprovalConfig,
                          batch_approval_window_hours: parseInt(e.target.value)
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Max Auto Amount ($)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={autoApprovalConfig.max_auto_amount}
                        onChange={(e) => setAutoApprovalConfig({
                          ...autoApprovalConfig,
                          max_auto_amount: parseFloat(e.target.value)
                        })}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-6">
                    <button
                      onClick={updateAutoApprovalConfig}
                      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Update Configuration
                    </button>
                  </div>
                </div>
              </div>

              {/* Monitored Inventory Table */}
              <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Monitored Inventory Items
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    Items being monitored for automatic approval request generation
                  </p>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Item
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Location
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Current Stock
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Minimum
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Unit Price
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {monitoredInventory.map((item) => (
                        <tr key={item.item_id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{item.name}</div>
                            <div className="text-sm text-gray-500">{item.item_id}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.location}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.current_quantity}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            {item.minimum_threshold}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              item.is_emergency 
                                ? 'bg-red-100 text-red-800'
                                : item.is_low_stock 
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-green-100 text-green-800'
                            }`}>
                              {item.is_emergency ? 'Emergency' : item.is_low_stock ? 'Low Stock' : 'Normal'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                            ${item.unit_price.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
