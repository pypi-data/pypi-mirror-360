#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 19:35
# @Author  : HEXU
# @File    : connect.py
# @Description :
import os

import redis.retry
from time import sleep
from redis.client import Redis
from redis.sentinel import Sentinel
from redis.cluster import RedisCluster, ClusterNode
from redis.exceptions import ConnectionError, TimeoutError
from intelliw.utils.logger import _get_framework_logger
from intelliw.utils.redis import common

logger = _get_framework_logger()


class RedisConnect:
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
            self.is_ipv6 = os.environ.get('USE_IPV6', '').lower() == 'true'

            if not common.check_mode(self.type):
                logger.error("mode is not supported")
                return

            if self.type == "single":
                host, port = self.get_host(self.url)
                self.redis_client = Redis(host=host, port=port, db=self.db,
                                          password=self.password, decode_responses=False,
                                          max_connections=self.pool_size, retry_on_timeout=True)

            elif self.type == "cluster":
                self.nodes = []
                for url in self.url.split(','):
                    host, port = self.get_host(url)
                    self.nodes.append(ClusterNode(host=host, port=port))

                self.redis_client = RedisCluster(startup_nodes=self.nodes, decode_responses=False,
                                                 password=self.password, max_connections=self.pool_size,
                                                 socket_timeout=2, retry_on_timeout=True)

            elif self.type == "sentinel":
                self.nodes = [self.get_host(url) for url in self.url.split(',')]
                self.redis_sentinel = Sentinel(self.nodes, sentinel_kwargs={'password': self.sentinel_password},
                                               socket_timeout=1.0)
                self.redis_client = self._get_sentinel_client()

            self._ping_with_retries()

        except Exception as e:
            self.redis_client = None
            logger.error(f"Error initializing Redis client: {e}")

    def get_host(self, url):
        if self.is_ipv6:
            split = url.rindex(":")
            port = url[split + 1:]
            host = url[:split].replace("]", "").replace("[", "")
        else:
            host, port = self.url.split(':')
        return host, int(port)

    def _get_sentinel_client(self):
        try:
            return self.redis_sentinel.master_for(self.master_name, socket_timeout=1.0,
                                                  password=self.password, db=self.db,
                                                  decode_responses=False, max_connections=self.pool_size)
        except ConnectionError as e:
            logger.error(f"Error connecting to Redis Sentinel master: {e}")
            return None

    def _ping_with_retries(self):
        """重试机制，在 Redis 启动时进行 ping 以确保连接可用"""
        attempts = 0
        while attempts < self.retry_attempts:
            try:
                if self.redis_client:
                    self.redis_client.ping()
                    logger.info("Redis connection established.")
                    break
            except (ConnectionError, TimeoutError) as e:
                attempts += 1
                logger.warning(f"Attempt {attempts} failed: {e}. Retrying in {self.retry_delay} seconds...")
                sleep(self.retry_delay)
        else:
            logger.error("Failed to connect to Redis after multiple attempts.")
            self.redis_client = None

    def __del__(self):
        pass
