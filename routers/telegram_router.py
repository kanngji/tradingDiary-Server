from fastapi import APIRouter
import os
from telethon import TelegramClient
from dotenv import load_dotenv
import asyncio

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

client = TelegramClient('btc_session', api_id, api_hash)

# ✅ 채널 목록 (Kanji 버전)
channels = ["Cryptobantergroup0", "cryptoquant_official", "Crypto", "Cryptocurrency_Bitcoin_BTC"]

# ✅ FastAPI 앱 시작할 때 한 번만 client.start() 실행되게 만들기
client_started = False

async def ensure_client_started():
    global client_started
    if not client_started:
        await client.start()
        client_started = True

# ✅ 단일 채널 인기글 가져오기
async def fetch_popular_posts(channel_username, keyword="bitcoin", limit=100):
    await ensure_client_started()

    messages = []
    async for message in client.iter_messages(channel_username, limit=limit):
        if message.message and keyword.lower() in message.message.lower():
            messages.append({
                'text': message.message,
                'views': message.views or 0
            })

    sorted_messages = sorted(messages, key=lambda x: x['views'], reverse=True)
    return sorted_messages[:3]  # 각 채널 상위 3개만

# ✅ 전체 채널 인기글 API (채널별 묶음 반환)
@router.get("/popular-posts")
async def get_popular_posts(keyword: str = "bitcoin"):
    result = []

    for channel in channels:
        try:
            posts = await fetch_popular_posts(channel, keyword)
            result.append({
                'channel': channel,
                'posts': posts
            })
        except Exception as e:
            result.append({
                'channel': channel,
                'error': str(e),
                'posts': []
            })

    return result
