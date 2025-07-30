from copy import deepcopy
from datetime import datetime, timezone
from deepdiff import DeepDiff
from pymongo import DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
import json

from asyncio import Semaphore, gather

from . import DB_NAME, C103, C104, C106, C108, C101
from ..common.db_ops import get_collection


from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')


async def _compare_and_log_diff(
    code: str,
    new_doc: dict,              # ← 이미 dict 로 변환된 새 문서
    latest_doc: dict | None,    # ← MongoDB 에서 꺼낸 가장 최근 문서
    client: AsyncIOMotorClient
) -> bool:
    """
    두 문서의 차이를 비교하고,
    - 변경 없음  → False 반환
    - 변경 있음 → change_log 컬렉션에 diff 기록 후 True 반환
    """
    if latest_doc is None:          # 첫 저장
        return True

    # 원본 훼손 방지를 위해 deepcopy
    old = deepcopy(latest_doc)
    new = deepcopy(new_doc)

    # 비교 대상에서 제외할 필드
    for fld in ("_id", "날짜"):
        old.pop(fld, None)
        new.pop(fld, None)

    diff = DeepDiff(old, new, ignore_order=True)
    if not diff:
        print(f"[{code}] 기존 문서와 동일 → 저장 생략")
        return False

    # diff 를 로그에 남김
    await client[DB_NAME]["change_log"].insert_one({
        "코드": code,
        "변경시각": datetime.now(timezone.utc),
        "변경내용": json.loads(diff.to_json())
    })
    return True

T = C101 | C103 | C104 | C106 | list[C108] | None

async def save(col: str, code: str, data: T, client: AsyncIOMotorClient) -> dict:
    coll = get_collection(client, DB_NAME, col)
    doc = data.model_dump(by_alias=True, mode="python", exclude={"id", "_id"})

    # 같은 코드에 대해 날짜 내림차순으로 최신 1건 조회
    latest_doc = await coll.find_one({"코드": code}, sort=[("날짜", DESCENDING)])

    # 변경 여부 판단
    if not await _compare_and_log_diff(code, doc, latest_doc, client):
        return {"status": "unchanged"}

    # 새 문서 삽입
    insert_result = await coll.insert_one(doc)
    print(f"[{code}] 새 문서 삽입 → _id={insert_result.inserted_id}")

    # ▸ 최신 2 건만 남기고 나머지 삭제  -----------------------------
    #   (삽입 직후이므로 현재는 최소 1건 이상 존재)
    old_ids = [
        d["_id"]
        async for d in coll.find({"코드": code})
        .sort("날짜", DESCENDING)
        .skip(2)  # 최신 2건 건너뛰기
    ]
    if old_ids:
        del_res = await coll.delete_many({"_id": {"$in": old_ids}})
        print(f"[{code}] 이전 문서 {del_res.deleted_count}건 삭제")

    return {"status": "inserted", "_id": str(insert_result.inserted_id)}


ASYNC_LIMIT = 20                # 동시에 최대 20 개 Task

T_MANY = list[C101 | None] | dict[str, C103 | C104 | C106 | None] | list[C108 | None]

async def _save_one_wrapper(col: str, code: str, data: T,
                            client: AsyncIOMotorClient,
                            sem: Semaphore) -> dict:
    if data is None:
        return {"code": code, "status": "skipped"}

    async with sem:
        try:
            return await save(col, code, data, client)  # ← save() 반환 그대로
        except Exception as e:
            return {"code": code, "status": "error", "reason": str(e)}


async def save_many(col: str,
                    many_data: T_MANY,
                    client: AsyncIOMotorClient) -> list[dict]:
    sem = Semaphore(ASYNC_LIMIT)

    tasks = [
        _save_one_wrapper(col, code, data, client, sem)
        for code, data in many_data.items()
    ]

    results = await gather(*tasks)
    mylogger.debug(results)
    return results


async def fetch_latest_doc(col: str, code: str, client: AsyncIOMotorClient) -> dict | None:
    collection = get_collection(client, DB_NAME, col)

    # 최신 날짜 기준으로 정렬하여 1건만 조회
    latest_doc = await collection.find_one(
        {"코드": code},
        sort=[("날짜", DESCENDING)]
    )

    if not latest_doc:
        print(f"문서 없음: {code}")
        return None

    latest_doc["_id"] = str(latest_doc["_id"])

    return latest_doc


