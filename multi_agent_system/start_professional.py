#!/usr/bin/env python3
"""
Start Professional Server with Environment Variables
Sets up environment and starts the server properly
"""

import os
import sys
from pathlib import Path

# Set up environment first
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=str(env_file))
        print(f"✅ Environment loaded from {env_file}")
        
        # Verify key is loaded
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print(f"✅ Gemini API key loaded: {api_key[:10]}...")
        else:
            print("⚠️ Gemini API key not found")
    else:
        print(f"❌ .env file not found at {env_file}")
except ImportError:
    print("⚠️ python-dotenv not available")

# Now start the professional server
if __name__ == "__main__":
    print("\n🏥 Starting Professional Hospital Operations Server...")
    print("=" * 60)
    
    # Import and run the professional main
    from professional_main import app
    import uvicorn
    
    # Run with environment already loaded
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
