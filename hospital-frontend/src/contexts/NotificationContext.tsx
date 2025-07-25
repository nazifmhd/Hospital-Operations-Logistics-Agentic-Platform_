import React, { createContext, useContext, useEffect, useState } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';

interface Alert {
  id: string;
  type: string;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  department?: string;
  action_required?: boolean;
  read?: boolean;
}

interface NotificationContextType {
  alerts: Alert[];
  unreadCount: number;
  isConnected: boolean;
  markAsRead: (alertId: string) => void;
  clearAll: () => void;
  dismissAlert: (alertId: string) => void;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: React.ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const handleWebSocketMessage = (message: any) => {
    if (message.type === 'new_alert') {
      const newAlert: Alert = {
        ...message.data,
        read: false,
        timestamp: new Date().toISOString()
      };
      
      setAlerts(prev => [newAlert, ...prev].slice(0, 50)); // Keep last 50 alerts
    } else if (message.type === 'dashboard_update') {
      // Handle dashboard updates if needed
      console.log('Dashboard update received:', message.data);
    }
  };

  const { isConnected } = useWebSocket({
    url: 'ws://localhost:8000/ws',
    onMessage: handleWebSocketMessage,
    onConnect: () => console.log('Notifications WebSocket connected'),
    onDisconnect: () => console.log('Notifications WebSocket disconnected')
  });

  // Update unread count when alerts change
  useEffect(() => {
    const unread = alerts.filter(alert => !alert.read).length;
    setUnreadCount(unread);
  }, [alerts]);

  // Load initial notifications
  useEffect(() => {
    const loadInitialNotifications = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v2/notifications');
        if (response.ok) {
          const data = await response.json();
          setAlerts(data.notifications || []);
        }
      } catch (error) {
        console.error('Failed to load initial notifications:', error);
      }
    };

    loadInitialNotifications();
  }, []);

  const markAsRead = (alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId ? { ...alert, read: true } : alert
      )
    );
  };

  const clearAll = () => {
    setAlerts(prev => 
      prev.map(alert => ({ ...alert, read: true }))
    );
  };

  const dismissAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const value: NotificationContextType = {
    alerts,
    unreadCount,
    isConnected,
    markAsRead,
    clearAll,
    dismissAlert
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};
