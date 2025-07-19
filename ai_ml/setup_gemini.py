#!/usr/bin/env python3
"""
Gemini API Configuration Setup Script
Helps configure and test Gemini API integration for Hospital Supply Platform
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the ai_ml directory to the path
sys.path.append(str(Path(__file__).parent))

try:
    from llm_integration import IntelligentSupplyAssistant, LLMIntegrationService, GEMINI_CONFIGURED
    import google.generativeai as genai
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please run: pip install google-generativeai python-dotenv")
    sys.exit(1)

def setup_environment():
    """
    Interactive setup for Gemini API configuration
    """
    print("🚀 Hospital Supply Platform - Gemini API Setup")
    print("=" * 50)
    
    # Look for .env file in project root (parent directory)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file}")
        print("Please create a .env file in the project root directory.")
        return False
    
    print(f"✅ Found .env file at {env_file}")
    
    # Check if API key is already configured
    try:
        # Load existing .env to check current API key
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Check if API key is set and not the placeholder
        if 'GEMINI_API_KEY=' in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('GEMINI_API_KEY='):
                    current_key = line.split('=', 1)[1].strip()
                    if current_key and current_key != 'your_gemini_api_key_here':
                        print(f"✅ API key already configured")
                        # Set environment variable for current session
                        os.environ['GEMINI_API_KEY'] = current_key
                        return True
        
        print("⚠️ API key not found or not configured properly")
        
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False
    
    # Get API key from user if not configured
    print("\n🔑 Gemini API Key Configuration")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("❌ API key cannot be empty")
        return False
    
    # Update .env file
    try:
        # Replace the API key line
        lines = content.split('\n')
        updated_lines = []
        api_key_updated = False
        
        for line in lines:
            if line.startswith('GEMINI_API_KEY='):
                updated_lines.append(f'GEMINI_API_KEY={api_key}')
                api_key_updated = True
            else:
                updated_lines.append(line)
        
        if not api_key_updated:
            updated_lines.append(f'GEMINI_API_KEY={api_key}')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ API key saved to .env file")
        
        # Set environment variable for current session
        os.environ['GEMINI_API_KEY'] = api_key
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

async def test_api_connection():
    """
    Test the Gemini API connection
    """
    print("\n🧪 Testing Gemini API Connection")
    print("-" * 30)
    
    try:
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ API key not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test basic connection
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = await asyncio.to_thread(
            model.generate_content,
            "Test connection: Respond with 'Hospital Supply AI Connected' if you can process this."
        )
        
        if response.text and "Hospital Supply AI Connected" in response.text:
            print("✅ Gemini API connection successful!")
            return True
        else:
            print(f"⚠️ Unexpected response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

async def test_hospital_context():
    """
    Test hospital-specific context understanding
    """
    print("\n🏥 Testing Hospital Context Understanding")
    print("-" * 40)
    
    try:
        # Initialize the intelligent assistant
        assistant = IntelligentSupplyAssistant()
        
        # Test inventory analysis
        test_inventory = {
            "inventory": [
                {"name": "N95 Masks", "current_stock": 15, "minimum_stock": 50, "department": "ICU"},
                {"name": "Surgical Gloves", "current_stock": 200, "minimum_stock": 100, "department": "OR"}
            ]
        }
        
        print("📊 Testing inventory analysis...")
        analysis = await assistant.analyze_inventory_situation(
            test_inventory, 
            {"hospital_type": "General Hospital", "patient_load": "High"}
        )
        
        print(f"✅ Analysis completed with {analysis.confidence:.1%} confidence")
        print(f"📝 Response preview: {analysis.content[:200]}...")
        
        # Test natural language query
        print("\n💬 Testing natural language processing...")
        query_response = await assistant.natural_language_query(
            "What items are critically low in stock?",
            {"current_time": "2024-01-15T10:30:00"}
        )
        
        print(f"✅ Query processed with {query_response.confidence:.1%} confidence")
        print(f"📝 Response preview: {query_response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Hospital context test failed: {e}")
        return False

async def performance_benchmark():
    """
    Run performance benchmark tests
    """
    print("\n⚡ Performance Benchmark")
    print("-" * 25)
    
    try:
        service = LLMIntegrationService()
        
        # Test response times
        import time
        test_queries = [
            "Show me current inventory status",
            "What purchase orders need approval?",
            "Generate alert for low stock items",
            "Analyze supply chain risks"
        ]
        
        total_time = 0
        successful_queries = 0
        
        for query in test_queries:
            start_time = time.time()
            try:
                response = await service.process_natural_language_command(
                    query, {"test_mode": True}
                )
                end_time = time.time()
                response_time = end_time - start_time
                total_time += response_time
                
                if response['confidence'] > 0.5:
                    successful_queries += 1
                
                print(f"✅ '{query}' - {response_time:.2f}s (confidence: {response['confidence']:.1%})")
                
            except Exception as e:
                print(f"❌ '{query}' - Failed: {e}")
        
        avg_response_time = total_time / len(test_queries)
        success_rate = (successful_queries / len(test_queries)) * 100
        
        print(f"\n📈 Performance Summary:")
        print(f"   Average Response Time: {avg_response_time:.2f} seconds")
        print(f"   Success Rate: {success_rate:.1f}%")
        print(f"   Successful Queries: {successful_queries}/{len(test_queries)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False

def generate_test_report():
    """
    Generate a comprehensive test report
    """
    print("\n📊 System Configuration Report")
    print("=" * 35)
    
    # Check environment variables
    env_vars = {
        'GEMINI_API_KEY': bool(os.getenv('GEMINI_API_KEY')),
        'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'gemini'),
        'LLM_MODEL': os.getenv('LLM_MODEL', 'gemini-1.5-pro'),
        'HOSPITAL_NAME': os.getenv('HOSPITAL_NAME', 'General Hospital'),
        'LLM_TEMPERATURE': os.getenv('LLM_TEMPERATURE', '0.3'),
    }
    
    print("🔧 Configuration Status:")
    for var, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value}")
    
    print(f"\n🏥 Hospital Context:")
    print(f"   Name: {os.getenv('HOSPITAL_NAME', 'Not Set')}")
    print(f"   Type: {os.getenv('HOSPITAL_TYPE', 'Not Set')}")
    print(f"   Location: {os.getenv('HOSPITAL_LOCATION', 'Not Set')}")
    
    print(f"\n🤖 LLM Configuration:")
    print(f"   Provider: {os.getenv('LLM_PROVIDER', 'gemini')}")
    print(f"   Model: {os.getenv('LLM_MODEL', 'gemini-1.5-pro')}")
    print(f"   Temperature: {os.getenv('LLM_TEMPERATURE', '0.3')}")
    print(f"   Gemini Configured: {'✅' if GEMINI_CONFIGURED else '❌'}")

async def main():
    """
    Main setup and testing workflow
    """
    print("🏥 Hospital Supply Platform - LLM Integration Setup & Test")
    print("=" * 60)
    
    # Step 1: Environment setup
    if not setup_environment():
        print("❌ Setup failed. Please check your configuration.")
        return
    
    # Reload environment from project root
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    load_dotenv(env_path, override=True)
    
    print(f"🔄 Loaded environment from {env_path}")
    
    # Step 2: API connection test
    if not await test_api_connection():
        print("❌ API connection failed. Please check your API key.")
        return
    
    # Step 3: Hospital context test
    if not await test_hospital_context():
        print("❌ Hospital context test failed.")
        return
    
    # Step 4: Performance benchmark
    await performance_benchmark()
    
    # Step 5: Generate report
    generate_test_report()
    
    print("\n🎉 Setup and testing completed successfully!")
    print("\n📋 Next Steps:")
    print("   1. Your Gemini API is working correctly")
    print("   2. Restart your FastAPI server from the project root")
    print("   3. Test the chat interface in your frontend")
    print("   4. Try asking: 'What items need reordering in the ICU?'")
    print("   5. Monitor performance in production")

if __name__ == "__main__":
    asyncio.run(main())
