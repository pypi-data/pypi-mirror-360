"""
iUAP HTTP auth protocol implementation
"""
import json
import os
import time
import math
import json as _py_json
import hashlib
import base64
import logging
import uuid
import sys
import requests
import requests.exceptions
import requests.packages

from intelliw.config import config
from intelliw.utils.context import header_ctx
from intelliw.utils.trace_log import TraceLog

requests.packages.urllib3.disable_warnings()
logger = logging.getLogger("request")

try:
    import jwt

    has_jwt_package = True
except ImportError:
    logger.warning(
        "\033[33mIf want use authsdk, you need: pip install pyjwt\033[0m")
    has_jwt_package = False

DEFAULT_TIMEOUT: float = 10.0


def replace_url(url):
    internal_aliyun = "intelliw-console.oss-cn-beijing-internal.aliyuncs.com"
    yy_oss = "intelliw-console.oss-cn-beijing.aliyuncs.com"
    return url.replace(internal_aliyun, yy_oss)


class AuthType:
    """
    AuthType
    """
    No = 0
    AuthSDK = 1
    YHT = 2

    AuthCache = {}


class Response:
    """
    Response
    """

    def __init__(self, resp: requests.Response, error: Exception = None):
        self.raw = resp
        self.error = error
        self.text = self.raw.text
        self.status = self.status_code = self.raw.status_code
        self.content = self.body = self.raw.content
        self.json = self._try_json(self.raw.json)

    def raise_for_status(self):
        """
        raise :class:`IuapRequestException <IuapRequestException>` if status is not 200
        """
        if self.status != 200:
            msg = f'http request error, status: [{self.status}], body: [{self.body}]'
            if self.error is not None:
                raise IuapRequestException(
                    msg + str(self.error)) from self.error
            raise IuapRequestException(msg)

    @staticmethod
    def _try_json(f):
        try:
            return f()
        except Exception:
            return None

    def __str__(self):
        return f'status: {self.status}, body: {self.body}, error: {self.error}'


class IuapRequestException(Exception):
    """
    IuapRequestException
    """
    pass

def async_report_trace_log(tenant_id: str, trace_log: TraceLog):
    executor = trace_log._get_executor()
    executor.submit(report_trace_log, tenant_id, trace_log)

def report_trace_log(tenant_id: str, trace_log: TraceLog):
    """
    :param trace_log
    """

    try:
        # 加签
        headers = {"Content-Type": "application/json"}
        headers['X-tenantId'] = tenant_id
        auth_type = AuthType.AuthSDK
        url = f"{os.environ['domain.url']}/iuap-aip-console/self/rest/api/traceLogs"

        if trace_log.endTime is None:
            trace_log.endTime = int(time.time() * 1000)

        if trace_log.timeCost is None:
            trace_log.calculate_time_cost()

        data = trace_log.to_dict()


        if has_jwt_package:
            headers, params = sign(url, {}, headers, auth_type)
        logger.info(f'trace log data:{data}')
        resp = __do_request(method="POST", url=url, headers=headers, params=params,
                            json=data, auth_type=auth_type, retry=2)
        logger.info("trace log resp: %s", resp)
    except Exception as e:
        logger.error(f"report trace log error: {str(e)}")

def get_module_config(url):
    """
    :param url
    """
    # 加签
    headers = {
        "Content-Type": "application/json",
        "X-tenantId": '0'
        }
    auth_type = AuthType.AuthSDK

    if has_jwt_package:
        headers, params = sign(url, {}, headers, auth_type)

    resp = __do_request(method="GET", url=url, headers=headers, params=params, auth_type=auth_type)
    resp.raise_for_status()
    response_body = resp.json
    return response_body

def download(url, output_path=None, method="GET", params=None, data=None, json=None, headers=None,
             auth_type=AuthType.No, ak=None, ase=None):
    """
    download file
    """
    # 加签
    if headers is None:
        headers = {}

    if ak is not None and ase is not None:
        auth_type = AuthType.AuthSDK

    if has_jwt_package and auth_type != AuthType.No:
        headers, params = sign(url, params, headers, auth_type, ak=ak, ase=ase)

    resp = __do_request(method=method, url=url, headers=headers,
                        data=data, params=params, json=json, auth_type=auth_type)
    if output_path is None:
        return resp
    else:
        resp.raise_for_status()
        if '<Error>' in resp.text:
            raise IuapRequestException(resp.text)
        mode = "w" if isinstance(resp.body, str) else "wb"
        with open(output_path, mode) as code:
            code.write(resp.body)


