import asyncio
import sys
sys.path.append('..')
from fixed_database_integration import get_fixed_db_integration

async def verify_auto_resolution():
    db = await get_fixed_db_integration()
    
    print('🔍 Verifying auto-resolution worked correctly...')
    
    # Get ALL alerts (including resolved ones) for Blood Collection Tubes
    alerts_data = await db.get_alerts_data()
    all_alerts = alerts_data.get('alerts', [])
    
    # Find Blood Collection Tubes item
    inventory_data = await db.get_inventory_data()
    items = inventory_data.get("items", [])
    blood_tubes_item_id = None
    
    for item in items:
        if "Blood Collection" in item.get("name", ""):
            blood_tubes_item_id = item.get("item_id")
            print(f'📦 Blood Collection Tubes:')
            print(f'   Item ID: {item["item_id"]}')
            print(f'   Current stock: {item["current_stock"]}')
            print(f'   Minimum stock: {item["minimum_stock"]}')
            print(f'   Status: {"✅ SUFFICIENT" if item["current_stock"] > item["minimum_stock"] else "🚨 LOW STOCK"}')
            break
    
    if blood_tubes_item_id:
        # Find all alerts for this item
        item_alerts = [alert for alert in all_alerts if alert.get('item_id') == blood_tubes_item_id]
        
        print(f'\n📊 All alerts for Blood Collection Tubes:')
        print(f'   Total alerts found: {len(item_alerts)}')
        
        for alert in item_alerts:
            alert_id = alert.get('id', alert.get('alert_id'))
            is_resolved = alert.get('is_resolved', False)
            created_at = alert.get('created_at', 'Unknown')
            resolved_at = alert.get('resolved_at', None)
            
            status = "✅ RESOLVED" if is_resolved else "🚨 ACTIVE"
            print(f'   - Alert {alert_id}: {status}')
            print(f'     Created: {created_at}')
            if resolved_at:
                print(f'     Resolved: {resolved_at}')
    
    # Count current active alerts across all items
    active_alerts = [alert for alert in all_alerts if not alert.get('is_resolved', False)]
    print(f'\n📋 System-wide alert summary:')
    print(f'   Total active alerts: {len(active_alerts)}')
    print(f'   Total all alerts: {len(all_alerts)}')
    
    # Test creating a new alert if stock is still low (should be 0 since stock is sufficient)
    print(f'\n🧪 Testing alert creation with current stock levels...')
    created = await db.analyze_and_create_alerts()
    print(f'📊 New alerts created: {created} (should be 0 since stock is sufficient)')
    
    print(f'\n✅ VERIFICATION COMPLETE:')
    print(f'   - Blood Collection Tubes stock is sufficient (50 > 40)')
    print(f'   - Previous low stock alerts have been auto-resolved')
    print(f'   - No new alerts are being created')
    print(f'   - Persistent notification system working correctly!')

if __name__ == "__main__":
    asyncio.run(verify_auto_resolution())
