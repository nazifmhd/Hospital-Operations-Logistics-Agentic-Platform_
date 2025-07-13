import React from 'react';
import { useSupplyData } from '../context/SupplyDataContext';
import { AlertTriangle, Clock, X, CheckCircle } from 'lucide-react';

const AlertsOverview = ({ alerts = [] }) => {
  const { resolveAlert } = useSupplyData();

  // Filter out any null/undefined alerts
  const validAlerts = alerts.filter(alert => alert && alert.id);

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

  const getAlertColor = (level) => {
    switch (level) {
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'high':
        return 'bg-orange-50 border-orange-200';
      case 'medium':
        return 'bg-yellow-50 border-yellow-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await resolveAlert(alertId);
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2" />
          Active Alerts
        </h2>
      </div>
      
      <div className="overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          {!validAlerts || validAlerts.length === 0 ? (
            <div className="p-6 text-center text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto text-green-500 mb-3" />
              <p>No active alerts</p>
              <p className="text-sm">All systems operating normally</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {validAlerts.map((alert) => (
                <div
                  key={alert.id || Math.random()}
                  className={`p-4 border-l-4 ${getAlertColor(alert.level || 'low')}`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      {getAlertIcon(alert.level || 'low')}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900">
                          {alert.type?.replace('_', ' ')?.toUpperCase() || 'ALERT'}
                        </h4>
                        <p className="text-sm text-gray-700 mt-1">
                          {alert.message || 'No message available'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {alert.created_at ? formatTime(alert.created_at) : 'Time unknown'}
                        </p>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => alert.id && handleResolveAlert(alert.id)}
                      className="ml-3 p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                      title="Resolve alert"
                      disabled={!alert.id}
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                  
                  {/* Alert Level Badge */}
                  <div className="mt-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      alert.level === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.level === 'high' ? 'bg-orange-100 text-orange-800' :
                      alert.level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {alert.level?.toUpperCase() || 'UNKNOWN'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AlertsOverview;
