import requests

print('📋 Current Auto Reorder Status:')
response = requests.get('http://localhost:8000/supply_inventory/auto_reorder_status')
reorders = response.json().get('auto_reorders', [])
print(f'Items pending approval: {len(reorders)}')
for item in reorders:
    source = item.get('source', 'unknown')
    print(f'  - {item["supply_name"]} (Source: {source})')

print('\n📦 Current Purchase Orders:')
response = requests.get('http://localhost:8000/supply_inventory/purchase_orders')
orders = response.json().get('purchase_orders', [])
print(f'Total purchase orders: {len(orders)}')
for order in orders[-3:]:  # Show last 3
    item_name = order.get('item_name', order.get('order_number'))
    supplier = order.get('supplier')
    cost = order.get('total_cost')
    print(f'  - {item_name} - {supplier} - ${cost}')
