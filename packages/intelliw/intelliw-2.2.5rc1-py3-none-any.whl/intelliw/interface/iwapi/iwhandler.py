import asyncio
import time
import types
import threading
import starlette.datastructures
from fastapi import Request as FARequest, Response as FAResponse
from fastapi.responses import StreamingResponse

import json
import traceback
from starlette.middleware.base import BaseHTTPMiddleware

from intelliw.utils import health_check
from intelliw.utils import message, aiocache
from intelliw.utils.aiocache import serializers
from intelliw.utils.intelliwapi import request as my_request, monitor
from intelliw.utils.context import header_ctx
from intelliw.utils.exception import LimitConcurrencyError
from intelliw.utils.logger import _get_framework_logger, inject_level, LogCfg

logger = _get_framework_logger()


class BaseHandler:
    """
    BaseHandler
    """

    def __init__(self, request: FARequest):
        self.infer_request = my_request.Request()
        self.fa_request = self.infer_request.raw = request

    async def handle_form_data(self):
        form_data = await self.fa_request._get_form()
        self.infer_request.form.get_dict = getattr(form_data, "_dict")
        for k, v in getattr(form_data, "_list"):
            if isinstance(v, starlette.datastructures.UploadFile):
                self.infer_request.files[k] = v
            _data = self.infer_request.form.get(k, [])
            _data.append(v)
            self.infer_request.form[k] = _data

    async def handle_json_data(self):
        self.infer_request.json = await self.fa_request.json()

    async def try_handle_json_data(self):
        try:
            self.infer_request.json = await self.fa_request.json()
        except json.decoder.JSONDecodeError:
            logger.error(f"request body JSONDecodeError, {traceback.format_exc()}")

    async def request_process(self):
        """
        Process incoming request data.

        Returns:
            Tuple[Union[Dict[str, Any], APIResponse], bool]: Parsed request data and success flag.
        """
        is_ok = True
        req_data = {}

        try:
            self.infer_request.header = self.fa_request.headers
            self.infer_request.method = self.fa_request.method
            self.infer_request.url = self.fa_request.url

            # Query parameters
            self.infer_request.query = self.fa_request.query_params._dict

            # Request body
            self.infer_request.body = await self.fa_request.body()
            content_type = self.infer_request.header.get('Content-Type', "").strip()

            # form
            if content_type.startswith('application/x-www-form-urlencoded') \
                    or content_type.startswith('multipart/form-data'):
                await self.handle_form_data()
                req_data = self.infer_request.form
            # json
            elif content_type.startswith('application/json') and self.infer_request.body:
                await self.handle_json_data()
                req_data = self.infer_request.json
            # body
            elif self.infer_request.body:
                await self.try_handle_json_data()
                req_data = self.infer_request.json

            # If the body is empty, try to get data from query parameters
            if not req_data:
                req_data = self.infer_request.query
        except Exception as e:
            logger.error(traceback.format_exc())
            msg = f"request解析错误: {e}, Body: {str(self.infer_request.body)}"
            req_data = message.APIResponse(400, "api", msg, msg)
            is_ok = False

        return req_data, is_ok

    async def response_process(self, data, func, need_feature):
        """
        response process
        """
        # 简单评估下是否为流式请求
        is_stream = isinstance(data, dict) and data.get('stream')

        try:
            result, emsg = await self.infer(data, func, need_feature, )
            if emsg is None:
                if is_stream and type(result) in (
                        types.GeneratorType, types.AsyncGeneratorType):
                    return result, True
                resp = message.APIResponse(200, "api", '', result)
            elif isinstance(emsg, LimitConcurrencyError):
                resp = message.APIResponse(message.ErrorCode.limit_exceeded, "api", result)
            else:
                resp = message.APIResponse(message.ErrorCode.invalid_request, "api", emsg, result)
        except Exception as e:
            logger.error(traceback.format_exc())
            msg = f"API服务处理推理数据错误 {e}"
            resp = message.APIResponse(message.ErrorCode.invalid_request, "api", msg, msg)
        return resp, False

    @aiocache.cached(key_builder=aiocache.common.key_builder,
                     skip_cache_func=aiocache.common.skip_cache_func,
                     cache=aiocache.Cache.REDIS, namespace="intelliw:N:cache",
                     serializer=serializers.PickleSerializer())
    async def infer(self, data, func, need_feature):
        return await self.fa_request.app.intelliw_setting["infer"].infer(
            data, self.infer_request, func, need_feature, )


class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: FARequest, call_next):
        request.state.req_start_time = time.time()
        request.state.ingress_start_time = request.headers.get('x-ingress-start-time')
        keywords = {'traceId': request.headers.get('traceId', '0')}
        yat = request.headers.get('yht_access_token')
        cookie = request.headers.get('cookie')
        if yat:
            keywords['yht_access_token'] = yat
        if cookie:
            keywords['cookie'] = cookie
        logger.debug(f'request headers keywords: {keywords}')
        header_ctx.set(keywords)

        response = await call_next(request)
        response.headers.update(keywords)
        return response


def get_api_config(request: FARequest):
    api_config = request.app.intelliw_setting[f'api-{request.url.path}']
    return api_config['func'], api_config.get('need_feature', False)


async def api_handler(request: FARequest):
    base = BaseHandler(request)
    request_data, is_ok = await base.request_process()
    result = {}
    # 进行推理处理
    if is_ok:
        func, need_feature = get_api_config(request)
        result, is_stream = await base.response_process(request_data, func, need_feature)
        if is_stream:
            return StreamingResponse(result, media_type="text/event-stream")
    if request.query_params.get('request_debug'):
        logger.warning(f'Request: {request_data}\nResponse: {result}')
    return FAResponse(content=str(result), media_type="application/json")


async def health_check_handler():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, health_check.health_check_process)
    if result:
        resp = message.HealthCheckResponse(200, "api", 'ok', "")
    else:
        resp = message.HealthCheckResponse(500, "api", 'error', "")
    return FAResponse(content=str(resp), media_type="application/json")


async def set_config(request: FARequest):
    try:
        data = await request.json()
        key = data.get('key')
        if key == 'log':
            level, delay = data.get('level', 'INFO'), min(data.get('delay', 600), 3600)
            inject_level(level)
            threading.Timer(delay, inject_level, (LogCfg.level,)).start()
        resp = {'code': 200, 'message': 'ok'}
    except Exception as e:
        logger.error(traceback.format_exc())
        resp = {'code': message.ErrorCode.invalid_request, 'message': str(e)}
    return FAResponse(content=str(resp), media_type="application/json")


async def service_monitoring(request: FARequest):
    data = await request.json()
    response_data = monitor.init_request_data(data)
    if response_data:
        return FAResponse(content=str(message.APIResponse(200, "api", '', response_data)),
                          media_type="application/json")
    # 查询
    if data.get('requestMode') == "query":
        response_data = monitor.monitor_query()
    # 请求监控
    elif data.get('requestMode') == "monitor":
        # 默认状态为监控任务运行中
        response_data = {"status": 1}
        monitor.monitor_request(data)

    resp = message.APIResponse(200, "api", '', response_data)
    return FAResponse(content=str(resp), media_type="application/json")


async def eureka_health_check_handler():
    resp = message.HealthCheckResponse(200, "api", 'ok', "")
    return FAResponse(content=str(resp), media_type="application/json")
