#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 19:35
# @Author  : HEXU
# @File    : async_connect.py
# @Description :
import asyncio
import os
from redis.asyncio.client import Redis
from redis.asyncio.sentinel import Sentinel
from redis.asyncio.cluster import RedisCluster, ClusterNode
from intelliw.utils.logger import _get_framework_logger
from intelliw.utils.redis import common
from redis.exceptions import ConnectionError, TimeoutError

logger = _get_framework_logger()


class AsyncRedisConnect:
    def __init__(self, client_type, url, password, sentinel_password=None, master_name=None, db=0, pool_size=10,
                 retry_attempts=3, retry_delay=2):
        try:
            self.db = db
            self.url = url
            self.redis_client = None
            self.type = client_type
            self.password = password
            self.pool_size = int(pool_size) if pool_size else 10
            self.sentinel_password = sentinel_password
            self.retry_attempts = retry_attempts
            self.retry_delay = retry_delay
            self.master_name = master_name

            if not common.check_mode(self.type):
                logger.error("mode is not supported")
                return

            if self.type == "single":
                self.host, self.port = self.url.split(':')
                self.redis_client = Redis(host=self.host, port=self.port, db=self.db,
                                          password=self.password,
                                          decode_responses=False, max_connections=self.pool_size,
                                          socket_timeout=2.0, retry_on_timeout=True)

            elif self.type == "cluster":
                self.nodes = [
                    ClusterNode(host=x.split(':')[0], port=int(x.split(':')[1]))
                    for x in self.url.split(',')
                ]
                self.redis_client = RedisCluster(startup_nodes=self.nodes, decode_responses=False,
                                                 password=self.password, max_connections=self.pool_size,
                                                 socket_timeout=2.0)

            elif self.type == "sentinel":
                self.nodes = [(x.split(':')[0], int(x.split(':')[1])) for x in self.url.split(',')]
                self.redis_sentinel = Sentinel(self.nodes, sentinel_kwargs={'password': self.sentinel_password},
                                               socket_timeout=1.0)
                self.redis_client = self._get_sentinel_client()

            # asyncio.run(self._ping_with_retries())

        except Exception as e:
            self.redis_client = None
            logger.error(f"Error initializing Redis client: {e}")

    def _get_sentinel_client(self):
        try:
            return self.redis_sentinel.master_for(self.master_name, socket_timeout=1.0,
                                                  password=self.password, db=self.db,
                                                  decode_responses=False, max_connections=self.pool_size)
        except ConnectionError as e:
            logger.error(f"Error connecting to Redis Sentinel master: {e}")
            return None

    async def _ping_with_retries(self):
        """重试机制，在 Redis 启动时进行 ping 以确保连接可用"""
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    logger.info("Redis connection established.")
                    break
            except (ConnectionError, TimeoutError) as e:
                attempts += 1
                logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
        else:
            logger.error("Failed to connect to Redis after multiple attempts.")
            self.redis_client = None

    async def ping(self):
        """异步ping操作"""
        try:
            await self.redis_client.setex("intelliw:N:cache:ping", 1, "pong")
            logger.info("Ping successful.")
        except Exception as e:
            logger.error(f"Ping failed: {e}")

    async def close(self):
        """手动关闭Redis连接"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed.")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")

    def __del__(self):
        pass
