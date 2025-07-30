#!/usr/bin/env python
# coding: utf-8
import time
import os
import sys
import logging
import threading
import logging.handlers
from datetime import datetime
from glob import glob

from intelliw.utils import string_to_function, gen_random_str
from intelliw.utils.colorlog import ColoredFormatter
from intelliw.utils.context import header_ctx

framework_logger = None
user_logger = None


def log_path():
    path = os.environ.get("INTELLIW_LOG_PATH") or \
           os.environ.get("intelliw.logger.path") or \
           "./logs/"
    code = os.environ.get("INSTANCE_POD_NAME", "pod")
    if not sys.platform.startswith('win') and os.environ.get('isPremises', 'false') != 'true':
        path = os.path.join(path, code, f'{datetime.now().strftime("%Y-%m-%d:%H:%M:%S")}')
    if not os.path.exists(path):
        os.makedirs(path)
    return path


class LogCfg:
    level = os.environ.get("intelliw.logger.level", logging.INFO)

    format = ('[%(traceid)s] [PID%(process)d] -%(name)s- %(asctime)s '
              '| %(levelname)4s | %(filename)s:%(lineno)s: %(message)s')

    colorful_format = ('[%(traceid)s] %(log_color)s[PID%(process)d] -%(name)s- %(asctime)s '
                       '| %(levelname)4s | %(filename)s:%(lineno)s: %(message)s')

    data_format = '%Y-%m-%d %H:%M:%S'
    path = log_path()


def inject_code():
    class MyLogRecord(logging.LogRecord):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.traceid = '0'

    logging.setLogRecordFactory(MyLogRecord)
    logging.PercentStyle._format = string_to_function('''
def _format(self, record):
    if '%(traceid)' not in self._fmt:
        self._fmt = f'[%(traceid)s] {self._fmt}'
    if not hasattr(record, 'traceid'):
        setattr(record, 'traceid', '0')
    return self._fmt % record.__dict__
    ''', "_format")


inject_code()


def is_file_handler(handler):
    return isinstance(handler, logging.FileHandler)


def update_file_handlers_level(new_level):
    # user logger
    logger_dict = logging.root.manager.loggerDict
    for logger_name, logger_obj in logger_dict.items():
        if isinstance(logger_obj, logging.Logger):
            for handler in logger_obj.handlers:
                if is_file_handler(handler):  # 检查是否为文件写入 handler
                    handler.setLevel(new_level)
                    logger_obj.setLevel(new_level)  # 同步更新 logger 的 level
    # root
    for handler in logging.root.handlers:
        if is_file_handler(handler):
            handler.setLevel(new_level)


def inject_level(level):
    level = logging._checkLevel(level)

    def getEffectiveLevel(self):
        """
        Get the effective level for this logger.

        Loop through this logger and its parents in the logger hierarchy,
        looking for a non-zero logging level. Return the first one found.
        """
        return level

    logging.Logger.getEffectiveLevel = getEffectiveLevel
    logging.Logger.manager._clear_cache()
    update_file_handlers_level(level)


class TraceIDFilter(logging.Filter):
    def filter(self, record):
        header = header_ctx.get()
        if isinstance(header, dict):
            record.traceid = header.get('traceId', '0')
        else:
            record.traceid = '0'
        return True


class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, base_filename, *args, **kwargs):
        self.base_filename = base_filename
        super().__init__(base_filename, *args, **kwargs)

    def doRollover(self):
        # 如果日志文件存在且需要滚动
        if self.stream:
            self.stream.close()
            self.stream = None

        # 获取当前时间作为文件名的一部分
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        rollover_filename = f"{self.base_filename}_{current_time}.log"

        # 重命名当前日志文件
        if os.path.exists(self.base_filename):
            os.rename(self.base_filename, rollover_filename)

        # 调用父类的方法来处理日志文件切换
        self.mode = 'w'
        self.stream = self._open()

        # 检查日志文件数量，删除最旧的多余文件
        self.clean_old_logs()

    def clean_old_logs(self):
        # 获取当前目录下所有的滚动日志文件
        log_files = glob(f"{self.base_filename}_*.log")
        if len(log_files) > self.backupCount:
            # 按文件的创建时间排序
            log_files.sort(key=os.path.getctime)
            # 删除多余的旧日志文件
            for log_file in log_files[:len(log_files) - self.backupCount]:
                os.remove(log_file)


class Logger:
    _instance_lock = threading.Lock()

    def __new__(cls):
        """ 单例,防止调用生成更多 """
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    if not os.path.exists(LogCfg.path):
                        os.makedirs(LogCfg.path)
                    Logger._instance = object.__new__(cls)
                    Logger.__global_logger(cls)
        return Logger._instance

    def __global_logger(cls):
        root_logger = logging.getLogger()
        root_logger.addFilter(TraceIDFilter())

        # set up the logger to write into file
        if os.access(LogCfg.path, os.W_OK):
            time_file_handler = CustomRotatingFileHandler(
                os.path.join(LogCfg.path, f'iw-algo-fx.log'),
                maxBytes=1024 * 1024 * 100,
                backupCount=100)
            time_file_handler.setLevel(LogCfg.level)
            time_file_handler.setFormatter(
                logging.Formatter(LogCfg.format)
            )
            root_logger.addHandler(time_file_handler)

        # Setup the logger to write into stdout
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(ColoredFormatter(LogCfg.colorful_format))
        root_logger.addHandler(consoleHandler)

        logging.Logger.root = root_logger
        logging.root = logging.Logger.root
        logging.Logger.manager = logging.Manager(logging.Logger.root)
        logging.root.setLevel(LogCfg.level)
        logging.LogRecord.traceid = '0'

        inject_level(LogCfg.level)
        logging.info("root logger init, level:%s", logging.getLevelName(LogCfg.level))

    def __init__(self):
        self.framework_logger = self._get_logger(
            "Framework Log", level=LogCfg.level, filename="iw-algo-fx-framework.log")
        self.user_logger = self._get_logger(
            "Algorithm Log", level=LogCfg.level, filename="iw-algo-fx-user.log")

    @staticmethod
    def _get_logger(logger_type, level=logging.INFO, format=None, filename=None):
        logger = logging.getLogger(logger_type)
        logger.addFilter(TraceIDFilter())

        if logger.handlers:
            return logger

        format = format or LogCfg.colorful_format
        if filename is not None:
            if os.access(LogCfg.path, os.W_OK):
                time_file_handler = CustomRotatingFileHandler(
                    os.path.join(LogCfg.path, filename),
                    maxBytes=1024 * 1024 * 50,
                    backupCount=30)
                formatter = ColoredFormatter(
                    format, datefmt=LogCfg.data_format)
                time_file_handler.setLevel(level)
                time_file_handler.setFormatter(formatter)
                logger.addHandler(time_file_handler)
        return logger


def _get_framework_logger():
    global framework_logger
    if framework_logger is None:
        framework_logger = Logger().framework_logger
    return framework_logger


def _get_algorithm_logger():
    global user_logger
    if user_logger is None:
        user_logger = Logger().user_logger
    return user_logger


def get_logger(name: str = "user", level: str = "INFO", format: str = None, filename: str = None):
    """get custom logs

    Args:
        name (str, optional): Logger unique name. Defaults to "user".
        level (str, optional): Logger level. Defaults to "INFO".
        format (str, optional): Format the specified record. Defaults to None.
        filename (str, optional): Save the name of the log file. Defaults to None.

    Returns:
        logger
    """
    return Logger()._get_logger(name, level, format, filename)
