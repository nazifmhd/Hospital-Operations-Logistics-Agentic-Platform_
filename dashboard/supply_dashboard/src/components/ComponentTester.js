import React, { useState, useEffect } from 'react';

const ComponentTester = () => {
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);

  const testEndpoints = async () => {
    setLoading(true);
    const endpoints = [
      { name: 'Dashboard', url: '/api/v2/dashboard' },
      { name: 'Inventory', url: '/api/v2/inventory' },
      { name: 'Recent Activity', url: '/api/v2/recent-activity' },
      { name: 'Users', url: '/api/v2/users' },
      { name: 'User Roles', url: '/api/v2/users/roles' },
      { name: 'Batches', url: '/api/v2/batches' },
      { name: 'Locations', url: '/api/v2/locations' },
      { name: 'Transfers', url: '/api/v2/inventory/transfers-list' }
    ];

    const results = {};
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`http://localhost:8000${endpoint.url}`);
        const data = await response.json();
        results[endpoint.name] = {
          status: response.status,
          success: response.ok,
          dataSize: JSON.stringify(data).length,
          hasData: Object.keys(data).length > 0,
          error: null
        };
      } catch (error) {
        results[endpoint.name] = {
          status: 'error',
          success: false,
          dataSize: 0,
          hasData: false,
          error: error.message
        };
      }
    }
    
    setTestResults(results);
    setLoading(false);
  };

  useEffect(() => {
    testEndpoints();
  }, []);

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-4">Component & API Testing Dashboard</h2>
      
      <button 
        onClick={testEndpoints}
        disabled={loading}
        className="mb-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Testing...' : 'Retest All Endpoints'}
      </button>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(testResults).map(([name, result]) => (
          <div key={name} className={`p-4 rounded-lg border-2 ${
            result.success ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'
          }`}>
            <h3 className="font-semibold text-lg">{name}</h3>
            <div className="mt-2 space-y-1">
              <p className={`text-sm ${result.success ? 'text-green-700' : 'text-red-700'}`}>
                Status: {result.status}
              </p>
              <p className="text-sm text-gray-600">
                Data Size: {result.dataSize} bytes
              </p>
              <p className="text-sm text-gray-600">
                Has Data: {result.hasData ? '✅' : '❌'}
              </p>
              {result.error && (
                <p className="text-sm text-red-600">
                  Error: {result.error}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-lg mb-2">Component Status Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h4 className="font-medium">✅ Working Components:</h4>
            <ul className="text-sm space-y-1">
              <li>• Professional Dashboard (with activity data)</li>
              <li>• Inventory Table (with real inventory)</li>
              <li>• User Management (with user data)</li>
              <li>• Analytics (with charts)</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium">⚠️ Components Needing Attention:</h4>
            <ul className="text-sm space-y-1">
              <li>• Batch Management (empty batches)</li>
              <li>• Multi-Location Inventory (empty locations)</li>
              <li>• AI/ML Dashboard (depends on AI endpoints)</li>
              <li>• Transfer Management (needs transfer data)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComponentTester;
