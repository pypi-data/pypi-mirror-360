#!/usr/bin/env python
# coding: utf-8
import asyncio
import json
import time
import traceback

from fastapi import FastAPI, Request as FARequest, Response as FAResponse, BackgroundTasks
from intelliw.utils.crontab import Crontab
from intelliw.datasets.datasets import get_dataset, get_datasource_writer, \
    DataSets, MultipleDataSets
from intelliw.core.recorder import Recorder
from intelliw.core.infer import Infer
from intelliw.utils import message
import uvicorn
from intelliw.datasets.datasource_base import DataSourceReaderException, DataSourceWriterException
from intelliw.utils import get_json_encoder, intelliwapi
from intelliw.config import config
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()

batchjob_infer = "batchjob-infer"

INFER_CONTROLLER: Infer = None  # type: ignore
intelliw_setting = {}


def get_batch_msg(issuccess, msg, status=True, starttime=None, user_param={}, system_param={}):
    """
    批处理上报信息，inferTaskStatus 不为空，会被记录为一次调用，标识一次批处理的状态
    """
    infer_task_status = []
    if status:
        infer_task_status = [
            {
                "id": config.INFER_ID, "issuccess": issuccess,
                "starttime": starttime, "endtime": int(time.time() * 1000),
                "message": msg
            }
        ]
    out_msg = [
        {
            'status': 'start' if issuccess else 'end',
            'inferid': config.INFER_ID,
            'instanceid': config.INSTANCE_ID,
            'inferTaskStatus': infer_task_status,
            "params": {"user": user_param, "system": system_param}
        }
    ]
    return json.dumps(out_msg, cls=get_json_encoder(), ensure_ascii=False)


def validate_batch_job(reporter, path):
    global INFER_CONTROLLER
    INFER_CONTROLLER = Infer(path, reporter)
    msg = get_batch_msg(True, '定时推理校验通过，上线成功', status=False)
    reporter.report(message.CommonResponse(200, batchjob_infer,
                                           '定时推理校验通过，上线成功',
                                           json.dumps(msg, cls=get_json_encoder(), ensure_ascii=False)))


def infer_job(reporter, dataset_cfg, output_dataset_cfg, params={}):
    """
    request json {"user":None, "system": None}
    response json {
                    'status': 'start' if issuccess else 'end',
                    'inferid': config.INFER_ID,
                    'instanceid': config.INSTANCE_ID,
                    'inferTaskStatus': inferTaskStatus,
                    "params": {"user":None, "system": None}
                }
    """
    user_param = params.get("user", {})
    system_param = params.get("system", {})

    def input():
        datasets = get_dataset(dataset_cfg)
        alldata = datasets.read_all_data()
        # 保持与训练一致
        if isinstance(datasets, MultipleDataSets):
            return alldata
        elif isinstance(datasets, DataSets):
            return [alldata]
        else:
            return None

    def output(r):
        writer = get_datasource_writer(output_dataset_cfg)
        res_data = writer.write(r)
        if res_data['status'] != 1:
            raise DataSourceWriterException(res_data['msg'])

    start_time = int(time.time() * 1000)
    result, stack_info, info = None, None, ""
    try:
        # 输入
        alldata = input()

        # 批处理
        global INFER_CONTROLLER
        pipeline = INFER_CONTROLLER.pipeline
        infer_func = getattr(pipeline.instance, "infer")
        arg = [alldata] if infer_func.__code__.co_argcount > 1 else []  # 获取函数参数数量
        pipeline.instance.request = intelliwapi.Request(user_param=user_param)
        result = infer_func(*arg)
        logger.info('批处理处理结果 %s', result)

        # 输出
        output(result)
    except DataSourceReaderException as e:
        info = f"批处理输入数据错误: {e}"
        stack_info = f"{info}, stack:\n{traceback.format_exc()}"
    except DataSourceWriterException as e:
        info = f"批处理输出数据错误: {e}"
        stack_info = f"{info}, stack:\n{traceback.format_exc()}"
    except Exception as e:
        info = f"批处理执行错误: {e}"
        stack_info = f"{info}, stack:\n{traceback.format_exc()}"
    else:
        info = "批处理输出数据成功"
    finally:
        status_code = 200
        if stack_info is not None:
            status_code = 500
            logger.error(stack_info)

        msg = get_batch_msg(True, info, user_param=result,
                            system_param=system_param, starttime=start_time)
        reporter.report(
            message.CommonResponse(status_code, batchjob_infer, info, msg)
        )


class JobServer:
    @staticmethod
    async def healthcheck():
        resp = message.HealthCheckResponse(200, "api", 'ok', "")
        return FAResponse(content=str(resp), media_type="application/json")

    @staticmethod
    async def run(req: FARequest, background_tasks: BackgroundTasks):
        r = await req.json()
        args = intelliw_setting[f'api-batch-predict']
        logger.info("server job start")

        background_tasks.add_task(
            infer_job,
            args["reporter"],
            args["dataset_cfg"],
            args["output_dataset_cfg"],
            r
        )
        return FAResponse(content=json.dumps({"code": "1", "message": "server job start"}),
                          media_type="application/json")


class BatchService:
    def __init__(self, corn, path, dataset_cfg, output_dataset_cfg, response_addr=None, task='infer'):
        self.reporter = Recorder(response_addr)
        if task != 'infer':
            _msg = '批处理任务任务错误，TASK环境变量必须为infer'
            msg = get_batch_msg(False, _msg, status=False)
            self.reporter.report(message.CommonResponse(500, batchjob_infer,
                                                        _msg,
                                                        json.dumps(msg, cls=get_json_encoder(), ensure_ascii=False)))
        self.corn = corn
        self.only_server = not corn
        self.dataset_cfg = dataset_cfg
        self.output_dataset_cfg = output_dataset_cfg
        self.path = path
        intelliw_setting['api-batch-predict'] = {"reporter": self.reporter, "dataset_cfg": self.dataset_cfg,
                                                 "output_dataset_cfg": self.output_dataset_cfg}

    def _format_parse(self):
        return [{
            'crontab': f.strip(),
            'func': infer_job,
            'args': (self.reporter, self.dataset_cfg, self.output_dataset_cfg)
        } for f in self.corn.split("|")]

    def _cronjob(self):
        job_list = self._format_parse()
        crontab = Crontab(job_list, True)
        crontab.start()
        logger.info("Start cronjob")

    def _server(self):
        app = FastAPI(
            json_encoder=get_json_encoder()
        )
        app.add_api_route(
            '/batch-predict', endpoint=JobServer.run, methods=['get', 'post'])
        app.add_api_route(
            "/healthcheck", endpoint=JobServer.healthcheck, methods=["POST", "GET"])
        logger.info(
            "Server Start: \n\033[33m[POST] /batch-predict\n[POST, GET] /healthcheck\033[0m"
        )
        asyncio.set_event_loop(asyncio.new_event_loop())
        uvicorn.run(
            app=app,
            host="0.0.0.0",
            port=8888,
        )

    def run(self):
        validate_batch_job(self.reporter, self.path)
        if self.only_server:
            logger.info(
                "\033[33mCronjob Format is Empty, Only Server Mode\033[0m")
            self._server()
        else:
            logger.info(
                "\033[33mCronjob Format is %s,Cronjob and Server Mode\033[0m", self.corn)
            self._cronjob()
            self._server()
