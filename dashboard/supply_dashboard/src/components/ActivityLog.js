import React, { useState } from 'react';
import { Clock, Filter, X, CheckCircle, AlertTriangle, Info } from 'lucide-react';

/**
 * ActivityLog Component
 * Displays activity logs with filtering capabilities
 */
const ActivityLog = ({ 
  activities = [], 
  title = "Activity Log", 
  showFilter = true, 
  maxHeight = "400px",
  compact = false 
}) => {
  const [filter, setFilter] = useState('all');

  const getActivityIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'info':
        return <Info className="h-4 w-4 text-blue-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-500';
      case 'warning':
        return 'bg-yellow-500';
      case 'info':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const filteredActivities = activities.filter(activity => 
    filter === 'all' || activity.type === filter
  );

  const activityTypes = ['all', ...new Set(activities.map(a => a.type))];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Clock className="h-5 w-5 mr-2 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <span className="ml-2 px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
              {filteredActivities.length} items
            </span>
          </div>
        </div>

        {/* Filter Controls */}
        {showFilter && activityTypes.length > 2 && (
          <div className="mt-3 flex items-center space-x-4">
            <Filter className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Filter:</span>
            <div className="flex space-x-2">
              {activityTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setFilter(type)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    filter === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  {type === 'all' ? 'All' : type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Activity List */}
      <div className="overflow-y-auto" style={{ maxHeight }}>
        <div className={compact ? "divide-y divide-gray-200" : "p-4 space-y-3"}>
          {filteredActivities.map((activity, index) => (
            <div 
              key={activity.id || index} 
              className={compact 
                ? "flex items-center justify-between py-3 px-4 hover:bg-gray-50" 
                : "bg-gray-50 border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              }
            >
              <div className="flex items-start space-x-3 flex-1">
                {compact ? (
                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${getActivityColor(activity.type)}`}></div>
                ) : (
                  <div className="mt-1">
                    {getActivityIcon(activity.type)}
                  </div>
                )}
                
                <div className="flex-1 min-w-0">
                  <p className={compact ? "text-sm font-medium text-gray-900" : "text-sm font-semibold text-gray-900"}>
                    {activity.action}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {activity.item} • {activity.location}
                  </p>
                  
                  {!compact && activity.details && (
                    <p className="text-xs text-gray-500 mt-2">{activity.details}</p>
                  )}
                  
                  {!compact && (
                    <div className="flex items-center mt-2 space-x-4">
                      {activity.user && (
                        <span className="text-xs text-gray-400">by {activity.user}</span>
                      )}
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        activity.type === 'success' ? 'bg-green-100 text-green-800' :
                        activity.type === 'warning' ? 'bg-yellow-100 text-yellow-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {activity.type}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="text-right flex-shrink-0 ml-4">
                <span className="text-xs font-medium text-gray-500">{activity.time}</span>
              </div>
            </div>
          ))}
        </div>

        {filteredActivities.length === 0 && (
          <div className="text-center py-8">
            <Clock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500">No activities found</p>
            {filter !== 'all' && (
              <button
                onClick={() => setFilter('all')}
                className="mt-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Show all activities
              </button>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      {!compact && (
        <div className="p-3 border-t border-gray-200 bg-gray-50 rounded-b-lg">
          <p className="text-xs text-gray-500 text-center">
            {activities.length > 0 
              ? `Showing ${filteredActivities.length} of ${activities.length} activities`
              : 'No activities recorded'
            }
          </p>
        </div>
      )}
    </div>
  );
};

export default ActivityLog;
