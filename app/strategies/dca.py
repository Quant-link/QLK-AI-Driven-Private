import time
import argparse
from decimal import Decimal
from typing import List, Dict, Tuple, Optional

from app.routing.dex_clients.base import DexClient
from app.routing.dex_clients.zerox import ZeroXClient
from app.routing.dex_clients.oneinch import OneInchClient
from app.routing.dex_clients.openocean import OpenOceanClient
from app.routing.dex_clients.coingecko import CoingeckoClient
from app.strategies.arbitrage_and_twap import fetch_all_usd_prices, TOKEN_INFO

class DCAStrategy:
    """
    Dollar-Cost Averaging strategy with multi-DEX fallback and sanity checks:
    - Prioritizes 0x price endpoint, then 1inch, then OpenOcean, finally Coingecko spot price.
    - Filters out quotes deviating >100% from spot market; uses least-deviant if all exceed threshold.
    """
    def __init__(self, dex_clients: List[DexClient], usd_prices: Dict[str, Decimal]):
        self.dex_clients = dex_clients
        self.usd_prices = usd_prices

    def _fetch_best_quote(
        self,
        from_symbol: str,
        to_symbol: str,
        amount: Decimal
    ) -> Tuple[DexClient, Decimal]:
        spot_price = self.usd_prices.get(from_symbol.lower())
        if spot_price is None:
            raise RuntimeError(f"No spot price for {from_symbol}")
        expected_qty = amount / spot_price
        best_pair: Optional[Tuple[DexClient, Decimal]] = None
        best_dev = Decimal('Infinity')
        threshold = Decimal('1.0')
        for dex in self.dex_clients:
            try:
                quote = dex.get_quote(from_symbol, to_symbol, amount)
            except Exception:
                continue
            deviation = abs(quote - expected_qty) / expected_qty
            if deviation <= threshold:
                return dex, quote
            if deviation < best_dev:
                best_dev = deviation
                best_pair = (dex, quote)
        if best_pair:
            return best_pair
        raise RuntimeError(f"No valid quotes for {from_symbol}->{to_symbol}")

    def _execute_trade(
        self,
        dex: DexClient,
        from_symbol: str,
        to_symbol: str,
        amount: Decimal
    ) -> str:
        return dex.swap(from_symbol, to_symbol, amount)

    def run(
        self,
        from_symbol: str,
        to_symbol: str,
        total_usd: Decimal,
        intervals: int,
        delay_seconds: int = 3600
    ):
        amount_per_trade = (total_usd / intervals).quantize(Decimal('0.0001'))
        print(f"Starting DCA for {to_symbol.upper()}: {intervals} trades of {amount_per_trade} {from_symbol} each.")
        for i in range(1, intervals + 1):
            try:
                dex, received = self._fetch_best_quote(from_symbol, to_symbol, amount_per_trade)
                tx = self._execute_trade(dex, from_symbol, to_symbol, amount_per_trade)
                received_str = format(received, 'f')
                print(f"  {to_symbol.upper()} DCA {i}/{intervals}: Bought {received_str} on {dex.name}")
            except Exception as err:
                print(f"  {to_symbol.upper()} DCA {i}/{intervals} failed: {err}")
            if i < intervals:
                time.sleep(delay_seconds)
        print(f"Completed DCA for {to_symbol.upper()}.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run DCA for USDT-based pairs across tokens."
    )
    parser.add_argument(
        "--total-usd", dest="total_usd", required=True,
        type=Decimal,
        help="Total USD amount to spend per token"
    )
    parser.add_argument(
        "--intervals", dest="intervals", default=1,
        type=int,
        help="Number of DCA intervals per token"
    )
    parser.add_argument(
        "--delay", dest="delay_seconds", default=3600,
        type=int,
        help="Delay between intervals in seconds"
    )
    parser.add_argument(
        "--tokens", dest="tokens", nargs="*", default=["all"],
        help="List of target symbols or 'all' for every token"
    )
    args = parser.parse_args()

    usd_prices = fetch_all_usd_prices()
    dex_clients: List[DexClient] = [
        ZeroXClient(), OneInchClient(), OpenOceanClient(), CoingeckoClient()
    ]
    strategy = DCAStrategy(dex_clients=dex_clients, usd_prices=usd_prices)
    from_symbol = "USDT"

    targets = args.tokens
    if "all" in targets:
        targets = [sym for sym in TOKEN_INFO if sym.lower() != from_symbol.lower()]
    for to_symbol in targets:
        strategy.run(
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            total_usd=args.total_usd,
            intervals=args.intervals,
            delay_seconds=args.delay_seconds
        )

if __name__ == "__main__":
    main()
