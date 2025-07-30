#!/usr/bin/env python3
"""
Test OpenAI Integration
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_openai_configuration():
    print("🚀 Testing OpenAI Integration")
    print("=" * 50)
    
    # Load .env from project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / '.env'
    
    print(f"📁 Loading .env from: {env_file}")
    load_dotenv(env_file)
    
    # Check configuration
    provider = os.getenv('LLM_PROVIDER', 'openai')
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    print(f"🔧 Provider: {provider}")
    print(f"🤖 Model: {model}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'NOT_FOUND'}")
    
    if not api_key:
        print("❌ OpenAI API key not found!")
        return False
    
    # Test OpenAI directly
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized")
        
        # Test simple API call
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful hospital supply assistant."},
                {"role": "user", "content": "Say hello briefly"}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Test Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

async def test_llm_integration():
    print("\n🔍 Testing LLM Integration Module")
    print("=" * 50)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from llm_integration import IntelligentSupplyAssistant, LLM_CONFIGURED, OPENAI_CONFIGURED
        
        print(f"📊 LLM_CONFIGURED: {LLM_CONFIGURED}")
        print(f"📊 OPENAI_CONFIGURED: {OPENAI_CONFIGURED}")
        
        if not LLM_CONFIGURED:
            print("❌ No LLM configured")
            return False
        
        # Initialize assistant
        assistant = IntelligentSupplyAssistant()
        print("✅ LLM Assistant initialized")
        
        # Test conversation method (if it exists)
        if hasattr(assistant, 'process_conversation'):
            print("🧪 Testing conversation...")
            response = await assistant.process_conversation("Hello, how are you?")
            print(f"✅ Response: {response}")
        else:
            print("ℹ️ process_conversation method not available")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_comprehensive_agent():
    print("\n🤖 Testing Comprehensive AI Agent")
    print("=" * 50)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from comprehensive_ai_agent import process_agent_conversation
        
        print("🧪 Testing agent conversation...")
        response = await process_agent_conversation("Hello", "test_user", "test_session")
        
        print(f"✅ Agent Response: {response.get('response', 'No response')[:100]}...")
        print(f"📊 Response type: {type(response)}")
        
        # Test JSON serialization
        import json
        json_response = json.dumps(response, indent=2)
        print(f"✅ JSON serialization successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🚀 Hospital Supply Platform - OpenAI Integration Test")
    print("=" * 70)
    
    # Test OpenAI configuration
    openai_ok = test_openai_configuration()
    
    # Test LLM integration
    llm_ok = await test_llm_integration()
    
    # Test comprehensive agent
    agent_ok = await test_comprehensive_agent()
    
    print("\n" + "=" * 70)
    print("📋 FINAL RESULTS:")
    print(f"   OpenAI API: {'✅ WORKING' if openai_ok else '❌ FAILED'}")
    print(f"   LLM Integration: {'✅ WORKING' if llm_ok else '❌ FAILED'}")
    print(f"   Comprehensive Agent: {'✅ WORKING' if agent_ok else '❌ FAILED'}")
    
    if openai_ok and llm_ok and agent_ok:
        print("🎉 All systems operational with OpenAI!")
        print("💡 Your agent will now use OpenAI instead of Gemini")
    else:
        print("⚠️ Some issues detected. Check configuration.")

if __name__ == "__main__":
    asyncio.run(main())
