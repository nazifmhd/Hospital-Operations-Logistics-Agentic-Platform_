import React, { useState, useEffect, useMemo } from 'react';
import { 
  BellIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  FunnelIcon,
  XMarkIcon,
  ClockIcon,
  TruckIcon,
  ShieldCheckIcon,
  ArrowsRightLeftIcon
} from '@heroicons/react/24/outline';
import { format, formatDistanceToNow, isToday, isYesterday } from 'date-fns';

const EnhancedNotificationPanel = ({ notifications = [], onMarkAsRead, onClearAll, onRefresh }) => {
  const [filter, setFilter] = useState('all');
  const [groupBy, setGroupBy] = useState('type');
  const [showDetails, setShowDetails] = useState({});
  const [expandedGroups, setExpandedGroups] = useState({});

  // Notification type configurations
  const notificationConfig = {
    auto_transfer: {
      icon: ArrowsRightLeftIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      label: 'Auto Transfer',
      priority: 'normal'
    },
    multi_auto_transfer: {
      icon: TruckIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      label: 'Multi-Location Transfer',
      priority: 'high'
    },
    safety_buffer_transfer: {
      icon: ShieldCheckIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: 'Safety Buffer',
      priority: 'preventive'
    }
  };

  // Filter notifications
  const filteredNotifications = useMemo(() => {
    return notifications.filter(notification => {
      if (filter === 'all') return true;
      if (filter === 'unread') return notification.status === 'active';
      if (filter === 'transfers') return notification.type.includes('transfer');
      return notification.type === filter;
    });
  }, [notifications, filter]);

  // Group notifications
  const groupedNotifications = useMemo(() => {
    if (groupBy === 'none') return { 'All Notifications': filteredNotifications };
    
    const groups = {};
    
    filteredNotifications.forEach(notification => {
      let groupKey;
      
      switch (groupBy) {
        case 'type':
          groupKey = notificationConfig[notification.type]?.label || notification.type;
          break;
        case 'date':
          const date = new Date(notification.created_at);
          if (isToday(date)) groupKey = 'Today';
          else if (isYesterday(date)) groupKey = 'Yesterday';
          else groupKey = format(date, 'MMM dd, yyyy');
          break;
        case 'priority':
          groupKey = notificationConfig[notification.type]?.priority || 'normal';
          break;
        case 'item':
          groupKey = notification.data?.item_name || 'Unknown Item';
          break;
        default:
          groupKey = 'All';
      }
      
      if (!groups[groupKey]) groups[groupKey] = [];
      groups[groupKey].push(notification);
    });

    // Sort groups by priority/recency
    const sortedGroups = {};
    const sortedKeys = Object.keys(groups).sort((a, b) => {
      if (groupBy === 'priority') {
        const priorityOrder = { 'high': 0, 'normal': 1, 'preventive': 2 };
        return priorityOrder[a] - priorityOrder[b];
      }
      if (groupBy === 'date') {
        if (a === 'Today') return -1;
        if (b === 'Today') return 1;
        if (a === 'Yesterday') return -1;
        if (b === 'Yesterday') return 1;
      }
      return a.localeCompare(b);
    });
    
    sortedKeys.forEach(key => {
      sortedGroups[key] = groups[key].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
    });
    
    return sortedGroups;
  }, [filteredNotifications, groupBy]);

  const toggleDetails = (notificationId) => {
    setShowDetails(prev => ({
      ...prev,
      [notificationId]: !prev[notificationId]
    }));
  };

  const toggleGroup = (groupKey) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupKey]: !prev[groupKey]
    }));
  };

  const formatTimeAgo = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return 'Recently';
    }
  };

  const getNotificationSummary = (notification) => {
    const data = notification.data || {};
    const config = notificationConfig[notification.type] || {};
    
    switch (notification.type) {
      case 'auto_transfer':
        return `Transferred ${data.quantity || 0} units of ${data.item_name || 'item'} from ${data.from_location || 'source'} to ${data.to_location || 'destination'}`;
      
      case 'multi_auto_transfer':
        return `Multi-transfer: ${data.total_quantity || 0} units of ${data.item_name || 'item'} from ${data.source_count || 0} locations to ${data.to_location || 'destination'}`;
      
      case 'safety_buffer_transfer':
        return `Proactive transfer: ${data.quantity || 0} units of ${data.item_name || 'item'} to maintain safety buffer`;
      
      default:
        return data.details || 'Autonomous system activity';
    }
  };

  const getNotificationDetails = (notification) => {
    const data = notification.data || {};
    const details = [];
    
    if (data.item_id) details.push(`Item ID: ${data.item_id}`);
    if (data.transfer_id) details.push(`Transfer ID: ${data.transfer_id}`);
    if (data.priority) details.push(`Priority: ${data.priority.toUpperCase()}`);
    if (data.from_location) details.push(`From: ${data.from_location}`);
    if (data.to_location) details.push(`To: ${data.to_location}`);
    if (data.quantity) details.push(`Quantity: ${data.quantity} units`);
    
    return details;
  };

  if (!notifications.length) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center">
          <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No notifications</h3>
          <p className="mt-1 text-sm text-gray-500">
            All system activities will appear here when they occur.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <BellIcon className="h-6 w-6 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Notifications ({filteredNotifications.length})
            </h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onRefresh}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
              title="Refresh notifications"
            >
              <ClockIcon className="h-5 w-5" />
            </button>
            {onClearAll && (
              <button
                onClick={onClearAll}
                className="px-3 py-1 text-sm text-red-600 hover:text-red-800 transition-colors"
              >
                Clear All
              </button>
            )}
          </div>
        </div>
        
        {/* Filters and Controls */}
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <FunnelIcon className="h-4 w-4 text-gray-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Types</option>
              <option value="unread">Unread Only</option>
              <option value="auto_transfer">Auto Transfers</option>
              <option value="multi_auto_transfer">Multi-Transfers</option>
              <option value="safety_buffer_transfer">Safety Buffers</option>
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">Group by:</span>
            <select
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
              className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="type">Type</option>
              <option value="date">Date</option>
              <option value="priority">Priority</option>
              <option value="item">Item</option>
              <option value="none">No Grouping</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      <div className="max-h-96 overflow-y-auto">
        {Object.entries(groupedNotifications).map(([groupKey, groupNotifications]) => (
          <div key={groupKey} className="border-b border-gray-100 last:border-b-0">
            {/* Group Header */}
            {groupBy !== 'none' && (
              <div 
                className="px-6 py-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => toggleGroup(groupKey)}
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-medium text-gray-700">{groupKey}</h3>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded-full">
                      {groupNotifications.length}
                    </span>
                    <div className={`transform transition-transform ${expandedGroups[groupKey] ? 'rotate-90' : ''}`}>
                      ▶
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Group Content */}
            {(groupBy === 'none' || expandedGroups[groupKey] !== false) && (
              <div className="divide-y divide-gray-100">
                {groupNotifications.map((notification) => {
                  const config = notificationConfig[notification.type] || {};
                  const IconComponent = config.icon || InformationCircleIcon;
                  
                  return (
                    <div
                      key={notification.id}
                      className={`p-4 hover:bg-gray-50 transition-colors ${config.bgColor} border-l-4 ${config.borderColor}`}
                    >
                      <div className="flex items-start space-x-3">
                        <div className={`flex-shrink-0 ${config.color}`}>
                          <IconComponent className="h-6 w-6" />
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900">
                              {config.label || notification.type}
                            </p>
                            <div className="flex items-center space-x-2">
                              <span className="text-xs text-gray-500">
                                {formatTimeAgo(notification.created_at)}
                              </span>
                              <button
                                onClick={() => toggleDetails(notification.id)}
                                className="text-xs text-blue-600 hover:text-blue-800"
                              >
                                {showDetails[notification.id] ? 'Less' : 'More'}
                              </button>
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mt-1">
                            {getNotificationSummary(notification)}
                          </p>
                          
                          {/* Details Panel */}
                          {showDetails[notification.id] && (
                            <div className="mt-3 p-3 bg-white rounded-md border border-gray-200">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                {getNotificationDetails(notification).map((detail, index) => (
                                  <div key={index} className="text-gray-600">
                                    {detail}
                                  </div>
                                ))}
                              </div>
                              
                              {notification.data?.details && (
                                <div className="mt-2 text-xs text-gray-500 italic">
                                  {notification.data.details}
                                </div>
                              )}
                              
                              <div className="mt-2 text-xs text-gray-400">
                                Created: {format(new Date(notification.created_at), 'MMM dd, yyyy h:mm a')}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Summary Footer */}
      <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div>
            Showing {filteredNotifications.length} of {notifications.length} notifications
          </div>
          <div className="flex items-center space-x-4">
            {Object.entries(notificationConfig).map(([type, config]) => {
              const count = notifications.filter(n => n.type === type).length;
              if (count === 0) return null;
              
              return (
                <div key={type} className="flex items-center space-x-1">
                  <div className={`w-3 h-3 rounded-full ${config.bgColor} border ${config.borderColor}`} />
                  <span className="text-xs">{config.label}: {count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnhancedNotificationPanel;
