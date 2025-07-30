'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2023-05-24 15:15:48
LastEditors: Hexu
Description: api处理函数
FilePath: /iw-algo-fx/intelliw/interface/apihandler.py
'''
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI

import json
import threading

from intelliw.config import config
from intelliw.core.infer import Infer
from intelliw.utils import message, util
from intelliw.interface.iwapi import iwhandler
from intelliw.utils import get_json_encoder
from intelliw.utils.intelliwapi import gunicorn_server
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


def set_initializer(func, *args):
    ApiService.initializer = _INITIALIZER(func, *args)


class _INITIALIZER:
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def run(self):
        return self.func(*self.args)


class Application:
    """推理服务路由类
    example:
        @Application.route("/infer-api", method='get', need_feature=True)
        def infer(self, test_data):
            pass
    args:
        path           访问路由   /infer-api
        method         访问方式，支持 get post push delete head patch options
        need_feature   是否需要使用特征工程, 如果是自定义与推理无关的函数, 请设置False
    """

    # Set URL handlers
    HANDLERS = []

    def __init__(self, custom_router):
        self.app = FastAPI(json_encoder=get_json_encoder())
        self.app.intelliw_setting = {}
        self.handler_process(custom_router)

    def __call__(self):
        return self.app

    @classmethod
    def route(cls, path, **options):
        """
        register api route
        """

        def decorator(function):
            cls.HANDLERS.append((
                path,
                {'func': function.__name__,
                 'method': options.pop('method', 'post').lower(),
                 'need_feature': options.pop('need_feature', True)}))
            return function

        return decorator

    def handler_process(self, routers):
        # 加载自定义api, 配置在algorithm.yaml中
        for router in routers:
            Application.HANDLERS.append((
                router["path"],
                {'func': router["func"],
                 'method': router.get("method", "post").lower(),
                 'need_feature': router.get("need_feature", True)}))

        # 检查用户是否完全没有配置路由
        if len(Application.HANDLERS) == 0:
            Application.HANDLERS.append((
                '/predict',
                {'func': 'infer', 'method': 'post', 'need_feature': True}))  # 默认值

        # 任务检测
        Application.HANDLERS.append((
            '/intelliw-worker',
            {'func': 'intelliw-worker', 'method': 'get', 'need_feature': False}
        ))

        # 集中绑定路由
        _route_cache = {}
        # 路由重复统计
        _route_dup_dict = dict()

        for router, info in Application.HANDLERS:
            # 确保路由以斜杠开头
            if not router.startswith("/"):
                router = "/" + router

            # 获取函数、方法及是否需要特征处理的信息
            func = info['func']
            methods = info['method'].split(",")
            need_feature = info['need_feature']

            # 检查路由是否已存在
            route_key = router + func
            if _route_cache.get(route_key, None):
                continue
            _route_cache[route_key] = True

            # 添加路由配置
            self.app.intelliw_setting[f'api-{router}'] = info
            self.app.add_api_route(router, endpoint=iwhandler.api_handler, methods=methods)

            # 记录并警告重复路由
            if router in _route_dup_dict:
                prev_func = _route_dup_dict[router]
                logger.warning("方法: %s, 访问路径：%s 将被 方法: %s 覆盖", prev_func, router, func)

            logger.info("方法: %s 加载成功, 访问路径：%s, 访问方法: %s, 是否需要特征处理: %s", func, router, methods,
                        need_feature)

        # healthcheck
        # gateway
        self.app.add_api_route(
            '/healthcheck',
            endpoint=iwhandler.health_check_handler, methods=['get', 'post'])
        # eureka
        self.app.add_api_route(
            '/CloudRemoteCall/',
            endpoint=iwhandler.eureka_health_check_handler, methods=['get', 'post'])
        # serviceMonitoring
        self.app.add_api_route(
            '/serviceMonitoring',
            endpoint=iwhandler.service_monitoring, methods=['post'])
        # set config
        self.app.add_api_route(
            '/config',
            endpoint=iwhandler.set_config, methods=['post'])

        # middleware
        self.app.add_middleware(iwhandler.RequestTimingMiddleware)


class ApiService:
    """
    intelliw api service
    """
    _instance = None
    _init_flag = False

    initializer = None

    def __new__(cls, *args, **kwargs):
        # 1.判断类属性是否为空对象，若为空说明第一个对象还没被创建
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, port, path, response_addr):
        if ApiService._init_flag:
            return
        ApiService._init_flag = True
        self.port = port  # 8888
        self.infer = Infer(path, response_addr)
        self.app = Application(self.infer.pipeline.custom_router).app
        self.reporter = self.infer.pipeline.recorder
        self.app.intelliw_setting.update({"infer": self.infer, "reporter": self.reporter})
        self._report_start()

    def _report_start(self):
        """
        report start
        """
        self.reporter.report(message.CommonResponse(
            200, "inferstatus", '',
            json.dumps([{'status': 'start',
                         'inferid': config.INFER_ID,
                         'instanceid': config.INSTANCE_ID,
                         'inferTaskStatus': []}],
                       cls=get_json_encoder(), ensure_ascii=False)
        ))

    @staticmethod
    def _eureka_server():
        if len(config.EUREKA_SERVER) > 0:
            from intelliw.core.linkserver import linkserver
            try:
                should_register = config.EUREKA_APP_NAME != ''
                iports = json.loads(config.REGISTER_CLUSTER_ADDRESS)
                profile = config.EUREKA_ZONE or 'test'
                linkserver.client(
                    config.EUREKA_SERVER, config.EUREKA_PROVIDER_ID,
                    should_register, config.EUREKA_APP_NAME, iports, profile)
                logger.info("eureka server client init success, register:%s, server name: %s",
                            should_register, config.EUREKA_APP_NAME)
            except Exception as e:
                logger.error(
                    f"eureka server client init failed, error massage: {e}")

    def thread_pool_init(self, thread):
        # 给测试放开口子
        if os.environ.get('THREAD_NO_LIMIT') == 'true':
            thread = 999
            logger.warning("thread no limit")

        initializer, initargs = None, ()
        if self.initializer is not None:
            def threading_init(pool, func, *args):
                t = threading.currentThread().ident
                pool[t] = func(*args)

            initializer = threading_init
            initargs = (
                self.infer.pipeline.thread_data_pool,
                self.initializer.func,
                *self.initializer.args
            )

        self.infer.pipeline.max_wait_task = min(999, max(2, config.INFER_MAX_TASK_RATIO * thread))
        self.infer.pipeline.async_executor = ThreadPoolExecutor(
            thread, initializer=initializer, initargs=initargs, thread_name_prefix="IntelliwServerPool")

    def _fastapi_server(self):
        config.MAINPID = str(os.getpid())

        worker, thread = util.get_worker_count(
            config.CPU_COUNT,
            config.INFER_MULTI_THREAD_COUNT,
            config.INFER_MULTI_PROCESS
        )

        config.INFER_MULTI_PROCESS_COUNT = worker
        self.thread_pool_init(thread)

        isIpv6 = os.environ.get('USE_IPV6', 'false') == 'true'
        # 多进程
        if config.INFER_MULTI_PROCESS:
            setting = gunicorn_server.default_config(
                f'[::]:{self.port}' if isIpv6 else f'0.0.0.0:{self.port}',
                workers=worker,
            )
            server = gunicorn_server.GunServer(self.app, setting, logger)
        else:
            # 默认模式
            server = gunicorn_server.UvicornServer(
                self.app,
                "::" if isIpv6 else "0.0.0.0", self.port
            )

        logger.info("\033[34mServer init success, workers: %s, threads: %s, max wait task: %s \033[0m",
                    worker, thread, self.infer.pipeline.max_wait_task)
        server.run()

    def run(self):
        """
        start server
        """
        self._eureka_server()
        self._fastapi_server()
