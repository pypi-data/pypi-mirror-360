from functools import wraps
import threading
from typing import Union, List
from intelliw.utils import iuap_request


try:
    from eurekapy import http_client, eureka_client
    has_eurekapy_package = True

    # AuthHttpClient 重写HttpClient， 方便做加签
    class AuthHttpClient(http_client.HttpClient):
        def urlopen(self, request: Union[str, http_client.HttpRequest] = None,
                    data: bytes = None, timeout: float = None) -> http_client.HttpResponse:

            if isinstance(request, http_client.HttpRequest):
                req = request
            elif isinstance(request, str):
                req = http_client.HttpRequest(request)
            else:
                raise http_client.URLError("Unvalid URL")
            req.add_header("YYCtoken", iuap_request.sign_authsdk(req.url, None))
            req.add_header("Content-Type", "application/json")
            # import requests
            # resp = requests.request(
            #     req.method if req.method else "get", req.url, headers=req.headers, data=data)
            # print("-------", resp.text, resp.status_code)
            return super().urlopen(req, data, timeout)

    http_client.set_http_client(AuthHttpClient())
except ImportError:
    has_eurekapy_package = False


class LinkServerError(Exception):
    pass


class LinkServiceType:
    RPC = 'rpc'
    HTTP = 'http'
    LOCAL = 'local'


class LinkBase:
    def __init__(self) -> None:
        self.config = None

    def __call__(self, config: List[dict] = None):
        def wrapper(function):
            @wraps(function)
            def inner(*args, **kwargs):
                return function(*args, **kwargs)
            return inner
        return wrapper


