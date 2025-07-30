'''
Author: Hexu
Date: 2022-09-26 13:34:19
LastEditors: Hexu
LastEditTime: 2022-12-26 16:18:04
FilePath: /iw-algo-fx/intelliw/utils/redis/__init__.py
Description: 
'''
import asyncio
import os

try:
    import redis
except ImportError:
    raise ImportError("\033[31mIf use redis, you need: pip install redis (>=5.0.1) \033[0m")

from .connect import RedisConnect
from .connect_async import AsyncRedisConnect
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()

redis_product_code = 'iuap-aip-console-redis'


def _get_args(client_type=None, url=None, password=None, sentinel_password=None, mater_name=None, db=None,
              pool_size=None):
    rc = redis_product_code
    return (
        client_type or os.environ[f'{rc}_REDIS_TYPE'],
        url or os.environ[f'{rc}_REDIS_URL'],
        password or os.environ[f'{rc}_REDIS_PASSWORD'],
        sentinel_password or os.environ[f'{rc}_REDIS_SENTINEL_PASSWORD'],
        mater_name or os.environ[f'{rc}_REDIS_MASTER_NAME'],
        db or os.environ[f'{rc}_REDIS_DATABASE'],
        pool_size or os.environ[f'{rc}_REDIS_POOL_SIZE']
    )


def get_client(client_type=None, url=None, password=None, sentinel_password=None, master_name=None, db=None,
               pool_size=None):
    redis_client = None

    try:
        args = _get_args(client_type, url, password, sentinel_password, master_name, db, pool_size)
    except KeyError:
        logger.error('Redis args get error: yms config download error or redis config not in yms config')
    else:
        redis_client = RedisConnect(*args).redis_client

    return redis_client


def get_async_client(client_type=None, url=None, password=None, sentinel_password=None, mater_name=None, db=None,
                     pool_size=None):
    redis_client = None

    try:
        args = _get_args(client_type, url, password, sentinel_password, mater_name, db, pool_size)
        conn = AsyncRedisConnect(*args)
        # asyncio.run(conn.ping())
    except KeyError:
        logger.error('Redis args get error: yms config download error or redis config not in yms config')
    except Exception as e:
        logger.error(f'Redis connect error: {e}')
    else:
        redis_client = conn.redis_client
    return redis_client