def stream_download(url, output_path, method="get", params=None, body=None, json=None, headers=None,
                    auth_type=AuthType.No, ak=None, ase=None):
    """
    stream_download 流式下载文件
    """
    chunk_size = 1024

    def report_hook(plan, speed):
        logger.info("dataset downloading: {:.3f}% {:.3f}MB/s".format(
            plan, speed / (chunk_size ** 2)))

    # 加签
    if headers is None:
        headers = {}

    if ak is not None and ase is not None:
        auth_type = AuthType.AuthSDK

    if has_jwt_package and auth_type != AuthType.No:
        headers, params = sign(url, params, headers, auth_type, ak=ak, ase=ase)

    # 请求下载地址，以流式的。打开要下载的文件位置。
    with requests.request(method=method, url=url, stream=True, verify=False, data=body, params=params, json=json,
                          timeout=DEFAULT_TIMEOUT) as r, open(output_path, 'wb') as file:
        total_size = int(r.headers['content-length'])
        start_time = time.time()  # 请求开始的时间
        download_content_size = 0  # 下载的字节大小
        temp_size = 0  # 上秒的下载大小
        plan = 0  # 进度下载完成的百分比

        # 开始下载每次请求chunk_size字节
        for idx, content in enumerate(r.iter_content(chunk_size=chunk_size)):
            file.write(content)
            download_content_size += len(content)
            plan = (download_content_size / total_size) * 100
            if time.time() - start_time > 1:
                start_time = time.time()
                speed = download_content_size - temp_size
                if idx % 5 == 0:
                    report_hook(plan, speed)
                temp_size = download_content_size


def get(url: str, headers: dict = None, params: dict = None, timeout: float = DEFAULT_TIMEOUT,
        auth_type=AuthType.AuthSDK, ak=None, ase=None, retry=True) -> Response:
    """
    get request

    :param auth_type: 是否需要鉴权, 0 不需要, 1 authsdk, 2 yht
    :param timeout: request timeout
    :param url: request url
    :param headers: request headers
    :param params: request url params
    :param ak: 用户自定义access key
    :param ase: 用户自定义access secret
    :param retry: 重试, 0或false为不重试，可以设置重试次数
    :return: Response
    """
    return sign_and_request(url, 'GET', headers, params, timeout=timeout, auth_type=auth_type, ak=ak, ase=ase,
                            retry=retry)


def post_json(url: str, headers: dict = None, params: dict = None, json: object = None,
              timeout: float = DEFAULT_TIMEOUT, auth_type=AuthType.AuthSDK, ak=None, ase=None,
              retry: [bool, int] = True) -> Response:
    """
    post request, send data as json


    :param auth_type: 是否需要鉴权, 0 不需要, 1 authsdk, 2 yht
    :param timeout: request timeout
    :param url: request url
    :param headers: request headers
    :param params: request url parameters
    :param json: request body. if data is not `str`, it will be serialized as json.
    :param ak: 用户自定义access key
    :param ase: 用户自定义access secret
    :param retry: 重试, 0或false为不重试，可以设置重试次数
    :return: Response
    """

    if headers is None:
        headers = {}
    headers['Content-type'] = 'application/json; charset=UTF-8'
    return sign_and_request(url, 'POST', headers, params, json=json,
                            timeout=timeout, auth_type=auth_type, ak=ak, ase=ase, retry=retry)


def post(url: str, headers: dict = None, params: dict = None, data: object = None, json=None,
         timeout: float = DEFAULT_TIMEOUT, auth_type=AuthType.AuthSDK, ak=None, ase=None,
         retry: [bool, int] = True) -> Response:
    """
    post request, send data


    :param auth_type: 是否需要鉴权 0 不需要 1 authsdk 2 yht
    :param timeout: request timeout
    :param url: request url
    :param headers: request headers
    :param params: request url parameters
    :param data: request body. if data is not `str`, it will be serialized as json.
    :param ak: 用户自定义access key
    :param ase: 用户自定义access secret
    :param retry: 重试, 0或false为不重试，可以设置重试次数
    :return: Response
    """

    if headers is None:
        headers = {}

    if json is not None:
        headers['Content-type'] = 'application/json; charset=UTF-8'

    return sign_and_request(url, 'POST', headers, params, data=data, json=json,
                            timeout=timeout, auth_type=auth_type, ak=ak, ase=ase, retry=retry)


