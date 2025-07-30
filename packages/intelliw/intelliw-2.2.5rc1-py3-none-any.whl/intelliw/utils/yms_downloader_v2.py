import base64
import os
import time
import traceback
import logging
import requests
import json
from urllib.parse import urlparse
from collections import defaultdict
from intelliw.utils.iuap_request import sign_authsdk
from intelliw.utils.iuap_request import get_module_config
from intelliw.utils.yms_encrypt_util import YmsEncryptUtil
from intelliw.utils.yms_config_util import parse_replace_config

from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()

logger_code = "intelliw.logger.level"



def set_env(k, v):
    if k not in os.environ:
        os.environ[k] = str(v)


class YmsSysEnv:
    YMS_ENV_CONFIG_PATH = './yms_env_config.yaml'
    YMS_ENV_CONFIG_NEW_PATH = './yms_env_config_new.yaml'
    YMS_ENV_RESP_CONFIG_FILE = './yms_env_resp_config.json'
    YMS_ENV_RESP_CONFIG_NEW_FILE = './yms_env_resp_config_new.json'
    YMS_ENV_LOCAL_YONBIP_CONFIG_DIR = '/app/config/global/'
    YMS_YONBIP_CONFIG_FN = 'yonbip_config.json'
    YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_DIR = '/app/config/middleware/'
    YMS_MIDDLEWARE_CONFIG_FN = 'yms_middleware.json'
    # YMS_ENV_LOCAL_MODULE_CONFIG_DIR = '/app/config/global/'
    YMS_MODULE_CONFIG_FN = 'module_config.json'

    DB_FIELDS = [
        "tenantList",
        "validationQuery",
        "defaultCatalog",
        "logAbandoned",
        "password",
        "maxIdle",
        "testWhileIdle",
        "ts",
        "removeAbandoned",
        "removeAbandonedTimeout",
        "defaultAutoCommit",
        "testOnConnect",
        "minIdle",
        "initialSize",
        "maxWait",
        "dbType",
        "url",
        "testOnBorrow",
        "minEvictableIdleTimeMillis",
        "timeBetweenEvictionRunsMillis",
        "testOnReturn",
        "driverClassName",
        "maxActive",
        "username",
        "validationQueryTimeout",
        "name",
        "lastUpdateTime",
   ]

    def __init__(self):
        self.init_config()
        self.yms_enc_tools = YmsEncryptUtil()
        self.special_env_map = {}
        self.mid_info_map = {}
        self.is_premises = False
        self.local_cache = None
        self.local_cache_new = None
        self.clients = {}

    def init_config(self):
        self.ACCESS_KEY = os.getenv('ACCESS_KEY') or os.getenv('access.key') or os.getenv('cf_clientAccessKey')
        self.ACCESS_SECRET = os.getenv('ACCESS_SECRET') or os.getenv('access.secret') or os.getenv('cf_clientAccessSecret')
        self.YMS_CONSOLE_ADDRESS = os.getenv('YMS_CONSOLE_ADDRESS') or os.getenv('disconf.conf_server_host')
        self.YMS_CONSOLE_ACTIVE = os.getenv('YMS_CONSOLE_ACTIVE') or os.getenv('mw_profiles_active')
        self.YMS_CONSOLE_APP_CODE = os.getenv('YMS_CONSOLE_APP_CODE', 'iuap-aip-console')
        self.YMS_ALGVEC_APP_CODE = os.getenv('YMS_ALGVEC_APP_CODE', 'iuap-aip-algvec')
        self.YMS_CONFIG_FILE_ADDRESS = f"{self.YMS_CONSOLE_ADDRESS}/api/v2/config/file"
        self.YMS_CONFIG_NEW_FILE_ADDRESS = f"{self.YMS_CONSOLE_ADDRESS}/api/v2/config/new/file"
        self.YMS_CONFIG_MODULE_URL = os.getenv('YMS_CONFIG_MODULE_URL', '/self/rest/api/moduleConfig')
        self.CONFIG_HOME = os.getenv('CONFIG_HOME')
        self.YMS_ENV_LOCAL_YONBIP_CONFIG_PATH = f'{self.YMS_ENV_LOCAL_YONBIP_CONFIG_DIR}{self.YMS_YONBIP_CONFIG_FN}' \
            if self.CONFIG_HOME is None \
            else f'{self.CONFIG_HOME}/{self.YMS_YONBIP_CONFIG_FN}'
        
        self.YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_PATH = f'{self.YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_DIR}{self.YMS_MIDDLEWARE_CONFIG_FN}' \
            if self.CONFIG_HOME is None \
            else f'{self.CONFIG_HOME}/{self.YMS_MIDDLEWARE_CONFIG_FN}'

    def _env_precess(self, env):
        for config_group in env['ymsConfigGroupVos']:
            for config in config_group['configItems']:
                code = config['code']
                value: str = config['value']
                if value.find('#{') >= 0:
                    self.special_env_map[code] = value
                    continue
                if value.startswith('YMS(') and value.endswith(')'):
                    # value = decode_yms_pw(value)
                    value = self.yms_enc_tools.decrypt(value)

                if code == logger_code:
                    value = os.environ.get(logger_code) or value

                if code == "isPremises":
                    self.is_premises = value == 'true'
                try:
                    set_env(code, value)
                    self.mid_info_map[code] = value
                except Exception as e:
                    logger.error("set yms environ error: {}, Key:{}, Value:{}".format(e, code, value))

                if self.local_cache is not None:
                    self.local_cache.write(f"{code}={value}\n")

    def _env_read_kv(self, env, raw_dict):
        for  key, value in env.items():
            if key == '_meta':
                continue
            if value is not None and value.startswith('YMS(') and value.endswith(')'):
                value = self.yms_enc_tools.decrypt(value)

            if key == logger_code:
                value = os.environ.get(logger_code) or value

            if key == "isPremises":
                self.is_premises = value == 'true'
            raw_dict[key] = value

    def _env_precess_new(self, raw_dict, env):
        for  key, value in env.items():
            if key == '_meta':
                continue
            if value is not None and value.startswith('YMS(') and value.endswith(')'):
                value = self.yms_enc_tools.decrypt(value)

            if key == logger_code:
                value = os.environ.get(logger_code) or value

            if key == "isPremises":
                self.is_premises = value == 'true'
            raw_dict[key] = value
        
        done_dict = parse_replace_config(raw_dict)
        if done_dict is None:
            return
        for key, value in done_dict.items():
            try:
                set_env(key, value)
            except Exception as e:
                logger.error("set yms environ error: {}, Key:{}, Value:{}".format(e, key, value))

            if self.local_cache_new is not None:
                self.local_cache_new.write(f"{key}={value}\n")

    def _generate_value(self, result: str):
        if result.find('#{') >= 0:
            for k, v in self.mid_info_map.items():
                variable = '#{' + k + '#}'
                if result.find(variable) >= 0:
                    result = result.replace(variable, v)
        return result

    def init_children_info(self, children):
        for c in children:
            if c.get('ymsConfigGroupVos'):
                self._env_precess(c)

            if c.get('children'):
                self.init_children_info(c['children'])

    def _get_local_cache(self):
        if self.local_cache is None and not os.path.exists(self.YMS_ENV_CONFIG_PATH):
            self.local_cache = open(self.YMS_ENV_CONFIG_PATH, "w")
        return self.local_cache

    def _get_local_cache_new(self):
        if self.local_cache_new is None and not os.path.exists(self.YMS_ENV_CONFIG_NEW_PATH):
            self.local_cache_new = open(self.YMS_ENV_CONFIG_NEW_PATH, "w")
        return self.local_cache_new

    def close_file(self):
        if self.local_cache is not None and not self.local_cache.closed:
            self.local_cache.close()
            self.local_cache = None

    def close_file_new(self):
        if self.local_cache_new is not None and not self.local_cache_new.closed:
            self.local_cache_new.close()
            self.local_cache_new = None

    def init_envs(self, env):
        self._get_local_cache()

        if not env:
            logger.warning('YMS配置为空')
            return

        self._env_precess(env['data'])

        if env['data'].get('children'):
            self.init_children_info(env['data']['children'])

        for code, value in self.special_env_map.items():
            value = self._generate_value(value)

            try:
                set_env(code, value)
                self.mid_info_map[code] = value
            except Exception as e:
                logger.error("set yms environ error: {}, Key:{}, Value:{}".format(e, code, value))

            if self.local_cache is not None:
                self.local_cache.write(f"{code}={value}\n")


    def flat_clients(self):
        if not self.clients:
            logger.warning('YMS新的 clients配置为空')
            self.clients = {}
            return
        results = defaultdict(set)
        for key in self.clients:
            for client_key in self.clients[key]:
                if isinstance(self.clients[key][client_key], list):
                    for client_name in self.clients[key][client_key]:
                        results[client_key].add(client_name)
                else:
                    logger.warning(f"YMS新的 clients配置格式错误 client_key: {client_key}, type:{self.clients[key][client_key]}")
        
        return results


    def init_envs_new(self, env):

        if not env:
            logger.warning('YMS新配置为空')
            return

        raw_dict = {}
        for config_key in env:
            if config_key.startswith("config."):
                self._env_read_kv(env[config_key], raw_dict)
            elif config_key.startswith("client."):
                self.clients[config_key] = env[config_key]
            else:
                pass
                # (f'key: {config_key}, value: {env[config_key]}')
        
        replaced_dict = parse_replace_config(raw_dict)

        if replaced_dict is None:
            return
        for key, value in replaced_dict.items():
            try:
                set_env(key, value)
            except Exception as e:
                logger.error("set yms environ error: {}, Key:{}, Value:{}".format(e, key, value))

            if self.local_cache_new is not None:
                self.local_cache_new.write(f"{key}={value}\n")

    def init_connection_pools_new(self, middleware, connection_pool_codes):
        if not middleware:
            return
        connection_pools = middleware.get('connectionPools')

        datasources = middleware.get('datasources')
        for connection_code in connection_pool_codes:
            datasource = datasources.get(connection_code)
            if not datasource:
                logger.warning(f'connection_code: {connection_code} datasource not found')
                continue
            pools = datasource.get('pools')
            routeEnable = datasource.get('routeEnable')
            defaultSchema = datasource.get('defaultSchema')
            defaultDs = datasource.get('defaultDs')
            translateEnable = datasource.get('translateEnable')
            translateStrict = datasource.get('translateStrict')

            # 处理连接池 begin ===========================
            if pools is None:
                logger.warning(f'connection_code: {connection_code} pools not found')
                continue

            for pool_name in pools:
                connection_info = connection_pools.get(pool_name)
                if not connection_info:
                    logger.warning(f'connection_code: {connection_code}, pool_name: {pool_name} connection_info not found')
                    continue
                # 生成连接信息 
                # 如果 为defaultDs, 则使用connection_code， 否则使用 {connection_code}_{pool_name}
                pre_connection_code = connection_code if pool_name == defaultDs else f'{connection_code}_{pool_name}'
                schema_key = f'{pre_connection_code}_DB_DEFAULT_SCHEMA'
                set_env(schema_key, defaultSchema)
                if self.local_cache_new is not None:
                    self.local_cache_new.write(f"{schema_key}={defaultSchema}\n")
                for db_field in self.DB_FIELDS:
                    key = f'{pre_connection_code}_DB_{db_field.upper()}'
                    value = connection_info.get(db_field)
                    if db_field == 'password':
                        value = self.yms_enc_tools.decrypt( connection_info.get('password'))
                    elif db_field == 'url' and value is not None:
                        if value.startswith('jdbc:'):
                            parsed_url = urlparse(value[5:])
                            host, port = parsed_url.netloc.split(':')
                            set_env(f'{pre_connection_code}_DB_HOST', host)
                            set_env(f'{pre_connection_code}_DB_PORT', port)
                            if self.local_cache_new is not None:
                                self.local_cache_new.write(f"{pre_connection_code}_DB_HOST={host}\n")
                                self.local_cache_new.write(f"{pre_connection_code}_DB_PORT={port}\n")
                    set_env(key, value)
                    if self.local_cache_new is not None:
                        self.local_cache_new.write(f"{key}={value}\n")
            # 处理连接池 begin ===========================

    def init_redis_new(self, middleware, redis_codes):
        if not middleware:
            return
        redis_pools = middleware.get('redis.pools')
        redis_regions = middleware.get('redis.regions')

        for redis_code in redis_codes:
            redis_region = redis_regions[redis_code]
            pool_name = redis_region.get('pool')
            mode = redis_region.get('mode')
            tenantSensitive = redis_region.get('tenantSensitive')
            namespace = redis_region.get('namespace')
            lastUpdateTime = redis_region.get('lastUpdateTime')
            database = redis_region.get('database')

            pool_info = redis_pools.get(pool_name)
            if pool_info:
                if pool_info['type'] == 'single':
                    set_env(f'{redis_code}_REDIS_URL', f"{pool_info['host']}:{pool_info['port']}")
                    if self.local_cache_new is not None:
                        self.local_cache_new.write(
                            f"{redis_code}_REDIS_URL={pool_info['host']}:{pool_info['port']}\n")
                else:
                    set_env(f'{redis_code}_REDIS_URL', pool_info['nodes'])
                    if self.local_cache_new is not None:
                        self.local_cache_new.write(f"{redis_code}_REDIS_URL={pool_info['nodes']}\n")

                value = self.yms_enc_tools.decrypt(pool_info.get('password', ''))
                # sentinel_value = decode_yms_pw(pool_info.get('sentinelPassword', ''))
                sentinel_value = self.yms_enc_tools.decrypt(pool_info.get('sentinelPassword', ''))
                set_env(f'{redis_code}_REDIS_TYPE', f"{pool_info.get('type', '')}")
                set_env(f'{redis_code}_REDIS_DATABASE', f'{database}')
                set_env(f'{redis_code}_REDIS_MODE', f'{mode}')
                set_env(f'{redis_code}_REDIS_PASSWORD', value)
                set_env(f'{redis_code}_REDIS_SENTINEL_PASSWORD', sentinel_value)
                set_env(f'{redis_code}_REDIS_MASTER_NAME', f"{pool_info.get('masterName', '')}")
                set_env(f'{redis_code}_REDIS_POOL_SIZE', f"{pool_info.get('maxIdle', '')}")

                if self.local_cache_new is not None:
                    self.local_cache_new.write(f"{redis_code}_REDIS_TYPE={pool_info.get('type', '')}\n")
                    self.local_cache_new.write(f"{redis_code}_REDIS_DATABASE={database}\n")
                    self.local_cache_new.write(f"{redis_code}_REDIS_MODE={mode}\n")
                    self.local_cache_new.write(f"{redis_code}_REDIS_PASSWORD={value}\n")
                    self.local_cache_new.write(f"{redis_code}_REDIS_SENTINEL_PASSWORD={sentinel_value}\n")
                    self.local_cache_new.write(
                        f"{redis_code}_REDIS_MASTER_NAME={pool_info.get('masterName', '')}\n")
                    self.local_cache_new.write(f"{redis_code}_REDIS_POOL_SIZE={pool_info.get('maxIdle', '')}\n")


    def init_redis(self, redis):
        if not redis:
            return

        for c in redis['clients']:
            pool_name = c['pool']
            database = c.get('database')
            redis_code = c['name']

            pool_info = None
            for p in redis['pools']:
                if p['name'] == pool_name:
                    pool_info = p

            if pool_info:
                if pool_info['type'] == 'single':
                    set_env(f'{redis_code}_REDIS_URL', f"{pool_info['host']}:{pool_info['port']}")
                    if self.local_cache is not None:
                        self.local_cache.write(
                            f"{redis_code}_REDIS_URL={pool_info['host']}:{pool_info['port']}\n")
                else:
                    set_env(f'{redis_code}_REDIS_URL', pool_info['nodes'])
                    if self.local_cache is not None:
                        self.local_cache.write(f"{redis_code}_REDIS_URL={pool_info['nodes']}\n")

                value = self.yms_enc_tools.decrypt(pool_info.get('password', ''))
                # sentinel_value = decode_yms_pw(pool_info.get('sentinelPassword', ''))
                sentinel_value = self.yms_enc_tools.decrypt(pool_info.get('sentinelPassword', ''))
                set_env(f'{redis_code}_REDIS_TYPE', f"{pool_info.get('type', '')}")
                set_env(f'{redis_code}_REDIS_DATABASE', f'{database}')
                set_env(f'{redis_code}_REDIS_PASSWORD', value)
                set_env(f'{redis_code}_REDIS_SENTINEL_PASSWORD', sentinel_value)
                set_env(f'{redis_code}_REDIS_MASTER_NAME', f"{pool_info.get('masterName', '')}")
                set_env(f'{redis_code}_REDIS_POOL_SIZE', f"{pool_info.get('max-idle', '')}")

                if self.local_cache is not None:
                    self.local_cache.write(f"{redis_code}_REDIS_TYPE={pool_info.get('type', '')}\n")
                    self.local_cache.write(f"{redis_code}_REDIS_DATABASE={database}\n")
                    self.local_cache.write(f"{redis_code}_REDIS_PASSWORD={value}\n")
                    self.local_cache.write(f"{redis_code}_REDIS_SENTINEL_PASSWORD={sentinel_value}\n")
                    self.local_cache.write(
                        f"{redis_code}_REDIS_MASTER_NAME={pool_info.get('masterName', '')}\n")
                    self.local_cache.write(f"{redis_code}_REDIS_POOL_SIZE={pool_info.get('max-idle', '')}\n")

    def __del__(self):
        self.close_file()
        self.close_file_new()


