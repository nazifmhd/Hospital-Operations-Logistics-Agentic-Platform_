import React from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { AlertTriangle, CheckCircle, Clock, X } from 'lucide-react';

const AlertsPanel = () => {
  const { dashboardData, resolveAlert, loading } = useSupplyData();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const alerts = dashboardData?.alerts || [];
  const validAlerts = alerts.filter(alert => alert && alert.id); // Filter out null/undefined alerts
  const activeAlerts = validAlerts.filter(alert => !alert.resolved);
  const criticalAlerts = activeAlerts.filter(alert => alert.level === 'critical');
  const highAlerts = activeAlerts.filter(alert => alert.level === 'high');
  const mediumAlerts = activeAlerts.filter(alert => alert.level === 'medium');
  const lowAlerts = activeAlerts.filter(alert => alert.level === 'low');

  const handleResolveAlert = async (alertId) => {
    try {
      await resolveAlert(alertId);
    } catch (error) {
      console.error('Failed to resolve alert:', error);
      alert('Failed to resolve alert');
    }
  };

  const getAlertIcon = (level) => {
    switch (level) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'medium':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-blue-500" />;
    }
  };

  const getAlertStyle = (level) => {
    switch (level) {
      case 'critical':
        return 'border-l-red-500 bg-red-50';
      case 'high':
        return 'border-l-orange-500 bg-orange-50';
      case 'medium':
        return 'border-l-yellow-500 bg-yellow-50';
      default:
        return 'border-l-blue-500 bg-blue-50';
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const AlertSection = ({ title, alerts, defaultExpanded = true }) => {
    const [expanded, setExpanded] = React.useState(defaultExpanded);

    if (alerts.length === 0) return null;

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div 
          className="px-6 py-4 border-b border-gray-200 cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            <div className="flex items-center space-x-2">
              <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded-full text-sm font-medium">
                {alerts.length}
              </span>
              <button className="text-gray-400 hover:text-gray-600">
                {expanded ? '−' : '+'}
              </button>
            </div>
          </div>
        </div>
        
        {expanded && (
          <div className="divide-y divide-gray-200">
            {alerts.map((alert) => (
              <div
                key={alert.id || Math.random()} // Fallback key
                className={`p-4 border-l-4 ${getAlertStyle(alert.level || 'low')}`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    {getAlertIcon(alert.level)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h4 className="text-sm font-medium text-gray-900">
                          {alert.type?.replace('_', ' ')?.toUpperCase() || 'ALERT'}
                        </h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          alert.level === 'critical' ? 'bg-red-100 text-red-800' :
                          alert.level === 'high' ? 'bg-orange-100 text-orange-800' :
                          alert.level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {alert.level?.toUpperCase() || 'UNKNOWN'}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">
                        {alert.message || 'No message available'}
                      </p>
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                        <span>Item ID: {alert.item_id || 'Unknown'}</span>
                        <span>{formatTime(alert.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleResolveAlert(alert.id)}
                    className="ml-3 p-2 rounded-md text-gray-400 hover:text-gray-600 hover:bg-white transition-colors"
                    title="Resolve alert"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-white shadow-sm rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center">
          <AlertTriangle className="h-6 w-6 mr-2" />
          Alert Management
        </h1>
        <p className="mt-2 text-gray-600">
          Monitor and manage all supply inventory alerts
        </p>
      </div>

      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-red-500">
              <AlertTriangle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Critical</p>
              <p className="text-2xl font-bold text-red-600">{criticalAlerts.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-orange-500">
              <AlertTriangle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">High</p>
              <p className="text-2xl font-bold text-orange-600">{highAlerts.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-yellow-500">
              <Clock className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Medium</p>
              <p className="text-2xl font-bold text-yellow-600">{mediumAlerts.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-500">
              <AlertTriangle className="h-6 w-6 text-white" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Low</p>
              <p className="text-2xl font-bold text-blue-600">{lowAlerts.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts Sections */}
      {activeAlerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <CheckCircle className="h-16 w-16 mx-auto text-green-500 mb-4" />
          <h2 className="text-xl font-medium text-gray-900 mb-2">No Active Alerts</h2>
          <p className="text-gray-600">All systems are operating normally</p>
        </div>
      ) : (
        <>
          <AlertSection title="Critical Alerts" alerts={criticalAlerts} />
          <AlertSection title="High Priority Alerts" alerts={highAlerts} />
          <AlertSection title="Medium Priority Alerts" alerts={mediumAlerts} />
          <AlertSection title="Low Priority Alerts" alerts={lowAlerts} />
        </>
      )}

      {/* Quick Actions */}
      {activeAlerts.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={async () => {
                try {
                  const lowPriorityAlerts = activeAlerts.filter(alert => alert.level === 'low');
                  for (const alert of lowPriorityAlerts) {
                    await handleResolveAlert(alert.id);
                  }
                  alert(`Resolved ${lowPriorityAlerts.length} low priority alerts`);
                } catch (error) {
                  console.error('Failed to resolve alerts:', error);
                  alert('Failed to resolve some alerts');
                }
              }}
              disabled={lowAlerts.length === 0}
              className={`btn ${lowAlerts.length === 0 ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-secondary hover:bg-gray-300'}`}
            >
              Resolve All Low Priority ({lowAlerts.length})
            </button>
            <button 
              onClick={() => {
                const reportData = {
                  timestamp: new Date().toISOString(),
                  summary: {
                    total_alerts: activeAlerts.length,
                    critical: criticalAlerts.length,
                    high: highAlerts.length,
                    medium: mediumAlerts.length,
                    low: lowAlerts.length
                  },
                  alerts: activeAlerts
                };
                
                const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `alerts_report_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
              }}
              className="btn btn-primary"
            >
              Generate Report
            </button>
            <button 
              onClick={() => {
                const csvContent = [
                  ['ID', 'Type', 'Level', 'Message', 'Item ID', 'Created At'],
                  ...activeAlerts.map(alert => [
                    alert.id || '',
                    alert.type || '',
                    alert.level || '',
                    alert.message || '',
                    alert.item_id || '',
                    alert.created_at || ''
                  ])
                ].map(row => row.join(',')).join('\n');
                
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `alerts_export_${new Date().toISOString().split('T')[0]}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
              }}
              className="btn btn-secondary"
            >
              Export Alerts
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;
