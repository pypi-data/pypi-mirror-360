from typing import Literal
from datetime import datetime, time, timezone
from pymongo import ASCENDING, DESCENDING, ReplaceOne
from motor.motor_asyncio import AsyncIOMotorClient

from . import DB_NAME, C101
from ..common.db_ops import get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "c101"

async def save(data: C101 | None, client: AsyncIOMotorClient) -> dict:
    if not data:
        return {"status": "unchanged"}

    coll = get_collection(client, DB_NAME, COL_NAME)
    # 애플리케이션 초기화 단계에서 한 번만 호출하는 것이 이상적
    await coll.create_index([("날짜", DESCENDING), ("코드", ASCENDING)], unique=True)

    # ───── 날짜 범위(Filter) ─────
    dt_utc = data.날짜.astimezone(timezone.utc)
    start  = datetime.combine(dt_utc.date(), time.min, tzinfo=timezone.utc)
    end    = datetime.combine(dt_utc.date(), time.max, tzinfo=timezone.utc)

    filter_ = {"날짜": {"$gte": start, "$lt": end}, "코드": data.코드}

    # ───── 기존 문서 여부 확인 ─────
    existing = await coll.find_one(filter_, {"_id": 1})
    # ※ projection 으로 _id 만 가져와 트래픽 최소화

    # ───── 새 문서(dict) 생성 ─────
    doc = data.model_dump(by_alias=True, mode="python", exclude={"id", "_id"})
    doc["날짜"] = dt_utc          # 시·분·초 유지하여 저장

    if existing:
        # 기존 문서가 있으면 _id 를 그대로 유지해야 immutable 오류가 나지 않음
        doc["_id"] = existing["_id"]        # ObjectId
    # existing 이 없으면 _id 를 넣지 말고 그대로 두면, replace_one(upsert=True)가
    # 새 ObjectId 를 자동 생성하면서 삽입한다.

    # ───── replace (upsert) ─────
    result = await coll.replace_one(filter_, doc, upsert=True)

    if result.upserted_id:
        return {"status": "inserted", "_id": str(result.upserted_id)}
    elif result.modified_count:
        return {"status": "replaced", "_id": str(existing["_id"])}
    else:
        # theoretically 발생하기 어려움(내용 완전히 동일)
        return {"status": "unchanged"}


async def save_many(many_data: list[C101 | None], client: AsyncIOMotorClient) -> dict:
    coll = get_collection(client, DB_NAME, COL_NAME)
    # 한 번만 생성하는 것이 이상적
    await coll.create_index([("날짜", 1), ("코드", 1)], unique=True)

    operations = []
    for model in many_data:
        if model is None:
            continue

        # ───── Pydantic → dict ─────
        doc = model.model_dump(by_alias=True, mode="python", exclude={"id", "_id"})

        # 날짜+코드 조합이 이미 있으면 해당 문서를 통째로 교체,
        # 없으면 upsert 로 새로 삽입
        filter_ = {"날짜": doc["날짜"], "코드": doc["코드"]}
        operations.append(ReplaceOne(filter_, doc, upsert=True))

    if operations:
        result = await coll.bulk_write(operations, ordered=False)
        inserted = result.upserted_count  # 새로 들어간 갯수
        updated = result.modified_count  # 내용이 바뀐 갯수
        print(f"저장 완료: inserted={inserted}, updated={updated}")
        return {"inserted": inserted, "updated": updated}
    else:
        print("저장할 작업 없음")
        return {"inserted": 0, "updated": 0}


async def get_latest(code: str, client: AsyncIOMotorClient) -> C101 | None:
    collection = get_collection(client, DB_NAME, COL_NAME)
    doc = await collection.find_one(
        {"코드": code},
        sort=[("날짜", DESCENDING)]
    )

    if doc:
        doc["_id"] = str(doc["_id"])
        mylogger.debug(doc)
        return C101(**doc)
    else:
        mylogger.warning(f"데이터 없음: {code}")
        return None


async def get_name(code: str, client: AsyncIOMotorClient) -> str | None:
    c101_data = await get_latest(code, client)
    if c101_data is None:
        return None
    else:
        return c101_data.종목명


SortOrder = Literal["asc", "desc"]

async def get_all_data(code: str, client: AsyncIOMotorClient, sort: SortOrder = 'asc') -> list[C101]:
    """
    지정한 종목 코드의 C101 도큐먼트 전체를 날짜 기준으로 정렬하여 반환합니다.

    Args:
        code (str): 조회할 종목 코드 (예: "005930").
        client (AsyncIOMotorClient): 비동기 MongoDB 클라이언트 인스턴스.
        sort (Literal["asc", "desc"], optional): 날짜 정렬 방식.
            - "asc": 오름차순 (과거 → 최신)
            - "desc": 내림차순 (최신 → 과거)
            기본값은 "asc".

    Returns:
        list[C101]: 정렬된 C101 모델 리스트.
                    문서가 없을 경우 빈 리스트를 반환합니다.
    """
    collection = get_collection(client, DB_NAME, COL_NAME)
    sort_order = ASCENDING if sort == "asc" else DESCENDING
    cursor = collection.find({"코드": code}).sort("날짜", sort_order)
    docs = await cursor.to_list(length=None)

    if not docs:
        print(f"[{code}] 관련 문서 없음")
        return []

    result: list[C101] = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])  # ObjectId → str (C101에서 id: str)
        result.append(C101(**doc))

    return result

