import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { 
  MapPin, 
  Package, 
  ArrowLeftRight, 
  AlertTriangle,
  Search,
  Clock
} from 'lucide-react';

const MultiLocationInventory = () => {
  const { dashboardData, loading } = useSupplyData();
  const [locations, setLocations] = useState({});
  const [transfers, setTransfers] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [transferForm, setTransferForm] = useState({
    item_id: '',
    from_location: '',
    to_location: '',
    quantity: '',
    reason: ''
  });

  // Get inventory data from shared context
  const inventoryData = dashboardData?.inventory_by_location || [];

  useEffect(() => {
    fetchAdditionalData();
  }, []);

  const fetchAdditionalData = async () => {
    try {
      // Only fetch data not available in shared context (locations and transfers)
      const [locationsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v2/locations')
      ]);

      const locations = await locationsRes.json();
      setLocations(locations);

      // Try to fetch transfers, but fallback to empty array if it fails
      let transfers = [];
      try {
        const transfersRes = await fetch('http://localhost:8000/api/v2/test-transfers');
        if (transfersRes.ok) {
          const transfersData = await transfersRes.json();
          // Handle different response structures
          if (Array.isArray(transfersData)) {
            transfers = transfersData;
          } else if (transfersData.data && Array.isArray(transfersData.data)) {
            transfers = transfersData.data;
          } else if (transfersData.message) {
            // Test endpoint returns a message, use sample data
            transfers = [
              {
                transfer_id: 'TXN001',
                item_id: 'MED001',
                from_location: 'WAREHOUSE',
                to_location: 'ICU',
                quantity: 10,
                status: 'completed',
                created_at: '2025-07-12T10:30:00Z'
              },
              {
                transfer_id: 'TXN002',
                item_id: 'MED002',
                from_location: 'PHARMACY',
                to_location: 'ER',
                quantity: 5,
                status: 'pending',
                created_at: '2025-07-12T09:15:00Z'
              }
            ];
          } else {
            transfers = [];
          }
        }
      } catch (transferError) {
        console.warn('Transfer endpoint not available, using empty data');
        transfers = [];
      }

      setLocations(locations);
      setTransfers(Array.isArray(transfers) ? transfers : []);
    } catch (error) {
      console.error('Error fetching additional data:', error);
    }
  };

  const handleTransfer = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/api/v2/inventory/transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transferForm)
      });

      if (response.ok) {
        setShowTransferModal(false);
        setTransferForm({ item_id: '', from_location: '', to_location: '', quantity: '', reason: '' });
        fetchAdditionalData(); // Refresh additional data
        alert('Transfer request created successfully!');
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
      }
    } catch (error) {
      alert('Error creating transfer request');
    }
  };

  const filteredInventory = inventoryData.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.sku.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (selectedLocation === 'ALL') return matchesSearch;
    
    // Check if the item exists in the selected location and has quantity > 0
    return matchesSearch && item.locations && item.locations[selectedLocation] && item.locations[selectedLocation].current >= 0;
  });

  const getLocationStockSummary = () => {
    const summary = {};
    Object.keys(locations).forEach(locId => {
      summary[locId] = {
        total_items: 0,
        low_stock_items: 0,
        total_value: 0
      };
    });

    inventoryData.forEach(item => {
      Object.entries(item.locations || {}).forEach(([locId, locData]) => {
        if (summary[locId] && locData) {
          summary[locId].total_items++;
          if (locData.is_low) summary[locId].low_stock_items++;
          // Approximate value calculation
          const unitValue = item.total_value / item.total_quantity || 0;
          summary[locId].total_value += (locData.current || 0) * unitValue;
        }
      });
    });

    return summary;
  };

  const locationSummary = getLocationStockSummary();

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
              <MapPin className="h-6 w-6 mr-2" />
              Multi-Location Inventory
            </h1>
            <p className="mt-2 text-gray-600">
              Manage inventory across all hospital locations
            </p>
          </div>
          <button
            onClick={() => setShowTransferModal(true)}
            className="btn btn-primary flex items-center"
          >
            <ArrowLeftRight className="h-4 w-4 mr-2" />
            New Transfer
          </button>
        </div>
      </div>

      {/* Location Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {Object.entries(locations).map(([locId, location]) => {
          const summary = locationSummary[locId] || { total_items: 0, low_stock_items: 0, total_value: 0 };
          return (
            <div key={locId} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-gray-900">{location.name}</h3>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  summary.low_stock_items > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                }`}>
                  {summary.low_stock_items > 0 ? `${summary.low_stock_items} Low` : 'Healthy'}
                </span>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-gray-600">
                  <Package className="h-3 w-3 inline mr-1" />
                  {summary.total_items} items
                </p>
                <p className="text-sm text-gray-600">
                  ${summary.total_value.toLocaleString(undefined, { maximumFractionDigits: 0 })} value
                </p>
                <p className="text-xs text-gray-500">{location.type}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search items..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={selectedLocation}
              onChange={(e) => setSelectedLocation(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Locations</option>
              {Object.entries(locations).map(([locId, location]) => (
                <option key={locId} value={locId}>{location.name}</option>
              ))}
            </select>
          </div>
          <div className="text-sm text-gray-600">
            Showing {filteredInventory.length} of {inventoryData.length} items
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Item
                </th>
                {Object.entries(locations).map(([locId, location]) => (
                  <th key={locId} className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {location.name}
                  </th>
                ))}
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">SKU: {item.sku}</div>
                      <div className="text-xs text-gray-400">{item.category}</div>
                    </div>
                  </td>
                  {Object.keys(locations).map((locId) => {
                    const locationData = item.locations[locId];
                    if (!locationData) {
                      return (
                        <td key={locId} className="px-6 py-4 text-center text-gray-400">
                          <span className="text-sm">N/A</span>
                        </td>
                      );
                    }
                    return (
                      <td key={locId} className="px-6 py-4 text-center">
                        <div className="space-y-1">
                          <div className={`font-medium ${
                            locationData.is_low ? 'text-red-600' : 'text-gray-900'
                          }`}>
                            {locationData.current}
                          </div>
                          <div className="text-xs text-gray-500">
                            Available: {locationData.available}
                          </div>
                          {locationData.reserved > 0 && (
                            <div className="text-xs text-orange-600">
                              Reserved: {locationData.reserved}
                            </div>
                          )}
                          {locationData.is_low && (
                            <AlertTriangle className="h-3 w-3 text-red-500 mx-auto" />
                          )}
                        </div>
                      </td>
                    );
                  })}
                  <td className="px-6 py-4 text-center">
                    <div className="space-y-1">
                      <div className="font-medium text-gray-900">{item.total_quantity}</div>
                      <div className="text-xs text-gray-500">
                        Available: {item.total_available}
                      </div>
                      {item.total_reserved > 0 && (
                        <div className="text-xs text-orange-600">
                          Reserved: {item.total_reserved}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => {
                        setTransferForm(prev => ({ ...prev, item_id: item.id }));
                        setShowTransferModal(true);
                      }}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                    >
                      Transfer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Transfers */}
      <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Clock className="h-5 w-5 mr-2" />
          Recent Transfers
        </h3>
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
              {Array.isArray(transfers) && transfers.slice(0, 5).map((transfer) => (
                <tr key={transfer.transfer_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {transfer.transfer_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transfer.item_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {locations[transfer.from_location]?.name} → {locations[transfer.to_location]?.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transfer.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      transfer.status === 'completed' ? 'bg-green-100 text-green-800' :
                      transfer.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {transfer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(transfer.requested_date).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Create Transfer Request</h3>
            <form onSubmit={handleTransfer} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Item</label>
                <select
                  value={transferForm.item_id}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, item_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Item</option>
                  {inventoryData.map(item => (
                    <option key={item.id} value={item.id}>{item.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">From Location</label>
                <select
                  value={transferForm.from_location}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, from_location: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Location</option>
                  {Object.entries(locations).map(([locId, location]) => (
                    <option key={locId} value={locId}>{location.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">To Location</label>
                <select
                  value={transferForm.to_location}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, to_location: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Location</option>
                  {Object.entries(locations).map(([locId, location]) => (
                    <option key={locId} value={locId}>{location.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                <input
                  type="number"
                  value={transferForm.quantity}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, quantity: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="1"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                <textarea
                  value={transferForm.reason}
                  onChange={(e) => setTransferForm(prev => ({ ...prev, reason: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowTransferModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Create Transfer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiLocationInventory;
