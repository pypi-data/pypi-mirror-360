#!/usr/bin/env python
# coding: utf-8

import json
import threading
import traceback
from intelliw.utils.iuap_request import post
from intelliw.utils import get_json_encoder
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config
from intelliw.utils.global_val import gl

logger = _get_framework_logger()


class Recorder:
    # 单例锁
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """ 单例，防止调用生成更多环境变量dict """
        if not hasattr(Recorder, "_instance"):
            with Recorder._instance_lock:
                if not hasattr(Recorder, "_instance"):
                    Recorder._instance = object.__new__(cls)
                    gl.recorder = Recorder._instance
        return Recorder._instance

    def __init__(self, addr: str):
        # 上报地址
        assert isinstance(addr, (str, type(None))), "Recorder Addr must string"
        self.addr = addr
        self.seq = 0

    def report(self, msg, stdout=True):
        """
        上报
        """
        self.seq += 1
        trace_id = config.SERVICE_ID + '_p' + str(self.seq)
        if hasattr(type(msg), '__str__'):
            data = str(msg)
        else:
            data = json.dumps(msg, ensure_ascii=False,
                              cls=get_json_encoder())
        if self.addr is not None:
            logger.info('[report %s] start, Request: %s', trace_id, msg)
            try:
                headers = {'Content-Type': 'application/json',
                           'X-traceId': trace_id}
                response = post(url=self.addr, headers=headers,
                                data=data.encode('utf-8'))
                response.raise_for_status()
                if stdout:
                    logger.info(
                        '[report %s] success, Response: %s', trace_id, response.body)
            except Exception as e:
                stack_info = traceback.format_exc()
                logger.error(
                    "[report %s] failed, url: [%s], exception: [%s], stack:\n%s", trace_id, self.addr, e, stack_info)
        else:
            logger.info('[report local]Request: %s', msg)
