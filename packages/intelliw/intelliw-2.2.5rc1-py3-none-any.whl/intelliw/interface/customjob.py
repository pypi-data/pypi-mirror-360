'''
Author: Hexu
Date: 2022-08-24 16:52:17
LastEditors: Hexu
LastEditTime: 2023-03-27 14:07:11
FilePath: /iw-algo-fx/intelliw/interface/trainjob.py
Description: Train entrypoint
'''
import traceback
from intelliw.core.custom import Custom
from intelliw.core.recorder import Recorder
import intelliw.utils.message as message
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class CustomService:
    def __init__(self, path, procedure_type=None, response_addr=None):
        self.response_addr = response_addr
        self.path = path
        self.reporter = Recorder(response_addr)
        self.procedure_type = procedure_type

    def run(self):
        try:
            custom = Custom(self.path, self.response_addr, self.procedure_type)
            custom.run()
        except Exception as e:
            stack_info = traceback.format_exc()
            logger.error("自定义服务执行错误 {}, stack:\n{}".format(e, stack_info))
            self.reporter.report(
                message.CommonResponse(500, "custom_finish",
                                       "自定义服务执行错误 {}, stack:\n{}".format(e, stack_info),
                                       businessType=self.procedure_type))
