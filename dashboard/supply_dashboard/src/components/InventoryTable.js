import React, { useState } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { Package, Plus, Minus, Search } from 'lucide-react';

const InventoryTable = () => {
  const { dashboardData, updateInventory, loading } = useSupplyData();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [editingItem, setEditingItem] = useState(null);
  const [updateQuantity, setUpdateQuantity] = useState('');
  const [updateReason, setUpdateReason] = useState('');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const inventory = dashboardData?.inventory || [];

  // Helper function to get main location for display
  const getDisplayLocation = (item) => {
    if (!item.locations || typeof item.locations !== 'object') {
      return 'General';
    }
    
    // Find location with highest stock
    const locations = Object.entries(item.locations);
    if (locations.length === 0) return 'General';
    
    const mainLocation = locations.reduce((max, [location, data]) => {
      const current = data?.current || 0;
      const maxCurrent = max[1]?.current || 0;
      return current > maxCurrent ? [location, data] : max;
    });
    
    return mainLocation[0] || 'General';
  };

  // Filter inventory based on search and filters
  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || item.category === filterCategory;
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'low_stock' && item.is_low_stock) ||
                         (filterStatus === 'expired' && item.has_expired) ||
                         (filterStatus === 'normal' && !item.is_low_stock && !item.has_expired);
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const handleUpdateInventory = async (itemId, change, reason) => {
    try {
      await updateInventory(itemId, change, reason);
      setEditingItem(null);
      setUpdateQuantity('');
      setUpdateReason('');
    } catch (error) {
      console.error('Failed to update inventory:', error);
      alert('Failed to update inventory');
    }
  };

  const getStatusBadge = (item) => {
    if (item.has_expired) {
      return <span className="status-badge status-danger">Expired</span>;
    } else if (item.is_low_stock) {
      return <span className="status-badge status-warning">Low Stock</span>;
    } else if (item.expiring_soon_count && item.expiring_soon_count > 0) {
      return <span className="status-badge status-warning">Expiring Soon</span>;
    } else {
      return <span className="status-badge status-success">Normal</span>;
    }
  };

  const categories = [...new Set(inventory.map(item => item.category))];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <Package className="h-6 w-6 mr-2" />
          Inventory Management
        </h1>
        <p className="mt-2 text-gray-600">
          Manage and monitor all hospital supply inventory items
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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

          {/* Category Filter */}
          <div className="relative">
            <select
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="relative">
            <select
              className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="normal">Normal</option>
              <option value="low_stock">Low Stock</option>
              <option value="expired">Expired</option>
            </select>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Item
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
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
              {filteredInventory.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{item.name}</div>
                      <div className="text-sm text-gray-500">ID: {item.id}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {item.category.replace('_', ' ').toUpperCase()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{getDisplayLocation(item)}</div>
                    {item.locations && Object.keys(item.locations).length > 1 && (
                      <div className="text-xs text-gray-500">
                        +{Object.keys(item.locations).length - 1} more locations
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div className="font-medium">{item.total_quantity}</div>
                      <div className="text-xs text-gray-500">
                        Min: {item.minimum_threshold} | Max: {item.maximum_capacity}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className={`h-2 rounded-full ${
                            item.is_low_stock ? 'bg-red-500' : 'bg-green-500'
                          }`}
                          style={{
                            width: `${Math.min((item.total_quantity / item.maximum_capacity) * 100, 100)}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      <div className="font-medium">${item.total_value}</div>
                      <div className="text-xs text-gray-500">
                        ${item.unit_cost}/unit
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(item)}
                    {item.expiring_soon_count && item.expiring_soon_count > 0 && (
                      <div className="text-xs text-orange-600 mt-1">
                        {item.expiring_soon_count} items expiring soon
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {editingItem === item.id ? (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <input
                            type="number"
                            placeholder="±Quantity"
                            className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                            value={updateQuantity}
                            onChange={(e) => setUpdateQuantity(e.target.value)}
                          />
                          <input
                            type="text"
                            placeholder="Reason"
                            className="w-24 px-2 py-1 border border-gray-300 rounded text-sm"
                            value={updateReason}
                            onChange={(e) => setUpdateReason(e.target.value)}
                          />
                        </div>
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleUpdateInventory(item.id, parseInt(updateQuantity) || 0, updateReason)}
                            className="px-2 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700"
                          >
                            Save
                          </button>
                          <button
                            onClick={() => setEditingItem(null)}
                            className="px-2 py-1 bg-gray-300 text-gray-700 rounded text-xs hover:bg-gray-400"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex space-x-1">
                        <button
                          onClick={() => {
                            setEditingItem(item.id);
                            setUpdateQuantity('');
                            setUpdateReason('');
                          }}
                          className="p-1 text-blue-600 hover:text-blue-900"
                          title="Edit quantity"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleUpdateInventory(item.id, 1, 'Manual increment')}
                          className="p-1 text-green-600 hover:text-green-900"
                          title="Add 1"
                        >
                          <Plus className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleUpdateInventory(item.id, -1, 'Manual decrement')}
                          className="p-1 text-red-600 hover:text-red-900"
                          title="Remove 1"
                        >
                          <Minus className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {filteredInventory.length === 0 && (
          <div className="text-center py-12">
            <Package className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">No items found matching your criteria</p>
          </div>
        )}
      </div>

      {/* Summary */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">{filteredInventory.length}</div>
            <div className="text-sm text-gray-500">Items Shown</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">
              {filteredInventory.filter(item => item.is_low_stock).length}
            </div>
            <div className="text-sm text-gray-500">Low Stock</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-orange-600">
              {filteredInventory.filter(item => item.has_expired).length}
            </div>
            <div className="text-sm text-gray-500">Expired</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-600">
              ${filteredInventory.reduce((sum, item) => sum + item.total_value, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-500">Total Value</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryTable;
