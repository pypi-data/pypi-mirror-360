from motor.motor_asyncio import AsyncIOMotorClient
from . import _ops
from .models import Usdidx

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "usdidx"


async def save(data: Usdidx, client: AsyncIOMotorClient):
    return await _ops._save_one_collection(COL_NAME, data, client)


async def find(date_str: str, client: AsyncIOMotorClient):
    return await _ops.find(COL_NAME, date_str, client)


async def delete(date_str: str, client: AsyncIOMotorClient):
    return await _ops.delete(COL_NAME, date_str, client)

