
def detect_arbitrage(token_data: dict):
    opportunities = []

    for symbol, entries in token_data.items():
        if len(entries) < 2:
            continue

        sorted_entries = sorted(entries, key=lambda x: x['price'])
        lowest = sorted_entries[0]
        highest = sorted_entries[-1]

        diff = highest['price'] - lowest['price']
        percent_diff = (diff / lowest['price']) * 100

        if percent_diff >= 1.0:
            opportunities.append({
                "symbol": symbol,
                "buy_from": lowest['dex'],
                "buy_price": lowest['price'],
                "sell_to": highest['dex'],
                "sell_price": highest['price'],
                "profit_pct": round(percent_diff, 2)
            })

    return opportunities
