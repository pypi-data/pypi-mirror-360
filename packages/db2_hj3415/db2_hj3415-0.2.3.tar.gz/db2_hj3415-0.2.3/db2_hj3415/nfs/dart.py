from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import InsertOne, DESCENDING, ASCENDING
from pymongo.errors import BulkWriteError
from datetime import datetime, timezone, timedelta

from . import Dart, DB_NAME, get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "dart"

async def save_many(many_data: list[Dart], client: AsyncIOMotorClient) -> dict:
    if not many_data:
        return {"inserted_count": 0, "skipped": 0}

    coll = get_collection(client, DB_NAME, COL_NAME)

    await coll.create_index(
        [
            ("rcept_no", ASCENDING),
            ("stock_code", ASCENDING),
            ("rcept_dt", DESCENDING),
        ],
        unique=True,  # 세가지가 전부 중복일때 저장차단
    )

    ops = []
    for item in many_data:
        mylogger.debug(f"{item.rcept_dt} - {type(item.rcept_dt)}")
        ops.append(InsertOne(item.model_dump(mode="python", exclude={"_id"})))

    try:
        result = await coll.bulk_write(ops, ordered=False)
        return {"inserted_count": result.inserted_count, "skipped": 0}
    except BulkWriteError as e:
        skipped = len(e.details.get("writeErrors", []))
        inserted = e.details.get("nInserted", 0)
        return {"inserted_count": inserted, "skipped": skipped}


async def get_data_last_n_days(code: str, client: AsyncIOMotorClient, days: int = 30) -> list[Dart]:
    coll = get_collection(client, DB_NAME, COL_NAME)

    now_utc = datetime.now(timezone.utc)
    cutoff  = now_utc - timedelta(days=days)

    cursor = coll.find(
        {"stock_code": code, "rcept_dt": {"$gte": cutoff}}
    ).sort("rcept_dt", DESCENDING)

    docs = await cursor.to_list(length=None)
    if not docs:
        return []

    return [Dart(**doc) for doc in docs]


async def get_data_today(client: AsyncIOMotorClient) -> list[Dart]:
    coll = get_collection(client, DB_NAME, COL_NAME)

    now_utc = datetime.now(timezone.utc)
    start = datetime(now_utc.year, now_utc.month, now_utc.day, tzinfo=timezone.utc)
    mylogger.debug(f"start = {start}")
    end   = start + timedelta(days=1)
    mylogger.debug(f"end = {end}")

    cursor = coll.find({"rcept_dt": {"$gte": start, "$lt": end}}).sort("rcept_dt", DESCENDING)

    docs = await cursor.to_list(length=None)
    if not docs:
        return []

    return [Dart(**doc) for doc in docs]