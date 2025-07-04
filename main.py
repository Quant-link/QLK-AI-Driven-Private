from app.config.tokens import TOKENS
from app.aggregator.price_feed import fetch_token_data
from app.ai.arbitrage_detector import detect_arbitrage

def main():
    token_data = {}

    print("\n📊 Token Analysis:")
    for symbol in TOKENS:
        data = fetch_token_data(symbol)
        if data:
            print(f"🔹 {symbol} on {data['dex']}")
            print(f"   Price: ${data['price']} | Liquidity: ${data['liquidity']} | Volume: ${data['volume']} | Volatility: {data['volatility']}%")
            token_data[symbol] = [data]

    print("\n🧠 Arbitrage Opportunities:")
    results = detect_arbitrage(token_data)
    if not results:
        print("No arbitrage detected.")
    else:
        for opp in results:
            print(f"🔀 {opp['symbol']} → Buy from {opp['buy_from']} @ ${opp['buy_price']} | Sell to {opp['sell_to']} @ ${opp['sell_price']} | Profit: {opp['profit_pct']}%")

if __name__ == "__main__":
    main()
