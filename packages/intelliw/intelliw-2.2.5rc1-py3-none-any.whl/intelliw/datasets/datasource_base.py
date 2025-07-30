#!/usr/bin/env python
# coding: utf-8
'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-25 14:30:29
LastEditors: Hexu
Description: Algorithm -> DataSourceReader -> DataSource
FilePath: /iw-algo-fx/intelliw/datasets/datasource_base.py
'''

from collections.abc import Iterable
from abc import ABCMeta, abstractmethod
from intelliw.config import config
from intelliw.utils.logger import _get_framework_logger


logger = _get_framework_logger()


class DataSourceType:
    '''输入数据源类型'''
    # 大类
    # 空
    EMPTY = 0  
    # 表格类别
    TABLE_TYPE = 6  
    TABLE_TYPE_LIST = [1, 2, 3, 9]
    # 图像类别
    CV_TYPE = 7  
    CV_TYPE_LIST = [4]
    # 文本类别
    NLP_TYPE = 8  
    NLP_TYPE_LIST = [21]
    # 大模型类别
    LARGE_MODEL_LIST = [24]

    # 子类
    REMOTE_CSV = 1  # 远程csv
    INTELLIV = 2  # 智能分析
    LOCAL_CSV = 3  # 本地 csv
    IW_IMAGE_DATA = 4  # 图片数据源
    IW_FACTORY_DATA = 5  # 数据工场数据集
    NLP_CORPORA = 21  # nlp语料
    SEMANTIC = 9  # 语义模型

    LARGE_MODEL = 24  # 大模型

    SQL = 998
    USER = 999


class AlgorithmsType:
    '''算法类型'''
    CLASSIFICATION = 3  # 分类算法
    TIME_SERIES = 9  # 时间序列


class DatasetType:
    TRAIN = 'train_set'
    VALID = 'validation_set'
    TEST = 'test_set'


class AbstractDataSource(metaclass=ABCMeta):
    """
    数据源定义
    """

    @abstractmethod
    def total(self) -> int:
        """
        获取数据源总数据条数
        :return: 数据源总数据条数
        """
        pass

    @abstractmethod
    def reader(self, page_size=100000, offset=0, limit=0, transform_function=None,
               dataset_type='train_set') -> Iterable:
        """
        获取一个读取该数据源的 iterator
        :param page_size: 读取分页大小
        :param offset:    开始读取的数据 index
        :param limit:     读取条数
        :param transform_function: 转换函数
        :return: 数据源 iterator
        """
        pass


class DataSourceReaderException(Exception):
    def ignore_stack(self):
        return True


class DataSourceWriterException(Exception):
    def ignore_stack(self):
        return True


class AbstractDataSourceWriter(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.table_columns = None

    @abstractmethod
    def write(self, data, starttime):
        pass


class DatasetSelector:
    """
    DatasetSelector 
    """
    func = {}
    args = {}

    @classmethod
    def register_func(cls, key, value, args):
        cls.func[key] = value
        cls.args[key] = args

    @classmethod
    def parse(cls, cfg: dict) -> AbstractDataSource:
        stype = cfg["SOURCE_TYPE"]
        func = cls.func[stype]
        args = cls.args[stype]
        logger.info('\033[33mDatasetSelector: %s\033[0m', func.__name__)
        try:
            kwargs = cls._parse_args(args, cfg)
        except Exception:
            errmsg = f"Source Type: {stype}, Need Parameters: [{list(args.values())}]"
            raise DataSourceReaderException(errmsg)
        return func(**kwargs), stype

    @staticmethod
    def _parse_args(args: dict, cfg: dict) -> dict:
        kwargs = {}
        for param, key in args.items():
            if key == "INPUT_DATA_SOURCE_TRAIN_TYPE":
                value = cfg.get(key, getattr(config, key))
            elif isinstance(key, list):
                for _key in key:
                    value = cfg.get(_key)
                    if value:
                        break
            else:
                value = cfg[key]
            kwargs[param] = value
        return kwargs
