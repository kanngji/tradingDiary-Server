from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient('btc_session', api_id, api_hash)

async def main():
    await client.start()  # 여기서 전화번호 & 코드 입력 요청
    print("✅ 세션 파일 생성 완료!")

import asyncio
asyncio.run(main())