def put_file(url: str, headers: dict = None, params: dict = None, data: object = None,
             timeout: float = DEFAULT_TIMEOUT, auth_type=AuthType.No, ak=None, ase=None,
             retry: [bool, int] = True) -> Response:
    """
    put file
    """
    if headers is None:
        headers = {'Content-Type': 'application/octet-stream'}
    return sign_and_request(url, 'PUT', headers, params, data=data,
                            timeout=timeout, auth_type=auth_type, ak=ak, ase=ase, retry=retry)


def sign_and_request(url: str,
                     method: str = 'GET',
                     headers: dict = None,
                     params: dict = None,
                     data: bytes = None,
                     json: dict = None,
                     timeout: float = DEFAULT_TIMEOUT,
                     auth_type=AuthType.AuthSDK,
                     ak=None, ase=None, retry=True) -> Response:
    """
    sign and do request

    :param url: request url, without query
    :param method: Http request method, GET, POST...
    :param headers: request headers
    :param params: parameters will be sent as url parameters. Also used to generate signature if sign_params is None.
    :param data: request body
    :param json: Request body in Json format
    :param timeout: url access timeout
    :param auth_type: 是否需要鉴权 0 不需要 1 authsdk 2 yht
    :param ak: 用户自定义access key
    :param ase: 用户自定义access secret
    :param retry: 重试, 0或false为不重试，可以设置重试次数
    :return: response body
    """
    if headers is None:
        headers = {}

    # auth
    sign(url, params, headers, auth_type, ak=ak, ase=ase)
    return __do_request(url, method, headers, params, data, json, timeout=timeout, auth_type=auth_type, retry=retry)


def sign(url: str, params: dict, headers: dict, auth_type=AuthType.AuthSDK, ak=None, ase=None, refresh=False):
    if ak is not None and ase is not None:
        auth_type = AuthType.AuthSDK

    if has_jwt_package and auth_type == AuthType.AuthSDK:
        if params is None:
            params = {}
        params['AuthSdkServer'] = "true"
        headers['YYCtoken'] = sign_authsdk(url, params, ak=ak, ase=ase)
    elif auth_type == AuthType.YHT:
        yht_access_token = headers.get('yht_access_token')
        if yht_access_token is None or yht_access_token == '':
            yht_access_token = sign_yht(headers, refresh)
        headers['cookie'] = f'yht_access_token={yht_access_token}'
    return headers, params


def sign_authsdk(url: str, params: dict, ak=None, ase=None) -> str:
    """
    generate iuap signature

    :param url: request url, without parameters
    :param params:  request parameters, x-www-form-urlencoded request's body parameters should also be included.
    :param ak: ACCESS KEY
    :param ase: ACCESS SECRET
    :return: iuap signature
    """
    if not ak:
        ak = os.environ.get('ACCESS_KEY') or config.ACCESS_KEY
    if not ase:
        ase = os.environ.get('ACCESS_SECRET') or config.ACCESS_SECRET

    issue_at = __issue_at()
    sign_key = __build_sign_key(ak, ase, issue_at, url)
    jwt_payload = {
        "sub": url,
        "iss": ak,
        "iat": issue_at
    }
    if params is not None and len(params) > 0:
        sorted_params = sorted(params.items())
        for item in sorted_params:
            if item[1] is None:
                val = ''
            elif len(str(item[1])) >= 1024:
                val = str(__java_string_hashcode(str(item[1])))
            else:
                val = str(item[1])
            jwt_payload[item[0]] = val

    jwt_token = jwt.encode(jwt_payload, key=sign_key, algorithm='HS256')
    return jwt_token if isinstance(jwt_token, str) else jwt_token.decode('utf-8')


