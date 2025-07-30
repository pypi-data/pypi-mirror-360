'''
Author: Hexu
Date: 2022-08-24 16:52:17
LastEditors: Hexu
LastEditTime: 2023-03-27 14:07:11
FilePath: /iw-algo-fx/intelliw/interface/trainjob.py
Description: Train entrypoint
'''
import traceback
from intelliw.core.al_decorator import flame_prof_process
from intelliw.core.trainer import Trainer
from intelliw.core.recorder import Recorder
from intelliw.datasets.datasets import get_dataset
import intelliw.utils.message as message
from intelliw.utils.logger import _get_framework_logger

logger = _get_framework_logger()


class TrainServer:
    def __init__(self, path, dataset_cfg, response_addr=None):
        self.response_addr = response_addr
        self.path = path
        self.reporter = Recorder(response_addr)
        self.dataset_cfg = dataset_cfg

    @flame_prof_process
    def run(self):
        try:
            trainer = Trainer(self.path, self.response_addr)
            datasets = get_dataset(self.dataset_cfg)
            trainer.train(datasets)
        except (Exception, SystemExit) as e:
            stack_info = traceback.format_exc()
            logger.error("训练执行错误 {}, stack:\n{}".format(e, stack_info))
            self.reporter.report(
                message.CommonResponse(500, "train_fail", "训练执行错误 {}, stack:\n{}".format(e, stack_info)))
