import asyncio
import aiohttp
import json

async def check_activities_after_analysis():
    """Check activities before and after analysis"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("=== Checking Activities After Analysis ===")
        
        async with session.get(f"{base_url}/api/v3/enhanced-agent/activities") as response:
            if response.ok:
                data = await response.json()
                activities = data.get('activities', [])
                
                print(f"Total activities: {len(activities)}")
                
                # Count by action type
                action_counts = {}
                for activity in activities:
                    action_type = activity.get('action_type', 'unknown')
                    action_counts[action_type] = action_counts.get(action_type, 0) + 1
                
                print(f"Action type counts: {action_counts}")
                
                # Show recent activities
                print("\nRecent 5 activities:")
                for i, activity in enumerate(activities[:5]):
                    print(f"  {i+1}. {activity.get('action_type')} - {activity.get('item_name')} - {activity.get('department')} -> {activity.get('target_department', 'N/A')}")
                    print(f"     Reason: {activity.get('reason')}")
                    print(f"     Time: {activity.get('timestamp')}")
                    print(f"     Status: {activity.get('status')}")
                
                # Check for inter-transfer activities specifically
                inter_transfers = [a for a in activities if a.get('action_type') == 'inter_transfer']
                print(f"\nInter-transfer activities: {len(inter_transfers)}")
                
                if inter_transfers:
                    print("Inter-transfer details:")
                    for transfer in inter_transfers[:3]:
                        print(f"  - {transfer.get('item_name')} from {transfer.get('department')} to {transfer.get('target_department')}")
                        print(f"    Reason: {transfer.get('reason')}")
                        print(f"    Status: {transfer.get('status')}")
                
                # Now check the recent activity API to see if formatting is the issue
                print("\n=== Checking Recent Activity API ===")
                
                async with session.get(f"{base_url}/api/v2/recent-activity") as recent_response:
                    if recent_response.ok:
                        recent_data = await recent_response.json()
                        recent_activities = recent_data.get('activities', [])
                        print(f"Recent activity API has {len(recent_activities)} activities")
                        
                        if recent_activities:
                            print("First recent activity:")
                            print(f"  Description: {recent_activities[0].get('description', 'No description')}")
                            print(f"  Type: {recent_activities[0].get('type', 'No type')}")
                            print(f"  Title: {recent_activities[0].get('title', 'No title')}")

if __name__ == "__main__":
    asyncio.run(check_activities_after_analysis())
