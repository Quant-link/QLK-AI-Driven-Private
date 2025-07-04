import requests
import time

def get_token_info(query: str):

    try:
        base_url = "https://api.dexscreener.com/latest/dex/search"
        response = requests.get(base_url, params={"q": query})
        response.raise_for_status()
        data = response.json()

        if data.get("pairs"):
            best_pair = data["pairs"][0]
            return {
                "chain": best_pair["chainId"],
                "address": best_pair["pairAddress"]
            }

        symbol_query = query.upper()
        response = requests.get(base_url, params={"q": symbol_query})
        response.raise_for_status()
        data = response.json()

        if data.get("pairs"):
            best_pair = data["pairs"][0]
            return {
                "chain": best_pair["chainId"],
                "address": best_pair["pairAddress"]
            }

        return None
    except Exception as e:
        print(f"❌ Dexscreener error for {query}: {e}")
        time.sleep(0.5)
        return None
