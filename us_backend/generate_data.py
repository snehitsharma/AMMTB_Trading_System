import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_data():
    # Parameters
    start_price = 150.0
    days = 30
    volatility = 0.02
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq='B') # Business days
    
    # Generate prices
    prices = [start_price]
    for _ in range(len(dates) - 1):
        change = np.random.normal(0, volatility)
        prices.append(prices[-1] * (1 + change))
        
    # Create DataFrame
    df = pd.DataFrame(index=dates)
    df['Date'] = dates
    df['Open'] = prices
    df['High'] = [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices]
    df['Low'] = [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices]
    df['Close'] = prices
    df['Volume'] = np.random.randint(1000000, 5000000, size=len(dates))
    df['Adj Close'] = prices
    
    # Ensure data dir exists
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    output_path = os.path.join('data', 'AAPL.csv')
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} rows of data to {output_path}")

if __name__ == "__main__":
    generate_data()
