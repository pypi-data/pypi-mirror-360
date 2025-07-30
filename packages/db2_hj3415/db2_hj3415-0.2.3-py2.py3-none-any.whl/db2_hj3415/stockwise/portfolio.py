from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

from ..common.db_ops import get_collection
from .models import Portfolio
from . import DB_NAME

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "portfolio"

async def save(portfolio_data: Portfolio, client: AsyncIOMotorClient) -> dict:
    if not portfolio_data:
        mylogger.warning("Portfolio 데이터가 None입니다.")
        return {"status": "unchanged"}

    collection = get_collection(client, DB_NAME, COL_NAME)
    await collection.create_index([("user_id", 1), ("코드", 1)], unique=True)
    # upsert 필터: 동일한 user_id + 종목코드 조합 기준
    filter_ = {
        "user_id": portfolio_data.user_id,
        "코드": portfolio_data.코드,
    }

    # 날짜 업데이트
    data = portfolio_data.model_dump(by_alias=True, exclude_unset=True)
    data["last_updated"] = datetime.utcnow()

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


async def get_portfolios_by_user_id(user_id: str, client: AsyncIOMotorClient) -> list[Portfolio]:
    collection = get_collection(client, DB_NAME, COL_NAME)

    cursor = collection.find({"user_id": user_id})
    portfolios = []
    async for doc in cursor:
        portfolios.append(Portfolio(**doc))
    return portfolios