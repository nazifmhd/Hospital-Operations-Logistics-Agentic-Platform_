import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Wifi, WifiOff, RefreshCw } from 'lucide-react';

const ConnectionStatusBanner = ({ error, loading, onRetry }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState('checking');

  useEffect(() => {
    // Check connection status
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health', { 
          method: 'GET',
          timeout: 5000 
        });
        
        if (response.ok) {
          setConnectionStatus('connected');
        } else {
          setConnectionStatus('error');
        }
      } catch (err) {
        setConnectionStatus('disconnected');
      }
    };

    if (error || loading) {
      checkConnection();
      // Check every 10 seconds when there's an error
      const interval = setInterval(checkConnection, 10000);
      return () => clearInterval(interval);
    } else {
      setConnectionStatus('connected');
    }
  }, [error, loading]);

  const handleRetry = () => {
    setConnectionStatus('checking');
    if (onRetry) {
      onRetry();
    }
  };

  const handleDismiss = () => {
    setIsVisible(false);
  };

  // Don't show banner if no error and not loading
  if (!error && !loading && connectionStatus === 'connected') {
    return null;
  }

  // Don't show if manually dismissed
  if (!isVisible) {
    return null;
  }

  const getStatusConfig = () => {
    if (loading || connectionStatus === 'checking') {
      return {
        bgColor: 'bg-blue-50 border-blue-200',
        textColor: 'text-blue-800',
        icon: <RefreshCw className="h-5 w-5 animate-spin" />,
        title: 'Connecting...',
        message: 'Establishing connection to the hospital supply system.'
      };
    }

    if (error || connectionStatus === 'disconnected') {
      return {
        bgColor: 'bg-red-50 border-red-200',
        textColor: 'text-red-800',
        icon: <WifiOff className="h-5 w-5" />,
        title: 'Connection Error',
        message: error || 'Unable to connect to the backend server. Please ensure the server is running.'
      };
    }

    if (connectionStatus === 'error') {
      return {
        bgColor: 'bg-yellow-50 border-yellow-200',
        textColor: 'text-yellow-800',
        icon: <AlertTriangle className="h-5 w-5" />,
        title: 'Server Issues',
        message: 'The server is responding but there may be issues. Some features might be limited.'
      };
    }

    return {
      bgColor: 'bg-green-50 border-green-200',
      textColor: 'text-green-800',
      icon: <CheckCircle className="h-5 w-5" />,
      title: 'Connected',
      message: 'Successfully connected to the hospital supply system.'
    };
  };

  const config = getStatusConfig();

  return (
    <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-md w-full mx-4`}>
      <div className={`${config.bgColor} border rounded-lg p-4 shadow-lg`}>
        <div className="flex items-start">
          <div className={`${config.textColor} mr-3 mt-0.5`}>
            {config.icon}
          </div>
          <div className="flex-1">
            <h3 className={`text-sm font-medium ${config.textColor}`}>
              {config.title}
            </h3>
            <p className={`text-sm ${config.textColor} mt-1 opacity-90`}>
              {config.message}
            </p>
            {(error || connectionStatus === 'disconnected') && (
              <div className="mt-3 flex space-x-2">
                <button
                  onClick={handleRetry}
                  className={`text-xs px-3 py-1 rounded ${config.textColor} bg-white border border-current hover:bg-gray-50 transition-colors`}
                  disabled={connectionStatus === 'checking'}
                >
                  {connectionStatus === 'checking' ? 'Retrying...' : 'Retry Connection'}
                </button>
                <button
                  onClick={handleDismiss}
                  className={`text-xs px-3 py-1 rounded ${config.textColor} hover:opacity-75 transition-opacity`}
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>
          {!error && connectionStatus === 'connected' && (
            <button
              onClick={handleDismiss}
              className={`${config.textColor} hover:opacity-75 transition-opacity ml-2`}
            >
              ×
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionStatusBanner;
