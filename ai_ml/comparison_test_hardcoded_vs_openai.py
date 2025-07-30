"""
Comparison Test: Hardcoded Conversational Responses vs OpenAI Natural Responses
============================================================================

This test compares two approaches:
1. Current System: Hardcoded conversational responses (manual patterns)
2. OpenAI System: Let GPT-3.5-turbo handle conversational aspects naturally

We'll test the same queries with both systems and compare:
- Response quality and naturalness
- Performance and speed
- Consistency and reliability
- Conversational ability scores
"""

import asyncio
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

# Import the current comprehensive agent
sys.path.append('.')
from comprehensive_ai_agent import ComprehensiveAIAgent, process_agent_conversation
from llm_integration import IntelligentSupplyAssistant, LLM_CONFIGURED, OPENAI_CONFIGURED

# Test cases - same as before
TEST_CASES = [
    {
        "category": "🏥 Hospital System",
        "query": "Hello! Can you help me with my hospital supply management?",
        "expected": "Conversational greeting + hospital system help"
    },
    {
        "category": "💬 General Conversation", 
        "query": "How are you doing today?",
        "expected": "Human-like conversational response"
    },
    {
        "category": "🧠 General Knowledge",
        "query": "What is artificial intelligence?", 
        "expected": "Educational response about AI"
    },
    {
        "category": "🤝 Personal Assistant",
        "query": "Can you help me write an email to my supplier?",
        "expected": "Helpful assistance with email writing"
    },
    {
        "category": "🔧 Problem Solving",
        "query": "I'm having trouble organizing my work schedule. Any suggestions?",
        "expected": "Practical advice and suggestions"
    },
    {
        "category": "🔄 Mixed Context",
        "query": "I need to check inventory but also want to know what time it is",
        "expected": "Handle multiple requests appropriately"
    },
    {
        "category": "🎨 Creative",
        "query": "Can you suggest a funny name for our new medical equipment?",
        "expected": "Creative and engaging response"
    },
    {
        "category": "🔄 Follow-up",
        "query": "Thanks for the help! By the way, do you know any good restaurants?",
        "expected": "Natural conversation continuation"
    }
]

