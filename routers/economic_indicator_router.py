from fastapi import APIRouter
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

router = APIRouter(prefix="/api/economic-indicators", tags=["economicIndicators"])

FRED_API_KEY = os.getenv("FRED_API_KEY")

# 가져올 시리즈 ID 목록
series_ids = {
    "gdp": "GDP",
    "unemployment_rate": "UNRATE",
    "cpi": "CPIAUCSL",
    "consumer_sentiment": "UMCSENT",
    "federal_funds_rate": "FEDFUNDS",
    "nonfarm_payrolls": "PAYEMS"
}

async def fetch_indicator(series_id):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "sort_order": "desc",  # 최신 데이터가 앞에 오게
        "limit": 1             # 최신 1개만
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    if "observations" in data and data["observations"]:
        obs = data["observations"][0]
        return {
            "date": obs["date"],
            "value": obs["value"]
        }
    else:
        return {
            "date": None,
            "value": None
        }

@router.get("/latest")
async def get_latest_indicators():
    results = {}

    for name, sid in series_ids.items():
        result = await fetch_indicator(sid)
        results[name] = result

    return results