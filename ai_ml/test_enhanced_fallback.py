#!/usr/bin/env python3
"""
Enhanced Fallback Response Quality Test
Tests the improved fallback system to ensure Gemini-quality responses
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_ai_agent import ComprehensiveAIAgent, ConversationContext

class FallbackQualityTester:
    def __init__(self):
        self.agent = None
        self.test_scenarios = [
            {
                "name": "Critical Inventory Alert",
                "message": "We're out of ventilator filters in ICU, this is urgent!",
                "expected_elements": [
                    "CRITICAL", "ICU", "ventilator filters", "urgent", 
                    "immediate action", "emergency suppliers", "recommendations"
                ],
                "mock_action_results": {
                    "get_inventory_status": {
                        "inventory": [
                            {
                                "name": "Ventilator Filter - HEPA",
                                "current_stock": 0,
                                "minimum_stock": 20,
                                "location": "ICU Storage",
                                "unit_cost": 45.00
                            },
                            {
                                "name": "IV Fluid 0.9% Saline",
                                "current_stock": 5,
                                "minimum_stock": 25,
                                "location": "ICU Pharmacy",
                                "unit_cost": 12.50
                            }
                        ]
                    },
                    "get_active_alerts": {
                        "alerts": [
                            {
                                "message": "Critical: Ventilator filters out of stock",
                                "severity": "critical",
                                "department": "ICU"
                            }
                        ]
                    }
                }
            },
            {
                "name": "Department Analytics Request",
                "message": "Can you show me analytics for Surgery department inventory performance?",
                "expected_elements": [
                    "Analytics", "Surgery", "performance", "metrics", "insights",
                    "trends", "optimization", "KPI"
                ],
                "mock_action_results": {
                    "get_inventory_status": {
                        "inventory": [
                            {
                                "name": "Surgical Sutures 3-0",
                                "current_stock": 150,
                                "minimum_stock": 100,
                                "location": "Surgery Storage",
                                "unit_cost": 8.75
                            },
                            {
                                "name": "Surgical Gloves Size 7",
                                "current_stock": 85,
                                "minimum_stock": 200,
                                "location": "Surgery Prep",
                                "unit_cost": 0.45
                            }
                        ]
                    }
                }
            },
            {
                "name": "General Procurement Inquiry",
                "message": "I need to order more lab reagents for blood testing",
                "expected_elements": [
                    "Procurement", "lab reagents", "blood testing", "recommendations",
                    "supplier", "quantity", "lead times"
                ],
                "mock_action_results": {
                    "get_inventory_status": {
                        "inventory": [
                            {
                                "name": "Blood Testing Reagent Kit",
                                "current_stock": 12,
                                "minimum_stock": 50,
                                "location": "Lab Storage",
                                "unit_cost": 125.00
                            }
                        ]
                    }
                }
            }
        ]
    
    async def setup_agent(self):
        """Initialize the agent for testing"""
        try:
            self.agent = ComprehensiveAIAgent()
            await self.agent.initialize()
            print("✅ Agent initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            # Create a minimal agent for testing
            self.agent = ComprehensiveAIAgent()
            self.agent.rag_system = None  # Will work without RAG for fallback testing
    
    async def test_fallback_quality(self, scenario):
        """Test fallback response quality for a specific scenario"""
        print(f"\n🧪 Testing: {scenario['name']}")
        print(f"📝 Message: {scenario['message']}")
        
        # Analyze the message intent
        intent_analysis = await self.agent._analyze_message_intent(scenario['message'])
        print(f"🎯 Detected Intent: {intent_analysis['primary_intent']}")
        print(f"🏷️  Entities: {intent_analysis['entities']}")
        
        # Generate fallback response
        fallback_response = await self.agent._generate_fallback_response(
            scenario['message'],
            intent_analysis,
            scenario['mock_action_results']
        )
        
        print(f"\n📄 Fallback Response ({len(fallback_response)} chars):")
        print("=" * 60)
        print(fallback_response)
        print("=" * 60)
        
        # Quality analysis
        quality_score = self.analyze_response_quality(fallback_response, scenario)
        print(f"\n📊 Quality Score: {quality_score['total_score']}/100")
        
        return {
            "scenario": scenario['name'],
            "response": fallback_response,
            "quality": quality_score,
            "length": len(fallback_response),
            "intent": intent_analysis['primary_intent']
        }
    
    def analyze_response_quality(self, response, scenario):
        """Analyze the quality of the fallback response"""
        quality_metrics = {
            "element_coverage": 0,  # How many expected elements are present
            "detail_level": 0,      # Level of detail and analysis
            "structure": 0,         # Organization and formatting
            "actionability": 0,     # Concrete next steps provided
            "context_awareness": 0   # Understanding of scenario context
        }
        
        response_lower = response.lower()
        
        # Element coverage (30 points)
        expected_elements = scenario['expected_elements']
        found_elements = sum(1 for element in expected_elements if element.lower() in response_lower)
        quality_metrics["element_coverage"] = min(30, (found_elements / len(expected_elements)) * 30)
        
        # Detail level (25 points)
        if len(response) > 1000:  # Comprehensive response
            quality_metrics["detail_level"] += 15
        elif len(response) > 500:  # Good detail
            quality_metrics["detail_level"] += 10
        elif len(response) > 200:  # Basic detail
            quality_metrics["detail_level"] += 5
        
        # Check for specific analysis elements
        analysis_indicators = ["analysis", "status", "recommendations", "insights", "metrics"]
        found_analysis = sum(1 for indicator in analysis_indicators if indicator in response_lower)
        quality_metrics["detail_level"] += min(10, found_analysis * 2)
        
        # Structure (20 points)
        structure_indicators = ["**", "•", "###", "####", "---", "Status", "Recommendations"]
        found_structure = sum(1 for indicator in structure_indicators if indicator in response)
        quality_metrics["structure"] = min(20, found_structure * 3)
        
        # Actionability (15 points)
        action_indicators = ["next steps", "recommended", "action", "contact", "implement", "review"]
        found_actions = sum(1 for indicator in action_indicators if indicator.lower() in response_lower)
        quality_metrics["actionability"] = min(15, found_actions * 3)
        
        # Context awareness (10 points)
        context_indicators = scenario.get('mock_action_results', {}).keys()
        context_elements = ["inventory", "alerts", "department", "stock", "critical", "urgent"]
        found_context = sum(1 for element in context_elements if element.lower() in response_lower)
        quality_metrics["context_awareness"] = min(10, found_context * 2)
        
        total_score = sum(quality_metrics.values())
        
        return {
            "metrics": quality_metrics,
            "total_score": round(total_score, 1),
            "grade": self.get_quality_grade(total_score),
            "found_elements": found_elements,
            "total_elements": len(expected_elements)
        }
    
    def get_quality_grade(self, score):
        """Convert numeric score to letter grade"""
        if score >= 90:
            return "A+ (Excellent - Gemini Quality)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Acceptable)"
        else:
            return "D (Needs Improvement)"
    
    async def run_comprehensive_test(self):
        """Run all test scenarios and generate report"""
        print("🚀 Starting Enhanced Fallback Quality Test")
        print("=" * 80)
        
        await self.setup_agent()
        
        results = []
        total_score = 0
        
        for scenario in self.test_scenarios:
            try:
                result = await self.test_fallback_quality(scenario)
                results.append(result)
                total_score += result['quality']['total_score']
            except Exception as e:
                print(f"❌ Error testing {scenario['name']}: {e}")
                results.append({
                    "scenario": scenario['name'],
                    "error": str(e),
                    "quality": {"total_score": 0}
                })
        
        # Generate final report
        self.generate_test_report(results, total_score)
        
        return results
    
    def generate_test_report(self, results, total_score):
        """Generate comprehensive test report"""
        print(f"\n📋 ENHANCED FALLBACK QUALITY TEST REPORT")
        print("=" * 80)
        
        avg_score = total_score / len(results) if results else 0
        overall_grade = self.get_quality_grade(avg_score)
        
        print(f"🎯 Overall Performance: {avg_score:.1f}/100 - {overall_grade}")
        print(f"🧪 Tests Completed: {len(results)}")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n📊 Individual Test Results:")
        print("-" * 60)
        
        for result in results:
            if 'error' in result:
                print(f"❌ {result['scenario']}: ERROR - {result['error']}")
            else:
                quality = result['quality']
                print(f"✅ {result['scenario']}:")
                print(f"   Score: {quality['total_score']}/100 ({quality['grade']})")
                print(f"   Length: {result['length']} characters")
                print(f"   Intent: {result['intent']}")
                print(f"   Elements Found: {quality['found_elements']}/{quality['total_elements']}")
        
        print(f"\n💡 Quality Assessment:")
        print("-" * 40)
        
        if avg_score >= 85:
            print("🎉 EXCELLENT: Fallback responses match Gemini quality!")
            print("   ✅ Detailed analysis and insights")
            print("   ✅ Professional formatting and structure")
            print("   ✅ Actionable recommendations")
            print("   ✅ Context-aware responses")
        elif avg_score >= 70:
            print("👍 GOOD: Fallback responses are high quality")
            print("   💡 Consider adding more detailed analysis")
            print("   💡 Enhance contextual awareness")
        else:
            print("⚠️  NEEDS IMPROVEMENT: Fallback quality below expectations")
            print("   🔧 Add more comprehensive analysis")
            print("   🔧 Improve response structure")
            print("   🔧 Include more actionable recommendations")
        
        print(f"\n🔍 Comparison with Requirements:")
        print(f"   Target: Gemini-quality responses (85+ score)")
        print(f"   Achieved: {avg_score:.1f}/100")
        print(f"   Status: {'✅ PASSED' if avg_score >= 85 else '⚠️ NEEDS WORK'}")

async def main():
    """Main test execution"""
    tester = FallbackQualityTester()
    
    try:
        results = await tester.run_comprehensive_test()
        
        # Save results for analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"fallback_quality_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
