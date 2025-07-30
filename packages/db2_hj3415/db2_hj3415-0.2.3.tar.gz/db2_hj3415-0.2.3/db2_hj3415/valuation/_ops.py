from pymongo import ASCENDING
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, time
from bson import ObjectId

from . import DB_NAME, MilData, RedData
from ..common.db_ops import get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

T = RedData | MilData

async def save(col: str, data: T, client: AsyncIOMotorClient) -> dict:
    collection = get_collection(client, DB_NAME, col)
    await collection.create_index([("날짜", ASCENDING), ("코드", ASCENDING)], unique=True)

    if not data.날짜:
        data.날짜 = datetime.now(timezone.utc)

    # 날짜 기준 중복 확인
    today = data.날짜.date()

    existing = await collection.find_one({
        "코드": data.코드,
        "날짜": {
            "$gte": datetime.combine(today, time.min).replace(tzinfo=timezone.utc),
            "$lt": datetime.combine(today, time.max).replace(tzinfo=timezone.utc)
        }
    })
    mylogger.debug(f"이미 저장된 오늘 날짜 데이터가 있나?: {existing}")

    if existing:
        return {"status": "skipped", "reason": "already_saved_today"}

    # datetime 그대로 유지하기 위해 mode='python' 사용
    doc = data.model_dump(by_alias=True, mode='python', exclude_none=False)

    # ObjectId가 존재하면 업데이트, 아니면 삽입
    if '_id' in doc:
        if doc['_id'] is None:
            doc.pop('_id')  # None이면 제거하여 MongoDB에서 자동 생성되게 함
        else:
            doc['_id'] = ObjectId(doc['_id']) if isinstance(doc['_id'], str) else doc['_id']
            await collection.replace_one({'_id': doc['_id']}, doc, upsert=True)
            return {"status": "updated", "_id": str(doc['_id'])}

    result = await collection.insert_one(doc)
    data.id = str(result.inserted_id)
    return {"status": "inserted", "_id": data.id}


async def save_many(col: str, many_data: dict[str, T], client: AsyncIOMotorClient) -> dict:
    results = {}

    # 이 방식이 속도는 느리지만 제일 간단하고 안정적인 방식임.
    for code, data in many_data.items():
        try:
            result = await save(col, data, client)
            results[code] = result
        except Exception as e:
            # 에러 발생 시 로깅 또는 실패 처리
            results[code] = {"status": "error", "error": str(e)}
            mylogger.error(f"[{code}] 저장 중 오류 발생: {e}")

    return results
