from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

mongo_client = AsyncIOMotorClient(MONGO_URI)

# 사용할 데이터베이스 이름 정하기 (예: user_logs)
mongo_db = mongo_client["user_logs"]