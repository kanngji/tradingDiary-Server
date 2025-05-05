from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/api/longshort", tags=["longshort"])

# ✅ Binance Long/Short Ratio
async def fetch_binance_ratio():
    url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
    params = {"symbol": "BTCUSDT", "period": "5m", "limit": 1}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        print("Binance 응답:", response.text)  # ★ 추가
        data = response.json()
        if data:
            long_ratio = float(data[0]["longAccount"]) * 100
            short_ratio = float(data[0]["shortAccount"]) * 100
            return {"long": round(long_ratio, 2), "short": round(short_ratio, 2)}
    return {"long": 0, "short": 0}

async def fetch_binance_top_ratio():
    url = "https://fapi.binance.com/futures/data/topLongShortPositionRatio"
    params = {"symbol": "BTCUSDT", "period": "5m", "limit": 1}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        print("Binance Top Traders 응답:", response.text)
        data = response.json()
        if data:
            long_ratio = float(data[0]["longAccount"]) * 100
            short_ratio = float(data[0]["shortAccount"]) * 100
            return {"long": round(long_ratio, 2), "short": round(short_ratio, 2)}
    return {"long": 0, "short": 0}

# ✅ API 엔드포인트
@router.get("/ratios")
async def get_long_short_ratios():
    binanceEntire = await fetch_binance_ratio()
    binanceTop = await fetch_binance_top_ratio()
    return {
        "binanceEntire": binanceEntire,
        "binanceTop": binanceTop
    }