def sign_yht(headers=None, refresh=False):
    # 本地获取会被运维拦住，只能手动复制一个
    if not config.is_server_mode():
        if config.TEMPORARY_USER_COOKIE:
            return config.TEMPORARY_USER_COOKIE
        else:
            raise SignError("为配置用户Token",
                            "本地调试数据集，请先在Cookie中获取用户Token, 并配置到环境变量 TEMPORARY_USER_COOKIE ")

    # 在线模式
    xTenantId = None
    TENANT_ID = os.environ.get('TENANT_ID') or config.TENANT_ID
    if headers is not None:
        xTenantId = headers.get('X-tenantId')
    
    if xTenantId is None:
        logger.debug(f"X-tenantId not found, use default tenantId:{TENANT_ID}")
        xTenantId =  TENANT_ID
    cache_key = f'yhtToken_{xTenantId}'
    token = AuthType.AuthCache.get(cache_key, {"expire": 0})
    expire = token.get("expire")

    if not refresh and (expire != 0 and time.time() < expire):
        logger.warning("Get Cache Key: %s, Cache Token: %s", cache_key, token)
        return token['token']
    else:
        # 请求 AI工作坊获取
        resp = get(config.GENERATOR_YHT_URL, headers)
        resp.raise_for_status()
        try:
            token = resp.json['data']['yhtToken']
            logger.warning("Get X-tenantId: %s, New Token: %s", xTenantId, token)
            AuthType.AuthCache[cache_key] = {
                'expire': time.time() + 60, "token": token}
        except Exception as e:
            msg = f"Get YHTToken Failed: {e}, resp body: [{resp.body}], resp json: {resp.json}"
            logger.error(msg)
            raise Exception(msg)
        return token


def __issue_at():
    issue_at = int(time.time())
    issue_at = math.floor(issue_at / 600) * 600
    return issue_at


def __build_sign_key(access_key, access_secret, access_ts, url):
    str_key = access_key + access_secret + str(access_ts * 1000) + url
    sign_key_bytes = hashlib.sha256(str_key.encode('UTF-8')).digest()
    return base64.standard_b64encode(sign_key_bytes).decode('UTF-8')


def __java_string_hashcode(s: str):
    h = 0
    for c in s:
        h = (31 * h + ord(c)) & 0xFFFFFFFF
    return ((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000


def __do_request(url: str,
                 method: str = 'GET',
                 headers: dict = {},
                 params: dict = {},
                 data: bytes = None,
                 json: object = None,
                 timeout: float = DEFAULT_TIMEOUT,
                 auth_type=AuthType.No, retry: [bool, int] = True) -> Response:
    # header format
    if headers is None:
        headers = {}

    xTenantId = headers.get('X-tenantId')
    if xTenantId is None:
        TENANT_ID = os.environ.get('TENANT_ID') or config.TENANT_ID
        headers = {
            **headers,
            **{'X-tenantId': TENANT_ID,
            'tenant_id': TENANT_ID,
            'tenantId': TENANT_ID,
            'instanceID': TENANT_ID,
            }
        }
    else:
        headers = {
            **headers,
            **{
            'tenant_id': xTenantId,
            'tenantId': xTenantId,
            'instanceID': xTenantId,
            }
        }

    retry_count = 4
    if type(retry) == int and retry > 0:
        retry_count = retry

    for i in range(1, retry_count + 1):
        try:
            if i == 2:
                url = replace_url(url)
            logger.debug("request: %s %s %s %s %s %s", method, url, params, data, json, headers)
            resp = requests.request(
                method=method, url=url, params=params, data=data,
                json=json, headers=headers, verify=False, timeout=timeout
            )
            body = resp.text
            # 验签失败重试
            if "<title>登录</title>" in body:
                raise SignError("跳转登陆页, 请重新登录", f"Token验证未通过, 跳转登陆页")
            return Response(resp)
        except (requests.exceptions.RequestException, SignError) as e:
            if not retry or i == retry_count:
                raise e
            time.sleep(2)
            headers, _ = sign(url, params, headers, auth_type, refresh=True)
            try:
                body = e.response.text if hasattr(e.response, "text") else e.response
            except:
                body = ""
            logger.warning(
                "request retry time: %s, url: %s, body: %s, error: %s",
                i, url, body, e)


class SignError(Exception):
    def __init__(self, body="", msg=""):
        self.response = body
        self.msg = msg

    def __str__(self):
        return self.msg

    @staticmethod
    def ignore_stack():
        return True


if __name__ == '__main__':
    # post_json("http://www.google.com", timeout=1, retry=5)
    now = time.time() * 1000
    # trace_log("hexutest", now, {"test": 1}, {"test": 2})
