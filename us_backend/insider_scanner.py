import aiohttp
import asyncio
import db

async def get_insider_candidates():
    """
    Scrapes OpenInsider.com for 'Cluster Buys' (Multiple insiders buying).
    Returns a list of high-conviction ticker symbols.
    """
    # Static Page for Purchases (Most reliable)
    url = "http://openinsider.com/latest-insider-purchases"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    candidates = []
    try:
        await db.add_log("INFO", "🕵️ Scanning OpenInsider for Cluster Buys...")
        print(f"🕵️ Scanning OpenInsider Cluster Buys...")
        
        # Use aiohttp for async
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    await db.add_log("ERROR", f"⚠️ OpenInsider Unreachable: {response.status}")
                    print(f"⚠️ OpenInsider Unreachable: {response.status}")
                    return []
                text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        
        # OpenInsider table rows are in a standard HTML table
        table = soup.find('table', {'class': 'tinytable'})
        if not table:
            await db.add_log("WARNING", "OpenInsider table not found. Structure changed?")
            return []

        rows = table.find_all('tr')
        await db.add_log("DEBUG", f"Found {len(rows)} rows. Analyzing...")
        
        # Skip header row [0]
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 12:
                continue
            
            # Extract Data
            ticker = cols[3].text.strip()
            trade_type = cols[6].text.strip() 
            price_str = cols[8].text.strip().replace('$','').replace(',','')
            qty_str = cols[9].text.strip().replace('+','').replace(',','')
            value_str = cols[12].text.strip().replace('$','').replace(',','')
            
            # Filters
            # 1. Must be a Purchase
            if "Purchase" not in trade_type:
                continue
                
            # 2. Must be significant size (e.g. > $50k cluster total)
            try:
                value = float(value_str)
                if value < 50000:
                    # await db.add_log("DEBUG", f"Skipping {ticker}: Size too small (${value})") # Too noisy
                    continue
            except: continue

            # If good, add to list (avoid duplicates)
            if ticker not in candidates:
                candidates.append(ticker)
                await db.add_log("ACTION", f"✅ Found Candidate: {ticker} (Value: ${value:,.0f} | Type: {trade_type})")
        
        if not candidates:
             await db.add_log("INFO", "Scan complete. No high-conviction cluster buys found this cycle.")
        else:
             await db.add_log("SUCCESS", f"✅ OpenInsider Found {len(candidates)} Candidates: {candidates}")
        
        return candidates

    except Exception as e:
        await db.add_log("ERROR", f"❌ Scanner Error: {e}")
        print(f"❌ Scanner Error: {e}")
        return []

if __name__ == "__main__":
    # Test Run
    c = get_insider_candidates()
    print(c)
