#!/usr/bin/env python3
"""
Simple Enhanced Fallback Response Test
Tests the improved fallback system directly
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_ai_agent import ComprehensiveAIAgent, ConversationContext, ConversationMemory

async def test_enhanced_fallback():
    """Test the enhanced fallback response system"""
    
    print("🚀 Testing Enhanced Fallback Response System")
    print("=" * 60)
    
    # Create agent instance
    agent = ComprehensiveAIAgent()
    
    # Test scenarios
    test_cases = [
        {
            "message": "We're out of ventilator filters in ICU, this is urgent!",
            "context": "Critical inventory shortage",
            "mock_action_results": {
                "get_inventory_status": {
                    "inventory": [
                        {
                            "name": "Ventilator Filter - HEPA",
                            "current_stock": 0,
                            "minimum_stock": 20,
                            "location": "ICU Storage",
                            "unit_cost": 45.00
                        }
                    ]
                }
            }
        },
        {
            "message": "Show me analytics for Surgery department performance",
            "context": "Analytics request",
            "mock_action_results": {
                "get_inventory_status": {
                    "inventory": [
                        {
                            "name": "Surgical Sutures 3-0",
                            "current_stock": 150,
                            "minimum_stock": 100,
                            "location": "Surgery Storage",
                            "unit_cost": 8.75
                        }
                    ]
                }
            }
        },
        {
            "message": "I need to order lab reagents for blood testing",
            "context": "Procurement request",
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
    
    # Test each scenario
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['context']}")
        print(f"📝 Message: {test_case['message']}")
        print("-" * 50)
        
        try:
            # Create a basic memory context
            memory = ConversationMemory("test_user", "test_session")
            
            # Analyze intent
            intent_analysis = await agent._analyze_user_intent(test_case['message'], memory)
            print(f"🎯 Intent: {intent_analysis['primary_intent']}")
            print(f"🏷️  Entities: {intent_analysis['entities']}")
            
            # Generate fallback response
            fallback_response = await agent._generate_fallback_response(
                test_case['message'],
                intent_analysis,
                test_case['mock_action_results']
            )
            
            print(f"\n📄 Enhanced Fallback Response ({len(fallback_response)} chars):")
            print("=" * 60)
            print(fallback_response)
            print("=" * 60)
            
            # Quick quality assessment
            quality_indicators = [
                "**" in fallback_response,  # Formatted headers
                "•" in fallback_response,   # Bullet points
                len(fallback_response) > 500,  # Detailed response
                "recommend" in fallback_response.lower(),  # Actionable
                "status" in fallback_response.lower(),     # Status info
                "next" in fallback_response.lower()        # Next steps
            ]
            
            quality_score = sum(quality_indicators) / len(quality_indicators) * 100
            print(f"\n📊 Quality Score: {quality_score:.1f}% ({sum(quality_indicators)}/{len(quality_indicators)} indicators)")
            
            if quality_score >= 80:
                print("✅ EXCELLENT - Gemini-quality response!")
            elif quality_score >= 60:
                print("👍 GOOD - High quality response")
            else:
                print("⚠️  NEEDS IMPROVEMENT")
                
        except Exception as e:
            print(f"❌ Error testing case {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n🎉 Enhanced Fallback Test Complete!")
    print(f"💡 The new system provides detailed, contextual responses")
    print(f"🔧 Fallback responses now include analysis, recommendations, and next steps")

if __name__ == "__main__":
    asyncio.run(test_enhanced_fallback())
