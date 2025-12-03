import ccxt.async_support as ccxt
import asyncio

class MarketData:
    def __init__(self):
        self.exchange = ccxt.kraken()

    async def get_price(self, symbol: str) -> float:
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None
        finally:
            await self.exchange.close()

    async def close(self):
        await self.exchange.close()
