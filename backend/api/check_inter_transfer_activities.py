import asyncio
import aiohttp
import json

async def check_inter_transfer_activities():
    """Check if inter-transfer activities are showing up in recent activities"""
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        print("=== Checking Inter-Transfer Activities ===")
        
        # Check Enhanced Agent activities directly
        async with session.get(f"{base_url}/api/v3/enhanced-agent/activities") as response:
            if response.ok:
                data = await response.json()
                activities = data.get('activities', [])
                
                print(f"Enhanced Agent activities: {len(activities)}")
                
                # Count by type
                activity_types = {}
                for activity in activities:
                    action_type = activity.get('action_type', 'unknown')
                    activity_types[action_type] = activity_types.get(action_type, 0) + 1
                
                print(f"Activity types: {activity_types}")
                
                # Show inter-transfer activities specifically
                inter_transfers = [a for a in activities if a.get('action_type') == 'inter_transfer']
                print(f"\nInter-transfer activities: {len(inter_transfers)}")
                
                for i, transfer in enumerate(inter_transfers):
                    item = transfer.get('item_name', 'Unknown')
                    source = transfer.get('department', 'Unknown')
                    target = transfer.get('target_department', 'Unknown')
                    quantity = transfer.get('quantity', 0)
                    reason = transfer.get('reason', 'No reason')
                    
                    print(f"  {i+1}. {item}")
                    print(f"     {source} → {target}")
                    print(f"     Quantity: {quantity}")
                    print(f"     Reason: {reason}")
                    print(f"     Timestamp: {transfer.get('timestamp', 'N/A')}")
                    print()
        
        print("=== Checking Recent Activity API ===")
        
        # Check recent activity API
        async with session.get(f"{base_url}/api/v2/recent-activity") as response:
            if response.ok:
                data = await response.json()
                activities = data.get('activities', [])
                
                # Find Enhanced Agent activities
                agent_activities = [a for a in activities if a.get('data_source') == 'enhanced_agent']
                print(f"Enhanced Agent activities in recent API: {len(agent_activities)}")
                
                # Check if inter-transfers are included
                inter_transfer_activities = []
                for activity in agent_activities:
                    if 'transfer' in activity.get('description', '').lower() or 'inter' in activity.get('action', '').lower():
                        inter_transfer_activities.append(activity)
                
                print(f"Inter-transfer activities in recent API: {len(inter_transfer_activities)}")
                
                if inter_transfer_activities:
                    print("Sample inter-transfer activity:")
                    sample = inter_transfer_activities[0]
                    print(f"  Action: {sample.get('action', 'N/A')}")
                    print(f"  Description: {sample.get('description', 'N/A')}")
                    print(f"  Location: {sample.get('location', 'N/A')}")
                    print(f"  Details: {sample.get('details', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(check_inter_transfer_activities())
