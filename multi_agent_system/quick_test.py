"""Quick test of the two previously failing endpoints"""
import asyncio
import aiohttp

async def test_failing_endpoints():
    async with aiohttp.ClientSession() as session:
        # Test supply_inventory/query
        print("🧪 Testing supply_inventory/query...")
        try:
            async with session.post(
                "http://localhost:8000/supply_inventory/query",
                json={"query": "get all supplies"}
            ) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS - Got {len(data.get('items', []))} items")
                else:
                    text = await response.text()
                    print(f"   ❌ FAILED - {text[:100]}...")
        except Exception as e:
            print(f"   ❌ ERROR - {e}")
        
        # Test purchase_orders
        print("\n🧪 Testing purchase_orders...")
        try:
            async with session.get("http://localhost:8000/supply_inventory/purchase_orders") as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ SUCCESS - Got {len(data.get('purchase_orders', []))} orders")
                else:
                    text = await response.text()
                    print(f"   ❌ FAILED - {text[:100]}...")
        except Exception as e:
            print(f"   ❌ ERROR - {e}")

if __name__ == "__main__":
    asyncio.run(test_failing_endpoints())
