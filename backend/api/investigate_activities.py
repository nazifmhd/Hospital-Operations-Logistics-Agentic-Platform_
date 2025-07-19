import asyncio
import aiohttp
import json

async def investigate_activity_types():
    """Investigate what types of activities are being generated"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("=== Investigating Activity Types ===")
        
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
                
                # Show samples of each type
                for action_type in action_counts:
                    matching_activities = [a for a in activities if a.get('action_type') == action_type]
                    if matching_activities:
                        sample = matching_activities[0]
                        print(f"\nSample {action_type} activity:")
                        print(f"  Item: {sample.get('item_name')}")
                        print(f"  Department: {sample.get('department')}")
                        print(f"  Target: {sample.get('target_department')}")
                        print(f"  Reason: {sample.get('reason')}")
                        print(f"  Status: {sample.get('status')}")
                        print(f"  Priority: {sample.get('priority')}")
                
                # Check for potential inter-transfer conditions
                print(f"\n=== Checking for inter-transfer conditions ===")
                
                # Trigger enhanced agent analysis to see if new activities are generated
                print("Triggering enhanced agent analysis...")
                async with session.post(f"{base_url}/api/v3/enhanced-agent/analyze") as analyze_response:
                    if analyze_response.ok:
                        analyze_data = await analyze_response.json()
                        print(f"Analysis result: {analyze_data}")
                    else:
                        print(f"Analysis failed: {analyze_response.status}")

if __name__ == "__main__":
    asyncio.run(investigate_activity_types())
