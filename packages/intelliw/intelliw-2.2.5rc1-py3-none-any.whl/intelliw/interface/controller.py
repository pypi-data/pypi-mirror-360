#!/usr/bin/env python
# coding: utf-8
'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2023-05-16 16:53:49
LastEditors: Hexu
Description: 线上调用的入口文件
FilePath: /iw-algo-fx/intelliw/interface/controller.py
'''
import sys
import traceback

from absl.flags import argparse_flags as argparse

from intelliw.config import config
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class FrameworkArgs:
    """
    FrameworkArgs
    """

    def __init__(self, args=None):
        self.path = "" if args is None else args.path
        self.method = "importalg" if args is None else args.method
        self.name = "predict" if args is None else args.name
        self.format = "" if args is None else args.format
        self.task = "infer" if args is None else args.task
        self.port = 8888 if args is None else args.port
        self.response = None if args is None else args.response
        self.output = "" if args is None else args.output


def __parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--path", default="",
                        type=str, help="package path")
    parser.add_argument("-m", "--method", default="importalg",
                        type=str, help="method")
    parser.add_argument("-n", "--name", default="predict",
                        type=str, help="name")
    parser.add_argument("-o", "--output", default="", type=str, help="output")
    parser.add_argument("-f", "--format", default="",
                        type=str, help="batch format")
    parser.add_argument("-t", "--task", default="infer",
                        type=str, help="task type: infer/train")
    parser.add_argument("--port", default=8888, type=int, help="port")
    parser.add_argument("-r", "--response",
                        default=None, type=str,
                        help="response addr, which can be used to report status")

    return parser.parse_args()


def main(args):
    """
    intelliw main
    """
    try:
        config.FRAMEWORK_MODE = {
            "importalg": config.FrameworkMode.Import,
            "importmodel": config.FrameworkMode.Import,
            "train": config.FRAMEWORK_MODE or config.FrameworkMode.Train,
            "apiservice": config.FrameworkMode.Infer,
            "batchservice": config.FrameworkMode.Batch,
            "custom": config.FRAMEWORK_MODE
        }.get(args.method, config.FRAMEWORK_MODE)

        if args.method == "importalg":
            from intelliw.core.pipeline import Pipeline
            Pipeline(args.response).importalg(args.path, False)
        elif args.method == "importmodel":
            from intelliw.core.pipeline import Pipeline
            Pipeline(args.response).importmodel(args.path, False)
        elif args.method == "train":
            from intelliw.interface.trainjob import TrainServer
            train = TrainServer(args.path, config.DATASET_INFO, args.response)
            train.run()
        elif args.method == "apiservice":
            from intelliw.interface.iwapi.iwapp import ApiService
            api_service = ApiService(args.port, args.path, args.response)
            api_service.run()
        elif args.method == "batchservice":
            from intelliw.interface.batchjob import BatchService
            batch_service = BatchService(
                args.format, args.path, config.DATASET_INFO,
                config.OUTPUT_DATASET_INFO, args.response, args.task)
            batch_service.run()
        elif args.method == "custom":
            from intelliw.interface.customjob import CustomService
            custom_service = CustomService(args.path, config.FRAMEWORK_MODE, args.response)
            custom_service.run()

        sys.exit(0)
    except Exception:
        logger.error("fail to execute and stack:\n%s", traceback.format_exc())
        sys.exit(1)


def run():
    """
    run intelliw
    """
    framework_args = FrameworkArgs(__parse_args())
    # 初始化环境变量
    config.update_by_env()
    main(framework_args)


if __name__ == '__main__':
    run()
