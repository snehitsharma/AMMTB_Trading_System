
import aiohttp
import asyncio

async def test_net():
    print("Testing connection to google.com...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.google.com", timeout=5) as resp:
                print(f"Google status: {resp.status}")
    except Exception as e:
        print(f"Google connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_net())
