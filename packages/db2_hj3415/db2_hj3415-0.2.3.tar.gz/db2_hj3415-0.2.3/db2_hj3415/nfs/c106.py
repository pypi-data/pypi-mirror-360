from typing import Literal
from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from pymongo import DESCENDING, ASCENDING
from pymongo import IndexModel

from . import _c10346, C106, DB_NAME
from ..common.db_ops import get_collection

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "c106"

async def ensure_indexes(client: AsyncIOMotorClient):
    coll = get_collection(client, DB_NAME, COL_NAME)
    await coll.create_indexes([
        IndexModel([("날짜", DESCENDING), ("코드", ASCENDING)], unique=True),
        IndexModel("q.항목"),
        IndexModel("y.항목"),
    ])

async def save(code: str, data: C106, client: AsyncIOMotorClient) -> dict:
    await ensure_indexes(client)
    return await _c10346.save(COL_NAME, code, data, client)


async def save_many(many_data: dict[str, C106|None], client: AsyncIOMotorClient) -> list[dict]:
    await ensure_indexes(client)
    return await _c10346.save_many(COL_NAME, many_data, client)


ReturnType = C106 | dict[str, pd.DataFrame] | None


async def get_latest(code: str, client: AsyncIOMotorClient, as_type: Literal["model", "dataframe"] = "model") -> ReturnType:
    if as_type == "model":
        return await _c10346.get_latest_as_model(COL_NAME, code, client)

    elif as_type == "dataframe":
        return await _c10346.get_latest_doc_as_df_dict(COL_NAME, code, client)

    else:
        raise ValueError(f"지원하지 않는 반환 타입: '{as_type}' (허용값: 'model', 'dataframe')")


async def has_doc_changed(code: str, client: AsyncIOMotorClient) -> bool:
    """
    C106 컬렉션에서 종목 코드에 대해 최신 두 개의 문서를 비교하여 변경 여부를 확인합니다.

    비교 대상 문서가 두 개 미만이면 True를 반환하여 새 문서로 간주합니다.
    비교는 `_id`, `날짜` 필드를 제외하고 수행하며, 변경 내용이 있을 경우 change_log에 기록됩니다.

    Args:
        code (str): 종목 코드 (6자리 문자열).
        client (AsyncIOMotorClient): MongoDB 비동기 클라이언트 인스턴스.

    Returns:
        bool: 문서가 변경되었는지 여부. True면 변경됨 또는 비교 불가 상태.
    """
    return await _c10346.has_doc_changed(COL_NAME, code, client)