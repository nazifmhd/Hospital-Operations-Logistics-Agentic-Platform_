import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSupplyData } from '../context/SupplyDataContext';
import AgentChatInterface from './AgentChatInterface';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  DollarSign, 
  MapPin,
  Clock,
  ShoppingCart,
  BarChart3,
  Shield,
  X,
  Filter,
  Bot
} from 'lucide-react';

const ProfessionalDashboard = () => {
  const navigate = useNavigate();
  const { dashboardData, loading, error } = useSupplyData();
  const [actionLoading, setActionLoading] = useState(null);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [activityFilter, setActivityFilter] = useState('all');
  const [recentActivities, setRecentActivities] = useState([]);
  const [allActivities, setAllActivities] = useState([]);
  const [showAgentChat, setShowAgentChat] = useState(false);
  const [agentAvailable, setAgentAvailable] = useState(true); // Always available since it's self-contained
  const [llmAvailable, setLlmAvailable] = useState(false);

  // Fetch real-time activities from database only
  const fetchRecentActivities = useCallback(async () => {
    try {
      // Fetch from the main recent activity endpoint only
      const response = await fetch('http://localhost:8000/api/v2/recent-activity');
      
      if (response.ok) {
        const data = await response.json();
        const activities = data.activities || [];
        
        // Format activities for dashboard display
        const formattedActivities = activities.map(activity => ({
          id: activity.id,
          type: activity.type,
          action: activity.action,
          item: activity.item,
          location: activity.location,
          description: activity.description,
          details: activity.details,
          timestamp: activity.timestamp,
          user: activity.user,
          status: activity.status,
          icon: activity.icon || (
            activity.type === 'smart_distribution' ? '🎯' :
            activity.type === 'automated_supply_action' ? '�' : '🤖'
          ),
          time: new Date(activity.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })
        }));
        
        setRecentActivities(formattedActivities.slice(0, 5)); // Show 5 most recent in the dashboard
        setAllActivities(formattedActivities); // Show all in the modal
        
        console.log('Fetched recent activities:', formattedActivities.length);
      } else {
        console.error('Failed to fetch recent activities');
        setRecentActivities([]);
        setAllActivities([]);
      }
      
      if (allActivities.length === 0) {
        console.info('No activities found from any source');
      } else {
        console.log(`Using ${allActivities.length} activities from database and enhanced agent`);
      }
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      // No fallback - show empty state if all sources are unavailable
      setRecentActivities([]);
      setAllActivities([]);
    }
  }, []);

  // Check LLM availability
  const checkLLMAvailability = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v2/llm/status');
      if (response.ok) {
        const data = await response.json();
        setLlmAvailable(data.llm_available);
      }
    } catch (error) {
      console.warn('LLM service not available:', error);
      setLlmAvailable(false);
    }
  }, []);

  useEffect(() => {
    fetchRecentActivities();
    checkLLMAvailability();
    // Refresh activities every 60 seconds
    const interval = setInterval(fetchRecentActivities, 60000);
    return () => clearInterval(interval);
  }, [fetchRecentActivities]);

  // Quick Action Handlers
  const handleCreatePurchaseOrder = async () => {
    setActionLoading('po');
    try {
      // Create a new purchase order via API
      const response = await fetch('http://localhost:8000/api/v2/workflow/purchase_order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          department_id: 'DEPT-001',
          items: [
            {
              item_id: 'ITEM-001',
              quantity: 100,
              unit_price: 25.50,
              justification: 'Emergency restock - low inventory levels'
            }
          ],
          urgency: 'high',
          requested_by: 'System Admin',
          notes: 'Created via Quick Action - Professional Dashboard'
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ Purchase Order Created Successfully!\n\nOrder ID: ${result.order_id}\nStatus: ${result.status}\nTotal Items: ${result.total_items}\nTotal Value: $${result.total_value}\n\nRedirecting to workflow page...`);
        navigate('/workflow');
      } else {
        throw new Error('Failed to create purchase order');
      }
    } catch (error) {
      console.error('Error creating purchase order:', error);
      alert('Failed to create purchase order. Please try again.');
    } finally {
      setActionLoading(null);
    }
  };

  const handleTransferInventory = async () => {
    setActionLoading('transfer');
    try {
      // Create a smart transfer suggestion via API
      const response = await fetch('http://localhost:8000/api/v2/transfers/smart-suggestion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          analysis_type: 'urgent_rebalancing',
          include_critical_only: true
        })
      });

      if (response.ok) {
        const suggestions = await response.json();
        alert(`🤖 Smart Transfer Analysis Complete!\n\n${suggestions.recommendations.length} transfer opportunities identified.\n\nRedirecting to transfer management...`);
        navigate('/transfers', { state: { suggestions: suggestions.recommendations } });
      } else {
        // Fallback to regular navigation
        navigate('/transfers');
      }
    } catch (error) {
      console.error('Error generating transfer suggestions:', error);
      navigate('/transfers');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReviewAlerts = async () => {
    try {
      // Get alert summary before navigation
      const response = await fetch('http://localhost:8000/api/v2/alerts');
      if (response.ok) {
        const alerts = await response.json();
        const criticalCount = alerts.filter(a => a.priority === 'critical').length;
        const highCount = alerts.filter(a => a.priority === 'high').length;
        
        if (criticalCount > 0 || highCount > 0) {
          alert(`⚠️ Alert Summary:\n\n• ${criticalCount} Critical Alerts\n• ${highCount} High Priority Alerts\n\nRedirecting to alerts panel...`);
        }
      }
      navigate('/alerts');
    } catch (error) {
      console.error('Error fetching alert summary:', error);
      navigate('/alerts');
    }
  };

  const handleGenerateReport = async () => {
    setActionLoading('report');
    try {
      // Generate a comprehensive analytics report
      const response = await fetch('http://localhost:8000/api/v2/analytics/comprehensive-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_type: 'executive_summary',
          time_period: '30d',
          include_forecasting: true,
          include_recommendations: true
        })
      });

      if (response.ok) {
        const report = await response.json();
        alert(`📊 Analytics Report Generated!\n\nReport ID: ${report.report_id}\n• ${report.total_items_analyzed} items analyzed\n• ${report.insights_generated} insights generated\n• ${report.recommendations_count} recommendations\n\nRedirecting to analytics dashboard...`);
        navigate('/analytics', { state: { reportData: report } });
      } else {
        navigate('/analytics');
      }
    } catch (error) {
      console.error('Error generating analytics report:', error);
      navigate('/analytics');
    } finally {
      setActionLoading(null);
    }
  };

  const handleComplianceCheck = async () => {
    setActionLoading('compliance');
    try {
      const response = await fetch('http://localhost:8000/api/v2/analytics/compliance');
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

  const handleViewAllActivities = () => {
    setShowActivityModal(true);
  };

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
            {/* AI Agent Assistant Button */}
            {agentAvailable && (
              <button
                onClick={() => setShowAgentChat(true)}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                <Bot className="w-5 h-5" />
                <span className="font-medium">AI Assistant</span>
                <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">Agent</span>
              </button>
            )}
            
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
                      {type === 'all' ? 'All' : (type || '').charAt(0).toUpperCase() + (type || '').slice(1)}
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
                          <p className="text-xs text-gray-500 mt-2">
                            {typeof activity.details === 'string' ? activity.details : 
                             typeof activity.details === 'object' && activity.details ? 
                             `${activity.details.item_name || ''} ${activity.details.quantity ? `(${activity.details.quantity} units)` : ''} ${activity.details.department ? `in ${activity.details.department}` : ''}`.trim() :
                             activity.description || 'Activity details'
                            }
                          </p>
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

      {/* Comprehensive AI Agent Chat Interface */}
      {agentAvailable && showAgentChat && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-full max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold flex items-center">
                <Bot className="w-6 h-6 mr-2 text-blue-600" />
                AI Agent Assistant
              </h3>
              <button
                onClick={() => setShowAgentChat(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="flex-1 overflow-hidden">
              <AgentChatInterface />
            </div>
          </div>
        </div>
      )}

      {/* Floating AI Agent Button */}
      {agentAvailable && !showAgentChat && (
        <button
          onClick={() => setShowAgentChat(true)}
          className="fixed bottom-6 right-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl z-40 transition-all duration-200 hover:from-blue-700 hover:to-purple-700 group"
          title="Open AI Agent Assistant"
        >
          <Bot className="w-6 h-6 group-hover:scale-110 transition-transform" />
          <span className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
            AI Agent
          </span>
        </button>
      )}
    </div>
  );
};

export default ProfessionalDashboard;
