"""
Quick test script for optimized Gemini API timeout handling
"""

import asyncio
import time
from comprehensive_ai_agent import get_comprehensive_agent

async def test_timeout_performance():
    """Test the agent's performance with timeout optimizations"""
    print("🚀 Testing Comprehensive AI Agent Timeout Optimizations")
    print("=" * 60)
    
    agent = await get_comprehensive_agent()
    
    test_queries = [
        "What's the current inventory status?",
        "Show me ICU supplies",
        "I need to order masks urgently",
        "What alerts are active?",
        "Generate pharmacy analytics"
    ]
    
    total_start_time = time.time()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        start_time = time.time()
        
        try:
            response = await agent.process_conversation(query, f"test_user_{i}")
            end_time = time.time()
            duration = end_time - start_time
            
            response_preview = response['response'][:150] + "..." if len(response['response']) > 150 else response['response']
            
            print(f"⏱️  Duration: {duration:.2f}s")
            print(f"📊 Actions: {len(response.get('actions', []))}")
            print(f"💬 Response: {response_preview}")
            
            if duration < 12:
                print("✅ Good response time!")
            elif duration < 20:
                print("⚠️  Acceptable response time")
            else:
                print("❌ Slow response time")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    total_duration = time.time() - total_start_time
    print(f"\n📈 Total test duration: {total_duration:.2f}s")
    print(f"📊 Average per query: {total_duration / len(test_queries):.2f}s")
    
    print("\n🎯 Optimization Results:")
    print("• Timeout reduced from 30s → 10s (first attempt)")
    print("• Retry timeout: 8s (with simplified prompt)")  
    print("• Intelligent fallback responses when LLM times out")
    print("• Prompt optimization for faster processing")
    print("• Gemini Flash model for speed over Gemini Pro")

if __name__ == "__main__":
    asyncio.run(test_timeout_performance())