class LinkService:
    """LinkService提供模型编排功能

    客户端生成:
      1 不注册服务： 通过open()方法进行客户端连接, 但是不会将此服务注册在服务中心
      2 注册服务: 通过register()方法进行客户端连接, 并将此服务注册在注册中心

    模型编排:
      1 通过设置self.config, 进行自动编排
        config格式如下:
            config = [
                {"name": "test1", "method": "get", "router": "/api-get", "type": "rpc"},
                {"name": "test2", "method": "get", "router": "http://ip:port/api-get", "type": "http"},
            ]

      2 手动调用rpc服务
        创建客户端连接后， 通过do_server()进行远程服务调用

    """
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(LinkService, "_instance"):
            with LinkService._instance_lock:
                if not hasattr(LinkService, "_instance"):
                    LinkService._instance = object.__new__(cls)
        return LinkService._instance

    def __init__(self) -> None:
        self._client = eureka_client
        self.config = None

    def client(self, eureka_server: str, provider_id: str, should_register: bool = False, server_name: str = "", server_iports: list = [], profile: str = "test"):
        """生成客户端连接

        Args:
            eureka_server (str): eureka服务地址
            providerId (str): 租户id.
            should_register (bool, optional): 是否注册当前服务. Defaults to False.
            server_iports (int, optional): 注册服务ip和端口, should_register is True 是必填. Defaults to [],  e.g.:["192.168.0.1:8080", "192.168.0.2:8080"]
            server_name (str, optional): 注册服务名称, should_register is True 是必填. Defaults to 0.
            profile (str, optional): 服务命名空间
        """
        if should_register:
            self.register(eureka_server, provider_id,
                          server_name, server_iports, profile)
        else:
            self.open(eureka_server, provider_id, profile)

    def open(self, eureka_server: str, provider_id: str, profile: str = "test"):
        """生成客户端连接, 但是不会将此服务注册在服务中心

        Args:
            eureka_server (str): eureka服务地址.
            providerId (str): 租户id.
            profile (str, optional): 服务命名空间
        """
        self._client.init(
            eureka_server=eureka_server,
            should_register=False,
            profile=profile,
            prefer_same_zone=False,
            prefer_same_profile=True,
            payload={"providerId": provider_id}
        )

    def register(self, eureka_server: str, provider_id: str, server_name: str, server_iports: list = [], profile: str = "test"):
        """生成客户端连接, 并将此服务注册在注册中心

        Args:
            eureka_server (str): eureka服务地址.
            provider_id (str): 租户id.
            server_name (str): 注册服务名称
            server_iports (list, optional): 注册服务端口
            profile (str, optional): 服务命名空间
        """
        if not server_iports or not server_name or not eureka_server or not provider_id:
            raise LinkServerError(
                f"register must need:\nip and port:{server_iports}\nname: {server_name}\neureka_server: {eureka_server}\nprovider_id: {provider_id}")

        # 会根据ip数量开启多组心跳检测
        for iport in server_iports:
            ip, port = iport.split(":")
            instance_id = f'{iport}@{provider_id}'
            metadata = {
                "instanceId": instance_id,
                "context": "",
                "all_iports": f"[\"{iport}\"]",
            }
            self._client.init(
                app_name=server_name,
                instance_ip=ip,
                instance_port=int(port),
                instance_id=instance_id,
                metadata=metadata,
                eureka_server=eureka_server,
                ha_strategy=eureka_client.HA_STRATEGY_RANDOM,
                payload={"providerId": provider_id, "appRemark": ""},
                profile=profile,
                renewal_interval_in_secs=10,
            )

    def do_server(self, name: str, router: str, data: Union[dict, str, bool, int] = None, method: str = "POST"):
        """手动请求rpc服务

        Args:
            name (str): 注册服务名称
            router (str): 请求路由 e.g./predict
            data (Union[dict, str, bool, int], optional): 请求内容. Defaults to None.
            method (str, optional): 请求方式. Defaults to "GET".

        Returns:
            Union[dict, str, bool, int], optional:  response.json
        """
        try:
            data = self._rpc_request(name, router, method, data)
        except Exception as e:
            raise LinkServerError(
                f"link server error:\n server info: {name}-{router}-{method}, error msg: {e}")
        return data

    def __call__(self, config: List[dict] = None):
        """调用装饰器, 自动编排使用

        Args:
            config (List[dict], optional): 调用配置. Defaults to None. 优先使用传入配置
        """
        def wrapper(function):
            @wraps(function)
            def inner(*args, **kwargs):
                # 无调用
                if not config and not self.config:
                    return function(*args, **kwargs)

                # 优先传入的配置
                self.config = config or self.config
                # 调用开始
                data = self._choice_data(args)
                for server in self.config:
                    stype = server["type"]
                    if stype == LinkServiceType.LOCAL:
                        data = self._local(function, data)
                    else:
                        data = self._request(server, data)
                return data
            return inner
        return wrapper

    def _choice_data(self, args):
        # 自己调用的时候data可能在第1位， 服务调用的时候， 会在第2位， 第1位为self
        for idx, arg in enumerate(args):
            if idx < 2:
                if isinstance(arg, (dict, str, list, bool, int)):
                    return arg
            else:
                break
        return None

    def _local(self, function, data):
        try:
            return function(data) if data is not None else function()
        except Exception as e:
            raise LinkServerError(
                f"link server error: error server: local,  error msg: {e}")

    def _request(self, server, data):
        try:
            stype = server["type"]
            method = server["method"]
            router = server["router"]
            if stype == LinkServiceType.RPC:
                data = self._rpc_request(server["name"], router, method, data)
            elif stype == LinkServiceType.HTTP:
                data = self._http_request(router, method, data)
            if "extrainfo" in data and "data" in data:
                data = data["data"]
        except Exception as e:
            raise LinkServerError(
                f"link server error:\n server info: {server}, error msg: {e}")
        return data

    def _http_request(self, router, method, data):
        header = {"Content-Type": "application/json"}
        resp = iuap_request.sign_and_request(
            router, method, json=data, headers=header)
        return resp.json

    def _rpc_request(self, server, router, method, data):
        resp = self._client.do_service(
            server, router, return_type="json", method=method, data=data, timeout=30, prefer_ip=True)
        return resp


linkserver = LinkService() if has_eurekapy_package else LinkBase()
