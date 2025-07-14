import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSupplyData } from '../context/SupplyDataContext';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  Users, 
  DollarSign, 
  MapPin,
  Clock,
  CheckCircle,
  Building,
  ShoppingCart,
  BarChart3,
  Shield,
  X,
  Filter
} from 'lucide-react';

const ProfessionalDashboard = () => {
  const navigate = useNavigate();
  const { dashboardData, loading, error } = useSupplyData();
  const [actionLoading, setActionLoading] = useState(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [activityFilter, setActivityFilter] = useState('all');

  // Quick Action Handlers
  const handleCreatePurchaseOrder = async () => {
    setActionLoading('po');
    try {
      // Navigate to inventory page where purchase orders can be created from recommendations
      navigate('/inventory');
      // Could also show a modal or create a dedicated PO creation page
    } catch (error) {
      console.error('Error navigating to purchase order creation:', error);
      alert('Failed to navigate to purchase order creation');
    } finally {
      setActionLoading(null);
    }
  };

  const handleTransferInventory = async () => {
    setActionLoading('transfer');
    try {
      // For now, show an alert about the transfer feature
      // In a full implementation, this would open a transfer modal or page
      alert('Inventory Transfer feature requires authentication. This would open a transfer interface for moving items between locations.');
    } catch (error) {
      console.error('Error accessing transfer functionality:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReviewAlerts = () => {
    navigate('/alerts');
  };

  const handleGenerateReport = async () => {
    setActionLoading('report');
    try {
      // Navigate to analytics page which has reporting capabilities
      navigate('/analytics');
    } catch (error) {
      console.error('Error navigating to reports:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplianceCheck = async () => {
    setActionLoading('compliance');
    try {
      const response = await fetch('http://localhost:8001/api/v2/analytics/compliance');
      if (response.ok) {
        const complianceData = await response.json();
        alert(`Compliance Check Complete:\n\n` +
              `• Total Items Tracked: ${complianceData.total_items_tracked}\n` +
              `• Compliant Items: ${complianceData.compliant_items}\n` +
              `• Pending Reviews: ${complianceData.pending_reviews}\n` +
              `• Expired Certifications: ${complianceData.expired_certifications}\n` +
              `• Compliance Score: ${complianceData.compliance_score}%\n\n` +
              `Status: ${complianceData.compliance_score === 100 ? '✅ All systems compliant' : '⚠️ Issues detected'}`);
      } else {
        throw new Error('Failed to fetch compliance data');
      }
    } catch (error) {
      console.error('Error running compliance check:', error);
      alert('Failed to run compliance check. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  // Enhanced activity data (simulating more comprehensive activity log)
  const getAllActivities = () => {
    const baseTime = new Date();
    return [
      { 
        id: 1,
        action: 'Inventory transfer completed', 
        item: 'Surgical Gloves', 
        location: 'ICU → ER', 
        time: '5 min ago', 
        type: 'success',
        user: 'Dr. Smith',
        details: '50 units transferred for emergency surgery prep'
      },
      { 
        id: 2,
        action: 'Low stock alert generated', 
        item: 'IV Bags (1000ml)', 
        location: 'Surgery Ward', 
        time: '12 min ago', 
        type: 'warning',
        user: 'System',
        details: 'Stock level: 193 units, below threshold of 226'
      },
      { 
        id: 3,
        action: 'Purchase order approved', 
        item: 'PO-2025-0143', 
        location: 'Procurement Dept', 
        time: '1 hr ago', 
        type: 'info',
        user: 'Admin Johnson',
        details: 'Total value: $2,500 for surgical supplies'
      },
      { 
        id: 4,
        action: 'Batch received and verified', 
        item: 'Surgical Masks (50 pack)', 
        location: 'Warehouse', 
        time: '2 hrs ago', 
        type: 'success',
        user: 'Warehouse Staff',
        details: '200 packs received, quality check passed'
      },
      { 
        id: 5,
        action: 'Compliance review completed', 
        item: 'Pharmaceuticals', 
        location: 'Pharmacy', 
        time: '3 hrs ago', 
        type: 'info',
        user: 'Compliance Officer',
        details: 'All medications within expiry guidelines'
      },
      { 
        id: 6,
        action: 'Critical stock alert resolved', 
        item: 'Morphine 10mg/ml', 
        location: 'ICU', 
        time: '4 hrs ago', 
        type: 'success',
        user: 'Dr. Wilson',
        details: 'Emergency restock completed, 25 vials added'
      },
      { 
        id: 7,
        action: 'Inventory audit initiated', 
        item: 'All PPE supplies', 
        location: 'Multiple locations', 
        time: '5 hrs ago', 
        type: 'info',
        user: 'Audit Team',
        details: 'Quarterly audit cycle beginning'
      },
      { 
        id: 8,
        action: 'Supplier delivery delayed', 
        item: 'Blood Collection Tubes', 
        location: 'Lab', 
        time: '6 hrs ago', 
        type: 'warning',
        user: 'Supplier ABC',
        details: 'Expected delivery pushed to tomorrow morning'
      },
      { 
        id: 9,
        action: 'Budget allocation updated', 
        item: 'ICU Department', 
        location: 'Financial Dept', 
        time: '8 hrs ago', 
        type: 'info',
        user: 'Finance Manager',
        details: 'Q3 budget increased by $25,000 for equipment'
      },
      { 
        id: 10,
        action: 'Waste disposal completed', 
        item: 'Expired medications', 
        location: 'Pharmacy', 
        time: '1 day ago', 
        type: 'success',
        user: 'Disposal Service',
        details: '12 items properly disposed, waste reduction 15%'
      }
    ];
  };

  const handleViewAllActivities = () => {
    setShowActivityModal(true);
  };

  // Get recent activities (first 5 for dashboard display)
  const recentActivities = getAllActivities().slice(0, 5);
  const allActivities = getAllActivities();

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
    </div>
  );

  if (error) return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-md">
      <p className="text-red-800">Error: {error}</p>
    </div>
  );

  if (!dashboardData) return null;

  const { summary, budget_summary, compliance_status, performance_metrics } = dashboardData;

  // Enhanced stats cards with professional metrics
  const statsCards = [
    {
      title: 'Total Items',
      value: summary.total_items,
      change: '+2.5%',
      icon: Package,
      color: 'blue',
      subtitle: `${summary.total_locations} locations`
    },
    {
      title: 'Critical Alerts',
      value: summary.critical_alerts,
      change: summary.overdue_alerts > 0 ? `${summary.overdue_alerts} overdue` : 'None overdue',
      icon: AlertTriangle,
      color: summary.critical_alerts > 0 ? 'red' : 'green',
      subtitle: 'Active alerts'
    },
    {
      title: 'Inventory Value',
      value: `$${(summary.total_value / 1000).toFixed(1)}K`,
      change: '+$12.3K',
      icon: DollarSign,
      color: 'green',
      subtitle: 'Total portfolio'
    },
    {
      title: 'Purchase Orders',
      value: summary.pending_pos,
      change: summary.overdue_pos > 0 ? `${summary.overdue_pos} overdue` : 'On track',
      icon: ShoppingCart,
      color: summary.overdue_pos > 0 ? 'orange' : 'blue',
      subtitle: 'Pending approval'
    },
    {
      title: 'Stock Health',
      value: `${Math.round(((summary.total_items - summary.low_stock_items) / summary.total_items) * 100)}%`,
      change: summary.critical_low_stock > 0 ? `${summary.critical_low_stock} critical` : 'Healthy',
      icon: TrendingUp,
      color: summary.critical_low_stock > 0 ? 'red' : 'green',
      subtitle: 'Optimal levels'
    },
    {
      title: 'Compliance Score',
      value: `${compliance_status.compliance_score}%`,
      change: 'Excellent',
      icon: Shield,
      color: 'green',
      subtitle: 'Regulatory compliance'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Professional Supply Management
            </h1>
            <p className="mt-2 text-gray-600">
              Enterprise-grade hospital inventory system
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">Last updated</p>
              <p className="font-medium">{new Date().toLocaleTimeString()}</p>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      {/* Enhanced Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-6">
        {statsCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className={`p-3 rounded-lg bg-${stat.color}-500`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className={`text-2xl font-bold text-${stat.color}-600`}>
                    {stat.value}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">{stat.subtitle}</p>
                  <p className={`text-sm font-medium mt-1 ${
                    stat.change.includes('+') ? 'text-green-600' : 
                    stat.change.includes('overdue') || stat.change.includes('critical') ? 'text-red-600' : 
                    'text-gray-600'
                  }`}>
                    {stat.change}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
        
        {/* Budget Overview */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <DollarSign className="h-5 w-5 mr-2" />
              Budget Overview
            </h3>
          </div>
          <div className="space-y-4">
            {Object.entries(budget_summary).map(([dept, budget]) => (
              <div key={dept} className="border-b border-gray-100 pb-3 last:border-b-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-900">{dept}</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    budget.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {budget.utilization.toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      budget.utilization > 80 ? 'bg-red-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(budget.utilization, 100)}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  ${budget.available.toLocaleString()} available
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <BarChart3 className="h-5 w-5 mr-2" />
              Performance Metrics
            </h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Order Fulfillment</span>
              <span className="font-semibold text-green-600">
                {performance_metrics.average_order_fulfillment_time} days
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Inventory Turnover</span>
              <span className="font-semibold text-blue-600">
                {performance_metrics.inventory_turnover_rate}x
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Stockout Incidents</span>
              <span className="font-semibold text-red-600">
                {performance_metrics.stockout_incidents}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Supplier Performance</span>
              <span className="font-semibold text-green-600">
                {performance_metrics.supplier_performance_avg}%
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Cost Savings YTD</span>
              <span className="font-semibold text-green-600">
                ${performance_metrics.cost_savings_ytd.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Waste Reduction</span>
              <span className="font-semibold text-green-600">
                {performance_metrics.waste_reduction_percentage}%
              </span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
          </div>
          <div className="space-y-3">
            <button 
              onClick={handleCreatePurchaseOrder} 
              className="w-full btn btn-primary flex items-center justify-center"
              disabled={actionLoading === 'po'}
            >
              {actionLoading === 'po' ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <ShoppingCart className="h-4 w-4 mr-2" />
              )}
              Create Purchase Order
            </button>
            <button 
              onClick={handleTransferInventory} 
              className="w-full btn btn-secondary flex items-center justify-center"
              disabled={actionLoading === 'transfer'}
            >
              {actionLoading === 'transfer' ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <MapPin className="h-4 w-4 mr-2" />
              )}
              Transfer Inventory
            </button>
            <button 
              onClick={handleReviewAlerts} 
              className="w-full btn btn-secondary flex items-center justify-center"
            >
              <AlertTriangle className="h-4 w-4 mr-2" />
              Review Alerts
            </button>
            <button 
              onClick={handleGenerateReport} 
              className="w-full btn btn-secondary flex items-center justify-center"
              disabled={actionLoading === 'report'}
            >
              {actionLoading === 'report' ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <BarChart3 className="h-4 w-4 mr-2" />
              )}
              Generate Report
            </button>
            <button 
              onClick={handleComplianceCheck} 
              className="w-full btn btn-secondary flex items-center justify-center"
              disabled={actionLoading === 'compliance'}
            >
              {actionLoading === 'compliance' ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Shield className="h-4 w-4 mr-2" />
              )}
              Compliance Check
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Clock className="h-5 w-5 mr-2" />
            Recent Activity
          </h3>
          <button 
            onClick={handleViewAllActivities} 
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View All
          </button>
        </div>
        <div className="space-y-3">
          {recentActivities.map((activity, index) => (
            <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center">
                <div className={`w-2 h-2 rounded-full mr-3 ${
                  activity.type === 'success' ? 'bg-green-500' :
                  activity.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                }`}></div>
                <div>
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.item} • {activity.location}</p>
                </div>
              </div>
              <span className="text-xs text-gray-500">{activity.time}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Activity Modal (for viewing all activities) */}
      {showActivityModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <div className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">All Recent Activities</h3>
                <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
                  {allActivities.filter(activity => 
                    activityFilter === 'all' || activity.type === activityFilter
                  ).length} items
                </span>
              </div>
              <button 
                onClick={() => setShowActivityModal(false)} 
                className="text-gray-400 hover:text-gray-600 transition-colors p-1 hover:bg-gray-100 rounded"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Filter Controls */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center space-x-4">
                <Filter className="h-4 w-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Filter by type:</span>
                <div className="flex space-x-2">
                  {['all', 'success', 'warning', 'info'].map((type) => (
                    <button
                      key={type}
                      onClick={() => setActivityFilter(type)}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        activityFilter === type
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                      }`}
                    >
                      {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Activity List */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="space-y-4">
                {allActivities
                  .filter(activity => activityFilter === 'all' || activity.type === activityFilter)
                  .map((activity) => (
                  <div key={activity.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3 flex-1">
                        <div className={`w-3 h-3 rounded-full mt-1 flex-shrink-0 ${
                          activity.type === 'success' ? 'bg-green-500' :
                          activity.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                        }`}></div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-gray-900">{activity.action}</p>
                          <p className="text-sm text-gray-600 mt-1">{activity.item} • {activity.location}</p>
                          <p className="text-xs text-gray-500 mt-2">{activity.details}</p>
                          <div className="flex items-center mt-2 space-x-4">
                            <span className="text-xs text-gray-400">by {activity.user}</span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              activity.type === 'success' ? 'bg-green-100 text-green-800' :
                              activity.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                            }`}>
                              {activity.type}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0 ml-4">
                        <span className="text-xs font-medium text-gray-500">{activity.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              
              {allActivities.filter(activity => activityFilter === 'all' || activity.type === activityFilter).length === 0 && (
                <div className="text-center py-8">
                  <Clock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500">No activities found for this filter</p>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-lg">
              <div className="flex justify-between items-center">
                <p className="text-xs text-gray-500">
                  Showing activities from the last 24 hours
                </p>
                <button
                  onClick={() => setShowActivityModal(false)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfessionalDashboard;
