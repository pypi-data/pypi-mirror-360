#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/22 16:45
# @Author  : HEXU
# @File    : test.py
# @Description :
import os
import asyncio
from datetime import datetime

from intelliw.utils.redis import get_client, get_async_client

os.environ['iuap-aip-console-redis_REDIS_TYPE'] = 'cluster'
os.environ['iuap-aip-console-redis_REDIS_URL'] = '172.20.32.142:6379,172.20.32.195:6379,172.20.32.16:6379'
os.environ['iuap-aip-console-redis_REDIS_PASSWORD'] = 'Vo14OCmocLJAC9Nd'
os.environ['iuap-aip-console-redis_REDIS_SENTINEL_PASSWORD'] = ''
os.environ['iuap-aip-console-redis_REDIS_MASTER_NAME'] = ''
os.environ['iuap-aip-console-redis_REDIS_DATABASE'] = ''
os.environ['iuap-aip-console-redis_REDIS_POOL_SIZE'] = '20'


def sync_client():
    rs = get_client()

    data_key = "intelliw:N:test"
    result_tag = rs.set(data_key, str(datetime.now()))
    print("sync_client set", result_tag)
    value = rs.get(data_key)
    print("sync_client get", value)


async def async_client():
    rs = get_async_client()

    data_key = "intelliw:N:test"
    result_tag = await rs.set(data_key, str(datetime.now()))
    print("async_client set", result_tag)
    value = await rs.get(data_key)
    print("async_client set", value)


if __name__ == '__main__':
    sync_client()
    asyncio.run(async_client())
