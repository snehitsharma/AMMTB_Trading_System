import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import time

class SentimentEngine:
    def __init__(self):
        self.cache = {} # {symbol: (data, timestamp)}
        self.cache_ttl = 900 # 15 minutes

    def get_finviz_data(self, symbol: str):
        """
        Scrape Finviz for news sentiment and insider trading.
        Uses caching to avoid excessive requests.
        """
        # Check Cache
        if symbol in self.cache:
            data, timestamp = self.cache[symbol]
            if time.time() - timestamp < self.cache_ttl:
                return data

        url = f"https://finviz.com/quote.ashx?t={symbol}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        try:
            req = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(req.content, 'html.parser')
            
            # 1. Analyze News Sentiment
            news_table = soup.find(id='news-table')
            sentiment_score = 0
            news_count = 0
            
            if news_table:
                rows = news_table.findAll('tr')
                total_polarity = 0
                
                # Analyze last 5 headlines
                for index, row in enumerate(rows):
                    if index > 4: break
                    
                    link_text = row.a.text
                    blob = TextBlob(link_text)
                    total_polarity += blob.sentiment.polarity
                    news_count += 1
                
                if news_count > 0:
                    sentiment_score = total_polarity / news_count

            # 2. Analyze Insider Trading
            insider_status = "NEUTRAL"
            insider_summary = ""
            
            try:
                tables = soup.findAll('table', class_='body-table')
                insider_table = None
                
                for table in tables:
                    headers = [th.text for th in table.findAll('td')]
                    if "Relationship" in str(headers) and "Transaction" in str(headers):
                        insider_table = table
                        break
                
                if insider_table:
                    rows = insider_table.findAll('tr')[1:] # Skip header
                    
                    buy_count = 0
                    sell_count = 0
                    
                    # Analyze last 3 transactions
                    for index, row in enumerate(rows):
                        if index > 2: break 
                        
                        cols = row.findAll('td')
                        if len(cols) < 5: continue
                        
                        transaction = cols[2].text # Buy, Sale, Option Exercise
                        
                        if "Buy" in transaction:
                            buy_count += 1
                        elif "Sale" in transaction:
                            sell_count += 1
                    
                    if sell_count > buy_count:
                        insider_status = "INSIDER_SELL"
                        insider_summary = f"Insider Selling ({sell_count} vs {buy_count})"
                    elif buy_count > sell_count:
                        insider_status = "INSIDER_BUY"
                        insider_summary = f"Insider Buying ({buy_count} vs {sell_count})"
                        
            except Exception as e:
                pass

            result = {
                "score": sentiment_score,
                "insider": insider_status,
                "summary": insider_summary
            }
            
            # Update Cache
            self.cache[symbol] = (result, time.time())
            return result

        except Exception as e:
            print(f"Sentiment Error ({symbol}): {e}")
            return {"score": 0, "insider": "NEUTRAL", "summary": "Error"}
