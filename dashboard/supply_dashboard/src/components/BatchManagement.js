import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { 
  Package2, 
  Calendar, 
  AlertTriangle, 
  Plus,
  Search,
  Filter,
  Clock,
  TrendingUp,
  Archive,
  CheckCircle,
  XCircle,
  Eye
} from 'lucide-react';

const BatchManagement = () => {
  const { dashboardData, loading } = useSupplyData();
  const [batches, setBatches] = useState([]);
  const [expiringBatches, setExpiringBatches] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [filterExpiry, setFilterExpiry] = useState('ALL');
  const [showBatchModal, setShowBatchModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [newBatch, setNewBatch] = useState({
    item_id: '',
    batch_number: '',
    manufacturing_date: '',
    expiry_date: '',
    quantity: '',
    location_id: ''
  });

  useEffect(() => {
    // Use sample data for batches since batch tracking is not yet in shared context
    // This should be updated when batch data is added to the WebSocket stream
    initializeBatchData();
  }, []);

  const initializeBatchData = () => {
    // Use sample data for batches since batch tracking is not yet in shared context
    // This should be updated when batch data is added to the WebSocket stream
    try {
      let batchesData = [];
      let expiringData = [];

      // Provide sample batch data with proper status fields and varied expiry dates
      const today = new Date();
      batchesData = [
        {
          id: 'MED001_BTH001',
          batch_number: 'BTH001',
          item_id: 'MED001',
          item_name: 'Surgical Gloves',
          manufacturing_date: '2024-01-15',
          expiry_date: '2026-01-15', // Good - more than 90 days
          quantity: 500,
          location: 'Surgery',
          quality_status: 'active',
          supplier_id: 'SUP001',
          cost_per_unit: 12.50
        },
        {
          id: 'MED002_BTH002',
          batch_number: 'BTH002',
          item_id: 'MED002',
          item_name: 'Face Masks',
          manufacturing_date: '2024-02-01',
          expiry_date: '2025-08-15', // Expiring soon - within 30 days
          quantity: 1000,
          location: 'ICU',
          quality_status: 'active',
          supplier_id: 'SUP002',
          cost_per_unit: 8.75
        },
        {
          id: 'MED003_BTH003',
          batch_number: 'BTH003',
          item_id: 'MED003',
          item_name: 'Blood Collection Tubes',
          manufacturing_date: '2024-12-01',
          expiry_date: '2025-10-01', // Warning - 30-90 days
          quantity: 200,
          location: 'Laboratory',
          quality_status: 'active',
          supplier_id: 'SUP003',
          cost_per_unit: 15.25
        },
        {
          id: 'MED004_BTH004',
          batch_number: 'BTH004',
          item_id: 'MED004',
          item_name: 'IV Fluids',
          manufacturing_date: '2024-06-01',
          expiry_date: '2025-06-01',
          quantity: 150,
          location: 'ICU',
          quality_status: 'quarantine',
          supplier_id: 'SUP001',
          cost_per_unit: 22.00
        },
        {
          id: 'MED005_BTH005',
          batch_number: 'BTH005',
          item_id: 'MED005',
          item_name: 'Antibiotics',
          manufacturing_date: '2023-08-01',
          expiry_date: '2025-01-01', // Expired
          quantity: 75,
          location: 'Pharmacy',
          quality_status: 'active',
          supplier_id: 'SUP004',
          cost_per_unit: 45.00
        },
        {
          id: 'MED006_BTH006',
          batch_number: 'BTH006',
          item_id: 'MED006',
          item_name: 'Syringes',
          manufacturing_date: '2023-12-01',
          expiry_date: '2024-12-01', // Expired
          quantity: 300,
          location: 'Emergency',
          quality_status: 'active',
          supplier_id: 'SUP002',
          cost_per_unit: 3.50
        },
        {
          id: 'MED007_BTH007',
          batch_number: 'BTH007',
          item_id: 'MED007',
          item_name: 'Bandages',
          manufacturing_date: '2024-03-01',
          expiry_date: '2027-03-01', // Good - long expiry
          quantity: 800,
          location: 'Emergency',
          quality_status: 'active',
          supplier_id: 'SUP003',
          cost_per_unit: 5.25
        }
      ];

      // Filter expiring batches based on our batch data
      expiringData = batchesData.filter(batch => {
        const expiry = new Date(batch.expiry_date);
        const today = new Date();
        const daysToExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
        return daysToExpiry <= 30 && daysToExpiry > 0;
      });

      setBatches(batchesData);
      setExpiringBatches(expiringData);
    } catch (error) {
      console.error('Error initializing batch data:', error);
    }
  };

  const handleCreateBatch = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v2/inventory/batches', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newBatch)
      });

      if (response.ok) {
        setShowBatchModal(false);
        setNewBatch({
          item_id: '',
          batch_number: '',
          manufacturing_date: '',
          expiry_date: '',
          quantity: '',
          location_id: ''
        });
        initializeBatchData();
        alert('Batch created successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Error creating batch');
    }
  };

  const handleUpdateBatchStatus = async (batchId, status) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v2/inventory/batches/${batchId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });

      if (response.ok) {
        initializeBatchData();
        alert(`Batch status updated to ${status}`);
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Error updating batch status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'quarantine':
        return 'bg-yellow-100 text-yellow-800';
      case 'expired':
        return 'bg-red-100 text-red-800';
      case 'recalled':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getExpiryStatus = (expiryDate) => {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const daysToExpiry = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));

    if (daysToExpiry < 0) return { status: 'expired', color: 'text-red-600', text: 'Expired' };
    if (daysToExpiry <= 30) return { status: 'expiring', color: 'text-orange-600', text: `${daysToExpiry} days` };
    if (daysToExpiry <= 90) return { status: 'warning', color: 'text-yellow-600', text: `${daysToExpiry} days` };
    return { status: 'good', color: 'text-green-600', text: `${daysToExpiry} days` };
  };

  const filteredBatches = batches.filter(batch => {
    const matchesSearch = batch.batch_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         batch.item_id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const batchStatus = batch.quality_status || batch.status || 'active';
    const matchesStatus = filterStatus === 'ALL' || batchStatus === filterStatus;
    
    let matchesExpiry = true;
    if (filterExpiry !== 'ALL') {
      const expiryStatus = getExpiryStatus(batch.expiry_date);
      matchesExpiry = expiryStatus.status === filterExpiry;
    }
    
    return matchesSearch && matchesStatus && matchesExpiry;
  });

  const batchStats = {
    total: batches.length,
    active: batches.filter(b => {
      const status = b.quality_status || b.status || 'active';
      return status === 'active';
    }).length,
    expiring: batches.filter(b => {
      if (!b.expiry_date) return false;
      const expiryStatus = getExpiryStatus(b.expiry_date);
      return expiryStatus.status === 'expiring';
    }).length,
    expired: batches.filter(b => {
      if (!b.expiry_date) return false;
      const expiryStatus = getExpiryStatus(b.expiry_date);
      return expiryStatus.status === 'expired';
    }).length,
    quarantine: batches.filter(b => {
      const status = b.quality_status || b.status || 'active';
      return status === 'quarantine';
    }).length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Package2 className="h-6 w-6 mr-2" />
              Batch Management
            </h1>
            <p className="mt-2 text-gray-600">
              Track and manage inventory batches, lots, and expiration dates
            </p>
          </div>
          <button
            onClick={() => setShowBatchModal(true)}
            className="btn btn-primary flex items-center"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Batch
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package2 className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Batches</p>
              <p className="text-2xl font-bold text-gray-900">{batchStats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Active</p>
              <p className="text-2xl font-bold text-gray-900">{batchStats.active}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="h-5 w-5 text-orange-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Expiring Soon</p>
              <p className="text-2xl font-bold text-gray-900">{batchStats.expiring}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="h-5 w-5 text-red-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Expired</p>
              <p className="text-2xl font-bold text-gray-900">{batchStats.expired}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Quarantine</p>
              <p className="text-2xl font-bold text-gray-900">{batchStats.quarantine}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Expiring Batches Alert */}
      {expiringBatches.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-orange-600 mr-2" />
            <div>
              <h3 className="text-sm font-medium text-orange-800">
                {expiringBatches.length} batch(es) expiring within 30 days
              </h3>
              <p className="text-sm text-orange-700 mt-1">
                Please review and take appropriate action for expiring inventory.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search batches..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Status</option>
              <option value="active">Active</option>
              <option value="quarantine">Quarantine</option>
              <option value="expired">Expired</option>
              <option value="recalled">Recalled</option>
            </select>
            <select
              value={filterExpiry}
              onChange={(e) => setFilterExpiry(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Expiry</option>
              <option value="expired">Expired</option>
              <option value="expiring">Expiring Soon</option>
              <option value="warning">Warning</option>
              <option value="good">Good</option>
            </select>
          </div>
          <div className="text-sm text-gray-600">
            Showing {filteredBatches.length} of {batches.length} batches
          </div>
        </div>
      </div>

      {/* Batches Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Batch Info
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Item
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Manufacturing
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Expiry
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredBatches.map((batch) => {
                const expiryStatus = getExpiryStatus(batch.expiry_date);
                const batchStatus = batch.quality_status || batch.status || 'active';
                const batchId = batch.id || batch.batch_id;
                return (
                  <tr key={batchId} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{batch.batch_number}</div>
                        <div className="text-sm text-gray-500">ID: {batchId}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{batch.item_name || batch.item_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{batch.quantity}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {new Date(batch.manufacturing_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm text-gray-900">
                          {new Date(batch.expiry_date).toLocaleDateString()}
                        </div>
                        <div className={`text-xs font-medium ${expiryStatus.color}`}>
                          {expiryStatus.text}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(batchStatus)}`}>
                        {batchStatus}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setSelectedBatch(batch)}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        {batchStatus === 'active' && expiryStatus.status === 'expiring' && (
                          <button
                            onClick={() => handleUpdateBatchStatus(batchId, 'quarantine')}
                            className="text-yellow-600 hover:text-yellow-800"
                          >
                            Quarantine
                          </button>
                        )}
                        {batchStatus === 'quarantine' && (
                          <button
                            onClick={() => handleUpdateBatchStatus(batchId, 'active')}
                            className="text-green-600 hover:text-green-800"
                          >
                            Activate
                          </button>
                        )}
                        {expiryStatus.status === 'expired' && batchStatus !== 'expired' && (
                          <button
                            onClick={() => handleUpdateBatchStatus(batchId, 'expired')}
                            className="text-red-600 hover:text-red-800"
                          >
                            Mark Expired
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* New Batch Modal */}
      {showBatchModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-screen overflow-y-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create New Batch</h3>
            <form onSubmit={handleCreateBatch} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Item ID</label>
                <input
                  type="text"
                  value={newBatch.item_id}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, item_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Batch Number</label>
                <input
                  type="text"
                  value={newBatch.batch_number}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, batch_number: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Manufacturing Date</label>
                <input
                  type="date"
                  value={newBatch.manufacturing_date}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, manufacturing_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Expiry Date</label>
                <input
                  type="date"
                  value={newBatch.expiry_date}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, expiry_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                <input
                  type="number"
                  value={newBatch.quantity}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, quantity: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Location ID</label>
                <input
                  type="text"
                  value={newBatch.location_id}
                  onChange={(e) => setNewBatch(prev => ({ ...prev, location_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowBatchModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Create Batch
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Batch Details Modal */}
      {selectedBatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-screen overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Batch Details</h3>
              <button
                onClick={() => setSelectedBatch(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XCircle className="h-6 w-6" />
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-500">Batch Number</label>
                <p className="text-lg font-semibold">{selectedBatch.batch_number}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Item</label>
                <p className="text-lg">{selectedBatch.item_name || selectedBatch.item_id}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Quantity</label>
                <p className="text-lg">{selectedBatch.quantity}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Status</label>
                <span className={`px-2 py-1 rounded-full text-sm font-medium ${getStatusColor(selectedBatch.quality_status || selectedBatch.status || 'active')}`}>
                  {selectedBatch.quality_status || selectedBatch.status || 'active'}
                </span>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Manufacturing Date</label>
                <p className="text-lg">{new Date(selectedBatch.manufacturing_date).toLocaleDateString()}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-500">Expiry Date</label>
                <p className="text-lg">{new Date(selectedBatch.expiry_date).toLocaleDateString()}</p>
              </div>
              {selectedBatch.location && (
                <div>
                  <label className="block text-sm font-medium text-gray-500">Location</label>
                  <p className="text-lg">{selectedBatch.location}</p>
                </div>
              )}
              {selectedBatch.supplier_id && (
                <div>
                  <label className="block text-sm font-medium text-gray-500">Supplier ID</label>
                  <p className="text-lg">{selectedBatch.supplier_id}</p>
                </div>
              )}
            </div>
            {selectedBatch.notes && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-500">Notes</label>
                <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md">{selectedBatch.notes}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchManagement;
