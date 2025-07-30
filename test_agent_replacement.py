"""
Test script to verify the comprehensive agent replacement
"""

import requests
import json

def test_agent_endpoints():
    """Test the comprehensive agent endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Comprehensive AI Agent Integration...")
    print("=" * 50)
    
    # Test 1: Check agent chat endpoint
    try:
        response = requests.post(
            f"{base_url}/api/v3/agent/chat",
            json={
                "message": "What's the current inventory status?",
                "user_id": "test_user",
                "session_id": "test_session"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Chat Endpoint: WORKING")
            print(f"   Response: {data.get('response', '')[:100]}...")
            print(f"   Actions: {len(data.get('actions', []))} performed")
        else:
            print(f"❌ Agent Chat Endpoint: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Agent Chat Endpoint: ERROR - {e}")
    
    # Test 2: Check agent capabilities
    try:
        response = requests.get(f"{base_url}/api/v3/agent/capabilities")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Capabilities Endpoint: WORKING")
            print(f"   Capabilities: {len(data.get('capabilities', []))} available")
        else:
            print(f"❌ Agent Capabilities Endpoint: FAILED ({response.status_code})")
            
    except Exception as e:
        print(f"❌ Agent Capabilities Endpoint: ERROR - {e}")
    
    print("\n🚀 Frontend Integration Points:")
    print("   • FloatingAIAssistant.js - Global floating button (bottom-right)")
    print("   • ProfessionalDashboard.js - Dashboard AI button + floating button")
    print("   • AgentChatInterface.js - New comprehensive chat interface")
    print("   • Old LLMChatInterface.js - Replaced successfully")
    
    print("\n📋 Testing Instructions:")
    print("   1. Start backend: cd backend/api && python professional_main_smart.py")
    print("   2. Start frontend: cd dashboard/supply_dashboard && npm start")
    print("   3. Look for floating AI button in bottom-right corner")
    print("   4. Test conversation: 'Show me ICU supplies'")
    print("   5. Verify agent performs actions and gives intelligent responses")

if __name__ == "__main__":
    test_agent_endpoints()
