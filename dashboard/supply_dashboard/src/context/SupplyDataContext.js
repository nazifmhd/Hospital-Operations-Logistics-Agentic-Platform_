import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const SupplyDataContext = createContext();

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useSupplyData = () => {
  const context = useContext(SupplyDataContext);
  if (!context) {
    throw new Error('useSupplyData must be used within a SupplyDataProvider');
  }
  return context;
};

export const SupplyDataProvider = ({ children }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [websocket, setWebsocket] = useState(null);

  // Initialize WebSocket connection
  useEffect(() => {
    let reconnectTimeout;
    
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket(`ws://localhost:8000/ws`);
        
        ws.onopen = () => {
          console.log('✅ WebSocket connected');
          setWebsocket(ws);
          setError(null); // Clear connection errors when WebSocket connects
        };
        
        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'dashboard_update' || message.type === 'initial_data') {
              setDashboardData(message.data);
              setLoading(false);
              setError(null);
            }
          } catch (err) {
            console.error('Error parsing WebSocket message:', err);
          }
        };
        
        ws.onclose = (event) => {
          console.log('❌ WebSocket disconnected', event.code, event.reason);
          setWebsocket(null);
          
          // Only attempt reconnect if not a deliberate close
          if (event.code !== 1000) {
            console.log('⏳ Attempting to reconnect WebSocket in 5 seconds...');
            reconnectTimeout = setTimeout(() => {
              connectWebSocket();
            }, 5000);
          }
        };
        
        ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          // Don't set error here as we'll fallback to HTTP API
          console.log('🔄 Falling back to HTTP API');
        };
        
        return ws;
      } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        return null;
      }
    };
    
    // Initial WebSocket connection
    const ws = connectWebSocket();
    
    return () => {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      if (ws) {
        ws.close(1000, 'Component unmounting');
      }
    };
  }, []);

  // Fetch initial data via HTTP
  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Fetch dashboard data (fallback if WebSocket fails)
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null); // Clear any previous errors
      
      // Test connection first
      const healthCheck = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 });
      if (healthCheck.status !== 200) {
        throw new Error('Server health check failed');
      }
      
      const response = await axios.get(`${API_BASE_URL}/api/v3/dashboard`, { timeout: 10000 });
      let data = response.data;
      
      // Ensure alerts and recommendations are arrays (they should come from database now)
      if (!Array.isArray(data.alerts)) {
        console.warn('Alerts data is not an array, converting to empty array');
        data.alerts = [];
      }
      
      if (!Array.isArray(data.recommendations)) {
        console.warn('Recommendations data is not an array, converting to empty array');
        data.recommendations = [];
      }
      
      // Add default values for any missing properties
      data = {
        totalItems: 0,
        lowStockCount: 0,
        alertCount: 0,
        totalValue: 0,
        departments: [],
        alerts: [],
        recommendations: [],
        recentActivity: [],
        ...data
      };
      
      setDashboardData(data);
      setError(null);
      console.log('✅ Dashboard data loaded successfully');
    } catch (err) {
      console.error('❌ Error fetching dashboard data:', err);
      
      // Provide more specific error messages
      let errorMessage = 'Failed to connect to server';
      if (err.code === 'ECONNREFUSED') {
        errorMessage = 'Server is not running. Please start the backend server.';
      } else if (err.code === 'ENOTFOUND') {
        errorMessage = 'Cannot reach server. Check your network connection.';
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please check the backend logs.';
      } else if (err.response?.status === 404) {
        errorMessage = 'API endpoint not found. Server may be starting up.';
      } else if (err.message.includes('timeout')) {
        errorMessage = 'Connection timeout. Server may be busy.';
      }
      
      setError(errorMessage);
      
      // Set minimal default data to prevent UI crashes
      setDashboardData({
        totalItems: 0,
        lowStockCount: 0,
        alertCount: 0,
        totalValue: 0,
        departments: [],
        alerts: [],
        recommendations: [],
        recentActivity: [],
        connectionStatus: 'disconnected'
      });
    } finally {
      setLoading(false);
    }
  };

  // Update inventory
  const updateInventory = async (itemId, quantityChange, reason, location = "General") => {
    try {
      await axios.post(`${API_BASE_URL}/api/v2/inventory/update`, {
        item_id: itemId,
        location: location,
        quantity_change: quantityChange,
        reason: reason
      });
      
      // Always refresh data after inventory update to ensure UI is up to date
      await fetchDashboardData();
    } catch (err) {
      throw new Error('Failed to update inventory');
    }
  };

  // Resolve alert
  const resolveAlert = async (alertId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/v2/alerts/${alertId}/resolve`);
      
      // Refresh data if WebSocket is not connected
      if (!websocket) {
        await fetchDashboardData();
      }
    } catch (err) {
      throw new Error('Failed to resolve alert');
    }
  };

  // Get procurement recommendations
  const getProcurementRecommendations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v2/procurement/recommendations`);
      return response.data;
    } catch (err) {
      throw new Error('Failed to fetch recommendations');
    }
  };

  // Get usage analytics
  const getUsageAnalytics = async (itemId, cacheBust = null) => {
    try {
      const url = cacheBust 
        ? `${API_BASE_URL}/api/v2/analytics/usage/${itemId}?t=${cacheBust}`
        : `${API_BASE_URL}/api/v2/analytics/usage/${itemId}`;
      const response = await axios.get(url);
      return response.data;
    } catch (err) {
      throw new Error('Failed to fetch usage analytics');
    }
  };

  // Get multi-location inventory
  const getMultiLocationInventory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v3/inventory/multi-location`);
      return response.data;
    } catch (err) {
      throw new Error('Failed to fetch multi-location inventory');
    }
  };

  const value = {
    dashboardData,
    loading,
    error,
    updateInventory,
    resolveAlert,
    getProcurementRecommendations,
    getUsageAnalytics,
    getMultiLocationInventory,
    refreshData: fetchDashboardData
  };

  return (
    <SupplyDataContext.Provider value={value}>
      {children}
    </SupplyDataContext.Provider>
  );
};
