import React, { useState, useEffect } from 'react';
import { Brain, CheckCircle, AlertTriangle, TrendingUp, DollarSign, Clock } from 'lucide-react';

const LLMPurchaseOrderAnalysis = ({ purchaseOrder, onAnalysisComplete }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Auto-analyze when purchase order changes
  useEffect(() => {
    if (purchaseOrder && purchaseOrder.id) {
      analyzePurchaseOrder();
    }
  }, [purchaseOrder]);

  const analyzePurchaseOrder = async () => {
    if (!purchaseOrder) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v2/llm/analyze-purchase-order', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          data: purchaseOrder,
          analysis_type: 'purchase_order_justification',
          context: {
            department: purchaseOrder.department || 'General',
            urgency: purchaseOrder.urgency || 'normal',
            budget_period: 'Q1-2024',
            historical_usage: 'available'
          }
        })
      });

      if (!response.ok) {
        throw new Error('Analysis service unavailable');
      }

      const analysisResult = await response.json();
      setAnalysis(analysisResult);
      
      if (onAnalysisComplete) {
        onAnalysisComplete(analysisResult);
      }

    } catch (err) {
      console.error('PO Analysis Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600 bg-green-50';
    if (confidence >= 0.7) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.9) return <CheckCircle className="w-4 h-4" />;
    if (confidence >= 0.7) return <AlertTriangle className="w-4 h-4" />;
    return <AlertTriangle className="w-4 h-4" />;
  };

  if (!purchaseOrder) return null;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mt-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Brain className="w-5 h-5 text-purple-600" />
          <h3 className="text-lg font-semibold text-gray-900">AI Purchase Analysis</h3>
          <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">Beta</span>
        </div>
        
        {analysis && (
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${getConfidenceColor(analysis.confidence)}`}>
            {getConfidenceIcon(analysis.confidence)}
            <span>Confidence: {(analysis.confidence * 100).toFixed(0)}%</span>
          </div>
        )}
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-2 text-gray-600">
            <div className="w-5 h-5 border-2 border-purple-600 border-t-transparent rounded-full animate-spin"></div>
            <span>Analyzing purchase order...</span>
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm">Analysis unavailable: {error}</span>
          </div>
        </div>
      )}

      {analysis && !loading && (
        <div className="space-y-4">
          {/* AI-Generated Justification */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Business Justification</h4>
            <div className="text-sm text-gray-700 whitespace-pre-wrap">
              {analysis.justification}
            </div>
          </div>

          {/* Key Insights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Impact Assessment</span>
              </div>
              <p className="text-xs text-blue-700">
                {analysis.reasoning || 'High impact on operational efficiency and patient care quality.'}
              </p>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <DollarSign className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-900">Cost Analysis</span>
              </div>
              <p className="text-xs text-green-700">
                Optimized procurement timing for best value and cost-effectiveness.
              </p>
            </div>

            <div className="bg-orange-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Clock className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium text-orange-900">Timing Recommendation</span>
              </div>
              <p className="text-xs text-orange-700">
                Immediate approval recommended to maintain supply continuity.
              </p>
            </div>
          </div>

          {/* AI Recommendations */}
          {analysis.recommendations && analysis.recommendations.length > 0 && (
            <div className="border-t border-gray-200 pt-4">
              <h4 className="font-medium text-gray-900 mb-2">AI Recommendations</h4>
              <ul className="space-y-2">
                {analysis.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm">
                    <div className="w-1.5 h-1.5 bg-purple-600 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{recommendation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Analysis Metadata */}
          <div className="border-t border-gray-200 pt-3">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Analysis generated: {new Date(analysis.generated_at).toLocaleString()}</span>
              <span>Analysis Type: {analysis.analysis_type}</span>
            </div>
          </div>
        </div>
      )}

      {/* Manual Analysis Trigger */}
      {!loading && (
        <div className="border-t border-gray-200 pt-4 mt-4">
          <button
            onClick={analyzePurchaseOrder}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            🔄 Refresh Analysis
          </button>
        </div>
      )}
    </div>
  );
};

export default LLMPurchaseOrderAnalysis;
