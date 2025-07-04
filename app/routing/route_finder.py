from app.routing.dex_clients.kyber import get_kyber_route
from app.routing.dex_clients.oneinch import get_oneinch_route
from app.routing.dex_clients.openocean import get_openocean_quote  # fonksiyon adı doğru kullanıldı

def get_best_route(from_token: str, to_token: str, amount: float):
    routes = []

    try:
        oneinch = get_oneinch_route(from_token, to_token, amount)
        if oneinch:
            routes.append({"source": "1inch", **oneinch})
    except Exception as e:
        print(f"[1inch Error] {e}")

    try:
        kyber = get_kyber_route(from_token, to_token, amount)
        if kyber:
            routes.append({"source": "kyber", **kyber})
    except Exception as e:
        print(f"[Kyber Error] {e}")

    try:
        openocean = get_openocean_quote(from_token, to_token, amount)  # doğru fonksiyon çağrısı
        if openocean:
            routes.append({"source": "OpenOcean", **openocean})
    except Exception as e:
        print(f"[OpenOcean Error] {e}")

    if not routes:
        return None

    return max(routes, key=lambda r: r["expectedAmountOut"])
