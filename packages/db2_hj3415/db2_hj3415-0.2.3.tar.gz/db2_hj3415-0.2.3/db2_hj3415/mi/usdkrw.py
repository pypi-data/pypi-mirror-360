from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from . import _ops
from .models import Usdkrw

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "usdkrw"


async def save(data: Usdkrw, client: AsyncIOMotorClient):
    return await _ops._save_one_collection(COL_NAME, data, client)


async def find(date_str: str, client: AsyncIOMotorClient):
    return await _ops.find(COL_NAME, date_str, client)


async def delete(date_str: str, client: AsyncIOMotorClient):
    return await _ops.delete(COL_NAME, date_str, client)


async def save_history(df: pd.DataFrame, client: AsyncIOMotorClient):
    numeric_columns = ["매매기준율", "전일대비", "현찰로 사실 때", "현찰로 파실 때", "송금 보내실 때", "송금 받으실 때"]
    await _ops._save_market_history_type1(df, COL_NAME, numeric_columns, client)
