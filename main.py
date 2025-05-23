# main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from routers import economic_indicator_router, telegram_router,longshort_router,signup_router,coinvolume_power_router,login_router,calendar_router
from sqlitedatabase import Base, engine
from orderbook_fetcher import fetch_binance,fetch_bybit,fetch_upbit,fetch_bithumb
from clients import clients
from middlewares.api_logger import log_middleware
import asyncio
from routers.coinvolume_power_router import (
    collect_binance_trades,
    collect_bybit_trades,
    collect_upbit_trades,
    collect_bithumb_trades,
)

app = FastAPI()  # ✅ 이게 꼭 있어야 함!

# ✅ logger 미들웨어 추가
app.middleware("http")(log_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://52.64.220.18:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# 🔥 telegram_router 추가!
app.include_router(telegram_router.router)
app.include_router(longshort_router.router)
app.include_router(economic_indicator_router.router)
app.include_router(signup_router.router)
app.include_router(coinvolume_power_router.router)
app.include_router(login_router.router)
app.include_router(calendar_router.router)



@app.get("/")
def main():
    return {"message": "FastAPI 서버가 정상 작동 중입니다!"}

@app.websocket("/ws/client")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # 연결 유지
    except:
        clients.remove(websocket)




@app.on_event("startup")
async def startup():
    asyncio.create_task(collect_binance_trades())
    asyncio.create_task(collect_bybit_trades())
    asyncio.create_task(collect_upbit_trades())
    asyncio.create_task(collect_bithumb_trades())
