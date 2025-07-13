import React, { useState } from 'react';
import { ShoppingCart, TrendingUp, DollarSign, Download, CheckCircle } from 'lucide-react';

const ProcurementRecommendations = ({ recommendations }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedOrders, setGeneratedOrders] = useState(null);

  const getUrgencyColor = (urgency) => {
    switch (urgency?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleGeneratePurchaseOrders = async () => {
    setIsGenerating(true);
    try {
      // Convert recommendations to purchase order format
      const purchaseOrderData = {
        items: recommendations.map(rec => ({
          item_id: rec.item_id,
          quantity: rec.recommended_quantity,
          estimated_cost: rec.estimated_cost || 0
        })),
        department: "Supply Management",
        urgency: "high",
        notes: "Generated from procurement recommendations"
      };
      
      const response = await fetch('http://localhost:8001/api/v2/purchase-orders/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(purchaseOrderData)
      });
      
      if (response.ok) {
        const order = await response.json();
        setGeneratedOrders([order]);
        
        // Show success message
        alert(`Successfully generated purchase order ${order.po_number}!`);
        
        // Optional: Download the order as a file
        downloadPurchaseOrders([order]);
      } else {
        const errorData = await response.text();
        console.error('Purchase order creation failed:', errorData);
        alert('Failed to generate purchase order. Authentication may be required.');
      }
    } catch (error) {
      console.error('Error generating purchase orders:', error);
      alert('Failed to generate purchase orders. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPurchaseOrders = (orders) => {
    const ordersData = {
      generated_date: new Date().toISOString(),
      total_orders: orders.length,
      orders: orders
    };
    
    const dataStr = JSON.stringify(ordersData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `purchase-orders-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  };

  const totalRecommendedCost = recommendations?.reduce((sum, rec) => sum + (rec.estimated_cost || 0), 0) || 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center">
            <ShoppingCart className="h-5 w-5 mr-2" />
            Procurement Recommendations
          </h2>
          {recommendations && recommendations.length > 0 && (
            <div className="text-sm text-gray-600">
              Total Est. Cost: <span className="font-semibold text-gray-900">${totalRecommendedCost.toLocaleString()}</span>
            </div>
          )}
        </div>
      </div>
      
      <div className="overflow-hidden">
        {!recommendations || recommendations.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <ShoppingCart className="h-12 w-12 mx-auto text-gray-400 mb-3" />
            <p>No procurement recommendations</p>
            <p className="text-sm">Inventory levels are adequate</p>
          </div>
        ) : (
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
                    Recommended Order
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Supplier
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Est. Cost
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Urgency
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recommendations.map((rec, index) => (
                  <tr key={rec.item_id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {rec.item_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          ID: {rec.item_id}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {rec.current_quantity} units
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <TrendingUp className="h-4 w-4 text-blue-500 mr-1" />
                        <span className="text-sm font-medium text-gray-900">
                          {rec.recommended_order} units
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {rec.supplier}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <DollarSign className="h-4 w-4 text-green-500 mr-1" />
                        <span className="text-sm font-medium text-gray-900">
                          ${rec.estimated_cost?.toLocaleString() || '0'}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUrgencyColor(rec.urgency)}`}>
                        {rec.urgency}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {recommendations && recommendations.length > 0 && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {recommendations.length} item{recommendations.length !== 1 ? 's' : ''} recommended for procurement
            </p>
            <div className="flex space-x-2">
              {generatedOrders && (
                <button
                  onClick={() => downloadPurchaseOrders(generatedOrders)}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Orders
                </button>
              )}
              <button
                onClick={handleGeneratePurchaseOrders}
                disabled={isGenerating}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin h-4 w-4 mr-2 border-2 border-white border-t-transparent rounded-full"></div>
                    Generating...
                  </>
                ) : generatedOrders ? (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Regenerate Orders
                  </>
                ) : (
                  <>
                    <ShoppingCart className="h-4 w-4 mr-2" />
                    Generate Purchase Orders
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcurementRecommendations;
