#!/usr/bin/env python3
"""
Test AI Agent as Conversational Chatbot
Tests various types of conversations and questions
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from comprehensive_ai_agent import process_agent_conversation

async def test_conversational_agent():
    """Test if the agent works as a conversational chatbot"""
    
    print("🤖 TESTING AI AGENT AS CONVERSATIONAL CHATBOT")
    print("=" * 60)
    
    # Test different types of conversations
    test_cases = [
        # 1. Hospital system related questions
        {
            "category": "🏥 Hospital System",
            "query": "Hello! Can you help me with my hospital supply management?",
            "expected": "Conversational greeting + hospital system help"
        },
        
        # 2. General conversation
        {
            "category": "💬 General Conversation", 
            "query": "How are you doing today?",
            "expected": "Human-like conversational response"
        },
        
        # 3. General knowledge question
        {
            "category": "🧠 General Knowledge",
            "query": "What is artificial intelligence?",
            "expected": "Educational response about AI"
        },
        
        # 4. Personal assistance
        {
            "category": "🤝 Personal Assistant",
            "query": "Can you help me write an email to my supplier?",
            "expected": "Helpful assistance with email writing"
        },
        
        # 5. Problem solving
        {
            "category": "🔧 Problem Solving",
            "query": "I'm having trouble organizing my work schedule. Any suggestions?",
            "expected": "Practical advice and suggestions"
        },
        
        # 6. Mixed hospital + general
        {
            "category": "🔄 Mixed Context",
            "query": "I need to check inventory but also want to know what time it is",
            "expected": "Handle multiple requests appropriately"
        },
        
        # 7. Creative request
        {
            "category": "🎨 Creative",
            "query": "Can you suggest a funny name for our new medical equipment?",
            "expected": "Creative and engaging response"
        },
        
        # 8. Follow-up conversation
        {
            "category": "🔄 Follow-up",
            "query": "Thanks for the help! By the way, do you know any good restaurants?",
            "expected": "Natural conversation continuation"
        }
    ]
    
    results = {
        "conversational": 0,
        "helpful": 0,
        "human_like": 0,
        "handles_general": 0,
        "total": len(test_cases)
    }
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{test['category']} - Test {i}")
        print(f"🔍 Query: \"{test['query']}\"")
        print(f"📋 Expected: {test['expected']}")
        
        try:
            response = await process_agent_conversation(test['query'], f"test_user_{i}")
            
            if isinstance(response, dict) and 'response' in response:
                response_text = response['response']
                
                print(f"💬 Response: {response_text[:200]}...")
                
                # Analyze response quality
                analysis = analyze_response_quality(test['query'], response_text, test['category'])
                
                print(f"📊 Analysis:")
                for criterion, passed in analysis.items():
                    status = "✅" if passed else "❌"
                    print(f"   {status} {criterion}")
                    if passed and criterion in results:
                        results[criterion] += 1
                
            else:
                print(f"❌ Invalid response format")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    # Final assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print(f"=" * 30)
    
    total_score = 0
    for category, score in results.items():
        if category != "total":
            percentage = (score / results["total"]) * 100
            print(f"{category.replace('_', ' ').title()}: {score}/{results['total']} ({percentage:.1f}%)")
            total_score += percentage
    
    overall_score = total_score / 4  # 4 main categories
    
    print(f"\n🏆 Overall Chatbot Score: {overall_score:.1f}%")
    
    if overall_score >= 80:
        print("🎉 EXCELLENT: Your agent works as a high-quality conversational chatbot!")
    elif overall_score >= 60:
        print("👍 GOOD: Your agent has good conversational abilities but can be improved")
    elif overall_score >= 40:
        print("⚠️ MODERATE: Your agent needs improvement for better conversation")
    else:
        print("❌ POOR: Your agent needs significant improvement to work as a chatbot")
    
    return overall_score

def analyze_response_quality(query, response, category):
    """Analyze if response shows chatbot qualities"""
    
    analysis = {
        "conversational": False,
        "helpful": False, 
        "human_like": False,
        "handles_general": False
    }
    
    response_lower = response.lower()
    
    # Check conversational tone
    conversational_indicators = [
        "i can help", "i'd be happy", "let me", "i understand", 
        "how can i", "i'm here", "glad to", "of course",
        "certainly", "absolutely", "sure", "i think"
    ]
    if any(indicator in response_lower for indicator in conversational_indicators):
        analysis["conversational"] = True
    
    # Check helpfulness
    helpful_indicators = [
        "here's", "try", "suggest", "recommend", "consider",
        "you might", "you could", "option", "solution", "advice"
    ]
    if any(indicator in response_lower for indicator in helpful_indicators):
        analysis["helpful"] = True
    
    # Check human-like responses
    human_like_indicators = [
        "i think", "in my opinion", "i believe", "i feel",
        "personally", "from my perspective", "i'd say"
    ]
    if any(indicator in response_lower for indicator in human_like_indicators):
        analysis["human_like"] = True
    
    # Check if handles general questions (not just hospital system)
    if category in ["💬 General Conversation", "🧠 General Knowledge", "🤝 Personal Assistant", "🔧 Problem Solving", "🎨 Creative"]:
        # If it gives a relevant response instead of "I can only help with hospital systems"
        rejection_indicators = [
            "i can only help with hospital", "outside my scope", 
            "i'm designed only for", "limited to hospital"
        ]
        if not any(rejection in response_lower for rejection in rejection_indicators):
            analysis["handles_general"] = True
    else:
        # For hospital-related queries, automatically pass this test
        analysis["handles_general"] = True
    
    return analysis

if __name__ == "__main__":
    asyncio.run(test_conversational_agent())
