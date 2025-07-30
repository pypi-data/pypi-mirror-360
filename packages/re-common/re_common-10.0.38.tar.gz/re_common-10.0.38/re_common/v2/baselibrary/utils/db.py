import os
import time

import aiomysql
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Tuple
from collections import namedtuple

from aiomysql import Pool, Connection, Cursor

DB_CONFIG = {
    "host": "192.168.98.64",
    "port": 4000,
    "user": "dataware_house_baseUser",
    "password": "FF19AF831AEBD580B450B16BF9264200",
    "db": "dataware_house_base",
    "charset": "utf8mb4",
    "minsize": 16,  # 最小连接数
    "maxsize": 128,  # 最大连接数
    "autocommit": False,  # 自动提交事务
    "pool_recycle": 3600,  # 每个连接的回收时间（秒），超过此时间后连接将被关闭并重新创建，避免失效连接
    "echo": False,  # 打印SQL语句
}

DB_CONFIG1 = {
    "host": "192.168.98.64",
    "port": 4000,
    "user": "foreign_fulltextUser",
    "password": "i4hIeasw1qpmhGN2nwL7",
    "db": "foreign_fulltext",
    "charset": "utf8mb4",
    "minsize": 16,  # 最小连接数
    "maxsize": 128,  # 最大连接数
    "autocommit": False,  # 自动提交事务
    "pool_recycle": 3600,  # 每个连接的回收时间（秒），超过此时间后连接将被关闭并重新创建，避免失效连接
    "echo": False,  # 打印SQL语句
}


async def get_pool_only(_DB_CONFIG: dict = None):
    global DB_CONFIG
    if _DB_CONFIG is not None:
        DB_CONFIG = _DB_CONFIG
    pool: Pool = await aiomysql.create_pool(**DB_CONFIG)
    return pool


@asynccontextmanager
async def get_db_pool(_DB_CONFIG: dict = None):
    """异步数据库连接池管理工具"""
    global DB_CONFIG
    if _DB_CONFIG is not None:
        DB_CONFIG = _DB_CONFIG
    pool: Pool = await aiomysql.create_pool(**DB_CONFIG)
    try:
        yield pool
    finally:
        pool.close()
        await pool.wait_closed()


@asynccontextmanager
async def get_session(pool: Pool) -> AsyncGenerator[Tuple[Connection, Cursor], None]:
    """获取数据库会话"""
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            yield conn, cursor


async def dictfetchall(cursor: Cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in await cursor.fetchall()]


async def namedtuplefetchall(cursor: Cursor):
    """
    Return all rows from a cursor as a namedtuple.
    Assume the column names are unique.
    """
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [nt_result(*row) for row in await cursor.fetchall()]


# main.py


aiomysql_pool = None
pool_lock = asyncio.Lock()  # 全局异步锁



async def init_aiomysql_pool_async():
    global aiomysql_pool
    if aiomysql_pool is None:
        async with pool_lock:
            if aiomysql_pool is None:
                print(f"[{os.getpid()}] Initializing aiomysql pool...")
                aiomysql_pool = await aiomysql.create_pool(**DB_CONFIG)
    return aiomysql_pool


motor_fs = None
client = None
motor_fs_lock = asyncio.Lock()  # 全局异步锁
_loop_id_mongo = None

async def check_connection(client):
    try:
        print("check mongodb client ping")
        await client.admin.command("ping")
        return True
    except Exception:
        return False


async def init_motor_async(uri, db_name, bucket_name, is_reload=False):
    global motor_fs, client, _loop_id_mongo
    is_ping = True

    if _loop_id_mongo is not None:
        loop_id = id(asyncio.get_running_loop())
        if loop_id != _loop_id_mongo:
            is_reload = True

    # 防止 每次都检查 只有 is_reload 时才检查连接
    if is_reload:
        is_ping = await check_connection(client)
    if motor_fs is None or not is_ping:
        async with motor_fs_lock:
            if motor_fs is None or not is_ping:
                print(f"[{os.getpid()}] Initializing motor_fs...")
                from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
                client = AsyncIOMotorClient(uri)
                db = client[db_name]
                motor_fs = AsyncIOMotorGridFSBucket(database=db, bucket_name=bucket_name)
                _loop_id_mongo = id(asyncio.get_running_loop())
    return motor_fs, client

# async def run_main():
#     while True:
#         uri = "mongodb://192.168.98.80:27001/wpdc"
#         db_name = "wpdc"
#         bucket_name = "sci_doc"
#         motor_fs, client = await init_motor_async(uri, db_name, bucket_name,is_reload=True)
#         # print(await check_connection(client))
#         time.sleep(3)
#
#
# if __name__ == "__main__":
#     asyncio.run(run_main())
