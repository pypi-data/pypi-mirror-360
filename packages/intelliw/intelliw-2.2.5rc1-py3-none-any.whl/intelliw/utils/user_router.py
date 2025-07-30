import threading
import os
import time
import requests
from typing import Dict, Optional, Any
from collections import OrderedDict
from intelliw.utils import iuap_request
from intelliw.config import config
import logging

logger = logging.getLogger('user_router')
logger.setLevel("INFO")
logger_code = "intelliw.logger.level"

class UserRouter:

    TENANT_ID_MAPPING_URI = "/self/tenantapi/acquireToken" # 获取租户ID映射关系

    def __init__(
        self,
        timeout: float = 5.0,
        cache_size: int = 1000,
        cache_ttl: int = 60  # 1分钟
    ):
        self.mapping_url = f"{os.environ.get('domain.url')}/{os.getenv('YMS_CONSOLE_APP_CODE', 'iuap-aip-console')}{UserRouter.TENANT_ID_MAPPING_URI}"
        self.timeout = timeout
        self.tenantid_cache_lock = threading.Lock()  # 专门用于tenantid缓存的锁
        self.token_cache_lock = threading.Lock()  # 专门用于token缓存的锁
        
        # tenantid缓存：{tenantid: (yms_key, timestamp)}
        self.tenantid_cache = OrderedDict()
        self.tenantid_cache_size = cache_size
        self.tenantid_cache_ttl = cache_ttl
        
        # Token缓存：{token: (yms_key, timestamp)}
        self.token_cache = OrderedDict()
        self.token_cache_size = cache_size
        self.token_cache_ttl = cache_ttl

    def _get_from_token_cache(self, token: str) -> Optional[str]:
        """从token缓存中获取 vecdb_code"""
        with self.token_cache_lock:
            if token in self.token_cache:
                vecdb_code, timestamp = self.token_cache[token]
                # 检查是否过期
                if time.time() - timestamp < self.token_cache_ttl:
                    # 更新访问时间（LRU特性）
                    self.token_cache.move_to_end(token)
                    return vecdb_code
                # 如果过期则移除
                del self.token_cache[token]
        return None
    
    def _get_from_tenantid_cache(self, tenantid: str) -> Optional[str]:
        """从tenantid缓存中获取 vecdb_code"""
        with self.tenantid_cache_lock:
            if tenantid in self.tenantid_cache:
                vecdb_code, timestamp = self.tenantid_cache[tenantid]
                # 检查是否过期
                if time.time() - timestamp < self.tenantid_cache_ttl:
                    # 更新访问时间（LRU特性）
                    self.tenantid_cache.move_to_end(tenantid)
                    return vecdb_code
                # 如果过期则移除
                del self.tenantid_cache[tenantid]
        return None

    def _add_to_token_cache(self, token: str, vecdb_code: str):
        """添加token到缓存"""
        with self.token_cache_lock:
            # 添加新条目
            self.token_cache[token] = (vecdb_code, time.time())
            
            # 维护缓存大小
            while len(self.token_cache) > self.token_cache_size:
                self.token_cache.popitem(last=False)

    def _add_to_tenantid_cache(self, tenantid: str, vecdb_code: str):
        """添加token到缓存"""
        with self.tenantid_cache_lock:
            # 添加新条目
            self.tenantid_cache[tenantid] = (vecdb_code, time.time())
            
            # 维护缓存大小
            while len(self.tenantid_cache) > self.tenantid_cache_size:
                self.tenantid_cache.popitem(last=False)

    def get_vecdb_code(self, tenant_id: Optional[str]=None, yht_access_token: Optional[str]=None):
        """
        获取租户路由 vecdb_code 信息
        :param tenant_id: 租户ID
        :param yht_access_token: 认证令牌
        :return: (状态, 路由向量库编码或错误信息)
        """

        if not tenant_id and not yht_access_token:
            logger.error("tenant_id and yht_access_token cannot be empty at the same time")
            return False, "tenant_id and yht_access_token cannot be empty at the same time"

        if yht_access_token:
            vecdb_code = self._get_from_token_cache(yht_access_token)
            if vecdb_code:
                return True, vecdb_code
        elif tenant_id:
            vecdb_code = self._get_from_tenantid_cache(tenant_id)
            if vecdb_code:
                return True, vecdb_code
        
        headers = {"Content-Type": "application/json"}
        params = {
            "type": "logicData"
        }
        if yht_access_token:
            headers['yht_access_token'] = yht_access_token
        else:
            if iuap_request.has_jwt_package:
                headers, params = iuap_request.sign(self.mapping_url, params, headers)
            headers['X-tenantId'] = tenant_id
        last_error = None
        for i in range(1, 3):
            try: 
                resp = requests.request( method="GET", url=self.mapping_url, params=params, verify=False, headers=headers, timeout=self.timeout)
                resp.raise_for_status()
                resp_json = resp.json()
                logger.info("request retry time: %s, url: %s, params: %s, resp: %s", i, self.mapping_url, params, resp_json)
                res_data = resp_json.get("data") if resp_json is not None else None
                if not res_data or not isinstance(res_data, dict):
                    return False, f"get_vecdb_code failed, res_data error, resp:{str(resp_json)}"
                vecdb_code = res_data.get("logicData")
                if vecdb_code:
                    if yht_access_token:
                        self._add_to_token_cache(yht_access_token, vecdb_code)
                    else:
                        self._add_to_tenantid_cache(tenant_id, vecdb_code)
                return True, vecdb_code

            except Exception as e:
                last_error = str(e)
                logger.error("request retry time: %s, url: %s, error: %s", i, self.mapping_url, e)
        return False, f"get_vecdb_code failed, {last_error}"


if __name__ == '__main__':
    print(UserRouter().get_vecdb_code("", ""))