#!/usr/bin/env python3
"""Quick test of Clinical Laboratory response"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai_ml'))
from comprehensive_ai_agent import process_agent_conversation

async def test_clinical():
    result = await process_agent_conversation(
        user_message="What are the inventory items I have in Clinical Laboratory location?",
        user_id="test_user",
        session_id="test_clinical"
    )
    response = result.get('response', '')
    print('Clinical Laboratory Response:')
    print('=' * 60)
    print(response)
    print('=' * 60)
    print(f'Contains "Blood Collection": {"Blood Collection" in response}')
    print(f'Contains "Blood Collection Tubes": {"Blood Collection Tubes" in response}')

if __name__ == "__main__":
    asyncio.run(test_clinical())
