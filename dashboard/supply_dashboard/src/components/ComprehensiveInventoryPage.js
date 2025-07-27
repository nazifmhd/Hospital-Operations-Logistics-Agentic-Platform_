import React, { useState, useEffect } from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { Package, Plus, Minus, Search, MapPin, ChevronDown, ChevronUp, AlertTriangle, CheckCircle, Clock, RefreshCw } from 'lucide-react';

const ComprehensiveInventoryPage = () => {
  const { dashboardData, updateInventory, loading } = useSupplyData();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [editingItem, setEditingItem] = useState(null);
  const [updateQuantity, setUpdateQuantity] = useState('');
  const [updateReason, setUpdateReason] = useState('');
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [multiLocationInventory, setMultiLocationInventory] = useState([]);
  const [loadingMultiLocation, setLoadingMultiLocation] = useState(false);
  
  // Bulk Smart Restock state
  const [bulkRestockItems, setBulkRestockItems] = useState('');
  const [bulkRestockQuantity, setBulkRestockQuantity] = useState('');

  // Fetch multi-location inventory data
  useEffect(() => {
    fetchMultiLocationInventory();
  }, []);

  const fetchMultiLocationInventory = async () => {
    try {
      setLoadingMultiLocation(true);
      // Add timestamp to prevent caching
      const timestamp = new Date().getTime();
      const response = await fetch(`http://localhost:8000/api/v3/inventory/multi-location?t=${timestamp}`, {
        method: 'GET',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      const data = await response.json();
      
      // Log the response for debugging
      console.log('📦 Multi-location inventory response:', data);
      
      // Check for ITEM-017 specifically
      const item017 = data.items?.find(item => item.item_id === 'ITEM-017');
      if (item017) {
        console.log('🔍 ITEM-017 data:', {
          name: item017.name,
          current_stock: item017.current_stock,
          locations: item017.locations?.length || 0
        });
      }
      
      setMultiLocationInventory(data.items || []);
    } catch (error) {
      console.error('Failed to fetch multi-location inventory:', error);
      setMultiLocationInventory([]);
    } finally {
      setLoadingMultiLocation(false);
    }
  };

  if (loading || loadingMultiLocation) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Use multi-location inventory if available, otherwise fall back to regular inventory
  const inventory = multiLocationInventory.length > 0 ? multiLocationInventory : (dashboardData?.inventory || []);

  // Toggle expanded state for an item
  const toggleExpanded = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  // Filter inventory based on search and filters
  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.item_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || item.category === filterCategory;
    const isLowStock = item.current_stock <= item.minimum_stock;
    const hasLowStockLocation = item.locations?.some(loc => loc.stock_status === 'LOW');
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'low_stock' && (isLowStock || hasLowStockLocation)) ||
                         (filterStatus === 'normal' && !isLowStock && !hasLowStockLocation);
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Validate inventory counts
  const validateInventoryCounts = (items) => {
    const validationResults = [];
    
    items.forEach(item => {
      if (item.locations && item.locations.length > 0) {
        const locationSum = item.locations.reduce((sum, loc) => sum + (loc.quantity || 0), 0);
        const isValid = locationSum === item.current_stock;
        
        validationResults.push({
          item_id: item.item_id,
          name: item.name,
          current_stock: item.current_stock,
          location_sum: locationSum,
          is_valid: isValid,
          locations: item.locations.map(loc => ({ 
            id: loc.location_id, 
            name: loc.location_name, 
            quantity: loc.quantity 
          }))
        });
      }
    });
    
    return validationResults;
  };

  // Get validation results
  const validationResults = validateInventoryCounts(filteredInventory);
  const invalidItems = validationResults.filter(result => !result.is_valid);

  // Log validation results for debugging
  if (invalidItems.length > 0) {
    console.warn('⚠️ Inventory Count Mismatches Found:', invalidItems);
  }

  // Execute specific distribution plan
  const executeDistributionPlan = async (itemId, distributionPlan, reason) => {
    try {
      const response = await fetch('/api/v2/inventory/execute-distribution-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: itemId,
          distribution_plan: distributionPlan,
          reason: reason
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to execute distribution plan');
      }

      const result = await response.json();
      console.log('✅ Distribution plan executed:', result);
      return result;
    } catch (error) {
      console.error('❌ Execute distribution plan failed:', error);
      throw error;
    }
  };

  // Smart stock distribution when receiving orders
  const smartStockDistribution = async (itemId, totalQuantity, reason = 'received_stock') => {
    try {
      // First, refresh the inventory data to get the latest location information
      await fetchMultiLocationInventory();
      
      // Small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Use the updated inventory data
      const currentInventory = multiLocationInventory.length > 0 ? multiLocationInventory : (dashboardData?.inventory || []);
      const item = currentInventory.find(i => i.item_id === itemId);
      if (!item) {
        throw new Error('Item not found');
      }

      // Get all locations for this item
      const locations = item.locations || [];
      
      // DEBUG: Log the locations data
      console.log('🔍 DEBUG Smart Distribution Data:', {
        item_id: itemId,
        item_name: item.name,
        locations: locations.map(loc => ({
          location_id: loc.location_id,
          location_name: loc.location_name,
          quantity: loc.quantity,
          minimum_threshold: loc.minimum_threshold,
          is_low_stock: (loc.quantity || 0) <= (loc.minimum_threshold || 5)
        }))
      });
      
      // Define location priorities (lower number = higher priority)
      const locationPriorities = {
        'ICU-01': 1,
        'ICU-02': 2,
        'ER-01': 3,
        'SURGERY-01': 4,
        'SURGERY-02': 5,
        'CARDIOLOGY': 6,
        'PHARMACY': 7,
        'LAB-01': 8,
        'MATERNITY': 9,
        'PEDIATRICS': 10,
        'ONCOLOGY': 11,
        'WAREHOUSE': 12
      };

      // Step 1: Identify low stock locations (at or below minimum threshold)
      const lowStockLocations = locations.filter(loc => {
        const currentStock = loc.quantity || 0;
        const minStock = loc.minimum_threshold || 5;
        return currentStock <= minStock; // Use <= to include borderline cases
      }).sort((a, b) => {
        // Sort by priority first, then by deficit
        const priorityA = locationPriorities[a.location_id] || 999;
        const priorityB = locationPriorities[b.location_id] || 999;
        if (priorityA !== priorityB) {
          return priorityA - priorityB;
        }
        const deficitA = (a.minimum_threshold || 5) - (a.quantity || 0);
        const deficitB = (b.minimum_threshold || 5) - (b.quantity || 0);
        return deficitB - deficitA; // Higher deficit first
      });

      // Step 2: Calculate distribution plan with safety buffers above minimum thresholds
      let remainingQuantity = totalQuantity;
      const distributionPlan = [];

      // First, fill low stock locations ABOVE their minimum levels with safety buffer
      for (const location of lowStockLocations) {
        if (remainingQuantity <= 0) break;
        
        const currentStock = location.quantity || 0;
        const minStock = location.minimum_threshold || 5;
        
        // Calculate safety buffer based on location priority (higher priority = larger buffer)
        const priority = locationPriorities[location.location_id] || 999;
        const safetyBufferPercent = priority <= 3 ? 0.5 : priority <= 6 ? 0.3 : 0.2; // 50%, 30%, or 20% buffer
        const safetyBuffer = Math.max(2, Math.ceil(minStock * safetyBufferPercent)); // At least 2 units buffer
        
        const targetStock = minStock + safetyBuffer; // Target is minimum + safety buffer
        const totalNeeded = targetStock - currentStock;
        
        if (totalNeeded > 0) {
          const allocatedQuantity = Math.min(totalNeeded, remainingQuantity);
          distributionPlan.push({
            location_id: location.location_id,
            location_name: location.location_name,
            quantity: allocatedQuantity,
            reason: `replenishment_to_${targetStock}_units_(min_${minStock}_+_buffer_${safetyBuffer})`,
            priority: 'high'
          });
          remainingQuantity -= allocatedQuantity;
        } else {
          // If already above target, still add minimal safety stock if very close to minimum
          const deficit = minStock - currentStock;
          if (deficit >= -2) { // Within 2 units of minimum
            const safetyStock = Math.min(3, remainingQuantity);
            if (safetyStock > 0) {
              distributionPlan.push({
                location_id: location.location_id,
                location_name: location.location_name,
                quantity: safetyStock,
                reason: 'additional_safety_stock',
                priority: 'high'
              });
              remainingQuantity -= safetyStock;
            }
          }
        }
      }

      // Step 3: Distribute remaining stock by location priority
      if (remainingQuantity > 0) {
        const sortedLocations = locations.sort((a, b) => {
          const priorityA = locationPriorities[a.location_id] || 999;
          const priorityB = locationPriorities[b.location_id] || 999;
          return priorityA - priorityB;
        });

        // Calculate total available capacity and priority weights
        const totalAvailableCapacity = sortedLocations.reduce((sum, loc) => {
          const maxCapacity = loc.maximum_capacity || 100;
          const currentStock = loc.quantity || 0;
          return sum + Math.max(0, maxCapacity - currentStock);
        }, 0);

        if (totalAvailableCapacity > 0) {
          // Calculate total weighted capacity for proportional distribution
          const totalWeightedCapacity = sortedLocations.reduce((sum, loc) => {
            const priority = locationPriorities[loc.location_id] || 999;
            const weight = Math.max(1, 13 - priority);
            const maxCapacity = loc.maximum_capacity || 100;
            const currentStock = loc.quantity || 0;
            const availableCapacity = Math.max(0, maxCapacity - currentStock);
            return sum + (weight * availableCapacity);
          }, 0);

          for (const location of sortedLocations) {
            if (remainingQuantity <= 0) break;
            
            const priority = locationPriorities[location.location_id] || 999;
            const weight = Math.max(1, 13 - priority); // Higher priority = higher weight
            const maxCapacity = location.maximum_capacity || 100;
            const currentStock = location.quantity || 0;
            const availableCapacity = Math.max(0, maxCapacity - currentStock);
            
            if (availableCapacity > 0) {
              // Calculate proportional allocation based on priority weight and available capacity
              const proportion = (weight * availableCapacity) / (totalWeightedCapacity || 1);
              let allocatedQuantity = Math.floor(remainingQuantity * proportion);
              
              // Give bonus to highest priority locations
              if (priority <= 3 && allocatedQuantity < remainingQuantity) {
                allocatedQuantity += 1;
              }
              
              // Ensure we don't exceed available capacity or remaining quantity
              allocatedQuantity = Math.min(allocatedQuantity, availableCapacity, remainingQuantity);
              
              if (allocatedQuantity > 0) {
                distributionPlan.push({
                  location_id: location.location_id,
                  location_name: location.location_name,
                  quantity: allocatedQuantity,
                  reason: 'priority_replenishment',
                  priority: priority <= 5 ? 'high' : 'normal'
                });
                remainingQuantity -= allocatedQuantity;
              }
            }
          }
        }

        // If there's still remaining stock, distribute it to the highest priority location with capacity
        if (remainingQuantity > 0 && sortedLocations.length > 0) {
          for (const location of sortedLocations) {
            const maxCapacity = location.maximum_capacity || 100;
            const currentStock = location.quantity || 0;
            const availableCapacity = Math.max(0, maxCapacity - currentStock);
            
            if (availableCapacity > 0) {
              const allocatedQuantity = Math.min(remainingQuantity, availableCapacity);
              if (allocatedQuantity > 0) {
                const existingPlan = distributionPlan.find(p => p.location_id === location.location_id);
                if (existingPlan) {
                  existingPlan.quantity += allocatedQuantity;
                } else {
                  distributionPlan.push({
                    location_id: location.location_id,
                    location_name: location.location_name,
                    quantity: allocatedQuantity,
                    reason: 'overflow_allocation',
                    priority: 'normal'
                  });
                }
                remainingQuantity -= allocatedQuantity;
                break;
              }
            }
          }
        }
      }

      console.log('📦 Smart Distribution Plan:', {
        item_id: itemId,
        item_name: item.name,
        total_quantity: totalQuantity,
        low_stock_locations: lowStockLocations.length,
        distribution_plan: distributionPlan,
        total_distributed: distributionPlan.reduce((sum, p) => sum + p.quantity, 0)
      });

      // Show distribution plan to user for confirmation
      const confirmMessage = `Smart Stock Distribution for ${item.name}:\n\n` +
        `Total Quantity: ${totalQuantity}\n` +
        `Low Stock Locations: ${lowStockLocations.length}\n\n` +
        `Distribution Plan:\n` +
        distributionPlan.map(p => 
          `• ${p.location_name}: +${p.quantity} (${p.reason})`
        ).join('\n') +
        `\n\nProceed with this distribution?`;

      if (window.confirm(confirmMessage)) {
        // Execute the exact distribution plan shown to the user
        await executeDistributionPlan(itemId, distributionPlan, reason);
        await fetchMultiLocationInventory(); // Refresh the data
        
        // Show success message
        alert(`✅ Successfully distributed ${totalQuantity} units of ${item.name} across ${distributionPlan.length} locations!`);
      }
    } catch (error) {
      console.error('Smart distribution failed:', error);
      alert(`Failed to distribute stock: ${error.message}`);
    }
  };

  // Increase stock function - now with smart distribution
  const increaseStock = async (itemId, quantity, reason = 'received_stock') => {
    try {
      // Always use smart distribution for stock increases
      await smartStockDistribution(itemId, quantity, reason);
    } catch (error) {
      console.error('Failed to increase stock:', error);
      alert('Failed to increase stock');
    }
  };

  // Decrease stock function
  const decreaseStock = async (itemId, quantity, reason = 'consumption') => {
    try {
      await updateInventory(itemId, -quantity, reason);
      await fetchMultiLocationInventory(); // Refresh the data
    } catch (error) {
      console.error('Failed to decrease stock:', error);
      alert('Failed to decrease stock');
    }
  };

  const handleUpdateInventory = async (itemId, change, reason) => {
    try {
      // Use smart distribution for positive changes (stock increases)
      if (change > 0) {
        // Always use smart distribution for stock increases
        await smartStockDistribution(itemId, change, reason);
      } else {
        // For decreases, use normal inventory update
        await updateInventory(itemId, change, reason);
        await fetchMultiLocationInventory(); // Refresh the data
      }
      
      setEditingItem(null);
      setUpdateQuantity('');
      setUpdateReason('');
    } catch (error) {
      console.error('Failed to update inventory:', error);
      alert('Failed to update inventory');
    }
  };

  // Bulk Smart Restock Handler
  const handleBulkSmartRestock = async () => {
    try {
      if (!bulkRestockItems || !bulkRestockQuantity) {
        alert('Please enter both item IDs and quantity');
        return;
      }

      const itemIds = bulkRestockItems.split(',').map(id => id.trim()).filter(id => id);
      const totalQuantity = parseInt(bulkRestockQuantity);

      if (itemIds.length === 0 || totalQuantity <= 0) {
        alert('Please enter valid item IDs and quantity');
        return;
      }

      const confirmMessage = `Process bulk smart restock?\n\n` +
        `Items: ${itemIds.join(', ')}\n` +
        `Total Quantity: ${totalQuantity}\n\n` +
        `This will intelligently distribute stock across all locations with:\n` +
        `• Low stock locations filled first\n` +
        `• Remaining stock distributed by location priority\n` +
        `• ICU and ER locations prioritized\n\n` +
        `Continue?`;

      if (window.confirm(confirmMessage)) {
        const results = [];
        
        for (const itemId of itemIds) {
          try {
            await smartStockDistribution(itemId, totalQuantity, 'received_stock');
            results.push(`✅ ${itemId}: Successfully distributed ${totalQuantity} units`);
          } catch (error) {
            results.push(`❌ ${itemId}: Failed - ${error.message}`);
          }
        }

        // Show results
        alert(`Bulk Smart Restock Results:\n\n${results.join('\n')}`);
        
        // Clear form
        setBulkRestockItems('');
        setBulkRestockQuantity('');
        
        // Refresh data
        await fetchMultiLocationInventory();
      }
    } catch (error) {
      console.error('Bulk smart restock failed:', error);
      alert(`Bulk smart restock failed: ${error.message}`);
    }
  };

  // Sync inventory with locations
  const syncInventoryWithLocations = async (itemId) => {
    try {
      const response = await fetch(`/api/v2/inventory/sync/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      
      if (response.ok && result.success) {
        alert(`✅ Synced ${itemId}: Total stock updated to ${result.synced_quantity} units`);
        await fetchMultiLocationInventory(); // Refresh the data
      } else {
        alert(`❌ Sync failed: ${result.message || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Failed to sync inventory:', error);
      alert('Failed to sync inventory');
    }
  };

  const getStatusBadge = (item) => {
    const isLowStock = item.current_stock <= item.minimum_stock;
    const hasLowStockLocation = item.locations?.some(loc => loc.stock_status === 'LOW');
    const hasHighStockLocation = item.locations?.some(loc => loc.stock_status === 'HIGH');
    
    if (isLowStock || hasLowStockLocation) {
      return <span className="status-badge status-warning">Low Stock</span>;
    } else if (hasHighStockLocation) {
      return <span className="status-badge status-info">High Stock</span>;
    } else {
      return <span className="status-badge status-success">Normal</span>;
    }
  };

  const getLocationStatusIcon = (status) => {
    switch (status) {
      case 'LOW':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'HIGH':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <CheckCircle className="h-4 w-4 text-blue-500" />;
    }
  };

  const categories = [...new Set(inventory.map(item => item.category))];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center">
              <Package className="h-6 w-6 mr-2" />
              Comprehensive Inventory Management
            </h1>
            <p className="mt-2 text-gray-600">
              Manage inventory levels across all hospital locations with increase/decrease controls
            </p>
          </div>
          <button
            onClick={fetchMultiLocationInventory}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh Data
          </button>
        </div>
      </div>

      {/* Validation Summary */}
      {invalidItems.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center mb-2">
            <AlertTriangle className="h-5 w-5 text-red-600 mr-2" />
            <h3 className="text-sm font-medium text-red-800">
              Inventory Count Mismatches Detected
            </h3>
          </div>
          <div className="text-sm text-red-700">
            {invalidItems.length} item(s) have mismatched counts between total stock and location sums.
          </div>
          <div className="mt-2 max-h-32 overflow-y-auto">
            {invalidItems.map((item) => (
              <div key={item.item_id} className="text-xs text-red-600 bg-white p-2 rounded mt-1">
                <strong>{item.name}</strong> (ID: {item.item_id}): 
                Total = {item.current_stock}, Location Sum = {item.location_sum}
              </div>
            ))}
          </div>
        </div>
      )}

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
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="low_stock">Low Stock</option>
            <option value="normal">Normal</option>
          </select>
        </div>
      </div>

      {/* Smart Restock Section */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Package className="h-5 w-5 mr-2 text-blue-600" />
              Smart Supplier Order Processing
            </h2>
            <p className="text-sm text-gray-600">
              Intelligently distribute received stock with location priority and low-stock handling
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Bulk Smart Restock */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Bulk Smart Restock</h3>
            <p className="text-sm text-gray-600 mb-3">
              Process multiple items from supplier delivery with intelligent distribution
            </p>
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Enter item IDs (comma-separated)"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                value={bulkRestockItems}
                onChange={(e) => setBulkRestockItems(e.target.value)}
              />
              <input
                type="number"
                placeholder="Total quantity received"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                value={bulkRestockQuantity}
                onChange={(e) => setBulkRestockQuantity(e.target.value)}
              />
              <button
                onClick={handleBulkSmartRestock}
                disabled={!bulkRestockItems || !bulkRestockQuantity}
                className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-md hover:from-blue-700 hover:to-indigo-700 disabled:bg-gray-400 flex items-center justify-center"
              >
                <Package className="w-4 h-4 mr-2" />
                Process Bulk Smart Restock
              </button>
            </div>
          </div>

          {/* Location Priority Display */}
          <div className="border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Location Priority System</h3>
            <p className="text-sm text-gray-600 mb-3">
              Stock distribution follows this priority order:
            </p>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span>1. ICU-01 (Critical)</span>
                <span className="text-red-600">High Priority</span>
              </div>
              <div className="flex justify-between">
                <span>2. ICU-02 (Critical)</span>
                <span className="text-red-600">High Priority</span>
              </div>
              <div className="flex justify-between">
                <span>3. ER-01 (Emergency)</span>
                <span className="text-orange-600">Medium Priority</span>
              </div>
              <div className="flex justify-between">
                <span>4. OR-01 (Surgery)</span>
                <span className="text-orange-600">Medium Priority</span>
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Low stock locations are filled first, then remaining stock is distributed by priority
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Item
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Current Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quick Actions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => {
                const validationResult = validationResults.find(v => v.item_id === item.item_id);
                const isCountValid = validationResult?.is_valid !== false;
                
                return (
                  <React.Fragment key={item.item_id}>
                    <tr className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <div className="ml-4">
                            <div className="flex items-center">
                              <div className="text-sm font-medium text-gray-900">
                                {item.name}
                              </div>
                              {!isCountValid && (
                                <div className="ml-2 flex items-center text-red-600" title="Count mismatch detected">
                                  <AlertTriangle className="h-4 w-4" />
                                </div>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">
                              {item.item_id} • {item.category}
                            </div>
                            {!isCountValid && validationResult && (
                              <div className="text-xs text-red-600 mt-1">
                                Total: {validationResult.current_stock} ≠ Sum: {validationResult.location_sum}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          <span className={`font-semibold text-lg ${!isCountValid ? 'text-red-600' : ''}`}>
                            {item.current_stock}
                          </span> {item.unit_of_measure}
                        </div>
                        <div className="text-sm text-gray-500">
                          Min: {item.minimum_stock} • Reorder: {item.reorder_point}
                        </div>
                        {item.locations && item.locations.length > 0 && (
                          <div className="flex items-center mt-1">
                            <MapPin className="h-4 w-4 text-gray-400 mr-1" />
                            <span className="text-xs text-gray-500">
                              {item.locations.length} locations
                            </span>
                            <button
                              onClick={() => toggleExpanded(item.item_id)}
                              className="ml-2 text-blue-600 hover:text-blue-800"
                            >
                              {expandedItems.has(item.item_id) ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(item)}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-1">
                          {/* Increase buttons */}
                          <button
                            onClick={() => increaseStock(item.item_id, 1)}
                            className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                            title="Increase by 1"
                          >
                            <Plus className="w-3 h-3" />
                            +1
                          </button>
                          <button
                            onClick={() => increaseStock(item.item_id, 5)}
                            className="flex items-center gap-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                            title="Increase by 5"
                          >
                            <Plus className="w-3 h-3" />
                            +5
                          </button>
                          {/* Decrease buttons */}
                          <button
                            onClick={() => decreaseStock(item.item_id, 1)}
                            className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            title="Decrease by 1"
                          >
                            <Minus className="w-3 h-3" />
                            -1
                          </button>
                          <button
                            onClick={() => decreaseStock(item.item_id, 5)}
                            className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                            title="Decrease by 5"
                          >
                            <Minus className="w-3 h-3" />
                            -5
                          </button>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setEditingItem(item.item_id)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Custom
                          </button>
                          <button
                            onClick={() => {
                              const quantity = prompt(`Enter quantity to smart restock for ${item.name}:`, '50');
                              if (quantity && !isNaN(quantity) && parseInt(quantity) > 0) {
                                smartStockDistribution(item.item_id, parseInt(quantity), 'received_stock');
                              }
                            }}
                            className="text-green-600 hover:text-green-900"
                            title="Smart restock with location priorities"
                          >
                            Smart Restock
                          </button>
                          {/* Show sync button only for items with mismatch */}
                          {validationResult && !validationResult.is_valid && (
                            <button
                              onClick={() => syncInventoryWithLocations(item.item_id)}
                              className="text-orange-600 hover:text-orange-900"
                              title="Sync total stock with location sums"
                            >
                              Sync
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                    
                    {/* Expanded location details */}
                    {expandedItems.has(item.item_id) && item.locations && (
                      <tr>
                        <td colSpan="5" className="px-6 py-4 bg-gray-50">
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium text-gray-900">
                                Storage Locations
                              </h4>
                              {validationResult && !validationResult.is_valid && (
                                <div className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
                                  ⚠️ Count mismatch: Total {validationResult.current_stock} ≠ Sum {validationResult.location_sum}
                                </div>
                              )}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {item.locations.map((location, index) => (
                                <div
                                  key={`${location.location_id}-${index}`}
                                  className="bg-white p-4 rounded-lg border border-gray-200"
                                >
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center">
                                      {getLocationStatusIcon(location.stock_status)}
                                      <span className="ml-2 text-sm font-medium text-gray-900">
                                        {location.location_name}
                                      </span>
                                    </div>
                                    <span className={`px-2 py-1 text-xs rounded-full ${
                                      location.stock_status === 'LOW' ? 'bg-red-100 text-red-800' :
                                      location.stock_status === 'HIGH' ? 'bg-green-100 text-green-800' :
                                      'bg-blue-100 text-blue-800'
                                    }`}>
                                      {location.stock_status}
                                    </span>
                                  </div>
                                  <div className="space-y-1 text-sm text-gray-600">
                                    <div className="font-medium">Stock: {location.quantity} {item.unit_of_measure}</div>
                                    <div>Min: {location.minimum_threshold}</div>
                                    <div>Capacity: {location.maximum_capacity}</div>
                                    <div className="text-xs text-gray-500">
                                      Updated: {new Date(location.last_updated).toLocaleDateString()}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit Modal */}
      {editingItem && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Update Inventory
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Quantity Change
                </label>
                <input
                  type="number"
                  value={updateQuantity}
                  onChange={(e) => setUpdateQuantity(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter quantity change (+/-)"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Reason
                </label>
                <select
                  value={updateReason}
                  onChange={(e) => setUpdateReason(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select reason</option>
                  <option value="received_stock">Received Stock</option>
                  <option value="used_supplies">Used Supplies</option>
                  <option value="expired_removed">Expired - Removed</option>
                  <option value="damaged_removed">Damaged - Removed</option>
                  <option value="inventory_adjustment">Inventory Adjustment</option>
                  <option value="consumption">Consumption</option>
                  <option value="transfer_in">Transfer In</option>
                  <option value="transfer_out">Transfer Out</option>
                </select>
              </div>
            </div>
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setEditingItem(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              >
                Cancel
              </button>
              <button
                onClick={() => handleUpdateInventory(editingItem, parseInt(updateQuantity), updateReason)}
                disabled={!updateQuantity || !updateReason}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
              >
                Update
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ComprehensiveInventoryPage;
