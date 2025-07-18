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
  const inventoryData = dashboardData?.inventory || [];
  const locationsData = dashboardData?.locations || [];

  useEffect(() => {
    fetchAdditionalData();
  }, []);

  const fetchAdditionalData = async () => {
    try {
      // Try to fetch transfers from the proper endpoint
      let transfers = [];
      try {
        const transfersRes = await fetch('http://localhost:8000/api/v2/inventory/transfers-list');
        if (transfersRes.ok) {
          const transfersData = await transfersRes.json();
          // Handle different response structures
          if (Array.isArray(transfersData)) {
            transfers = transfersData;
          } else if (transfersData.data && Array.isArray(transfersData.data)) {
            transfers = transfersData.data;
          } else if (transfersData.transfers && Array.isArray(transfersData.transfers)) {
            transfers = transfersData.transfers;
          } else {
            transfers = [];
          }
        }
      } catch (transferError) {
        console.warn('Could not fetch transfers:', transferError);
        transfers = [];
      }
      
      setTransfers(transfers);
    } catch (error) {
      console.error('Error fetching additional data:', error);
    }
  };

  const handleTransfer = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/inventory/transfer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transferForm)
      });

      if (response.ok) {
        setShowTransferModal(false);
        setTransferForm({
          item_id: '',
          from_location: '',
          to_location: '',
          quantity: '',
          reason: ''
        });
        // Refresh data
        fetchAdditionalData();
      } else {
        console.error('Transfer failed');
      }
    } catch (error) {
      console.error('Error creating transfer:', error);
    }
  };

  // Filter inventory based on search and location
  const filteredInventory = inventoryData.filter(item => {
    if (!item) return false;
    
    const matchesSearch = item.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.item_id?.toLowerCase().includes(searchTerm.toLowerCase());
    
    if (selectedLocation === 'ALL') return matchesSearch;
    
    // Check if the item exists in the selected location
    return matchesSearch && item.location_id === selectedLocation;
  });

  const getLocationStockSummary = () => {
    const summary = {};
    
    // Initialize summary for all locations from the locations data
    if (Array.isArray(locationsData)) {
      locationsData.forEach(loc => {
        summary[loc.location_id] = {
          total_items: 0,
          low_stock_items: 0,
          total_value: 0
        };
      });
    }

    inventoryData.forEach(item => {
      const locId = item.location_id;
      if (summary[locId]) {
        summary[locId].total_items++;
        if (item.current_stock <= item.minimum_stock) {
          summary[locId].low_stock_items++;
        }
        summary[locId].total_value += item.total_value || 0;
      }
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
              Monitor and manage inventory across all hospital locations
            </p>
          </div>
          <button
            onClick={() => setShowTransferModal(true)}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded flex items-center"
          >
            <ArrowLeftRight className="h-4 w-4 mr-2" />
            Create Transfer
          </button>
        </div>
      </div>

      {/* Location Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
        {locationsData.map((location) => {
          const summary = locationSummary[location.location_id] || { total_items: 0, low_stock_items: 0, total_value: 0 };
          return (
            <div key={location.location_id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search items..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Location Filter */}
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="ALL">All Locations</option>
            {locationsData.map((location) => (
              <option key={location.location_id} value={location.location_id}>
                {location.name}
              </option>
            ))}
          </select>
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
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Location
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock Level
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => (
                <tr key={item.item_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">ID: {item.item_id}</div>
                      <div className="text-xs text-gray-400">{item.category}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <span className="text-sm font-medium text-gray-900">
                      {locationsData.find(loc => loc.location_id === item.location_id)?.name || item.location_id}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-center">
                    <div>
                      <span className={`text-sm font-medium ${
                        item.current_stock <= item.minimum_stock ? 'text-red-600' : 'text-gray-900'
                      }`}>
                        {item.current_stock}
                      </span>
                      <div className="text-xs text-gray-500">
                        Min: {item.minimum_stock || 0}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-center">
                    {item.current_stock <= item.minimum_stock ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Low Stock
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Normal
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => {
                        setTransferForm({
                          ...transferForm,
                          item_id: item.item_id,
                          from_location: item.location_id
                        });
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
                  From
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  To
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Array.isArray(transfers) && transfers.slice(0, 5).map((transfer) => (
                <tr key={transfer.transfer_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {transfer.transfer_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transfer.item_name || transfer.item_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transfer.from_location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {transfer.to_location}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                    {transfer.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      transfer.status === 'completed' ? 'bg-green-100 text-green-800' :
                      transfer.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {transfer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-500">
                    {new Date(transfer.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {(!Array.isArray(transfers) || transfers.length === 0) && (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                    No recent transfers found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Transfer Modal */}
      {showTransferModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Create Transfer</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Item</label>
                  <select
                    value={transferForm.item_id}
                    onChange={(e) => setTransferForm({...transferForm, item_id: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Select Item</option>
                    {inventoryData.map(item => (
                      <option key={item.item_id} value={item.item_id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">From Location</label>
                  <select
                    value={transferForm.from_location}
                    onChange={(e) => setTransferForm({...transferForm, from_location: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Select From Location</option>
                    {locationsData.map((location) => (
                      <option key={location.location_id} value={location.location_id}>
                        {location.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">To Location</label>
                  <select
                    value={transferForm.to_location}
                    onChange={(e) => setTransferForm({...transferForm, to_location: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="">Select To Location</option>
                    {locationsData.map((location) => (
                      <option key={location.location_id} value={location.location_id}>
                        {location.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Quantity</label>
                  <input
                    type="number"
                    value={transferForm.quantity}
                    onChange={(e) => setTransferForm({...transferForm, quantity: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    placeholder="Enter quantity"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Reason</label>
                  <textarea
                    value={transferForm.reason}
                    onChange={(e) => setTransferForm({...transferForm, reason: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows="3"
                    placeholder="Transfer reason"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-2 mt-6">
                <button
                  onClick={() => setShowTransferModal(false)}
                  className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  onClick={handleTransfer}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Create Transfer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiLocationInventory;
