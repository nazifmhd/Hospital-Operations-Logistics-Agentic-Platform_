import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShoppingCart, 
  MapPin, 
  AlertTriangle, 
  BarChart3, 
  Shield 
} from 'lucide-react';

/**
 * Standalone Quick Actions Component
 * This component provides quick access to key professional dashboard functions
 */
const QuickActions = ({ className = '' }) => {
  const navigate = useNavigate();
  const [actionLoading, setActionLoading] = useState(null);

  // Quick Action Handlers
  const handleCreatePurchaseOrder = async () => {
    setActionLoading('po');
    try {
      // Navigate to inventory page where purchase orders can be created from recommendations
      navigate('/inventory');
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
      // Navigate to the transfer management page
      navigate('/transfers');
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

  const actions = [
    {
      id: 'po',
      label: 'Create Purchase Order',
      icon: ShoppingCart,
      handler: handleCreatePurchaseOrder,
      type: 'primary',
      description: 'Generate new purchase orders from recommendations'
    },
    {
      id: 'transfer',
      label: 'Transfer Inventory',
      icon: MapPin,
      handler: handleTransferInventory,
      type: 'secondary',
      description: 'Move items between hospital locations'
    },
    {
      id: 'alerts',
      label: 'Review Alerts',
      icon: AlertTriangle,
      handler: handleReviewAlerts,
      type: 'secondary',
      description: 'Check and resolve system alerts'
    },
    {
      id: 'report',
      label: 'Generate Report',
      icon: BarChart3,
      handler: handleGenerateReport,
      type: 'secondary',
      description: 'Access analytics and reporting tools'
    },
    {
      id: 'compliance',
      label: 'Compliance Check',
      icon: Shield,
      handler: handleComplianceCheck,
      type: 'secondary',
      description: 'Run regulatory compliance verification'
    }
  ];

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
        <span className="text-xs text-gray-500">{actions.length} actions available</span>
      </div>
      
      <div className="space-y-3">
        {actions.map((action) => {
          const Icon = action.icon;
          const isLoading = actionLoading === action.id;
          
          return (
            <button
              key={action.id}
              onClick={action.handler}
              disabled={isLoading || actionLoading !== null}
              className={`w-full btn btn-${action.type} flex items-center justify-center disabled:opacity-50 transition-all duration-200 hover:shadow-md group`}
              title={action.description}
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              ) : (
                <Icon className="h-4 w-4 mr-2 group-hover:scale-110 transition-transform" />
              )}
              {isLoading ? 'Processing...' : action.label}
            </button>
          );
        })}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-100">
        <p className="text-xs text-gray-500 text-center">
          Quick actions provide instant access to key professional features
        </p>
      </div>
    </div>
  );
};

export default QuickActions;
