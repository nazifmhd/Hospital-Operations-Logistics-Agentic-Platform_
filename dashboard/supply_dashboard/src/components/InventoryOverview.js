import React from 'react';
import { Clock, Package } from 'lucide-react';

const InventoryOverview = ({ inventory }) => {
  // Sort inventory by priority (low stock first, then expiring soon)
  const sortedInventory = inventory?.slice().sort((a, b) => {
    const aLowStock = a.current_stock <= a.minimum_stock;
    const bLowStock = b.current_stock <= b.minimum_stock;
    if (aLowStock && !bLowStock) return -1;
    if (!aLowStock && bLowStock) return 1;
    if (a.days_until_stockout && b.days_until_stockout) {
      return a.days_until_stockout - b.days_until_stockout;
    }
    return 0;
  }) || [];

  const getStockStatus = (item) => {
    const isExpired = item.expiry_date && new Date(item.expiry_date) < new Date();
    const isLowStock = item.current_stock <= item.minimum_stock;
    const daysUntilExpiry = item.expiry_date ? Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24)) : null;
    
    if (isExpired) return { label: 'Expired', color: 'bg-red-100 text-red-800' };
    if (isLowStock) return { label: 'Low Stock', color: 'bg-yellow-100 text-yellow-800' };
    if (daysUntilExpiry && daysUntilExpiry <= 30) {
      return { label: 'Expiring Soon', color: 'bg-orange-100 text-orange-800' };
    }
    return { label: 'Normal', color: 'bg-green-100 text-green-800' };
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <Package className="h-5 w-5 mr-2" />
          Inventory Overview
        </h2>
      </div>
      
      <div className="overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          {sortedInventory.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              No inventory data available
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {sortedInventory.slice(0, 10).map((item) => {
                const status = getStockStatus(item);
                const isLowStock = item.current_stock <= item.minimum_stock;
                return (
                  <div key={item.item_id} className="p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {item.name}
                        </h4>
                        <p className="text-sm text-gray-500">
                          {item.location_id} • {item.category?.replace('_', ' ') || 'Unknown Category'}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">
                            {item.current_stock}
                          </p>
                          <p className="text-xs text-gray-500">
                            Min: {item.minimum_stock}
                          </p>
                        </div>
                        
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                          {status.label}
                        </span>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-gray-500 mb-1">
                        <span>Stock Level</span>
                        <span>
                          {(() => {
                            const currentQty = Number(item.current_stock) || 0;
                            const minThreshold = Number(item.minimum_stock) || 1;
                            const maxThreshold = Number(item.maximum_stock) || minThreshold * 4;
                            const percentage = (currentQty / maxThreshold) * 100;
                            const safePercentage = isNaN(percentage) ? 0 : Math.round(Math.min(percentage, 100));
                            return safePercentage;
                          })()}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            isLowStock ? 'bg-red-500' : 'bg-green-500'
                          }`}
                          style={{
                            width: `${(() => {
                              const currentQty = Number(item.current_stock) || 0;
                              const minThreshold = Number(item.minimum_stock) || 1;
                              const maxThreshold = Number(item.maximum_stock) || minThreshold * 4;
                              const percentage = (currentQty / maxThreshold) * 100;
                              const safePercentage = isNaN(percentage) ? 0 : Math.min(percentage, 100);
                              return safePercentage;
                            })()}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    {/* Expiry Warning */}
                    {item.expiry_date && (() => {
                      const daysUntilExpiry = Math.ceil((new Date(item.expiry_date) - new Date()) / (1000 * 60 * 60 * 24));
                      return daysUntilExpiry <= 30 && (
                        <div className="mt-2 flex items-center text-xs text-orange-600">
                          <Clock className="h-3 w-3 mr-1" />
                          Expires in {daysUntilExpiry} days
                        </div>
                      );
                    })()}
                  </div>
                );
              })}
            </div>
          )}
        </div>
        
        {sortedInventory.length > 10 && (
          <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
            <p className="text-sm text-gray-500 text-center">
              Showing 10 of {sortedInventory.length} items
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default InventoryOverview;
