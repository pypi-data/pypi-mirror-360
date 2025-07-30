import logging
import os.path
import urllib

import requests
import importlib.util
from typing import List
from intelliw.config import config
from intelliw.utils.context import header_ctx


class HijackModelLoad:
    error = type("ModelLoadError", (Exception, object), {
        "__str__": lambda self: '''算法使用了未验证的运行环境：
         1. 请使用ONNX模型进行服务推理
         2. 请勿使用Paddle，TensorFlow等框架加载模型
             ''',
        "ignore_stack": lambda self: True
    })

    def __init__(self):

        self.config: List[dict] = [
            # {'package': 'torch', 'function': 'load'},
            {'package': 'paddle', 'function': 'load'},
            {'package': 'paddle', 'function': 'jit.load'},
            {'package': 'paddle', 'function': 'Model.load'},
            {'package': 'tensorflow', 'function': 'keras.models.load_model'},
            {'package': 'tensorflow', 'function': 'saved_model.load'}
        ]
        self.hijack()

    def hijack(self):
        for c in self.config:
            package = c['package']
            function = c['function']
            if importlib.util.find_spec(package):
                p = importlib.import_module(package)
                f_list = function.split(".")
                for f in f_list:
                    try:
                        setattr(p, f, HijackModelLoad._raise)
                        p = getattr(p, f)
                    except Exception as e:
                        print('hijack error:', e)

    def _raise(*args, **kwargs):
        raise HijackModelLoad.error


class HijackRequests:
    """
    注入requests包，在专属化环境写入证书信息，通过工作坊给的链接进行下载，然后将文件夹位置赋值给环境变量INTELLIW_SSL_FILEPATH
    如果都验证没问题，所有请求都注入证书, 否则都避开证书校验
    """

    @staticmethod
    def request(method, url, **kwargs):
        keywords = header_ctx.get()
        if 'headers' in kwargs:
            kwargs['headers'].update(keywords)
        else:
            kwargs['headers'] = keywords

        if config.INTELLIW_SSL_FILEPATH:
            path = config.INTELLIW_SSL_FILEPATH
            # 根据host判断的方式
            if os.path.isdir(path):
                var = urllib.parse.urlparse(url).netloc
                file_paths = [os.path.join(path, file_name) for file_name in os.listdir(path) if
                              os.path.splitext(file_name)[0] == var]
                if file_paths:
                    kwargs['verify'] = file_paths[0]
        else:
            kwargs['verify'] = False
        with requests.sessions.Session() as session:
            try:
                return session.request(method=method, url=url, **kwargs)
            except requests.exceptions.SSLError:
                kwargs['verify'] = False
                return session.request(method=method, url=url, **kwargs)

    def __init__(self):
        self.hijack()

    @staticmethod
    def hijack():
        requests.api.request = HijackRequests.request
        requests.request = HijackRequests.request


class HijackLogging:
    def __init__(self):
        self.hijack()

    @staticmethod
    def hijack():
        logging.LogRecord.traceid = '0'
