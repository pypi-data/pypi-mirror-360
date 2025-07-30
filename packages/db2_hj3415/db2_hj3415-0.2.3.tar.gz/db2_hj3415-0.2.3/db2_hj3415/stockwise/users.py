from motor.motor_asyncio import AsyncIOMotorClient

from ..common.db_ops import get_collection
from .models import User
from . import DB_NAME

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "users"

async def save(user_data: User, client: AsyncIOMotorClient) -> dict:
    if not user_data:
        mylogger.warning("User 데이터 없음 - 저장 생략")
        return {"status": "unchanged"}

    collection = get_collection(client, DB_NAME, COL_NAME)

    await collection.create_index("email", unique=True)
    await collection.create_index("username", unique=True)

    data = user_data.model_dump(by_alias=True, exclude_unset=True)

    filter_ = {"email": user_data.email}

    result = await collection.update_one(
        filter_,
        {"$set": data},
        upsert=True
    )

    if result.upserted_id:
        return {"status": "inserted", "id": str(result.upserted_id)}
    elif result.modified_count:
        return {"status": "updated"}
    else:
        return {"status": "unchanged"}


async def get_user_by_email(email: str, client: AsyncIOMotorClient) -> User | None:
    collection = get_collection(client, DB_NAME, COL_NAME)

    doc = await collection.find_one({"email": email})

    if doc:
        doc["_id"] = str(doc["_id"])
        return User(**doc)
    return None


async def get_user_by_username(username: str, client: AsyncIOMotorClient) -> User | None:
    collection = get_collection(client, DB_NAME, COL_NAME)

    doc = await collection.find_one({"username": username})

    if doc:
        doc["_id"] = str(doc["_id"])
        return User(**doc)
    return None