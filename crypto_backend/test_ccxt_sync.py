import ccxt

def test():
    exchange = ccxt.kraken()
    try:
        print("Fetching ticker...")
        ticker = exchange.fetch_ticker('BTC/USD')
        print(f"Price: {ticker['last']}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        exchange.close()

if __name__ == "__main__":
    test()
