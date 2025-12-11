
def calculate_confluence_score(insider_data, earnings_data, technicals, macro_data):
    # Base Sieve Score (Passing Sieve = +50)
    score = 50 
    report = ["Sieve Passed (+50)"]

    # 1. Insider Conviction (Max 30)
    # +30 pts: Insider Cluster Buy (3+ people) OR >$500k buy.
    insider_score = 0
    if insider_data:
        buys = [x for x in insider_data if 'Buy' in str(x.get('transactionType', ''))]
        
        # Check value -> approximate 'securitiesTransacted' * 'price' or just 'value' if available. 
        total_value = sum([float(x.get('securitiesTransacted') or 0) * float(x.get('price') or 0) for x in buys])
        
        if len(buys) >= 3: 
            insider_score += 30
            report.append("Cluster Buy (3+ officers)")
        elif total_value > 500000:
            insider_score += 30
            report.append(f"Whale Buy > $500k (${total_value/1000:.0f}k)")
        elif len(buys) > 0:
            insider_score += 10 # Base for any buy
            report.append("Single Insider Buy")
    score += min(insider_score, 30)

    # 2. Fundamental Catalyst (Max 25)
    # +25 pts: Earnings Surprise > 15% (Catalyst).
    fund_score = 0
    if earnings_data:
        estimated = earnings_data.get('estimatedEPS', 0)
        actual = earnings_data.get('actualEPS', 0)
        if estimated and actual:
            surprise_pct = (actual - estimated) / abs(estimated) if estimated != 0 else 0
            if surprise_pct > 0.15:
                fund_score += 25
                report.append(f"EPS Beat +{surprise_pct*100:.1f}%")
    score += fund_score

    # 3. Technical Structure (Max 25)
    # +15 pts: Volume Spike > 2x Average.
    # +10 pts: Golden Cross (EMA20 > EMA50).
    tech_score = 0
    if technicals:
        if technicals.get('vol_spike'): # Assuming this flag is > 2x
            tech_score += 15
            report.append("Volume Spike > 2x")
        if technicals.get('golden_cross'):
            tech_score += 10
            report.append("Golden Cross")
    score += tech_score

    # 4. Macro/Inst (Max 20)
    # +20 pts: Positive Sector/Macro Correlation.
    macro_score = 0
    if macro_data:
        # Simple Logic: If BTC is up, we assume Risk-On environment (Mock logic for now)
        # In real dragnet, we'd check Sector ETF
        if (macro_data.get('btc') or 0) > 90000: # Arbitrary bull level or check trend
             macro_score += 20
             report.append("Macro Risk-ON (BTC High)")
    score += macro_score

    return score, report
