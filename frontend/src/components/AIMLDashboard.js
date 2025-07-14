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
import { Line, Bar } from 'react-chartjs-2';

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
    const [forecast, setForecast] = useState(null);
    const [anomalies, setAnomalies] = useState([]);
    const [optimization, setOptimization] = useState(null);
    const [insights, setInsights] = useState(null);
    const [selectedItem, setSelectedItem] = useState('');
    const [loading, setLoading] = useState(false);
    const [inventory, setInventory] = useState([]);

    useEffect(() => {
        fetchAIStatus();
        fetchInventory();
        fetchAnomalies();
        fetchOptimization();
        fetchInsights();
    }, []);

    const fetchAIStatus = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/v2/ai/status');
            const data = await response.json();
            setAiStatus(data);
        } catch (error) {
            console.error('Error fetching AI status:', error);
        }
    };

    const fetchInventory = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/v2/inventory');
            const data = await response.json();
            setInventory(data.inventory || []);
            if (data.inventory && data.inventory.length > 0) {
                setSelectedItem(data.inventory[0].id);
            }
        } catch (error) {
            console.error('Error fetching inventory:', error);
        }
    };

    const fetchForecast = async (itemId) => {
        if (!itemId) return;
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:8001/api/v2/ai/forecast/${itemId}?days=30`);
            const data = await response.json();
            setForecast(data);
        } catch (error) {
            console.error('Error fetching forecast:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAnomalies = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/v2/ai/anomalies');
            const data = await response.json();
            setAnomalies(data.anomalies || []);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
        }
    };

    const fetchOptimization = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/v2/ai/optimization');
            const data = await response.json();
            setOptimization(data.optimization_results);
        } catch (error) {
            console.error('Error fetching optimization:', error);
        }
    };

    const fetchInsights = async () => {
        try {
            const response = await fetch('http://localhost:8001/api/v2/ai/insights');
            const data = await response.json();
            setInsights(data.insights);
        } catch (error) {
            console.error('Error fetching insights:', error);
        }
    };

    const initializeAI = async () => {
        try {
            await fetch('http://localhost:8001/api/v2/ai/initialize', { method: 'POST' });
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
                                    aiStatus?.status === 'ready' 
                                        ? 'bg-green-100 text-green-800' 
                                        : 'bg-red-100 text-red-800'
                                }`}>
                                    {aiStatus?.status === 'ready' ? '✅ Ready' : '❌ Not Ready'}
                                </span>
                                <span className="text-sm text-gray-600">
                                    Capabilities: {aiStatus?.capabilities?.length || 0}
                                </span>
                            </div>
                        </div>
                        {aiStatus?.status !== 'ready' && (
                            <button
                                onClick={initializeAI}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                            >
                                Initialize AI Engine
                            </button>
                        )}
                    </div>
                </div>

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
                                    <option key={item.id} value={item.id}>
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
                                        <span className="font-medium">Accuracy:</span> {(forecast.accuracy_score * 100).toFixed(1)}%
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
                        {anomalies.length > 0 ? (
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                {anomalies.map((anomaly, index) => (
                                    <div key={index} className="border rounded-lg p-3">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-medium">{anomaly.item_id}</span>
                                            <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(anomaly.severity)}`}>
                                                {anomaly.severity}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-600 mb-1">
                                            <strong>Type:</strong> {anomaly.anomaly_type}
                                        </p>
                                        <p className="text-sm text-gray-600 mb-1">
                                            <strong>Score:</strong> {anomaly.anomaly_score.toFixed(2)}
                                        </p>
                                        <p className="text-sm text-blue-600">
                                            💡 {anomaly.recommendation}
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
                                        {optimization.recommendations?.length || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Recommendations</div>
                                </div>
                                <div className="text-center p-3 bg-green-50 rounded-lg">
                                    <div className="text-2xl font-bold text-green-600">
                                        ${optimization.expected_savings?.toFixed(0) || 0}
                                    </div>
                                    <div className="text-sm text-gray-600">Expected Savings</div>
                                </div>
                                <div className="text-center p-3 bg-purple-50 rounded-lg">
                                    <div className="text-2xl font-bold text-purple-600">
                                        {optimization.optimization_method || 'N/A'}
                                    </div>
                                    <div className="text-sm text-gray-600">Method Used</div>
                                </div>
                                <div className="text-center p-3 bg-orange-50 rounded-lg">
                                    <div className="text-2xl font-bold text-orange-600">
                                        {optimization.computation_time?.toFixed(2) || 0}s
                                    </div>
                                    <div className="text-sm text-gray-600">Computation Time</div>
                                </div>
                            </div>
                            
                            {optimization.recommendations && optimization.recommendations.length > 0 && (
                                <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                        <thead className="bg-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Item
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Action
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Reorder Point
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Order Quantity
                                                </th>
                                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                    Service Level
                                                </th>
                                            </tr>
                                        </thead>
                                        <tbody className="bg-white divide-y divide-gray-200">
                                            {optimization.recommendations.slice(0, 5).map((rec, index) => (
                                                <tr key={index}>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                        {rec.item_id}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {rec.action}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {rec.reorder_point?.toFixed(0) || 'N/A'}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {rec.order_quantity?.toFixed(0) || 'N/A'}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {(rec.service_level_target * 100)?.toFixed(1) || 'N/A'}%
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
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
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Demand Trends */}
                            <div>
                                <h3 className="font-medium mb-3">📊 Demand Trends</h3>
                                {Object.keys(insights.demand_trends || {}).length > 0 ? (
                                    <div className="space-y-2 max-h-40 overflow-y-auto">
                                        {Object.entries(insights.demand_trends).map(([itemId, trend]) => (
                                            <div key={itemId} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                                                <span className="text-sm font-medium">{itemId}</span>
                                                <span className={`text-sm px-2 py-1 rounded ${
                                                    trend.direction === 'Increasing' ? 'bg-green-100 text-green-800' :
                                                    trend.direction === 'Decreasing' ? 'bg-red-100 text-red-800' :
                                                    'bg-gray-100 text-gray-800'
                                                }`}>
                                                    {trend.direction} ({trend.trend_percentage?.toFixed(1)}%)
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-sm">No trend data available</p>
                                )}
                            </div>

                            {/* Risk Factors */}
                            <div>
                                <h3 className="font-medium mb-3">⚠️ Risk Factors</h3>
                                {insights.risk_factors && insights.risk_factors.length > 0 ? (
                                    <div className="space-y-2 max-h-40 overflow-y-auto">
                                        {insights.risk_factors.map((risk, index) => (
                                            <div key={index} className="p-2 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                                                <p className="text-sm font-medium text-yellow-800">{risk.risk_type}</p>
                                                <p className="text-xs text-yellow-700">{risk.description}</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-sm">No risk factors identified</p>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center text-gray-500 h-32 flex items-center justify-center">
                            Loading insights...
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AIMLDashboard;
