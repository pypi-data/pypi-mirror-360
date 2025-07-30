'''
Author: Hexu
Date: 2022-07-25 10:36:04
LastEditors: Hexu
LastEditTime: 2023-03-21 10:08:46
FilePath: /iw-algo-fx/intelliw/feature.py
Description: 统一功能包入口
'''
# 🙅🙅🙅不要删除🙅🙅🙅
from intelliw.interface.iwapi.iwapp import (
    Application,
    set_initializer
)
from intelliw.core.linkserver import linkserver
from intelliw.utils.logger import _get_algorithm_logger as get_logger, _get_framework_logger
from intelliw.utils import exception
from intelliw.utils.storage_service import FileTransferDevice
from intelliw.datasets.datasets import get_datasource_writer as OutPutWriter
from intelliw.utils import context

try:
    from intelliw.utils.intelliwapi.workers import IntelliwWorker
except Exception as e:
    _get_framework_logger().warning(
        "\033[33mGunicorn can not used\033[0m, error: %s", e)

try:
    from intelliw.utils.spark_process.spark import Spark
except ImportError as e:
    _get_framework_logger().warning(
        "\033[33mIf want use spark, you need: pip install pyspark\033[0m, error: %s", e)

