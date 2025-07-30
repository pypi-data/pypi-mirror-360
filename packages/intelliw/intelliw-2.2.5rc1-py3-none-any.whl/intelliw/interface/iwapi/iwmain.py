#!/usr/bin/env python
# coding: utf-8
from intelliw.config import config

config.update_by_env()

from intelliw.interface.controller import FrameworkArgs, __parse_args
from intelliw.utils.logger import _get_framework_logger
from intelliw.interface.iwapi.iwapp import ApiService

logger = _get_framework_logger()
framework_args = FrameworkArgs(__parse_args())

config.FRAMEWORK_MODE = "infer"
api_service = ApiService(framework_args.port, framework_args.path, framework_args.response)

if __name__ == '__main__':
    api_service.run()