async def get_latest_as_model(col: str, code: str, client: AsyncIOMotorClient) -> C103 | C104 | C106 | None:
    latest_doc = await fetch_latest_doc(col, code, client)

    if not latest_doc:
        return None

    match col:
        case 'c103':
            return C103(**latest_doc)
        case 'c104':
            return C104(**latest_doc)
        case 'c106':
            return C106(**latest_doc)
        case _:
            raise ValueError(f"지원하지 않는 컬렉션 이름: {col}")


async def get_latest_doc_as_df_dict(col: str, code: str, client: AsyncIOMotorClient) -> dict[str, pd.DataFrame] | None:
    latest_doc = await fetch_latest_doc(col, code, client)

    if not latest_doc:
        return None

    keys_map = {
        'c103': [
            "손익계산서y", "재무상태표y", "현금흐름표y",
            "손익계산서q", "재무상태표q", "현금흐름표q"
        ],
        'c104': [
            '수익성y', '성장성y', '안정성y', '활동성y', '가치분석y',
            '수익성q', '성장성q', '안정성q', '활동성q', '가치분석q'
        ],
        'c106': ['q', 'y']
    }

    def make_df_dict(keys: list[str]) -> dict[str, pd.DataFrame]:
        """latest_doc에서 주어진 키들을 기반으로 DataFrame 생성"""
        return {
            key: pd.DataFrame(latest_doc.get(key) or []) for key in keys
        }

    def concat_by_suffix(dfs: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        """'q', 'y' 접미사 기준으로 그룹 후 하나의 DataFrame으로 합침"""
        grouped: dict[str, list[pd.DataFrame]] = {'q': [], 'y': []}

        for key, df in dfs.items():
            if key.endswith('q'):
                grouped['q'].append(df.assign(분류=key))
            elif key.endswith('y'):
                grouped['y'].append(df.assign(분류=key))

        def clean_df(df: pd.DataFrame) -> pd.DataFrame:
            # 모든 값이 NaN인 열 제거
            return df.dropna(axis=1, how='all')

        return {
            period: (
                pd.concat(
                    [clean_df(f) for f in frames if not f.empty],
                    ignore_index=True
                ) if any(not f.empty for f in frames) else pd.DataFrame()
            )
            for period, frames in grouped.items()
        }

    # 2. 실제 처리 로직
    match col:
        case 'c103':
            return make_df_dict(keys_map['c103'])

        case 'c104':
            raw_result = make_df_dict(keys_map['c104'])
            return concat_by_suffix(raw_result)

        case 'c106':
            return make_df_dict(keys_map['c106'])

        case _:
            raise ValueError(f"지원하지 않는 컬렉션 이름: {col}")


async def has_doc_changed(col: str, code: str, client: AsyncIOMotorClient) -> bool:
    """
    MongoDB에서 특정 컬렉션과 종목 코드에 대해 최신 두 개의 문서를 비교하여 변경 여부를 확인합니다.

    비교 대상 문서가 두 개 미만이면 True를 반환하여 새 문서로 간주합니다.
    비교는 `_id`, `날짜` 필드를 제외하고 수행하며, 변경 내용이 있을 경우 change_log에 기록됩니다.

    Args:
        col (str): 컬렉션 이름 (예: 'c103' 'c104', 'c106'등).
        code (str): 종목 코드 (6자리 문자열).
        client (AsyncIOMotorClient): MongoDB 비동기 클라이언트 인스턴스.

    Returns:
        bool: 문서가 변경되었는지 여부. True면 변경됨 또는 비교 불가 상태.
    """
    collection = get_collection(client, DB_NAME, col)

    # 최신 문서 2개 조회 (내림차순)
    docs = await collection.find({"코드": code}).sort("날짜", DESCENDING).limit(2).to_list(length=2)

    if len(docs) < 2:
        print(f"{code} 문서가 1개 이하임 - 비교 불가")
        return True  # 비교할 게 없으면 새로 저장해야 하므로 True

    new_doc, latest_doc = docs[0], docs[1]

    new_doc.pop("_id", None)
    new_doc.pop("날짜", None)
    latest_doc.pop("_id", None)
    latest_doc.pop("날짜", None)

    mylogger.debug(new_doc)
    mylogger.debug(latest_doc)

    # 비교 함수 호출
    return await _compare_and_log_diff(code, new_doc, latest_doc, client)



