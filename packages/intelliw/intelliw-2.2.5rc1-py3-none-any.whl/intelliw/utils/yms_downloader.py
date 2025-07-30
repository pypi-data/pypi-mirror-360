import base64
import os
import time
import traceback
import logging
import requests
from intelliw.utils.iuap_request import sign_authsdk

logger = logging.getLogger('yms_download')
logger.setLevel("INFO")
logger_code = "intelliw.logger.level"


def set_env(k, v):
    if k not in os.environ:
        os.environ[k] = str(v)


class YmsSysEnv:
    YMS_ENV_CONFIG_PATH = './yms_env_config.yaml'

    def __init__(self):
        self.init_config()
        self.special_env_map = {}
        self.mid_info_map = {}
        self.is_premises = False
        self.local_cache = None

    def init_config(self):
        self.ACCESS_KEY = os.getenv('ACCESS_KEY') or os.getenv('access.key')
        self.ACCESS_SECRET = os.getenv('ACCESS_SECRET') or os.getenv('access.secret')
        self.YMS_CONSOLE_ADDRESS = os.getenv('YMS_CONSOLE_ADDRESS') or os.getenv('disconf.conf_server_host')
        self.YMS_CONSOLE_ACTIVE = os.getenv('YMS_CONSOLE_ACTIVE') or os.getenv('mw_profiles_active')
        self.YMS_CONSOLE_APP_CODE = os.getenv('YMS_CONSOLE_APP_CODE', 'iuap-aip-console')
        self.YMS_CONFIG_FIlE_ADDRESS = f"{self.YMS_CONSOLE_ADDRESS}/api/v2/config/file"
        self.YMS_PW_DECODE_ADDRESS = f"{self.YMS_CONSOLE_ADDRESS}/api/v1/ymsConfig/enc/decValue"

    def _env_precess(self, env):
        for config_group in env['ymsConfigGroupVos']:
            for config in config_group['configItems']:
                code = config['code']
                value: str = config['value']
                if value.find('#{') >= 0:
                    self.special_env_map[code] = value
                    continue
                if value.startswith('YMS(') and value.endswith(')'):
                    value = decode_yms_pw(value)

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

    def close_file(self):
        if self.local_cache is not None and not self.local_cache.closed:
            self.local_cache.close()
            self.local_cache = None

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

                value = decode_yms_pw(pool_info.get('password', ''))
                sentinel_value = decode_yms_pw(pool_info.get('sentinelPassword', ''))
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


def decode_yms_pw(pw):
    resp = request_yms(yms_sys_env.YMS_PW_DECODE_ADDRESS,
                       method='POST',
                       data=[pw, ])

    if resp['success'] != 'true':
        logger.error(f"{resp['error_code']}:{resp['error_message']}")
        return ""

    data = resp.get('data', {})
    return data.get(pw, "")


def download_ca_file():
    from intelliw.utils.yaml_downloader import download
    workdir = os.getenv('WORKDIR', '/root')
    ca_path = os.path.join(workdir, 'cert')
    os.makedirs(ca_path, exist_ok=True)
    ca_url = os.getenv('CA_FILE_URL')
    if os.getenv('useGpaas') == 'true':
        ca_url = f"{os.environ['domain.url']}{ca_url}"
    try:
        download(ca_url, ca_path, True)
        logger.info("下载证书成功")
    except Exception as e:
        logger.error(f"下载证书失败: {e}, 证书下载地址: {ca_url}")


def run():
    try:
        yms_sys_env.init_config()
        if not yms_sys_env.YMS_CONSOLE_ADDRESS:
            logger.warning("未配置YMS_CONSOLE_ADDRESS，不进行YMS配置拉取")
            return

        resp = request_yms(yms_sys_env.YMS_CONFIG_FIlE_ADDRESS,
                           params={
                               'app': yms_sys_env.YMS_CONSOLE_APP_CODE,
                               'env': yms_sys_env.YMS_CONSOLE_ACTIVE}
                           )
        if resp.get('success') == 'false':
            logger.error(f"{resp['error_code']}:{resp['error_message']}")
            return

        yms_sys_env.init_envs(resp.get('environment'))
        yms_sys_env.init_redis(resp.get('redis'))
        logger.info("执行YMS配置拉取成功")

        download_ca_file()

    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error("yms配置下载失败: %s, 详细信息: %s", e, err_msg)
    finally:
        try:
            yms_sys_env.close_file()
        except:
            pass
