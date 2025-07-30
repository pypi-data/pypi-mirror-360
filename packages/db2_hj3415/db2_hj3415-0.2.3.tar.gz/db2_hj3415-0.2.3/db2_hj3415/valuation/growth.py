from motor.motor_asyncio import AsyncIOMotorClient

from . import GrowthData, _ops
from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "growth"


async def save(growth_data: GrowthData, client: AsyncIOMotorClient) -> dict:
    return await _ops.save(COL_NAME, growth_data, client)


async def save_many(many_data: dict[str, GrowthData], client: AsyncIOMotorClient) -> dict:
    return await _ops.save_many(COL_NAME, many_data, client)