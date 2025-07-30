from motor.motor_asyncio import AsyncIOMotorClient
import pandas as pd
from . import _ops
from .models import Kospi

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "kospi"


async def save(data: Kospi, client: AsyncIOMotorClient):
    return await _ops._save_one_collection(COL_NAME, data, client)


async def find(date_str: str, client: AsyncIOMotorClient):
    return await _ops.find(COL_NAME, date_str, client)


async def delete(date_str: str, client: AsyncIOMotorClient):
    return await _ops.delete(COL_NAME, date_str, client)


async def save_history(df: pd.DataFrame, client: AsyncIOMotorClient):
    numeric_columns = ["체결가", "전일비", "거래량(천주)", "거래대금(백만)"]
    await _ops._save_market_history_type1(df, COL_NAME, numeric_columns, client)
