#!/usr/bin/env python3
"""
Test Gemini API Connection
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import asyncio

def test_gemini_connection():
    print("🔍 Testing Gemini API Connection...")
    print("=" * 40)
    
    # Load .env from project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / '.env'
    
    print(f"📁 Loading .env from: {env_file}")
    print(f"📄 File exists: {env_file.exists()}")
    
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ .env file loaded")
    else:
        print("❌ .env file not found")
        return False
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "short"
        print(f"🔑 API Key found: {masked_key}")
    else:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    # Test Gemini configuration
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        print("✅ Gemini API configured")
        
        # Initialize model
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Gemini model initialized")
        
        # Test generation
        print("🧪 Testing simple generation...")
        response = model.generate_content(
            "Say hello in a friendly way",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=50
            )
        )
        
        print(f"✅ Test response: {response.text}")
        print("🎉 Gemini API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Gemini error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_llm_integration():
    print("\n🔍 Testing LLM Integration Module...")
    print("=" * 40)
    
    try:
        sys.path.append(str(Path(__file__).parent))
        from llm_integration import IntelligentSupplyAssistant, GEMINI_CONFIGURED
        
        print(f"📊 GEMINI_CONFIGURED: {GEMINI_CONFIGURED}")
        
        if GEMINI_CONFIGURED:
            assistant = IntelligentSupplyAssistant()
            print("✅ LLM Integration initialized")
            
            # Test simple query
            test_query = "Hello, how are you?"
            print(f"🧪 Testing query: {test_query}")
            
            response = asyncio.run(assistant.process_conversation(test_query))
            print(f"✅ Response: {response}")
            print("🎉 LLM Integration is working!")
            return True
        else:
            print("❌ Gemini not configured in LLM Integration")
            return False
            
    except Exception as e:
        print(f"❌ LLM Integration error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Hospital Supply Platform - Gemini Connection Test")
    print("=" * 60)
    
    # Test basic Gemini connection
    gemini_ok = test_gemini_connection()
    
    # Test LLM integration
    llm_ok = test_llm_integration()
    
    print("\n" + "=" * 60)
    print("📋 FINAL RESULTS:")
    print(f"   Gemini API: {'✅ WORKING' if gemini_ok else '❌ FAILED'}")
    print(f"   LLM Integration: {'✅ WORKING' if llm_ok else '❌ FAILED'}")
    
    if gemini_ok and llm_ok:
        print("🎉 All systems operational!")
    else:
        print("⚠️ Some issues detected. Check configuration.")
