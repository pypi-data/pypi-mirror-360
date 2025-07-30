from motor.motor_asyncio import AsyncIOMotorClient

from . import RedData, _ops

from utils_hj3415 import setup_logger


mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "red"


async def save(red_data: RedData, client: AsyncIOMotorClient) -> dict:
    return await _ops.save(COL_NAME, red_data, client)


async def save_many(many_data: dict[str, RedData], client: AsyncIOMotorClient) -> dict:
    return await _ops.save_many(COL_NAME, many_data, client)
