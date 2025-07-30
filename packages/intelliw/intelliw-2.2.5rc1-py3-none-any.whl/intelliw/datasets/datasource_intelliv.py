'''
Author: hexu
Date: 2021-10-14 14:54:05
LastEditTime: 2023-05-19 16:10:09
LastEditors: Hexu
Description: 从智能服务获取模型数据集
FilePath: /iw-algo-fx/intelliw/datasets/datasource_intelliv.py
'''
from concurrent.futures import ThreadPoolExecutor
import os
import time

from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, \
    DatasetSelector, DataSourceType

from intelliw.utils import iuap_request
from intelliw.utils.logger import _get_framework_logger
from intelliw.config import config

logger = _get_framework_logger()


class DataSourceIntelliv(AbstractDataSource):
    """
    智能分析数据源
    """

    def __init__(self, input_address, get_row_address, input_model_id):
        """
        智能分析数据源
        :param input_address:   获取数据 url
        :param get_row_address: 获取数据总条数 url
        :param input_model_id:  读取的数据模型
        """
        self.input_address = input_address
        self.input_model_id = input_model_id
        self.get_row_address = f"{get_row_address}/{input_model_id}/null"

        self.__total = None

    def total(self):
        if self.__total is not None:
            return self.__total
        response = iuap_request.get(
            self.get_row_address, auth_type=iuap_request.AuthType.YHT)

        if 200 != response.status or response.json is None:
            msg = "获取行数失败，url: {}, response: {}".format(
                self.get_row_address, response)
            raise DataSourceReaderException(msg)

        row_data = response.json
        self.__total = row_data['data']
        if not isinstance(self.__total, int):
            msg = f"获取行数返回结果错误, response: {row_data}, request_url: {self.get_row_address}"
            raise DataSourceReaderException(msg)
        return self.__total

    def reader(self, page_size=100000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.input_address, self.input_model_id, self.total(), page_size, offset, limit,
                             transform_function)

    class __Reader:
        def __init__(self, input_address, input_model_id, total, page_size=10000, offset=0, limit=0,
                     transform_function=None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            self.input_address = input_address
            self.input_model_id = input_model_id
            self.total_rows = total
            self.total_read = 0
            self.page_size = max(100, page_size)
            self.page_num = 1
            self.meta = []
            self.after_transform = 0
            self.transform_function = transform_function
            self.worker = min(3, max(1, os.cpu_count()))
            logger.info('数据获取中: 启用的获取线程 %s 条', self.worker)

        def get_data_bar(self):
            """数据拉取进度条"""
            try:
                proportion = round(
                    (self.total_read / self.total_rows) * 100, 2)
                logger.info(
                    "数据获取中: 共%s条数据, 已获取%s条, 进度%s%%", self.total_rows, self.total_read, proportion)
            except:
                pass

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            if self.total_read >= self.total_rows:
                logger.info('数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                raise StopIteration

            self.get_data_bar()

            try:
                with ThreadPoolExecutor(max_workers=self.worker) as executor:
                    futures, data_result = [], []
                    for _ in range(self.worker * 2):
                        futures.append(executor.submit(
                            self._read_page, self.page_num, self.page_size
                        ))
                        self.page_num += 1

                    for task in futures:
                        data_result.extend(task.result())
                    self.total_read += len(data_result)
                    if len(data_result) == 0:
                        logger.info(
                            '数据下载完成，共读取原始数据 {} 条'.format(self.total_read))
                        raise StopIteration

                    return_data = {"result": data_result, "meta": self.meta}
                    if self.transform_function is not None:
                        return_data = self.transform_function(return_data)
                    return return_data
            except StopIteration:
                raise StopIteration
            except Exception as e:
                logger.exception("智能分析数据源读取失败, input_address: [{}], model_id: [{}]".
                                 format(self.input_address, self.input_model_id))
                raise DataSourceReaderException(f'智能分析数据源读取失败:{e}')

        def _get_meta(self, meta):
            if not self.meta:
                self.meta = meta
            return self.meta

        def _data_process(self, data):
            assert data is not None, "智能分析数据接口未返回任何有效数据"
            if len(data) > 0:
                self._get_meta(data['meta'])
            return data['result']

        def _read_page(self, page_index, page_size):
            """
            调用智能分析接口，分页读取数据
            :param page_index: 页码，从 1 开始
            :param page_size:  每页大小
            :return:
            """
            request_data = {
                "modelId": self.input_model_id,
                "pager": {
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "pageCount": 0,
                    "recordCount": 0
                },
                "signDTO": {"ak": config.ACCESS_KEY,
                            "sign": config.ACCESS_SECRET,
                            "ts": int(time.time() * 1000)}
            }
            response = iuap_request.post_json(
                url=self.input_address, json=request_data, timeout=30,
                auth_type=iuap_request.AuthType.YHT)
            response.raise_for_status()
            return self._data_process(response.json)


DatasetSelector.register_func(DataSourceType.INTELLIV, DataSourceIntelliv, {
    "input_address": "INPUT_ADDR",
    "get_row_address": "INPUT_GETROW_ADDR",
    "input_model_id": "INPUT_MODEL_ID"})
