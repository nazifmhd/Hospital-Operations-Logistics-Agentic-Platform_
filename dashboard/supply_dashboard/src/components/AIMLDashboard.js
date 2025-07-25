import React, { useState, useEffect } from 'react';
import { 
    Chart as ChartJS, 
    CategoryScale, 
    LinearScale, 
    PointElement, 
    LineElement, 
    Title, 
    Tooltip, 
    Legend,
    BarElement
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const AIMLDashboard = () => {
    const [aiStatus, setAiStatus] = useState(null);
    const [workflowStatus, setWorkflowStatus] = useState(null);
    const [forecast, setForecast] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
    const [optimization, setOptimization] = useState(null);
    const [insights, setInsights] = useState(null);
    const [selectedItem, setSelectedItem] = useState('');
    const [loading, setLoading] = useState(false);
    const [inventory, setInventory] = useState([]);

    useEffect(() => {
        console.log('AIMLDashboard mounted - fetching initial data...');
        fetchAIStatus();
        fetchWorkflowStatus();
        fetchInventory();
        fetchAnomalies();
        fetchOptimization();
        fetchInsights();
        
        // Auto-refresh every 30 seconds
        const interval = setInterval(() => {
            fetchAIStatus();
            fetchWorkflowStatus();
        }, 30000);
        
        return () => clearInterval(interval);
    }, []);

    const fetchAIStatus = async () => {
        try {
            console.log('Fetching AI status from: http://localhost:8000/api/v2/ai/status');
            const response = await fetch('http://localhost:8000/api/v2/ai/status');
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('AI Status received:', data);
            console.log('ai_ml_available:', data.ai_ml_available);
            console.log('ai_ml_initialized:', data.ai_ml_initialized);
            setAiStatus(data);
        } catch (error) {
            console.error('Error fetching AI status:', error);
            setAiStatus({ error: error.message, ai_ml_available: false, ai_ml_initialized: false });
        }
    };

    const fetchWorkflowStatus = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/v2/workflow/status');
            const data = await response.json();
            setWorkflowStatus(data);
        } catch (error) {
            console.error('Error fetching workflow status:', error);
        }
    };

    const fetchInventory = async () => {
        try {
            console.log('Fetching inventory...');
            const response = await fetch('http://localhost:8000/api/v2/inventory');
            const data = await response.json();
            console.log('Inventory data received:', data);
            
            // Handle different response formats: direct array, data.inventory, or data.items
            const inventoryItems = Array.isArray(data) ? data : (data.inventory || data.items || []);
            console.log('Processed inventory items:', inventoryItems);
            
            // Remove duplicates based on item_id
            const uniqueInventoryItems = inventoryItems.filter((item, index, self) => 
                index === self.findIndex(i => i.item_id === item.item_id)
            );
            console.log('Unique inventory items:', uniqueInventoryItems.length, 'from', inventoryItems.length);
            
            setInventory(uniqueInventoryItems);
            if (uniqueInventoryItems.length > 0) {
                const firstItem = uniqueInventoryItems[0].item_id;
                console.log('Setting selected item to:', firstItem);
                setSelectedItem(firstItem);
            }
        } catch (error) {
            console.error('Error fetching inventory:', error);
        }
    };

    const fetchForecast = async (itemId) => {
        if (!itemId) return;
        console.log('Fetching forecast for item:', itemId);
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8000/api/v2/ai/forecast/${itemId}?days=30`);
            const data = await response.json();
            console.log('Forecast data received:', data);
            setForecast(data);
        } catch (error) {
            console.error('Error fetching forecast:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAnomalies = async () => {
        try {
            console.log('Fetching anomalies...');
            const response = await fetch('http://localhost:8000/api/v2/ai/anomalies');
            const data = await response.json();
            console.log('Anomalies data received:', data);
            setAnomalies(data.anomalies || []);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
        }
    };

    const fetchOptimization = async () => {
        try {
            console.log('Fetching optimization...');
            const response = await fetch('http://localhost:8000/api/v2/ai/optimization');
            const data = await response.json();
            console.log('Optimization data received:', data);
            setOptimization(data.optimization_results);
        } catch (error) {
            console.error('Error fetching optimization:', error);
        }
    };

    const fetchInsights = async () => {
        try {
            console.log('Fetching insights...');
            const response = await fetch('http://localhost:8000/api/v2/ai/insights');
            const data = await response.json();
            console.log('Insights data received:', data);
            setInsights(data.insights);
        } catch (error) {
            console.error('Error fetching insights:', error);
        }
    };

    const initializeAI = async () => {
        try {
            await fetch('http://localhost:8000/api/v2/ai/initialize', { method: 'POST' });
            setTimeout(fetchAIStatus, 2000); // Check status after 2 seconds
        } catch (error) {
            console.error('Error initializing AI:', error);
        }
    };

    useEffect(() => {
        if (selectedItem) {
            fetchForecast(selectedItem);
        }
    }, [selectedItem]);

    const forecastChartData = forecast ? {
        labels: Array.from({ length: forecast.predictions.length }, (_, i) => `Day ${i + 1}`),
        datasets: [
            {
                label: 'Demand Forecast',
                data: forecast.predictions,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            },
            {
                label: 'Lower Bound',
                data: forecast.confidence_intervals.map(ci => ci[0]),
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderDash: [5, 5],
                tension: 0.1
            },
            {
                label: 'Upper Bound',
                data: forecast.confidence_intervals.map(ci => ci[1]),
                borderColor: 'rgb(54, 162, 235)',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                borderDash: [5, 5],
                tension: 0.1
            }
        ]
    } : null;

    const getSeverityColor = (severity) => {
        switch (severity?.toLowerCase()) {
            case 'high': return 'text-red-600 bg-red-100';
            case 'medium': return 'text-yellow-600 bg-yellow-100';
            case 'low': return 'text-blue-600 bg-blue-100';
            default: return 'text-gray-600 bg-gray-100';
        }
    };

    return (
        <div className="p-6 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        🤖 AI/ML Analytics Dashboard
                    </h1>
                    <p className="text-gray-600">
                        Advanced predictive analytics and intelligent optimization for hospital supply management
                    </p>
                </div>

                {/* AI Status Card */}
                <div className="mb-6 bg-white rounded-lg shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-xl font-semibold mb-2">AI/ML Engine Status</h2>
                            <div className="flex items-center space-x-4">
                                <span className={`px-3 py-1 rounded-full text-sm ${
                                    aiStatus === null 
                                        ? 'bg-yellow-100 text-yellow-800'
                                        : (aiStatus?.ai_ml_available && aiStatus?.ai_ml_initialized)
                                            ? 'bg-green-100 text-green-800' 
                                            : 'bg-red-100 text-red-800'
                                }`}>
                                    {aiStatus === null 
                                        ? '🔄 Loading...' 
                                        : ((aiStatus?.ai_ml_available && aiStatus?.ai_ml_initialized) || (aiStatus?.ai_ml_available === true && aiStatus?.ai_ml_initialized === true) 
                                            ? '✅ Ready' 
                                            : '❌ Not Ready')
                                    }
                                </span>
                                <span className="text-sm text-gray-600">
                                    Capabilities: {aiStatus?.ai_ml_available ? 
                                        (aiStatus?.predictive_analytics?.enabled ? 1 : 0) + 
                                        (aiStatus?.demand_forecasting?.enabled ? 1 : 0) + 
                                        (aiStatus?.intelligent_optimization?.enabled ? 1 : 0) + 
                                        (aiStatus?.autonomous_agent?.enabled ? 1 : 0) : 0}
                                </span>
                                <button 
                                    onClick={fetchAIStatus}
                                    className="px-2 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
                                >
                                    Refresh Status
                                </button>
                            </div>
                        </div>
                        
                        
                        
                        {!(aiStatus?.ai_ml_available && aiStatus?.ai_ml_initialized) && (
                            <button
                                onClick={initializeAI}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Initialize AI Engine
                            </button>
                        )}
                    </div>
                </div>

                {/* AI/ML Capabilities Grid */}
                {aiStatus?.ai_ml_available && aiStatus?.ai_ml_initialized && (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        {/* Predictive Analytics */}
                        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">🔮</span>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">Predictive Analytics</h3>
                                        <p className="text-sm text-green-600">
                                            ✅ {aiStatus?.predictive_analytics?.enabled ? 'Active' : 'Inactive'}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-lg font-bold text-green-600">
                                        {(aiStatus?.predictive_analytics?.prediction_accuracy && typeof aiStatus.predictive_analytics.prediction_accuracy === 'number') 
                                            ? aiStatus.predictive_analytics.prediction_accuracy.toFixed(1) : '0'}%
                                    </div>
                                    <div className="text-xs text-gray-500">Accuracy</div>
                                </div>
                            </div>
                        </div>

                        {/* Demand Forecasting */}
                        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">📈</span>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">Demand Forecasting</h3>
                                        <p className="text-sm text-blue-600">
                                            ✅ {aiStatus?.demand_forecasting?.enabled ? 'Ready' : 'Disabled'}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-lg font-bold text-blue-600">
                                        {aiStatus?.demand_forecasting?.forecast_horizon_days || 0}
                                    </div>
                                    <div className="text-xs text-gray-500">Days Horizon</div>
                                </div>
                            </div>
                        </div>

                        {/* Intelligent Optimization */}
                        <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-purple-500">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">⚡</span>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">Smart Optimization</h3>
                                        <p className="text-sm text-purple-600">
                                            ✅ {aiStatus?.intelligent_optimization?.enabled ? 'Operational' : 'Disabled'}
                                        </p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-lg font-bold text-purple-600">
                                        {(aiStatus?.intelligent_optimization?.cost_savings_achieved && typeof aiStatus.intelligent_optimization.cost_savings_achieved === 'number') 
                                            ? aiStatus.intelligent_optimization.cost_savings_achieved.toFixed(1) : '0'}%
                                    </div>
                                    <div className="text-xs text-gray-500">Savings</div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Autonomous Operations Status */}
                {aiStatus?.ai_ml_available && aiStatus?.ai_ml_initialized && (
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6 border border-blue-200">
                        <div className="flex items-center mb-4">
                            <span className="text-3xl mr-3">🤖</span>
                            <div>
                                <h3 className="text-xl font-semibold text-gray-900">Autonomous Operations</h3>
                                <p className="text-blue-600">
                                    {aiStatus?.autonomous_agent?.automation_level || '100%'} Automation Mode - 
                                    System Making Real-time Decisions
                                </p>
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                                <div className="text-2xl font-bold text-green-600">
                                    {workflowStatus?.workflow_engine?.statistics?.approved_requests || 0}
                                </div>
                                <div className="text-sm font-medium">Auto Approvals</div>
                                <div className="text-xs text-gray-600">Completed</div>
                            </div>
                            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                                <div className="text-2xl font-bold text-blue-600">
                                    {workflowStatus?.auto_approval_service?.monitoring_status?.low_stock_items || 0}
                                </div>
                                <div className="text-sm font-medium">Inventory Monitoring</div>
                                <div className="text-xs text-gray-600">Items Tracked</div>
                            </div>
                            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                                <div className="text-2xl font-bold text-purple-600">
                                    {Math.round(aiStatus?.predictive_analytics?.prediction_accuracy || 0)}%
                                </div>
                                <div className="text-sm font-medium">Prediction Accuracy</div>
                                <div className="text-xs text-gray-600">AI Model</div>
                            </div>
                            <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                                <div className="text-2xl font-bold text-orange-600">
                                    {workflowStatus?.auto_approval_service?.monitoring_status?.emergency_items || 0}
                                </div>
                                <div className="text-sm font-medium">Critical Alerts</div>
                                <div className="text-xs text-gray-600">Active</div>
                            </div>
                        </div>

                        {/* Recent Autonomous Activities */}
                        {workflowStatus?.workflow_engine?.recent_activity?.recent_approvals && 
                         workflowStatus.workflow_engine.recent_activity.recent_approvals.length > 0 && (
                            <div className="mt-4">
                                <h4 className="text-lg font-semibold text-gray-900 mb-3">
                                    🕐 Recent Autonomous Activities
                                </h4>
                                <div className="bg-white rounded-lg p-4 shadow-sm">
                                    <div className="space-y-2 max-h-32 overflow-y-auto">
                                        {workflowStatus.workflow_engine.recent_activity.recent_approvals.slice(0, 3).map((approval, index) => (
                                            <div key={index} className="flex items-center justify-between p-2 bg-green-50 rounded">
                                                <div className="flex items-center">
                                                    <span className="text-green-600 mr-2">✅</span>
                                                    <span className="text-sm font-medium">{approval.item_name}</span>
                                                </div>
                                                <div className="text-right">
                                                    <div className="text-sm text-gray-600">
                                                        ${(approval.amount && typeof approval.amount === 'number') ? approval.amount.toFixed(2) : '0.00'}
                                                    </div>
                                                    <div className="text-xs text-gray-500">{approval.urgency}</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    {/* Demand Forecasting */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h2 className="text-xl font-semibold mb-4">📈 Demand Forecasting</h2>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Select Item:
                            </label>
                            <select
                                value={selectedItem}
                                onChange={(e) => setSelectedItem(e.target.value)}
                                className="w-full p-2 border border-gray-300 rounded-md"
                            >
                                {inventory.map(item => (
                                    <option key={item.item_id} value={item.item_id}>
                                        {item.name}
                                    </option>
                                ))}
                            </select>
                        </div>
                        
                        {loading ? (
                            <div className="flex items-center justify-center h-64">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                            </div>
                        ) : forecast && forecastChartData ? (
                            <div>
                                <div className="h-64 mb-4">
                                    <Line 
                                        data={forecastChartData} 
                                        options={{
                                            responsive: true,
                                            maintainAspectRatio: false,
                                            plugins: {
                                                title: {
                                                    display: true,
                                                    text: `30-Day Demand Forecast - ${forecast.item_name}`
                                                }
                                            }
                                        }}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <span className="font-medium">Method:</span> {forecast.method}
                                    </div>
                                    <div>
                                        <span className="font-medium">Accuracy:</span> {(forecast.accuracy_score && typeof forecast.accuracy_score === 'number') 
                                            ? (forecast.accuracy_score * 100).toFixed(1) : '0'}%
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 h-64 flex items-center justify-center">
                                Select an item to view forecast
                            </div>
                        )}
                    </div>

                    {/* Anomaly Detection */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h2 className="text-xl font-semibold mb-4">🚨 Anomaly Detection</h2>
                        {anomalies && anomalies.length > 0 ? (
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                {anomalies.map((anomaly, index) => (
                                    <div key={index} className="border rounded-lg p-3 bg-red-50">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-medium">{anomaly.item_id || 'No ID'}</span>
                                            <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(anomaly.severity)}`}>
                                                {anomaly.severity || 'unknown'}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600 mb-1">
                                            <strong>Type:</strong> {anomaly.anomaly_type || 'unknown'}
                                        </p>
                                        <p className="text-sm text-gray-600 mb-1">
                                            <strong>Score:</strong> {(anomaly.anomaly_score && typeof anomaly.anomaly_score === 'number') 
                                                ? anomaly.anomaly_score.toFixed(2) : '0.00'}
                                        </p>
                                        <p className="text-sm text-blue-600">
                                            💡 {anomaly.recommendation || 'No recommendation'}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 h-64 flex items-center justify-center">
                                <div>
                                    <p>✅ No anomalies detected</p>
                                    <p className="text-sm mt-2">All inventory levels are within normal ranges</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Optimization Results */}
                <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
                    <h2 className="text-xl font-semibold mb-4">⚡ Inventory Optimization</h2>
                    {optimization ? (
                        <div>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                                <div className="text-center p-3 bg-blue-50 rounded-lg">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {optimization.summary?.total_recommendations || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Total Recommendations</div>
                                    <div className="text-xs text-gray-500">Actions to take</div>
                                </div>
                                <div className="text-center p-3 bg-green-50 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">
                                        ${optimization.financial_impact?.total_monthly_savings?.toLocaleString() || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Monthly Savings</div>
                                    <div className="text-xs text-gray-500">Cost optimization</div>
                                </div>
                                <div className="text-center p-3 bg-purple-50 rounded-lg">
                                    <div className="text-2xl font-bold text-purple-600">
                                        {(optimization.performance_metrics?.overall_efficiency * 100)?.toFixed(1) || 'N/A'}%
                                    </div>
                                    <div className="text-sm text-gray-600">Efficiency Score</div>
                                    <div className="text-xs text-gray-500">Performance metric</div>
                                </div>
                                <div className="text-center p-3 bg-orange-50 rounded-lg">
                                    <div className="text-2xl font-bold text-orange-600">
                                        {optimization.summary?.redistribution_opportunities || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Critical Actions</div>
                                    <div className="text-xs text-gray-500">High priority items</div>
                                </div>
                            </div>
                            
                            {/* Enhanced Optimization Results */}
                            {optimization.recommendations && optimization.recommendations.length > 0 && (
                                <div className="space-y-6">
                                    {/* Financial Impact Summary */}
                                    {optimization.financial_impact && (
                                        <div className="bg-green-50 p-4 rounded-lg">
                                            <h3 className="font-semibold text-green-800 mb-2">💰 Financial Impact Analysis</h3>
                                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                                                <div>
                                                    <span className="font-medium">Total Monthly Savings:</span><br/>
                                                    <span className="text-green-600 font-bold">${optimization.financial_impact.total_monthly_savings}</span>
                                                </div>
                                                <div>
                                                    <span className="font-medium">ROI Percentage:</span><br/>
                                                    <span className="text-green-600 font-bold">{optimization.financial_impact.roi_percentage}%</span>
                                                </div>
                                                <div>
                                                    <span className="font-medium">Payback Period:</span><br/>
                                                    <span className="text-blue-600">{optimization.financial_impact.payback_period}</span>
                                                </div>
                                                <div>
                                                    <span className="font-medium">Implementation:</span><br/>
                                                    <span className="text-purple-600">{optimization.performance_metrics?.implementation_ease}</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}

                                    {/* Recommendations Table */}
                                    <div className="overflow-x-auto">
                                        <table className="min-w-full divide-y divide-gray-200">
                                            <thead className="bg-gray-50">
                                                <tr>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Recommendation
                                                    </th>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Item Details
                                                    </th>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Current Status
                                                    </th>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Action Required
                                                    </th>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Impact
                                                    </th>
                                                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                        Priority
                                                    </th>
                                                </tr>
                                            </thead>
                                            <tbody className="bg-white divide-y divide-gray-200">
                                                {optimization.recommendations.map((rec, index) => (
                                                    <tr key={index} className="hover:bg-gray-50">
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            <div>
                                                                <div className="font-medium text-gray-900">
                                                                    {rec.type === 'inventory_redistribution' ? '📦 Redistribution' : 
                                                                     rec.type === 'system_optimization' ? '⚡ System Optimization' : 
                                                                     rec.type || 'Optimization'}
                                                                </div>
                                                                <div className="text-xs text-gray-500">
                                                                    {rec.title || rec.type}
                                                                </div>
                                                            </div>
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            {rec.item_name ? (
                                                                <div>
                                                                    <div className="font-medium text-gray-900">{rec.item_name}</div>
                                                                    <div className="text-xs text-gray-500">{rec.item_id}</div>
                                                                    {rec.from_location && (
                                                                        <div className="text-xs text-blue-600">From: {rec.from_location}</div>
                                                                    )}
                                                                </div>
                                                            ) : (
                                                                <div className="text-sm text-gray-600">
                                                                    System-wide optimization
                                                                </div>
                                                            )}
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            {rec.current_stock !== undefined ? (
                                                                <div>
                                                                    <span className={`font-medium ${
                                                                        rec.current_stock === 0 ? 'text-red-600' : 
                                                                        rec.current_stock > (rec.minimum_threshold || 50) ? 'text-orange-600' :
                                                                        'text-gray-900'
                                                                    }`}>
                                                                        {rec.current_stock} units
                                                                    </span>
                                                                    {rec.minimum_threshold && (
                                                                        <div className="text-xs text-gray-500">
                                                                            Min: {rec.minimum_threshold}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ) : (
                                                                <div className="text-sm text-gray-600">
                                                                    {rec.total_items_analyzed ? `${rec.total_items_analyzed} items analyzed` : 'N/A'}
                                                                </div>
                                                            )}
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            {rec.recommended_transfer ? (
                                                                <div>
                                                                    <span className="font-medium text-blue-600">
                                                                        Transfer {rec.recommended_transfer} units
                                                                    </span>
                                                                    {rec.to_location && (
                                                                        <div className="text-xs text-gray-500">
                                                                            To: {rec.to_location}
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ) : rec.recommended_actions ? (
                                                                <div className="space-y-1">
                                                                    {rec.recommended_actions.slice(0, 2).map((action, i) => (
                                                                        <div key={i} className="text-xs text-blue-600">
                                                                            • {action}
                                                                        </div>
                                                                    ))}
                                                                </div>
                                                            ) : (
                                                                <span className="text-gray-500">No specific action</span>
                                                            )}
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            {rec.potential_cost_savings ? (
                                                                <div>
                                                                    <span className="font-medium text-green-600">
                                                                        {rec.potential_cost_savings}
                                                                    </span>
                                                                    {rec.efficiency_gain && (
                                                                        <div className="text-xs text-gray-500">
                                                                            +{rec.efficiency_gain} efficiency
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            ) : rec.estimated_monthly_savings ? (
                                                                <span className="font-medium text-green-600">
                                                                    ${rec.estimated_monthly_savings}/month
                                                                </span>
                                                            ) : (
                                                                <span className="text-gray-500">-</span>
                                                            )}
                                                        </td>
                                                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                                                rec.urgency === 'High' || rec.urgency === 'Critical' ? 'bg-red-100 text-red-800' :
                                                                rec.urgency === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                                                'bg-green-100 text-green-800'
                                                            }`}>
                                                                {rec.urgency || 'Low'}
                                                            </span>
                                                            {rec.confidence && (
                                                                <div className="text-xs text-gray-500 mt-1">
                                                                    {(rec.confidence * 100).toFixed(0)}% confidence
                                                                </div>
                                                            )}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>

                                    {/* Data Quality Indicators */}
                                    {optimization.quality_indicators && (
                                        <div className="bg-blue-50 p-4 rounded-lg">
                                            <h3 className="font-semibold text-blue-800 mb-2">📊 Analysis Quality</h3>
                                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                                                <div>
                                                    <span className="font-medium">Data Source:</span><br/>
                                                    <span className="text-blue-600">{optimization.data_source || 'Real-time'}</span>
                                                </div>
                                                <div>
                                                    <span className="font-medium">Method:</span><br/>
                                                    <span className="text-blue-600">{optimization.optimization_method}</span>
                                                </div>
                                                <div>
                                                    <span className="font-medium">Validation:</span><br/>
                                                    <span className="text-green-600">{optimization.quality_indicators.validation_status}</span>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 h-32 flex items-center justify-center">
                            Loading optimization results...
                        </div>
                    )}
                </div>

                {/* Predictive Insights */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h2 className="text-xl font-semibold mb-4">🔍 Predictive Insights</h2>
                    {insights ? (
                        <div>
                            {/* Insights Summary */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div className="text-center p-3 bg-blue-50 rounded-lg">
                                    <div className="text-2xl font-bold text-blue-600">
                                        {insights.length || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Total Insights</div>
                                    <div className="text-xs text-gray-500">AI-generated recommendations</div>
                                </div>
                                <div className="text-center p-3 bg-orange-50 rounded-lg">
                                    <div className="text-2xl font-bold text-orange-600">
                                        {insights.filter(i => i.impact === 'high').length || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">High Impact</div>
                                    <div className="text-xs text-gray-500">Critical insights</div>
                                </div>
                                <div className="text-center p-3 bg-green-50 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">
                                        {insights.filter(i => i.potential_savings).reduce((sum, i) => 
                                            sum + (parseInt(i.potential_savings?.replace(/[$,]/g, '')) || 0), 0) || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Potential Savings ($)</div>
                                    <div className="text-xs text-gray-500">Cost optimization</div>
                                </div>
                            </div>

                            {/* Insights List */}
                            <div className="space-y-4">
                                <h3 className="font-medium text-gray-900">🧠 AI-Generated Insights</h3>
                                {insights.length > 0 ? (
                                    <div className="space-y-3 max-h-96 overflow-y-auto">
                                        {insights.map((insight, index) => (
                                            <div key={index} className={`p-4 rounded-lg border-l-4 ${
                                                insight.impact === 'high' ? 'bg-red-50 border-red-400' :
                                                insight.impact === 'medium' ? 'bg-yellow-50 border-yellow-400' :
                                                'bg-blue-50 border-blue-400'
                                            }`}>
                                                {/* Insight Header */}
                                                <div className="flex items-start justify-between mb-2">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <span className={`text-sm font-medium px-2 py-1 rounded ${
                                                                insight.type === 'trend_analysis' ? 'bg-blue-100 text-blue-800' :
                                                                insight.type === 'cost_optimization' ? 'bg-green-100 text-green-800' :
                                                                insight.type === 'risk_assessment' ? 'bg-red-100 text-red-800' :
                                                                'bg-gray-100 text-gray-800'
                                                            }`}>
                                                                {insight.type === 'trend_analysis' ? '📈 Trend Analysis' :
                                                                 insight.type === 'cost_optimization' ? '💰 Cost Optimization' :
                                                                 insight.type === 'risk_assessment' ? '⚠️ Risk Assessment' :
                                                                 insight.type || 'Insight'}
                                                            </span>
                                                            <span className={`text-xs px-2 py-1 rounded-full ${
                                                                insight.impact === 'high' ? 'bg-red-100 text-red-600' :
                                                                insight.impact === 'medium' ? 'bg-yellow-100 text-yellow-600' :
                                                                'bg-green-100 text-green-600'
                                                            }`}>
                                                                {insight.impact} impact
                                                            </span>
                                                        </div>
                                                        <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                                                    </div>
                                                    {insight.confidence && (
                                                        <div className="text-right">
                                                            <div className="text-xs text-gray-500">Confidence</div>
                                                            <div className="text-sm font-medium text-gray-700">
                                                                {(insight.confidence * 100).toFixed(0)}%
                                                            </div>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Insight Content */}
                                                <p className="text-sm text-gray-700 mb-3">{insight.description}</p>

                                                {/* Insight Details */}
                                                <div className="flex items-center justify-between text-xs text-gray-600">
                                                    <div className="flex items-center gap-4">
                                                        {insight.data_points && (
                                                            <span>📊 {insight.data_points} data points</span>
                                                        )}
                                                        {insight.potential_savings && (
                                                            <span className="text-green-600 font-medium">
                                                                💵 {insight.potential_savings} savings
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>

                                                {/* Recommendation */}
                                                {insight.recommendation && (
                                                    <div className="mt-3 p-2 bg-white bg-opacity-60 rounded border">
                                                        <div className="text-xs font-medium text-gray-700 mb-1">💡 Recommendation:</div>
                                                        <div className="text-sm text-blue-700">{insight.recommendation}</div>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="text-center text-gray-500 py-8">
                                        <div className="text-gray-400 text-4xl mb-2">🤖</div>
                                        <p>No insights available at the moment</p>
                                        <p className="text-sm mt-1">AI analysis is continuously monitoring your inventory</p>
                                    </div>
                                )}

                                {/* Data Source Info */}
                                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center justify-between text-xs text-gray-600">
                                        <span>🔄 Data Source: Real-time inventory analysis</span>
                                        <span>🕒 Last Updated: {new Date().toLocaleTimeString()}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 h-32 flex items-center justify-center">
                            <div>
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                                <p>Loading predictive insights...</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AIMLDashboard;