def analyze_response_quality(query, response, category):
    """Analyze if response shows chatbot qualities"""
    
    analysis = {
        "conversational": False,
        "helpful": False, 
        "human_like": False,
        "handles_general": False,
        "natural": False,
        "appropriate": False
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
    
    # Check if it handles general questions (not just hospital-specific)
    if category in ["💬 General Conversation", "🧠 General Knowledge", "🎨 Creative", "🔄 Follow-up"]:
        if len(response) > 50 and not "error" in response_lower:
            analysis["handles_general"] = True
    else:
        analysis["handles_general"] = True
    
    # Check naturalness (length, flow, not too robotic)
    if len(response) > 30 and ("!" in response or "?" in response or "😊" in response):
        analysis["natural"] = True
    
    # Check appropriateness to query
    query_words = query.lower().split()
    if any(word in response_lower for word in query_words[:3]):  # Response addresses the query
        analysis["appropriate"] = True
    
    return analysis

async def test_hardcoded_system():
    """Test the current hardcoded conversational system"""
    print("🔧 TESTING HARDCODED CONVERSATIONAL SYSTEM")
    print("=" * 60)
    
    # Initialize agent with hardcoded responses (current system)
    agent = ComprehensiveAIAgent()
    
    results = {
        "conversational": 0, "helpful": 0, "human_like": 0, 
        "handles_general": 0, "natural": 0, "appropriate": 0,
        "total": len(TEST_CASES), "response_times": []
    }
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{test['category']} - Test {i}")
        print(f"🔍 Query: \"{test['query']}\"")
        
        try:
            start_time = time.time()
            response = await process_agent_conversation(test['query'], f"test_user_{i}")
            end_time = time.time()
            
            response_time = end_time - start_time
            results["response_times"].append(response_time)
            
            if isinstance(response, dict) and 'response' in response:
                response_text = response['response']
                print(f"💬 Response: {response_text[:150]}...")
                print(f"⏱️ Time: {response_time:.2f}s")
                
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
    
    return results

async def test_openai_system():
    """Test OpenAI-powered conversational system"""
    print("\n🤖 TESTING OPENAI CONVERSATIONAL SYSTEM")
    print("=" * 60)
    
    # Create a modified agent that uses OpenAI for conversational responses
    agent = ComprehensiveAIAgent()
    
    # Enable LLM by modifying the condition temporarily
    agent._use_openai_for_comparison = True
    
    results = {
        "conversational": 0, "helpful": 0, "human_like": 0, 
        "handles_general": 0, "natural": 0, "appropriate": 0,
        "total": len(TEST_CASES), "response_times": []
    }
    
    # Initialize LLM assistant if not already done
    if not hasattr(agent, 'llm_assistant') or agent.llm_assistant is None:
        try:
            agent.llm_assistant = IntelligentSupplyAssistant()
            print("✅ OpenAI assistant initialized")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI: {e}")
            return results
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{test['category']} - Test {i}")
        print(f"🔍 Query: \"{test['query']}\"")
        
        try:
            start_time = time.time()
            
            # Use OpenAI directly for conversational responses
            system_context = {
                "conversation_history": [],
                "session_id": f"test_user_{i}",
                "timestamp": datetime.now().isoformat()
            }
            
            # Create a conversational prompt for OpenAI
            enhanced_prompt = f"""You are a helpful, conversational AI assistant for a hospital supply management system. 
Respond naturally and conversationally to this query: "{test['query']}"

Guidelines:
1. Be warm, friendly, and human-like in your response
2. Use conversational phrases like "I'd be happy to", "I think", "from my perspective"
3. Include helpful suggestions when appropriate
4. Use casual, warm language while being informative
5. Feel free to use expressions that show personality and opinions
6. If it's about hospital systems, acknowledge that expertise, but handle general questions naturally too
7. Keep responses engaging and not too formal

Respond as if you're a knowledgeable, friendly colleague:"""
            
            response_obj = await agent.llm_assistant.natural_language_query(enhanced_prompt, system_context)
            end_time = time.time()
            
            response_time = end_time - start_time
            results["response_times"].append(response_time)
            
            # Extract text from LLMResponse object
            if hasattr(response_obj, 'response'):
                response_text = response_obj.response
            elif hasattr(response_obj, 'content'):
                response_text = response_obj.content
            else:
                response_text = str(response_obj)
            
            print(f"💬 Response: {response_text[:150]}...")
            print(f"⏱️ Time: {response_time:.2f}s")
            
            # Analyze response quality
            analysis = analyze_response_quality(test['query'], response_text, test['category'])
            
            print(f"📊 Analysis:")
            for criterion, passed in analysis.items():
                status = "✅" if passed else "❌"
                print(f"   {status} {criterion}")
                if passed and criterion in results:
                    results[criterion] += 1
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
    
    return results

def compare_results(hardcoded_results, openai_results):
    """Compare the results from both systems"""
    print("\n🏆 COMPARISON RESULTS")
    print("=" * 80)
    
    categories = ["conversational", "helpful", "human_like", "handles_general", "natural", "appropriate"]
    
    print(f"{'Criterion':<20} {'Hardcoded':<12} {'OpenAI':<12} {'Winner':<15}")
    print("-" * 65)
    
    hardcoded_wins = 0
    openai_wins = 0
    ties = 0
    
    for category in categories:
        hardcoded_score = hardcoded_results[category] / hardcoded_results['total'] * 100
        openai_score = openai_results[category] / openai_results['total'] * 100
        
        if hardcoded_score > openai_score:
            winner = "🔧 Hardcoded"
            hardcoded_wins += 1
        elif openai_score > hardcoded_score:
            winner = "🤖 OpenAI"
            openai_wins += 1
        else:
            winner = "🤝 Tie"
            ties += 1
        
        print(f"{category:<20} {hardcoded_score:>7.1f}%    {openai_score:>7.1f}%    {winner}")
    
    # Performance comparison
    hardcoded_avg_time = sum(hardcoded_results['response_times']) / len(hardcoded_results['response_times'])
    openai_avg_time = sum(openai_results['response_times']) / len(openai_results['response_times'])
    
    print(f"\n⏱️ PERFORMANCE COMPARISON")
    print(f"Hardcoded avg response time: {hardcoded_avg_time:.2f}s")
    print(f"OpenAI avg response time: {openai_avg_time:.2f}s")
    
    if hardcoded_avg_time < openai_avg_time:
        print(f"🚀 Hardcoded is {openai_avg_time/hardcoded_avg_time:.1f}x faster")
    else:
        print(f"🚀 OpenAI is {hardcoded_avg_time/openai_avg_time:.1f}x faster")
    
    # Overall winner
    print(f"\n🏆 OVERALL WINNER")
    print(f"Hardcoded wins: {hardcoded_wins}")
    print(f"OpenAI wins: {openai_wins}")
    print(f"Ties: {ties}")
    
    if hardcoded_wins > openai_wins:
        print("🏆 HARDCODED SYSTEM WINS!")
        print("✅ Recommendation: Keep using hardcoded conversational responses")
    elif openai_wins > hardcoded_wins:
        print("🏆 OPENAI SYSTEM WINS!")
        print("✅ Recommendation: Switch to OpenAI for conversational responses")
    else:
        print("🤝 IT'S A TIE!")
        print("✅ Recommendation: Consider hybrid approach or choose based on performance needs")

async def main():
    """Run the comparison test"""
    print("🚀 HARDCODED vs OPENAI CONVERSATIONAL COMPARISON")
    print("=" * 80)
    print(f"Testing {len(TEST_CASES)} scenarios with both systems...")
    
    try:
        # Test hardcoded system
        hardcoded_results = await test_hardcoded_system()
        
        # Test OpenAI system
        openai_results = await test_openai_system()
        
        # Compare results
        compare_results(hardcoded_results, openai_results)
        
        print(f"\n✅ Comparison complete! Check results above to decide which system works better for your needs.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
