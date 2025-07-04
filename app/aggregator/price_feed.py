import requests
import random
from app.config.tokens import TOKENS

def fetch_token_data(symbol):
    if symbol not in TOKENS:
        return []

    token_info = TOKENS[symbol]

    # === 1. Eğer adres varsa (manuel token) ===
    if "address" in token_info:
        chain = token_info["chain"]
        address = token_info["address"]
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
        is_pairs_api = True

    # === 2. Eğer sadece Coingecko ID varsa (slug üzerinden search) ===
    elif "id" in token_info:
        search_term = token_info["id"]
        url = f"https://api.dexscreener.com/latest/dex/search?q={search_term}"
        is_pairs_api = False

    else:
        print(f"⚠️ {symbol} has no usable address or id.")
        return []

    print(f"\n🔍 Fetching {symbol} from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {symbol}")
        return []

    data = response.json()

    # Parse response
    if is_pairs_api:
        if "pair" not in data:
            print(f"❌ No pair found for {symbol}")
            return []

        pair = data["pair"]
        pairs = [pair]
    else:
        pairs = data.get("pairs", [])
        if not pairs:
            print(f"❌ No pairs found for {symbol}")
            return []

    results = []
    for pair in pairs[:3]:  # sadece ilk 3 pariteyi al
        try:
            results.append({
                "symbol": symbol.upper(),
                "dex": pair.get("dexId", None),
                "price": float(pair["priceUsd"]),
                "liquidity": float(pair["liquidity"]["usd"]),
                "volume": float(pair["volume"]["h24"]),
                "volatility": round(random.uniform(0.0, 5.0), 2)
            })
        except Exception as e:
            print(f"⚠️ Parse error for {symbol}: {e}")
            continue

    return results