yms_sys_env = YmsSysEnv()


def request_yms(url, method="GET", params=None, data=None):
    for i in range(1, 5):
        try:
            token = sign_authsdk(url, params, yms_sys_env.ACCESS_KEY, yms_sys_env.ACCESS_SECRET)
            headers = {
                'Content-Type': 'application/json',
                'YYCtoken': token,
                'dcAddr': base64.b64encode(bytes(url, 'utf-8')).decode()
            }
            resp = requests.request(
                method=method, url=url, params=params,
                json=data, verify=False, headers=headers, timeout=5.0
            )
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if i == 4:
                raise e
            time.sleep(i * 2)
            try:
                body = e.response.text if hasattr(e.response, "text") else e.response
            except:
                body = ""
            logger.error(
                "request retry time: %s, url: %s, body: %s, error: %s",
                i, url, body, e)

def download_ca_file():
    from intelliw.utils.yaml_downloader import download
    workdir = os.getenv('WORKDIR', '/root')
    ca_path = os.path.join(workdir, 'cert')
    os.makedirs(ca_path, exist_ok=True)
    ca_url = os.getenv('CA_FILE_URL')
    if os.getenv('useGpaas') == 'true':
        ca_url = f"{os.environ['domain.url']}{ca_url}"
    if ca_url is None or ca_url == "":
        logger.warning("证书下载地址为空")
        return
    try:
        download(ca_url, ca_path, True)
        logger.info(f"下载证书成功, 证书下载地址: {ca_url}")
    except Exception as e:
        logger.error(f"下载证书失败: {e}, 证书下载地址: {ca_url}")

