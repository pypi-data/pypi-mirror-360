from motor.motor_asyncio import AsyncIOMotorClient
from typing import Any
import math
from pymongo import ASCENDING, UpdateOne, DESCENDING, ReplaceOne
import pandas as pd
from datetime import datetime, timezone, timedelta, time

from . import DATE_FORMAT, DB_NAME, C108
from ..common.db_ops import get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = 'c108'


# ─── constants ──────────────────────────────────────────
IDX = [("코드", ASCENDING), ("날짜", DESCENDING), ("제목", ASCENDING)]

# ─── main ───────────────────────────────────────────────
async def save(data: list[C108|None], client: AsyncIOMotorClient) -> dict:
    if not data:
        print("데이터 없음 - 저장 생략")
        return {"status": "unchanged"}

    coll = get_collection(client, DB_NAME, COL_NAME)
    await coll.create_index(IDX, unique=True)

    ops: list[ReplaceOne] = []

    for model in data:
        try:
            # Python-native dict (datetime 그대로 유지)
            doc = model.model_dump(mode="python", by_alias=True,
                               exclude={"id", "_id"}, exclude_none=True)

            # ── 날짜 UTC 자정으로 정규화 ────────────────────────
            dt_utc = model.날짜.astimezone(timezone.utc)
            normalized = datetime(dt_utc.year, dt_utc.month, dt_utc.day,
                                  tzinfo=timezone.utc)

            doc["날짜"] = normalized
            filt = {
                "코드": model.코드,
                "제목": model.제목,
                "날짜": normalized,
            }

            ops.append(ReplaceOne(filt, doc, upsert=True))

        except Exception as e:
            print(f"[{model.코드}] 변환 실패 ({model.제목}): {e}")

    if not ops:
        return {"inserted": 0, "updated": 0}

    res = await coll.bulk_write(ops, ordered=False)

    return {
        "inserted": res.upserted_count,
        "updated":  res.modified_count
    }


async def get_latest(code: str, client: AsyncIOMotorClient, days:int = 60) -> list[C108]:
    """
    최근 N일 이내의 C108 리포트 도큐먼트를 조회합니다.

    Args:
        code (str): 종목 코드 (예: "005930").
        client (AsyncIOMotorClient): 비동기 MongoDB 클라이언트.
        days (int, optional): 현재 시점에서 며칠 전까지의 데이터를 조회할지 설정합니다. 기본값은 60일.

    Returns:
        list[C108]: 조건에 해당하는 C108 도큐먼트 리스트. 일치하는 문서가 없을 경우 빈 리스트를 반환합니다.
    """
    collection = get_collection(client, DB_NAME, COL_NAME)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    cursor = collection.find(
        {
            "코드": code,
            "날짜": {"$gte": cutoff}
        }
    ).sort("날짜", DESCENDING)

    docs = await cursor.to_list(length=None)
    if not docs:
        return []
    else:
        c108s = []
        for doc in docs:
            doc["_id"] = str(doc["_id"])
            c108s.append(C108(**doc))
        return c108s


