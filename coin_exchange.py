import json
import websockets
import asyncio
import time

MAX_TRADES = 100

# 🔵 거래소별 체결 데이터 저장소
binance_trades = []
bybit_trades = []
upbit_trades = []
bithumb_trades =[]


# ✅ Binance 실시간 체결 수집기
async def collect_binance_trades():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    async with websockets.connect(url) as ws:
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            trade = {
                "price": float(data["p"]),
                "qty": float(data["q"]),
                "side": "SELL" if data["m"] else "BUY",
                "timestamp": data["T"]
            }
            binance_trades.append(trade)
            if len(binance_trades) > MAX_TRADES:
                binance_trades.pop(0)

# ✅ Bybit 실시간 체결 수집기
async def collect_bybit_trades():
    url = "wss://stream.bybit.com/v5/public/linear"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "op": "subscribe",
            "args": ["publicTrade.BTCUSDT"]
        }))
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get("topic") == "publicTrade.BTCUSDT":
                for item in data["data"]:
                    trade = {
                        "price": float(item["p"]),
                        "qty": float(item["v"]),
                        "side": "SELL" if item["S"] == "Sell" else "BUY",
                        "timestamp": item["T"]
                    }
                    bybit_trades.append(trade)
                    if len(bybit_trades) > MAX_TRADES:
                        bybit_trades.pop(0)

async def collect_upbit_trades():
    url = "wss://api.upbit.com/websocket/v1"
    async with websockets.connect(url, ping_interval=60) as ws:
        subscribe_data = [
            {"ticket": "kanji-btc"},
            {"type": "trade", "codes": ["KRW-BTC"]}
        ]
        await ws.send(json.dumps(subscribe_data))

        while True:
            binary_data = await ws.recv()
            data = json.loads(binary_data.decode("utf-8"))

            trade = {
                "price": float(data["trade_price"]),
                "qty": float(data["trade_volume"]),
                "side": "BUY" if data["ask_bid"] == "BID" else "SELL",
                "timestamp": int(data["timestamp"])  # ms
            }

            upbit_trades.append(trade)
            if len(upbit_trades) > MAX_TRADES:
                upbit_trades.pop(0)

async def collect_bithumb_trades():
    url = "wss://pubwss.bithumb.com/pub/ws"
    async with websockets.connect(url, ping_interval=60) as ws:
        subscribe_data = {
            "type": "transaction",
            "symbols": ["BTC_KRW"]
        }
        await ws.send(json.dumps(subscribe_data))
        #print("[BITHUMB] 구독 요청 전송 완료")

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") == "transaction" and "content" in data:
                for item in data["content"]["list"]:
                    trade = {
                        "price": float(item["contPrice"]),
                        "qty": float(item["contQty"]),
                        "side": "BUY" if item["buySellGb"] == "1" else "SELL",
                        "timestamp": int(time.time() * 1000)
                    }
                    #print("[BITHUMB] 체결 추가:", trade)
                    bithumb_trades.append(trade)
                    if len(bithumb_trades) > MAX_TRADES:
                        bithumb_trades.pop(0)

# ✅ 외부 접근용 getter
def get_binance_trades():
    return binance_trades[-50:]

def get_bybit_trades():
    return bybit_trades[-50:]

def get_upbit_trades():
    return upbit_trades[-50:]

def get_bithumb_trades():
    return bithumb_trades[-50:]