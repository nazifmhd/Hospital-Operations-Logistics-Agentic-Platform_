import asyncio
import aiohttp
import json

async def comprehensive_test():
    """Comprehensive test of all endpoints"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Database activities
        print("=== Test 1: Database Activities ===")
        try:
            async with session.get(f"{base_url}/api/v2/recent-activity") as response:
                print(f"Status: {response.status}")
                if response.ok:
                    data = await response.json()
                    print(f"Type: {type(data)}")
                    if isinstance(data, dict):
                        activities = data.get('activities', [])
                        print(f"DB Activities: {len(activities)}")
                        if activities:
                            print(f"First DB activity: {activities[0]}")
                    else:
                        print("ERROR: Response is not a dict")
                else:
                    print(f"ERROR: Status {response.status}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        print("\n=== Test 2: Enhanced Agent Activities ===")
        try:
            async with session.get(f"{base_url}/api/v3/enhanced-agent/activities") as response:
                print(f"Status: {response.status}")
                if response.ok:
                    data = await response.json()
                    print(f"Type: {type(data)}")
                    if isinstance(data, dict):
                        activities = data.get('activities', [])
                        print(f"Agent Activities: {len(activities)}")
                        if activities:
                            print(f"First Agent activity: {activities[0]}")
                            print(f"Agent activity keys: {list(activities[0].keys())}")
                    else:
                        print("ERROR: Response is not a dict")
                else:
                    print(f"ERROR: Status {response.status}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        print("\n=== Test 3: Direct Frontend Simulation ===")
        try:
            # Simulate frontend behavior
            async with session.get(f"{base_url}/api/v2/recent-activity") as db_resp:
                async with session.get(f"{base_url}/api/v3/enhanced-agent/activities") as agent_resp:
                    
                    all_activities = []
                    
                    # Process DB response
                    if db_resp.ok:
                        db_data = await db_resp.json()
                        db_activities = db_data.get('activities', [])
                        all_activities.extend(db_activities)
                        print(f"Added {len(db_activities)} DB activities")
                    
                    # Process Agent response 
                    if agent_resp.ok:
                        agent_data = await agent_resp.json()
                        agent_activities = agent_data.get('activities', [])
                        
                        # Format like frontend does
                        formatted_activities = []
                        for activity in agent_activities:
                            formatted = {
                                'id': activity.get('activity_id'),
                                'type': 'automated_supply_action',
                                'action': activity.get('action_type'),
                                'description': f"🤖 {activity.get('action_type', '').replace('_', ' ').upper()}: {activity.get('item_name', '')} ({activity.get('reason', '')})",
                                'details': {
                                    'item_name': activity.get('item_name'),
                                    'quantity': activity.get('quantity'),
                                    'department': activity.get('department'),
                                    'priority': activity.get('priority'),
                                    'status': activity.get('status')
                                },
                                'timestamp': activity.get('timestamp'),
                                'icon': '📦' if activity.get('action_type') == 'reorder' else '🔄',
                                'category': 'automation'
                            }
                            formatted_activities.append(formatted)
                        
                        all_activities.extend(formatted_activities)
                        print(f"Added {len(formatted_activities)} formatted agent activities")
                    
                    print(f"Total activities: {len(all_activities)}")
                    
                    if all_activities:
                        print(f"First activity: {all_activities[0]}")
                        print(f"First activity description: {all_activities[0].get('description', 'No description')}")
                        
                        # Check for the specific "reorder •" issue
                        for i, activity in enumerate(all_activities[:3]):
                            print(f"Activity {i+1} description: {activity.get('description', 'No description')}")
                    
        except Exception as e:
            print(f"ERROR in simulation: {e}")

if __name__ == "__main__":
    asyncio.run(comprehensive_test())