def read_json_to_dict(file_path, encoding='utf-8'):
    """
    读取 JSON 文件内容，返回以文件名为键的字典
    :param file_path: JSON 文件路径
    :param encoding: 文件编码格式（默认utf-8）
    :return: 格式如 { "filename.json": { ...json content } }
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            data = json.load(f)
        return {os.path.basename(file_path): data}
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 不存在")
        return {}
    except json.JSONDecodeError:
        print(f"错误：文件 {file_path} 不是有效的JSON格式")
        return {}

def run():
    try:
        yms_sys_env.init_config()
        succeed_flag = run_local()
        if succeed_flag:
            download_ca_file()
            return
        if not yms_sys_env.YMS_CONSOLE_ADDRESS:
            logger.warning("未配置YMS_CONSOLE_ADDRESS，不进行YMS配置拉取")
            return
        
        succeed_flag = run_new()
        if succeed_flag:
            download_ca_file()
            return
        
        succeed_flag = run_old()
        if succeed_flag:
            download_ca_file()
            return
        
        logger.error("YMS配置拉取失败，请检查YMS_CONSOLE_ADDRESS是否正确")

    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error("yms配置加载失败: %s, 详细信息: %s", e, err_msg)
    finally:
        try:
            yms_sys_env.close_file()
            yms_sys_env.close_file_new()
        except:
            pass

def run_local():
    try:
        resp = {}
        # 1. 本地获取配置文件
        if not os.path.exists(yms_sys_env.YMS_ENV_LOCAL_YONBIP_CONFIG_PATH):
            logger.warning(f"配置文件:{yms_sys_env.YMS_ENV_LOCAL_YONBIP_CONFIG_PATH} 不存在，请检查配置文件路径是否正确(或者忽略)")
            return False
        resp.update(read_json_to_dict(yms_sys_env.YMS_ENV_LOCAL_YONBIP_CONFIG_PATH))

        if not os.path.exists(yms_sys_env.YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_PATH):
            logger.warning(f"配置文件:{yms_sys_env.YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_PATH} 不存在，请检查配置文件路径是否正确(或者忽略)")
            return False
        resp.update(read_json_to_dict(yms_sys_env.YMS_ENV_LOCAL_YMS_MIDDLEWARE_CONFIG_PATH))

        # 更新环境变量
        yms_sys_env._get_local_cache_new()
        yms_sys_env.init_envs_new(resp.get('yonbip_config.json'))
        # 通过工作坊接口，获取 module_config.json 
        module_config_json_url = f'{os.environ.get("domain.url")}/{yms_sys_env.YMS_CONSOLE_APP_CODE}{yms_sys_env.YMS_CONFIG_MODULE_URL}'
        
        module_config_resp =  get_module_config(module_config_json_url)
        if module_config_resp is not None and 'SUCCESS' == module_config_resp.get('msg'):
            resp.update(module_config_resp.get('data'))
        else:
            logger.warning("通过工作坊接口，获取 module_config.json 失败")
            return False

        yms_sys_env.init_envs_new(resp.get('module_config.json'))
        filtered_clients = yms_sys_env.flat_clients()
        yms_sys_env.init_redis_new(resp.get('yms_middleware.json'), filtered_clients.get('redis'))
        yms_sys_env.init_connection_pools_new(resp.get('yms_middleware.json'), {f'{yms_sys_env.YMS_CONSOLE_APP_CODE}_datasource'})
        yms_sys_env.init_connection_pools_new(resp.get('yms_middleware.json'), {f'{yms_sys_env.YMS_ALGVEC_APP_CODE}_dataSource'})
        logger.info("执行yms配置本地加载成功")
        # 写入文件
        if "DEBUG" == os.environ.get(logger_code):
            with open(yms_sys_env.YMS_ENV_RESP_CONFIG_NEW_FILE, 'w') as f:
                f.write(json.dumps(resp, indent=4))
        return True


    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error("yms配置本地加载失败: %s, 详细信息: %s", e, err_msg)
        return False
    finally:
        try:
            yms_sys_env.close_file()
            yms_sys_env.close_file_new()
        except:
            pass

def run_new():
    try:
        params = {
                    'apps': [f'{yms_sys_env.YMS_CONSOLE_APP_CODE}',"iuap-aip-vpa"],
                    'env': yms_sys_env.YMS_CONSOLE_ACTIVE,
                    "version": "2.0.0", 
                    "keyStore": "true",
                    "c_isolate":"default"
                }
        resp = request_yms(yms_sys_env.YMS_CONFIG_NEW_FILE_ADDRESS,
                           params= params
                           )
        if resp.get('success') == 'false':
            logger.error(f"{resp['error_code']}:{resp['error_message']}")
            return False
        if "DEBUG" == os.environ.get(logger_code):
            with open(yms_sys_env.YMS_ENV_RESP_CONFIG_NEW_FILE, 'w') as f:
                f.write(json.dumps(resp, indent=4))
        
        yms_sys_env._get_local_cache_new()
        yms_sys_env.init_envs_new(resp.get('yonbip_config.json'))
        yms_sys_env.init_envs_new(resp.get('module_config.json'))
        filtered_clients = yms_sys_env.flat_clients()
        yms_sys_env.init_redis_new(resp.get('yms_middleware.json'), filtered_clients.get('redis'))
        yms_sys_env.init_connection_pools_new(resp.get('yms_middleware.json'), {f'{yms_sys_env.YMS_CONSOLE_APP_CODE}_datasource'})
        yms_sys_env.init_connection_pools_new(resp.get('yms_middleware.json'), {f'{yms_sys_env.YMS_ALGVEC_APP_CODE}_dataSource'})
        logger.info("执行新的YMS配置拉取成功")
        return True


    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error("yms配置下载失败: %s, 详细信息: %s", e, err_msg)
        return False
    finally:
        try:
            yms_sys_env.close_file()
            yms_sys_env.close_file_new()
        except:
            pass

def run_old():
    try:
        resp = request_yms(yms_sys_env.YMS_CONFIG_FILE_ADDRESS,
                           params={
                               'app': yms_sys_env.YMS_CONSOLE_APP_CODE,
                               'env': yms_sys_env.YMS_CONSOLE_ACTIVE,
                               "version": 1, 
                               "datacenter": "",
                               "keyStore": "",
                               }
                           )
        if resp.get('success') == 'false':
            logger.error(f"{resp['error_code']}:{resp['error_message']}")
            return False
        if "DEBUG" == os.environ.get(logger_code):
            with open(yms_sys_env.YMS_ENV_RESP_CONFIG_FILE, 'w') as f:
                f.write(json.dumps(resp, indent=4))
        yms_sys_env.init_envs(resp.get('environment'))
        yms_sys_env.init_redis(resp.get('redis'))
        logger.info("执行YMS配置拉取成功")
        return True

    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error("yms配置下载失败: %s, 详细信息: %s", e, err_msg)
        return False
    finally:
        try:
            yms_sys_env.close_file()
            yms_sys_env.close_file_new()
        except:
            pass
