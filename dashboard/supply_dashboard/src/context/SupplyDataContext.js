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
    const ws = new WebSocket(`ws://localhost:8000/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setWebsocket(ws);
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.type === 'dashboard_update' || message.type === 'initial_data') {
          setDashboardData(message.data);
          setLoading(false);
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWebsocket(null);
      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        fetchDashboardData();
      }, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
      // Fallback to HTTP API if WebSocket fails
      fetchDashboardData();
    };
    
    return () => {
      if (ws) {
        ws.close();
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
      const response = await axios.get(`${API_BASE_URL}/api/v2/dashboard`);
      let data = response.data;
      
      // If alerts or recommendations are empty, fetch sample data
      if (!data.alerts || data.alerts.length === 0) {
        try {
          const alertsResponse = await axios.get(`${API_BASE_URL}/api/v2/alerts/generate-sample`);
          data.alerts = alertsResponse.data.alerts || [];
        } catch (alertError) {
          console.warn('Could not fetch sample alerts:', alertError);
          data.alerts = [];
        }
      }
      
      if (!data.recommendations || data.recommendations.length === 0) {
        try {
          const recsResponse = await axios.get(`${API_BASE_URL}/api/v2/recommendations/generate-sample`);
          data.recommendations = recsResponse.data.recommendations || [];
        } catch (recError) {
          console.warn('Could not fetch sample recommendations:', recError);
          data.recommendations = [];
        }
      }
      
      setDashboardData(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error('Error fetching dashboard data:', err);
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
  const getUsageAnalytics = async (itemId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v2/analytics/usage/${itemId}`);
      return response.data;
    } catch (err) {
      throw new Error('Failed to fetch usage analytics');
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
    refreshData: fetchDashboardData
  };

  return (
    <SupplyDataContext.Provider value={value}>
      {children}
    </SupplyDataContext.Provider>
  );
};
