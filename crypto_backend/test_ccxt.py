import ccxt.async_support as ccxt
import asyncio

async def test():
    exchange = ccxt.binance()
    try:
        print("Fetching ticker...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"Price: {ticker['last']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await exchange.close()

if __name__ == "__main__":
    asyncio.run(test())
