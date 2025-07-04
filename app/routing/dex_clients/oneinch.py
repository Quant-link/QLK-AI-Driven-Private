import os
import requests
from decimal import Decimal
from dotenv import load_dotenv

from app.routing.dex_clients.base import DexClient

load_dotenv()

API_KEY = os.getenv("ONEINCH_API_KEY")
CHAIN_ID = 1 
ONEINCH_API_BASE = f"https://api.1inch.dev/swap/v5.0/{CHAIN_ID}"
QUOTE_URL = f"{ONEINCH_API_BASE}/quote"
TOKENS_URL = f"{ONEINCH_API_BASE}/tokens"
SWAP_URL  = f"{ONEINCH_API_BASE}/swap"

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def get_supported_tokens() -> dict:
    response = requests.get(TOKENS_URL, headers=headers)
    response.raise_for_status()
    return response.json().get("tokens", {})

def fetch_1inch_route(from_addr: str, to_addr: str, amount_int: int) -> dict:
    params = {
        "src": from_addr,
        "dst": to_addr,
        "amount": str(amount_int)
    }
    r = requests.get(QUOTE_URL, headers=headers, params=params)
    r.raise_for_status()
    d = r.json()
    return {
        "expectedAmountOut": Decimal(d["toAmount"]) / Decimal(10**18),
        "path": [from_addr, to_addr]
    }

class OneInchClient(DexClient):
    name = "1inch"

    def __init__(self):
        self.supported = get_supported_tokens()

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        if from_symbol not in self.supported or to_symbol not in self.supported:
            raise ValueError(f"Unsupported token: {from_symbol} or {to_symbol}")
        from_addr = self.supported[from_symbol]["address"]
        to_addr   = self.supported[to_symbol]["address"]
        amount_int = int(amount * (10 ** self.supported[from_symbol]["decimals"]))
        return fetch_1inch_route(from_addr, to_addr, amount_int)["expectedAmountOut"]

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        if from_symbol not in self.supported or to_symbol not in self.supported:
            raise ValueError(f"Unsupported token: {from_symbol} or {to_symbol}")
        from_addr = self.supported[from_symbol]["address"]
        to_addr   = self.supported[to_symbol]["address"]
        amount_int = str(int(amount * (10 ** self.supported[from_symbol]["decimals"])))
        params = {
            "src": from_addr,
            "dst": to_addr,
            "amount": amount_int
        }
        r = requests.get(SWAP_URL, headers=headers, params=params)
        r.raise_for_status()
        return r.json().get("txHash", "")
