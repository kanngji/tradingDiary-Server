# main.py
from fastapi import FastAPI
from routers import economic_indicator_router, telegram_router,longshort_router
from orderbook_fetcher import fetch_binance,fetch_bybit,fetch_upbit,fetch_bithumb
import asyncio
from coin_exchange import (
    collect_binance_trades,
    collect_bybit_trades,
    collect_upbit_trades,
    collect_bithumb_trades,
    get_bithumb_trades,
    get_upbit_trades,
    get_binance_trades,
    get_bybit_trades

)

app = FastAPI()  # ✅ 이게 꼭 있어야 함!

# 🔥 telegram_router 추가!
app.include_router(telegram_router.router)
app.include_router(longshort_router.router)
app.include_router(economic_indicator_router.router)



@app.get("/")
def main():
    return {"message": "FastAPI 서버가 정상 작동 중입니다!"}

@app.get("/api/orderbook")
def get_orderbook():
    return {
        "binance": fetch_binance(),
        "bybit": fetch_bybit(),
        "upbit": fetch_upbit(),
        "bithumb": fetch_bithumb(),
    }




@app.on_event("startup")
async def startup():
    asyncio.create_task(collect_binance_trades())
    asyncio.create_task(collect_bybit_trades())
    asyncio.create_task(collect_upbit_trades())
    asyncio.create_task(collect_bithumb_trades())

# ✅ Bithumb 실시간 체결 API
@app.get("/api/trades/bithumb")
def api_bithumb():
    print("[API] 현재 bithumb_trades 길이:", len(get_bithumb_trades()))
    return get_bithumb_trades()


@app.get("/api/trades/binance")
def binance():
    return get_binance_trades()

@app.get("/api/trades/bybit")
def bybit():
    return get_bybit_trades()

@app.get("/api/trades/upbit")
def api_upbit():
    return get_upbit_trades()

#@app.get("/api/trades/bithumb")
#def api_bithumb():
#    return get_bithumb_trades()