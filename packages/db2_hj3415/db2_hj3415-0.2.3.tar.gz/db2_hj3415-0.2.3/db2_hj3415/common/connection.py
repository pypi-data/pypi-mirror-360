# MongoDB 연결
import os
from motor.motor_asyncio import AsyncIOMotorClient

# 싱글톤 몽고 클라이언트 정의
MONGO_URI = os.getenv("MONGO_ADDR")
client: AsyncIOMotorClient = None

def get_mongo_client() -> AsyncIOMotorClient:
    global client
    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)
    return client

def close_mongo_client():
    if client:
        client.close()


from pymongo import MongoClient

client_sync: MongoClient = None  # 동기 클라이언트 타입으로 변경

def get_mongo_client_sync() -> MongoClient:
    """
    MongoDB 동기 클라이언트를 반환합니다.
    전역 client가 None일 경우 새 클라이언트를 생성합니다.
    """
    global client_sync
    if client_sync is None:
        client_sync = MongoClient(MONGO_URI)
    return client_sync

def close_mongo_client_sync():
    if client_sync:
        client_sync.close()
