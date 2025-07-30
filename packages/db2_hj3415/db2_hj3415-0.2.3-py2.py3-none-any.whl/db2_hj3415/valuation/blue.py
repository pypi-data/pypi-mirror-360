from motor.motor_asyncio import AsyncIOMotorClient

from . import BlueData, _ops

from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__, 'WARNING')

COL_NAME = "blue"


async def save(blue_data: BlueData, client: AsyncIOMotorClient) -> dict:
    return await _ops.save(COL_NAME, blue_data, client)


async def save_many(many_data: dict[str, BlueData], client: AsyncIOMotorClient) -> dict:
    return await _ops.save_many(COL_NAME, many_data, client)