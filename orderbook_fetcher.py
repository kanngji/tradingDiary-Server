import requests

def fetch_binance():
    res = requests.get("https://api.binance.com/api/v3/depth", params={"symbol": "BTCUSDT", "limit": 5})
    data = res.json()
    return {
        "exchange": "Binance",
        "bids": data["bids"],  # [price, quantity]
        "asks": data["asks"]
    }

def fetch_bybit():
    res = requests.get("https://api.bybit.com/v5/market/orderbook", params={"category": "linear", "symbol": "BTCUSDT"})
    data = res.json()
    return {
        "exchange": "Bybit",
        "bids": data["result"]["b"][:5],
        "asks": data["result"]["a"][:5]
    }

def fetch_upbit():
    res = requests.get("https://api.upbit.com/v1/orderbook", params={"markets": "KRW-BTC"})
    data = res.json()[0]
    return {
        "exchange": "Upbit",
        "bids": [(o["bid_price"], o["bid_size"]) for o in data["orderbook_units"][:5]],
        "asks": [(o["ask_price"], o["ask_size"]) for o in data["orderbook_units"][:5]]
    }

def fetch_bithumb():
    res = requests.get("https://api.bithumb.com/public/orderbook/BTC_KRW", params={"count": 5})
    data = res.json()["data"]
    return {
        "exchange": "Bithumb",
        "bids": [(o["price"], o["quantity"]) for o in data["bids"]],
        "asks": [(o["price"], o["quantity"]) for o in data["asks"]]
    }