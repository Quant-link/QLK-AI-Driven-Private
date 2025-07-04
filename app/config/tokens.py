import json
from app.routing.dex_clients.coingecko import fetch_top_100_tokens
from app.routing.dex_clients.dexscreener import get_token_info

TOKENS_PATH = "app/config/tokens.json"

def enrich_tokens_with_coingecko():
    top_tokens = fetch_top_100_tokens()
    enriched = []

    for token in top_tokens:
        try:
            token_id = token["id"]
            symbol = token["symbol"].upper()

            # 🧠 Fallback: Use ID first, then fallback to symbol
            token_info = get_token_info(token_id) or get_token_info(symbol)

            if token_info:
                enriched.append({
                    "id": token_id,
                    "symbol": symbol,
                    "usd_price": token.get("usd_price", token.get("current_price")),
                    "chain": token_info["chain"],
                    "address": token_info["address"]
                })
                print(f"✅ Added {symbol}: chain={token_info['chain']}, address={token_info['address']}")
            else:
                print(f"❌ No data for {symbol}")
        except Exception as e:
            print(f"⚠️ Error processing {token.get('symbol')}: {e}")
            continue

    return enriched

if __name__ == "__main__":
    all_tokens = enrich_tokens_with_coingecko()

    with open(TOKENS_PATH, "w") as f:
        json.dump(all_tokens, f, indent=2)

    print(f"\n✅ Saved {len(all_tokens)} tokens to {TOKENS_PATH}")
